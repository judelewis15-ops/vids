// Series intro shot, a pure function of time. Loaded into index.html?fly=<pin>
// by scripts/shoot-intro.mjs, which then calls window.__shot.setTime(t) once
// per frame and screenshots. Timeline (seconds, defaults):
//   0.00  hold on the fitted globe, tiny drift
//   0.40  whip: fly from the globe into the pin, camera tilting as it lands
//   1.25  land; region fills in, pin pulses, leader line and label pop
//   1.25+ slow tilted push south (hands off to the landscape shot)
(() => {
  const O = window.__origin;
  const map = O.map;
  const cfg = Object.assign(
    {
      pin: O.pinId,
      region: null, // GeoJSON path to highlight, e.g. data/regions/kwazulu-natal.json
      hold: 0.4,
      whip: 0.85,
      end: 4.0,
      landZoom: 6.7,
      endZoom: 7.6,
      landPitch: 50, // swoop in tilted, looking toward the horizon
      endPitch: 20, // then tilt down onto the land as the next shot will
      driftLat: -0.3, // degrees south over the settle, moving with the tilt
      liftPx: 240, // pin sits this far below centre so the label has room
      leader: [60, -175], // leader line end, px from the pin (clamped to the frame)
    },
    window.__shotConfig || {},
  );

  const props = O.props(cfg.pin) || {};
  const pinLL = O.coordsOf(cfg.pin);
  if (!pinLL) throw new Error("intro-shot: unknown pin " + cfg.pin);
  const c0 = map.getCenter();
  const start = { lng: c0.lng, lat: c0.lat, zoom: map.getZoom() };

  const clamp01 = (v) => Math.min(1, Math.max(0, v));
  const lerp = (a, b, u) => a + (b - a) * u;
  const easeInOutExpo = (u) =>
    u <= 0 ? 0 : u >= 1 ? 1 : u < 0.5
      ? Math.pow(2, 20 * u - 10) / 2
      : (2 - Math.pow(2, -20 * u + 10)) / 2;
  const easeOutCubic = (u) => 1 - Math.pow(1 - u, 3);
  const smooth = (u) => u * u * (3 - 2 * u);
  const spring = (u) => 1 - Math.pow(2, -10 * u) * Math.cos(u * Math.PI * 2.5);
  const win = (t, t0, dur) => clamp01((t - t0) / dur);

  // ---- Region highlight layers (below the pins) ----
  if (cfg.region) {
    fetch(cfg.region)
      .then((r) => r.json())
      .then((geo) => {
        map.addSource("shot-region", { type: "geojson", data: geo });
        map.addLayer(
          {
            id: "shot-region-fill",
            type: "fill",
            source: "shot-region",
            paint: { "fill-color": "#7C3AED", "fill-opacity": 0 },
          },
          "pin-glow",
        );
        map.addLayer(
          {
            id: "shot-region-line",
            type: "line",
            source: "shot-region",
            paint: {
              "line-color": "#1A0B2E",
              "line-width": 3,
              "line-opacity": 0,
            },
          },
          "pin-glow",
        );
        document.body.dataset.shotRegion = "1";
      });
  } else document.body.dataset.shotRegion = "1";

  // ---- Overlay: pulse ring, leader line, label ----
  const css = document.createElement("style");
  css.textContent = `
    @font-face { font-family: "Anton"; src: url(fonts/anton.woff2) format("woff2"); }
    @font-face { font-family: "Mont"; font-weight: 500; src: url(fonts/mont.woff2) format("woff2"); }
    @font-face { font-family: "Mont"; font-weight: 700; src: url(fonts/mont7.woff2) format("woff2"); }
    .shot { position: absolute; inset: 0; pointer-events: none; z-index: 5; overflow: hidden; }
    .shot-pulse { position: absolute; width: 44px; height: 44px; margin: -22px 0 0 -22px;
      border: 3px solid #1A0B2E; border-radius: 50%; opacity: 0; }
    .shot-leader { position: absolute; height: 4px; background: #1A0B2E; transform-origin: 0 50%;
      border-radius: 2px; }
    .shot-leader::after { content: ""; position: absolute; right: -6px; top: -4px; width: 12px; height: 12px;
      border-radius: 50%; background: #1A0B2E; }
    .shot-tag { position: absolute; width: max-content; max-width: 460px; padding: 20px 26px 22px 24px; background: #FAF7F2;
      color: #1A0B2E; border-left: 8px solid #7C3AED; border-radius: 6px;
      box-shadow: 0 18px 40px rgba(26,11,46,.18), 0 2px 6px rgba(26,11,46,.12);
      transform-origin: 0 100%; opacity: 0; }
    .shot-eyebrow { font: 700 19px/1.3 "Mont", "DM Sans", sans-serif; letter-spacing: .14em;
      text-transform: uppercase; color: #7C3AED; margin: 0 0 10px; }
    .shot-name { font: 400 62px/.95 "Anton", "Bebas Neue", Impact, sans-serif; text-transform: uppercase;
      letter-spacing: .01em; margin: 0; }
    .shot-latin { font: italic 500 24px/1.2 "Mont", "DM Sans", sans-serif; color: rgba(26,11,46,.62);
      margin: 10px 0 0; }
  `;
  document.head.appendChild(css);

  const overlay = document.createElement("div");
  overlay.className = "shot";
  overlay.innerHTML = `
    <div class="shot-pulse"></div><div class="shot-pulse"></div>
    <div class="shot-leader"></div>
    <div class="shot-tag">
      <p class="shot-eyebrow"></p>
      <h1 class="shot-name"></h1>
      <p class="shot-latin"></p>
    </div>`;
  document.getElementById("map").appendChild(overlay);
  const pulses = [...overlay.querySelectorAll(".shot-pulse")];
  const leader = overlay.querySelector(".shot-leader");
  const tag = overlay.querySelector(".shot-tag");
  const eyebrow = overlay.querySelector(".shot-eyebrow");
  eyebrow.replaceChildren(
    ...[props.region, props.country].filter(Boolean).flatMap((s, i) =>
      i ? [document.createElement("br"), s] : [s],
    ),
  );
  overlay.querySelector(".shot-name").textContent = props.name || cfg.pin;
  overlay.querySelector(".shot-latin").textContent = props.latin || "";
  const gloss = document.querySelector(".gloss");

  const tLand = cfg.hold + cfg.whip;

  function setTime(t) {
    // ---- Camera ----
    let lng, lat, zoom, pitch, lift;
    if (t < cfg.hold) {
      const u = t / cfg.hold;
      lng = start.lng; lat = start.lat;
      zoom = start.zoom + 0.06 * u;
      pitch = 0; lift = 0;
    } else if (t < tLand) {
      const u = easeInOutExpo((t - cfg.hold) / cfg.whip);
      lng = lerp(start.lng, pinLL[0], u);
      lat = lerp(start.lat, pinLL[1], u);
      zoom = lerp(start.zoom + 0.06, cfg.landZoom, u);
      pitch = cfg.landPitch * smooth(win((t - cfg.hold) / cfg.whip, 0.5, 0.5));
      lift = cfg.liftPx * u;
    } else {
      const v = easeOutCubic(win(t, tLand, cfg.end - tLand)) * 0.6 + 0.4 * win(t, tLand, cfg.end - tLand);
      lng = pinLL[0];
      lat = pinLL[1] + cfg.driftLat * v;
      zoom = lerp(cfg.landZoom, cfg.endZoom, v);
      pitch = lerp(cfg.landPitch, cfg.endPitch, v);
      lift = cfg.liftPx;
    }
    map.jumpTo({
      center: [lng, lat],
      zoom,
      pitch,
      bearing: 0,
      padding: { top: lift * 2, bottom: 0, left: 0, right: 0 },
    });
    if (gloss) gloss.style.opacity = String(1 - win(t, cfg.hold, 0.35));

    // ---- Region highlight ----
    if (map.getLayer("shot-region-fill")) {
      const r = easeOutCubic(win(t, tLand - 0.2, 0.35));
      map.setPaintProperty("shot-region-fill", "fill-opacity", 0.28 * r);
      map.setPaintProperty("shot-region-line", "line-opacity", 0.95 * r);
    }

    // ---- Pin-anchored overlay ----
    const p = map.project(pinLL);
    pulses.forEach((el, i) => {
      const u = win(t, tLand + i * 0.35, 0.8);
      const on = t >= tLand + i * 0.35 && u < 1;
      el.style.opacity = on ? String(0.7 * (1 - u)) : "0";
      el.style.transform = `translate(${p.x}px, ${p.y}px) scale(${1 + 3.2 * easeOutCubic(u)})`;
    });

    const [dx0, dy] = cfg.leader;
    // Keep the card inside the frame: slide it left if it would overflow,
    // and let the leader line follow.
    const W = map.getContainer().clientWidth;
    const cardW = tag.offsetWidth || 440;
    const cardLeft = Math.max(40, Math.min(p.x + dx0, W - 40 - cardW));
    const dx = cardLeft - p.x;
    const len = Math.hypot(dx, dy);
    const ang = (Math.atan2(dy, dx) * 180) / Math.PI;
    const lu = easeOutCubic(win(t, tLand + 0.05, 0.28));
    leader.style.opacity = lu > 0 ? "1" : "0";
    leader.style.transform = `translate(${p.x}px, ${p.y - 2}px) rotate(${ang}deg) scaleX(${lu})`;
    leader.style.width = `${len}px`;

    const tu = win(t, tLand + 0.26, 0.45);
    const sc = tu <= 0 ? 0.6 : lerp(0.6, 1, spring(tu));
    tag.style.opacity = String(clamp01(tu * 4));
    tag.style.left = `${p.x + dx}px`;
    tag.style.top = `${p.y + dy}px`;
    tag.style.transform = `translate(0, -100%) scale(${sc})`;
  }

  window.__shot = { setTime, cfg, tLand };
  document.body.dataset.shotReady = "1";
})();
