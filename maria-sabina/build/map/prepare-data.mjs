// Clips the raw Natural Earth 10m GeoJSON layers down to the North / Central
// America window the map sequence actually shows, and strips the properties
// the style does not use. Output goes to build/map/data/*.geojson.
//
// Usage: node maria-sabina/build/map/prepare-data.mjs [rawDir] [outDir]
// Raw files come from ./fetch-map-data.sh (GitHub mirror of Natural Earth).
import fs from "node:fs";
import path from "node:path";
import bboxClip from "@turf/bbox-clip";
import difference from "@turf/difference";
import ellipse from "@turf/ellipse";
import union from "@turf/union";

const RAW = process.argv[2] || "maria-sabina/build/map/data/raw/ne";
const OUT = process.argv[3] || "maria-sabina/build/map/data";

// lon min, lat min, lon max, lat max
const WIDE = [-140, 2, -50, 62]; // wide North America shot
const MEXICO = [-108, 13, -84, 27]; // mid and tight zooms

function bounds(c, b = [Infinity, Infinity, -Infinity, -Infinity]) {
  if (typeof c[0] === "number") {
    if (c[0] < b[0]) b[0] = c[0];
    if (c[1] < b[1]) b[1] = c[1];
    if (c[0] > b[2]) b[2] = c[0];
    if (c[1] > b[3]) b[3] = c[1];
  } else for (const x of c) bounds(x, b);
  return b;
}
const hits = (b, box) =>
  !(b[2] < box[0] || b[0] > box[2] || b[3] < box[1] || b[1] > box[3]);

function round(c) {
  if (typeof c[0] === "number")
    return [Math.round(c[0] * 1e4) / 1e4, Math.round(c[1] * 1e4) / 1e4];
  return c.map(round);
}

// bbox-clip can leave empty polygons behind; MapLibre's tiler throws on them.
function cleanPolygons(f) {
  const g = f.geometry;
  if (!g) return null;
  if (g.type === "Polygon") {
    const rings = g.coordinates.filter((r) => r && r.length >= 4);
    return rings.length ? { ...f, geometry: { type: "Polygon", coordinates: rings } } : null;
  }
  if (g.type === "MultiPolygon") {
    const polys = g.coordinates.map((p) => p.filter((r) => r && r.length >= 4)).filter((p) => p.length);
    return polys.length ? { ...f, geometry: { type: "MultiPolygon", coordinates: polys } } : null;
  }
  return f;
}

const layers = {
  // 10m country polygons give a coastline that still holds up at zoom 7.
  land: {
    file: "ne_10m_admin_0_countries",
    box: WIDE,
    props: ["ADMIN", "ADM0_A3"],
  },
  boundaries: {
    file: "ne_10m_admin_0_boundary_lines_land",
    box: WIDE,
    props: ["FEATURECLA"],
  },
  states: {
    file: "ne_10m_admin_1_states_provinces_lines",
    box: WIDE,
    props: ["ADM0_A3"],
    keep: (p) => ["MEX", "USA", "CAN", "GTM"].includes(p.ADM0_A3),
  },
  lakes: {
    file: "ne_10m_lakes",
    box: WIDE,
    props: ["name", "scalerank"],
    keep: (p) => p.scalerank <= 7,
  },
};

fs.mkdirSync(OUT, { recursive: true });
for (const [name, L] of Object.entries(layers)) {
  const src = path.join(RAW, L.file + ".geojson");
  const fc = JSON.parse(fs.readFileSync(src, "utf8"));
  const out = [];
  for (let f of fc.features) {
    if (!f.geometry) continue;
    if (L.keep && !L.keep(f.properties)) continue;
    if (!hits(bounds(f.geometry.coordinates), L.box)) continue;
    if (L.clip) f = cleanPolygons(bboxClip(f, L.box));
    if (!f || !f.geometry || !f.geometry.coordinates.length) continue;
    const props = {};
    for (const k of L.props) if (k in f.properties) props[k] = f.properties[k];
    out.push({
      type: "Feature",
      properties: props,
      geometry: { type: f.geometry.type, coordinates: round(f.geometry.coordinates) },
    });
  }
  const dst = path.join(OUT, name + ".geojson");
  fs.writeFileSync(dst, JSON.stringify({ type: "FeatureCollection", features: out }));
  const kb = Math.round(fs.statSync(dst).size / 1024);
  console.log(`${name.padEnd(11)} ${String(out.length).padStart(6)} features ${String(kb).padStart(7)} KB`);
}


const landFC = JSON.parse(fs.readFileSync(path.join(OUT, "land.geojson"), "utf8"));

// ---- spotlight subjects ----
// The dim layer covers everything except the subject: Mexico for shots 02-03,
// then Oaxaca, then the Sierra Mazateca. Each dim is the region between one
// subject and the next, so the three never stack.
const fc = (features) => ({ type: "FeatureCollection", features });
const write = (name, geo) => {
  const dst = path.join(OUT, name + ".geojson");
  fs.writeFileSync(dst, JSON.stringify(geo));
  console.log(`${name.padEnd(11)} ${String(Math.round(fs.statSync(dst).size / 1024)).padStart(7)} KB`);
};
const strip = (f, props = {}) => ({ type: "Feature", properties: props, geometry: { type: f.geometry.type, coordinates: round(f.geometry.coordinates) } });
const countries = JSON.parse(fs.readFileSync(path.join(RAW, "ne_10m_admin_0_countries.geojson"), "utf8"));
const mexico = strip(countries.features.find((f) => f.properties.ADMIN === "Mexico"), { name: "Mexico" });
const states = JSON.parse(fs.readFileSync(path.join(RAW, "ne_10m_admin_1_states_provinces.geojson"), "utf8"));
const oaxaca = strip(states.features.find((f) => f.properties.adm0_a3 === "MEX" && f.properties.name === "Oaxaca"), { name: "Oaxaca" });
// The Sierra Mazateca runs NW-SE above Huautla; an ellipse is close enough for a spotlight edge.
const sierra = strip(ellipse([-96.83, 18.17], 46, 28, { units: "kilometers", angle: -35, steps: 96 }), { name: "Sierra Mazateca" });
const world = { type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [[[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]]] } };
const diff = (a, b) => { try { return difference(fc([a, b])); } catch (e) { return difference(a, b); } };
write("subject-mexico", fc([mexico]));
write("subject-oaxaca", fc([oaxaca]));
write("subject-sierra", fc([sierra]));
write("dim-world", fc([diff(world, mexico)]));
write("dim-mexico", fc([diff(mexico, oaxaca)]));
write("dim-oaxaca", fc([diff(oaxaca, sierra)]));

// ---- ocean: the window minus every land polygon ----
// Drawn above the hillshade so seabed relief never shows. Built as a
// difference rather than by clipping Natural Earth's ocean polygon, which
// leaves sliver triangles along the clip edges.
{
  const landPolys = fc(landFC.features.map((f) => ({ type: "Feature", properties: {}, geometry: f.geometry })));
  let merged;
  try { merged = union(landPolys); } catch (e) { merged = landPolys.features.reduce((a, b) => union(a, b)); }
  const win = { type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [[[WIDE[0] - 5, WIDE[1] - 5], [WIDE[2] + 5, WIDE[1] - 5], [WIDE[2] + 5, WIDE[3] + 5], [WIDE[0] - 5, WIDE[3] + 5], [WIDE[0] - 5, WIDE[1] - 5]]] } };
  const ocean = diff(win, merged);
  write("ocean", fc([{ type: "Feature", properties: {}, geometry: { type: ocean.geometry.type, coordinates: round(ocean.geometry.coordinates) } }]));
}
