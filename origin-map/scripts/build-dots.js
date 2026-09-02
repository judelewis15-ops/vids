#!/usr/bin/env node
/* Generate data/land-dots.json: a lattice of points that fall on land.

   Land polygons are Natural Earth 1:110m. The script downloads the GeoJSON
   from the Natural Earth vector repo; if that is unreachable it falls back to
   the same dataset bundled in the world-atlas npm package (TopoJSON).

   Usage: node scripts/build-dots.js [--spacing 0.9] [--no-cos]

   By default longitude spacing is scaled by 1/cos(latitude) so dot density
   stays even across the sphere instead of bunching at the poles. Pass --no-cos
   for a plain lattice. */

const fs = require("fs");
const path = require("path");
const https = require("https");
const booleanPointInPolygon = require("@turf/boolean-point-in-polygon").default;

const SOURCE_URL =
  "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson";
const OUT = path.join(__dirname, "..", "data", "land-dots.json");

const args = process.argv.slice(2);
const spacing = Number(args[args.indexOf("--spacing") + 1]) || 0.9;
const cosScale = !args.includes("--no-cos");
const LAT_MIN = -60;
const LAT_MAX = 84;

const round2 = (n) => Math.round(n * 100) / 100;

function download(url) {
  return new Promise((resolve, reject) => {
    https
      .get(
        url,
        { headers: { "user-agent": "origin-map-build-dots" } },
        (res) => {
          if (res.statusCode !== 200)
            return reject(new Error(`HTTP ${res.statusCode}`));
          const chunks = [];
          res.on("data", (c) => chunks.push(c));
          res.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
        },
      )
      .on("error", reject);
  });
}

async function loadLand() {
  try {
    const text = await download(SOURCE_URL);
    const geo = JSON.parse(text);
    console.log(
      `land: Natural Earth 110m from ${SOURCE_URL} (${geo.features.length} features)`,
    );
    return geo;
  } catch (err) {
    console.log(
      `download failed (${err.message}); using world-atlas land-110m (Natural Earth 110m)`,
    );
    const topojson = require("topojson-client");
    const topo = require("world-atlas/land-110m.json");
    const geo = topojson.feature(topo, topo.objects.land);
    return geo.type === "FeatureCollection"
      ? geo
      : { type: "FeatureCollection", features: [geo] };
  }
}

function polygonsOf(fc) {
  // Split MultiPolygons into single polygons and precompute bounding boxes.
  const polys = [];
  for (const f of fc.features) {
    const g = f.geometry;
    if (!g) continue;
    const list =
      g.type === "Polygon"
        ? [g.coordinates]
        : g.type === "MultiPolygon"
          ? g.coordinates
          : [];
    for (const coords of list) {
      let minX = Infinity,
        minY = Infinity,
        maxX = -Infinity,
        maxY = -Infinity;
      for (const [x, y] of coords[0]) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
      polys.push({
        feature: {
          type: "Feature",
          geometry: { type: "Polygon", coordinates: coords },
        },
        bbox: [minX, minY, maxX, maxY],
      });
    }
  }
  return polys;
}

function onLand(polys, lng, lat) {
  const pt = { type: "Point", coordinates: [lng, lat] };
  for (const p of polys) {
    const [x0, y0, x1, y1] = p.bbox;
    if (lng < x0 || lng > x1 || lat < y0 || lat > y1) continue;
    if (booleanPointInPolygon(pt, p.feature)) return true;
  }
  return false;
}

(async () => {
  const land = await loadLand();
  const polys = polygonsOf(land);
  const features = [];
  let rows = 0;
  for (let i = 0; ; i++) {
    const lat = round2(LAT_MIN + i * spacing);
    if (lat > LAT_MAX) break;
    rows++;
    const step = cosScale
      ? spacing / Math.max(Math.cos((lat * Math.PI) / 180), 0.05)
      : spacing;
    for (let j = 0; ; j++) {
      const lng = round2(-180 + j * step);
      if (lng > 180) break;
      if (onLand(polys, lng, lat)) {
        features.push({
          type: "Feature",
          geometry: { type: "Point", coordinates: [lng, lat] },
          properties: { lat },
        });
      }
    }
  }
  const out = {
    type: "FeatureCollection",
    generated: {
      source: "Natural Earth 1:110m land",
      spacing,
      cosScale,
      latRange: [LAT_MIN, LAT_MAX],
    },
    features,
  };
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(out));
  console.log(
    `wrote ${path.relative(process.cwd(), OUT)}: ${features.length} points, ${rows} rows, spacing ${spacing}°, cosScale=${cosScale}, ${(fs.statSync(OUT).size / 1024).toFixed(0)} KB`,
  );
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
