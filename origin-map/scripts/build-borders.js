#!/usr/bin/env node
/* Generate data/borders.json: country boundary lines for the globe.

   Source is Natural Earth 1:50m admin-0 countries as bundled in the
   world-atlas npm package (TopoJSON), simplified to roughly 110m detail.
   The 50m set is used instead of 110m because 110m drops Gaza, and the map
   should show Palestine (West Bank and Gaza) as its own entity.

   Only shared land borders are drawn: coastlines are already implied by the
   land dots. Output is one MultiLineString at two decimal places.

   Usage: node scripts/build-borders.js [--weight 0.01] */

const fs = require("fs");
const path = require("path");
const tc = require("topojson-client");
const ts = require("topojson-simplify");

const args = process.argv.slice(2);
const weight = Number(args[args.indexOf("--weight") + 1]) || 0.01;
const OUT = path.join(__dirname, "..", "data", "borders.json");
const round2 = (n) => Math.round(n * 100) / 100;

const topo = require("world-atlas/countries-50m.json");
const countries = topo.objects.countries;
const name = (g) => (g.properties && g.properties.name) || "";

// Sanity: Palestine must be present as a separate feature with both parts.
const palestine = countries.geometries.find((g) => name(g) === "Palestine");
if (!palestine) throw new Error("Palestine is missing from the source data");
const parts = palestine.type === "MultiPolygon" ? palestine.arcs.length : 1;
if (parts < 2)
  throw new Error(`Palestine has ${parts} polygon(s); expected West Bank and Gaza`);

const simplified = ts.simplify(ts.presimplify(topo), weight);
// a !== b keeps only borders between two different countries.
const mesh = tc.mesh(simplified, simplified.objects.countries, (a, b) => a !== b);
const lines = mesh.coordinates
  .map((line) => {
    const out = [];
    for (const [x, y] of line) {
      const p = [round2(x), round2(y)];
      const last = out[out.length - 1];
      if (!last || last[0] !== p[0] || last[1] !== p[1]) out.push(p);
    }
    return out;
  })
  .filter((line) => line.length > 1);

// Both parts of Palestine must still have a drawn border after simplification.
const inBox = ([x, y], [x0, y0, x1, y1]) => x > x0 && x < x1 && y > y0 && y < y1;
const flat = lines.flat();
const gaza = flat.filter((p) => inBox(p, [34.2, 31.2, 34.6, 31.62])).length;
const westBank = flat.filter((p) => inBox(p, [34.85, 31.3, 35.6, 32.6])).length;
if (gaza < 2 || westBank < 4)
  throw new Error(
    `Palestine border lost in simplification (gaza ${gaza}, west bank ${westBank}); lower --weight`,
  );

const points = flat.length;
const out = {
  type: "Feature",
  properties: {},
  geometry: { type: "MultiLineString", coordinates: lines },
  generated: {
    source: "Natural Earth 1:50m admin-0 countries via world-atlas, simplified",
    weight,
    countries: countries.geometries.length,
    lines: lines.length,
    points,
  },
};
fs.writeFileSync(OUT, JSON.stringify(out));
console.log(
  `wrote ${OUT}: ${lines.length} lines, ${points} points, ${fs.statSync(OUT).size} bytes (gaza ${gaza} pts, west bank ${westBank} pts)`,
);
