/* global maplibregl */
// HO01 map, shots 02-04. Art direction: Harris / Vox Borders. Near-black base
// with a purple cast, one lit subject (Mexico -> Oaxaca -> Sierra Mazateca),
// everything else dimmed, a violet arc that draws on from New York, terrain
// that rises into the frame as the camera tilts. One continuous move.
//
// render-frames.mjs steps window.__ms.renderFrame(f) per frame; every frame is
// a pure function of its index so the export is deterministic. Nothing here
// is time-based. Labels and markers render in the page so they sit under the
// grain added in post.

const Q = new URLSearchParams(location.search);
const W = +(Q.get("w") || 1080), H = +(Q.get("h") || 1920);
// The art direction gives sizes in px for a 1080-wide design (11px city labels,
// 4px marker cores, 2px route). Those are scaled up so they survive a phone
// screen; pass textScale=1 / lineScale=1 for the literal values.
const TEXT_SCALE = +(Q.get("textScale") || 2.2);
const LINE_SCALE = +(Q.get("lineScale") || 1.4);
const stage = document.getElementById("stage");
stage.style.width = `${W}px`; stage.style.height = `${H}px`;
document.documentElement.style.setProperty("--s", TEXT_SCALE);

const FPS = 60;
const TOTAL = 480;                  // 8 s across shots 02 (0:07-0:09), 03 (0:09-0:12), 04 (0:12-0:15)
const SHOT3 = 120, SHOT4 = 300;     // frame each shot starts
const SETTLE = TOTAL - 48;          // last 800 ms: almost static, the label lands
const FADE = 36;                    // 600 ms spotlight fades
const STAGE_OAXACA = SHOT4;         // spotlight tightens to Oaxaca
const STAGE_SIERRA = SHOT4 + 90;    // then to the Sierra Mazateca

const NY = [-74.006, 40.7128];
const HUAUTLA = [-96.8431, 18.1308];

// Camera. Start: North America, New York in the upper right third.
const START = { center: [-92.5, 28.5], zoom: 3.5 };
const END = { center: HUAUTLA, zoom: 10.6, pitch: 58, bearing: -12 };
const PITCH_FROM_ZOOM = 6.6;        // state level: the tilt begins here
// Huautla lands just below centre: the padded centre sits low in the frame.
const PADDING = { top: Math.round(H * 0.16), bottom: 0, left: 0, right: 0 };
const ARC_BOW = +(Q.get("arcBow") || 0.14); // how far the arc bows off the great circle (0 = pure great circle)

// Palette. Contrast first: slate land on near-black water, ridge highlights that
// read from across the room, violet as the only colour. (The purple cast from the
// first pass was optional and is gone.)
const C = { water: "#07080C", land: "#2B303B", cream: "#FAF7F2", violet: "#7C3AED",
            shadow: "#04050A", highlight: "#B4BCCB", accent: "#4A5162", dim: "#07080C", lit: "#3A4150" };

// ---------- easing ----------
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const cubicOut = (t) => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
// CSS cubic-bezier(x1,y1,x2,y2) solved for y at time t.
function bezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (u) => ((ax * u + bx) * u + cx) * u, sy = (u) => ((ay * u + by) * u + cy) * u;
  return (t) => {
    t = clamp(t, 0, 1);
    let u = t;
    for (let i = 0; i < 8; i++) { const d = sx(u) - t; if (Math.abs(d) < 1e-5) break; u -= d / ((3 * ax * u + 2 * bx) * u + cx || 1e-6); }
    return sy(clamp(u, 0, 1));
  };
}
const zoomEase = bezier(0.6, 0, 0.12, 1);   // slow start, fast middle, long settle

const merc = ([lng, lat]) => {
  const s = Math.sin((lat * Math.PI) / 180);
  return [(lng + 180) / 360, 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)];
};
const unmerc = ([x, y]) => [x * 360 - 180, (Math.atan(Math.sinh(Math.PI * (1 - 2 * y))) * 180) / Math.PI];

// ---------- route: great circle, bowed a little so it reads as an arc ----------
function greatCircle(a, b, n) {
  const toR = (d) => (d * Math.PI) / 180, toD = (r) => (r * 180) / Math.PI;
  const [l1, p1] = [toR(a[0]), toR(a[1])], [l2, p2] = [toR(b[0]), toR(b[1])];
  const d = 2 * Math.asin(Math.sqrt(Math.sin((p2 - p1) / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin((l2 - l1) / 2) ** 2));
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const f = i / n, A = Math.sin((1 - f) * d) / Math.sin(d), B = Math.sin(f * d) / Math.sin(d);
    const x = A * Math.cos(p1) * Math.cos(l1) + B * Math.cos(p2) * Math.cos(l2);
    const y = A * Math.cos(p1) * Math.sin(l1) + B * Math.cos(p2) * Math.sin(l2);
    const z = A * Math.sin(p1) + B * Math.sin(p2);
    pts.push([toD(Math.atan2(y, x)), toD(Math.atan2(z, Math.sqrt(x * x + y * y)))]);
  }
  return pts;
}
function bowed(pts, bow) {
  if (!bow) return pts;
  const a = merc(pts[0]), b = merc(pts[pts.length - 1]);
  const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy);
  const nx = dy / len, ny = -dx / len; // perpendicular, bowing toward the Gulf
  return pts.map((p, i) => {
    const t = i / (pts.length - 1), m = merc(p), k = bow * len * Math.sin(Math.PI * t);
    return unmerc([m[0] + nx * k, m[1] + ny * k]);
  });
}
const ROUTE = bowed(greatCircle(NY, HUAUTLA, 400), ARC_BOW);
function routeAt(p) {
  const n = ROUTE.length - 1, i = Math.floor(p * n), r = p * n - i;
  if (i >= n) return ROUTE[n];
  return [lerp(ROUTE[i][0], ROUTE[i + 1][0], r), lerp(ROUTE[i][1], ROUTE[i + 1][1], r)];
}
function routeSlice(p) {
  if (p <= 0) return { type: "FeatureCollection", features: [] };
  const n = ROUTE.length - 1, i = Math.floor(p * n);
  const pts = ROUTE.slice(0, Math.min(i, n) + 1);
  if (i < n) pts.push(routeAt(p));
  return { type: "FeatureCollection", features: [{ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: pts } }] };
}
const drawProgress = (f) => cubicOut((f - SHOT3) / (SHOT4 - SHOT3)); // draws on over shot 03

// ---------- camera ----------
function baseCamera(f) {
  if (f < SHOT3) {
    const t = f / SHOT3;
    return { center: START.center, zoom: START.zoom + 0.04 * cubicOut(t), pitch: 0, bearing: 0, t: 0 };
  }
  const z0 = START.zoom + 0.04;
  const t = (f - SHOT3) / (TOTAL - SHOT3);
  const e = zoomEase(t);
  const zoom = lerp(z0, END.zoom, e);
  // Target glide: the destination's screen offset shrinks with the zoom, so
  // Huautla slides to centre while the arc draws on toward it.
  const c0 = merc(START.center), c1 = merc(END.center);
  const k = (1 - e) * Math.pow(2, z0 - zoom);
  const center = unmerc([c1[0] - (c1[0] - c0[0]) * k, c1[1] - (c1[1] - c0[1]) * k]);
  const bearing = END.bearing * cubicOut((f - SHOT3) / (SETTLE - SHOT3));
  return { center, zoom, pitch: 0, bearing, t };
}
// The tilt starts the frame the zoom passes state level and is done by the settle.
let PITCH_START = SHOT4;
for (let f = SHOT3; f < TOTAL; f++) if (baseCamera(f).zoom >= PITCH_FROM_ZOOM) { PITCH_START = f; break; }
function cameraAt(f) {
  const cam = baseCamera(f);
  cam.pitch = END.pitch * cubicOut((f - PITCH_START) / (SETTLE - PITCH_START));
  return cam;
}

// ---------- style ----------
const DEM = {
  type: "raster-dem",
  tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
  encoding: "terrarium", tileSize: 256, maxzoom: 13,
  attribution: "Terrain: Mapzen / AWS Terrain Tiles",
};
const EMPTY = { type: "FeatureCollection", features: [] };
const zi = (...stops) => ["interpolate", ["linear"], ["zoom"], ...stops];
const g = (name) => ({ type: "geojson", data: `/data/${name}.geojson` });
const hairline = () => ({ "line-color": C.cream, "line-opacity": 0.28, "line-width": 0.7 });

const style = {
  version: 8,
  sky: { "sky-color": "#07080C", "horizon-color": "#14161D", "fog-color": "#0E1016",
         "fog-ground-blend": 0.55, "horizon-fog-blend": 0.85, "sky-horizon-blend": 0.9, "atmosphere-blend": 0 },
  sources: {
    land: g("land"), ocean: g("ocean"), lakes: g("lakes"), boundaries: g("boundaries"), states: g("states"),
    litOaxaca: g("subject-oaxaca"), dimWorld: g("dim-world"), dimMexico: g("dim-mexico"), dimOaxaca: g("dim-oaxaca"),
    dem: DEM, demTerrain: DEM, route: { type: "geojson", data: EMPTY },
  },
  layers: [
    { id: "water", type: "background", paint: { "background-color": C.water } },
    { id: "land", type: "fill", source: "land", paint: { "fill-color": C.land } },
    { id: "hillshade", type: "hillshade", source: "dem",
      paint: { "hillshade-shadow-color": C.shadow, "hillshade-highlight-color": C.highlight, "hillshade-accent-color": C.accent,
               "hillshade-illumination-direction": 315, "hillshade-illumination-anchor": "map",
               "hillshade-exaggeration": zi(3, 0.55, 6, 0.8, 9, 1) } },
    { id: "ocean", type: "fill", source: "ocean", paint: { "fill-color": C.water } },
    { id: "lakes", type: "fill", source: "lakes", paint: { "fill-color": C.water } },
    { id: "lit-oaxaca", type: "fill", source: "litOaxaca", paint: { "fill-color": C.lit, "fill-opacity": 0 } },
    { id: "states", type: "line", source: "states", paint: hairline() },
    { id: "boundaries", type: "line", source: "boundaries", paint: hairline() },
    { id: "dim-world", type: "fill", source: "dimWorld", paint: { "fill-color": C.dim, "fill-opacity": 0 } },
    { id: "dim-mexico", type: "fill", source: "dimMexico", paint: { "fill-color": C.dim, "fill-opacity": 0 } },
    { id: "dim-oaxaca", type: "fill", source: "dimOaxaca", paint: { "fill-color": C.dim, "fill-opacity": 0 } },
    { id: "route-glow", type: "line", source: "route", layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": C.violet, "line-width": 8 * LINE_SCALE, "line-opacity": 0.35, "line-blur": 3 * LINE_SCALE } },
    { id: "route", type: "line", source: "route", layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": C.violet, "line-width": 2 * LINE_SCALE, "line-opacity": 1 } },
  ],
};

// ---------- overlays (labels, markers) ----------
const overlay = document.getElementById("overlay");
const el = (cls, html = "") => { const d = document.createElement("div"); d.className = cls; d.innerHTML = html; overlay.appendChild(d); return d; };
const S = TEXT_SCALE;
const CONNECT = 26 * S; // hairline length, 45 degrees up-right
function marker(name, side = 1) {
  const m = { core: el("core"), ring: el("ring"), connector: el("connector"), label: el("lbl city", name), side };
  if (side < 0) { m.connector.style.transform = "rotate(-135deg)"; m.label.style.transform = "translateX(-100%)"; }
  return m;
}
const ny = marker("New York", 1);
const hu = marker("Huautla de Jiménez", -1);
const sierraLbl = el("lbl region", "Sierra Mazateca");
const tip = el("tip");

function place(node, lngLat, dx = 0, dy = 0) {
  const p = map.project(lngLat);
  node.style.left = `${p.x + dx}px`; node.style.top = `${p.y + dy}px`;
  return p;
}
// Label: fade + 6px slide from the left over 300 ms.
function labelIn(node, f, at, out = Infinity) {
  const i = cubicOut((f - at) / 18), o = 1 - cubicOut((f - out) / 18);
  const a = i * o;
  node.style.opacity = a * (node.classList.contains("region") ? 0.6 : 1);
  return a;
}
// Marker: core pops, cream ring pulses outward once on arrival, then holds thin.
function markerAt(m, lngLat, f, at, labelAt, labelOut = Infinity) {
  const p = place(m.core, lngLat);
  m.core.style.opacity = cubicOut((f - at) / 6);
  const pulse = clamp((f - at) / 42, 0, 1);
  const arrived = f >= at;
  const scale = arrived ? (pulse < 1 ? 1 + 4.5 * cubicOut(pulse) : 2.6) : 0;
  place(m.ring, lngLat);
  m.ring.style.transform = `translate(-50%,-50%) scale(${scale})`;
  m.ring.style.opacity = !arrived ? 0 : pulse < 1 ? 0.9 * (1 - pulse) + 0.6 * pulse : 0.6;
  const a = labelIn(m.label, f, labelAt, labelOut);
  m.connector.style.opacity = a * 0.4 / 0.4;
  m.connector.style.width = `${CONNECT * a}px`;
  m.connector.style.left = `${p.x}px`; m.connector.style.top = `${p.y}px`;
  const ex = p.x + m.side * CONNECT * Math.SQRT1_2, ey = p.y - CONNECT * Math.SQRT1_2;
  m.label.style.left = `${ex + m.side * 6 * S - 6 * (1 - a)}px`;
  m.label.style.top = `${ey - 7 * S}px`;
  return { x: ex, y: ey, a };
}

function updateOverlays(f) {
  // Shot 02: New York arrives, label follows. Shot 03: label gone while the line draws.
  markerAt(ny, NY, f, 6, 14, SHOT3);
  // Leading dot on the arc while it draws.
  const p = drawProgress(f);
  if (f >= SHOT3 && f < SHOT4) { place(tip, routeAt(p)); tip.style.opacity = 1; } else tip.style.opacity = 0;
  // Shot 04: Huautla arrives as the line lands; labels land in the settle, staggered.
  const hp = markerAt(hu, HUAUTLA, f, SHOT4, SETTLE);
  const a2 = labelIn(sierraLbl, f, SETTLE + 12);
  sierraLbl.style.transform = "translateX(-100%)";
  sierraLbl.style.left = `${hp.x - 6 * S - 6 * (1 - a2)}px`;
  sierraLbl.style.top = `${hp.y - 7 * S + 15 * S}px`;
}

// ---------- spotlight ----------
function updateSpotlight(f) {
  const dim = 0.62;
  map.setPaintProperty("dim-world", "fill-opacity", dim * cubicOut(f / FADE));
  map.setPaintProperty("dim-mexico", "fill-opacity", dim * cubicOut((f - STAGE_OAXACA) / FADE));
  map.setPaintProperty("dim-oaxaca", "fill-opacity", dim * cubicOut((f - STAGE_SIERRA) / FADE));
  // The lit state gets a faint fill for as long as it is the subject.
  const lit = 0.35 * cubicOut((f - STAGE_OAXACA) / FADE) * (1 - cubicOut((f - STAGE_SIERRA) / FADE));
  map.setPaintProperty("lit-oaxaca", "fill-opacity", lit);
}

// ---------- map ----------
const map = new maplibregl.Map({
  container: "map", style, center: START.center, zoom: START.zoom, pitch: 0, bearing: 0,
  interactive: false, attributionControl: false, fadeDuration: 0,
  antialias: true, preserveDrawingBuffer: true, maxPitch: 70,
});
let loaded = false, terrainOn = false;
map.on("error", (e) => console.error("map error:", e.error ? (e.error.stack || e.error.message) : JSON.stringify(e)));
map.on("load", () => { loaded = true; });
function setTerrain(on) {
  if (on === terrainOn) return;
  try { map.setTerrain(on ? { source: "demTerrain", exaggeration: 1.8 } : null); terrainOn = on; }
  catch (e) { console.error("terrain:", e.message); }
}
function idle() {
  return new Promise((resolve) => {
    const timer = setTimeout(resolve, 60000);
    map.once("idle", () => { clearTimeout(timer); resolve(); });
    map.triggerRepaint();
  });
}

async function renderFrame(f) {
  const cam = cameraAt(f);
  setTerrain(cam.zoom >= PITCH_FROM_ZOOM);
  map.jumpTo({ center: cam.center, zoom: cam.zoom, pitch: cam.pitch, bearing: cam.bearing, padding: PADDING });
  map.getSource("route").setData(routeSlice(drawProgress(f)));
  updateSpotlight(f);
  updateOverlays(f);
  await idle();
  updateOverlays(f); // re-project once terrain has settled the screen positions
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  return cam;
}

window.__ms = { get loaded() { return loaded; }, FPS, TOTAL, PITCH_START, cameraAt, renderFrame };
