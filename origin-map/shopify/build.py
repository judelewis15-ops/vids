#!/usr/bin/env python3
"""Build a single HTML fragment that embeds the Origin Map inside a Shopify page.

Reads ../index.html, ../app.js, ../styles.css and ../data/pins.json and writes
page.html next to this script. Paste page.html into the page body in the
Shopify admin (Online Store > Pages > Add page > "<>" HTML view), or pass it
to the Admin API as the page body.

The map runs inside a #origin-map container instead of filling the viewport,
so the theme header and footer stay where they are.
"""
import json
import math
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
MAPLIBRE_VERSION = "5.24.0"
CDN = f"https://unpkg.com/maplibre-gl@{MAPLIBRE_VERSION}/dist/"
PREFIX = "#origin-map"

html = (ROOT / "index.html").read_text()
js = (ROOT / "app.js").read_text()
css = (ROOT / "styles.css").read_text()
data = json.loads((ROOT / "data/pins.json").read_text())
dots = json.loads((ROOT / "data/land-dots.json").read_text())


# ---------- Land dots: pack the lattice as row runs so the page stays small ----------
def js_round2(n):
    return math.floor(n * 100 + 0.5) / 100


def encode_dots(fc):
    """Rows of [rowIndex, j0, len, j0, len, ...]; decoded in the page with the
    same arithmetic as scripts/build-dots.js. Verified by round-trip below."""
    gen = fc["generated"]
    spacing, cos_scale = gen["spacing"], gen["cosScale"]
    lat0 = gen["latRange"][0]
    by_lat = {}
    for f in fc["features"]:
        lng, lat = f["geometry"]["coordinates"]
        by_lat.setdefault(lat, []).append(lng)
    rows = []
    for lat in sorted(by_lat):
        i = round((lat - lat0) / spacing)
        assert js_round2(lat0 + i * spacing) == lat, lat
        step = spacing / max(math.cos(math.radians(lat)), 0.05) if cos_scale else spacing
        js_ = sorted(round((lng + 180) / step) for lng in by_lat[lat])
        for j, lng in zip(js_, sorted(by_lat[lat])):
            assert js_round2(-180 + j * step) == lng, (lat, lng, j)
        row = [i]
        start, prev = js_[0], js_[0]
        for j in js_[1:]:
            if j != prev + 1:
                row += [start, prev - start + 1]
                start = j
            prev = j
        row += [start, prev - start + 1]
        rows.append(row)
    packed = {"lat0": lat0, "dlat": spacing, "cos": cos_scale, "rows": rows}
    # Round trip in Python mirrors the JS decoder exactly.
    count = 0
    for row in rows:
        lat = js_round2(lat0 + row[0] * spacing)
        step = spacing / max(math.cos(math.radians(lat)), 0.05) if cos_scale else spacing
        for k in range(1, len(row), 2):
            for j in range(row[k], row[k] + row[k + 1]):
                js_round2(-180 + j * step)
                count += 1
    assert count == len(fc["features"]), (count, len(fc["features"]))
    return packed


DOTS_DECODER = """const packed = JSON.parse(
      document.getElementById("origin-map-dots").textContent,
    );
    const round2 = (n) => Math.round(n * 100) / 100;
    const features = [];
    for (const row of packed.rows) {
      const lat = round2(packed.lat0 + row[0] * packed.dlat);
      const step = packed.cos
        ? packed.dlat / Math.max(Math.cos((lat * Math.PI) / 180), 0.05)
        : packed.dlat;
      for (let k = 1; k < row.length; k += 2) {
        for (let j = row[k]; j < row[k] + row[k + 1]; j++) {
          features.push({
            type: "Feature",
            geometry: { type: "Point", coordinates: [round2(-180 + j * step), lat] },
            properties: { lat },
          });
        }
      }
    }
    return { type: "FeatureCollection", features };"""

packed_dots = encode_dots(dots)


# ---------- CSS: scope every selector under #origin-map ----------
def transform_selector(sel):
    sel = sel.strip()
    if not sel:
        return None
    if sel == "html":
        return None
    if sel == ":root" or sel == "body":
        return PREFIX
    if sel.startswith("body."):
        return PREFIX + sel[4:]
    if sel.startswith("body "):
        return PREFIX + sel[4:]
    if sel.startswith(PREFIX):
        return sel
    return f"{PREFIX} {sel}"


def scope_css(src):
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    src = re.sub(r"html,\s*body\s*\{[^}]*\}", "", src)
    out, buf, in_str, i = [], "", None, 0
    while i < len(src):
        c = src[i]
        if in_str:
            buf += c
            if c == in_str and src[i - 1] != "\\":
                in_str = None
        elif c in "\"'":
            in_str = c
            buf += c
        elif c == "{":
            prelude = buf.strip()
            buf = ""
            if prelude.startswith("@"):
                out.append(prelude + " {\n")
            else:
                sels = [transform_selector(s) for s in prelude.split(",")]
                sels = [s for s in sels if s]
                out.append((", ".join(sels) if sels else PREFIX + " .never-matches") + " {\n")
        elif c == "}":
            out.append(buf)
            buf = ""
            out.append("}\n")
        elif c == ";":
            buf += c
            out.append(buf)
            buf = ""
        else:
            buf += c
        i += 1
    out.append(buf)
    result = "".join(out)
    # The container is the "viewport" now.
    result = result.replace("position: fixed", "position: absolute")
    result = re.sub(r"(\d+(?:\.\d+)?)d?vh\b", r"\1cqh", result)
    result = re.sub(r"(\d+(?:\.\d+)?)d?vw\b", r"\1cqw", result)
    result = re.sub(r"\n\s*\n+", "\n", result)
    return result


# Themes style headings, paragraphs, buttons and inputs inside page content
# (usually via .rte). Neutralise that before the map's own rules apply.
reset_css = f"""{PREFIX} h1, {PREFIX} h2, {PREFIX} h3, {PREFIX} p, {PREFIX} figure, {PREFIX} ul, {PREFIX} li, {PREFIX} small {{
  margin: 0;
  padding: 0;
  color: inherit;
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
  letter-spacing: normal;
  text-transform: none;
  text-align: left;
  list-style: none;
  border: 0;
  background: none;
}}
{PREFIX} button, {PREFIX} input, {PREFIX} a, {PREFIX} output {{
  margin: 0;
  color: inherit;
  font: inherit;
  letter-spacing: normal;
  text-transform: none;
  text-decoration: none;
  text-align: left;
  min-height: 0;
  min-width: 0;
  box-shadow: none;
  appearance: none;
  -webkit-appearance: none;
}}
{PREFIX} header, {PREFIX} section, {PREFIX} aside, {PREFIX} form, {PREFIX} nav {{
  margin: 0;
  padding: 0;
  border: 0;
  background: none;
  box-shadow: none;
  width: auto;
  max-width: none;
  height: auto;
  min-height: 0;
  display: block;
  align-items: normal;
  justify-content: normal;
  gap: 0;
}}
{PREFIX} img, {PREFIX} iframe, {PREFIX} svg {{
  max-width: none;
  margin: 0;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}}
"""

scoped_css = reset_css + scope_css(css) + f"""
{PREFIX} {{
  position: relative;
  /* Break out of the theme's content column and fill the viewport. */
  width: 100vw;
  margin-left: calc(50% - 50vw);
  height: 100vh;
  height: 100dvh;
  min-height: 520px;
  border-radius: 0;
  container-type: size;
  isolation: isolate;
}}
"""

# ---------- JS: no fetch, no document.body, wait for MapLibre ----------
app_js = js
app_js = app_js.replace('"use strict";', '"use strict";\n  const ROOT = document.getElementById("origin-map");', 1)
app_js = app_js.replace("document.body.classList", "ROOT.classList")
app_js, n = re.subn(
    r"const dataReady = fetch\(DATA_URL\)[\s\S]*?\n  \}\);\n",
    'const dataReady = Promise.resolve().then(() =>\n    JSON.parse(document.getElementById("origin-map-data").textContent),\n  );\n',
    app_js,
)
assert n == 1, "data loader not found"
app_js, n = re.subn(
    r"  // \[dots-loader\][\s\S]*?// \[/dots-loader\]\n",
    "  const loadDots = () =>\n    Promise.resolve().then(() => {\n    " + DOTS_DECODER + "\n    });\n",
    app_js,
)
assert n == 1, "dots loader not found"
assert "document.body" not in app_js

loader = f"""(function () {{
  function start() {{
{app_js}
  }}
  if (window.maplibregl) return start();
  var s = document.createElement("script");
  s.src = "{CDN}maplibre-gl.js";
  s.onload = start;
  s.onerror = start; // start() shows a message when the library is missing
  document.head.appendChild(s);
}})();"""

# ---------- HTML ----------
body = re.search(r"<body>([\s\S]*)</body>", html).group(1).strip()
body = re.sub(r"\s*<noscript>[\s\S]*?</noscript>", "", body)
data_json = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
dots_json = json.dumps(packed_dots, separators=(",", ":"))

page = f"""<!-- Origin Map: generated by shopify/build.py. Edit the source files, not this. -->
<link rel="stylesheet" href="{CDN}maplibre-gl.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
{scoped_css}</style>
<div id="origin-map" class="origin-map">
{body}
</div>
<script type="application/json" id="origin-map-data">{data_json}</script>
<script type="application/json" id="origin-map-dots">{dots_json}</script>
<script>
{loader}
</script>
"""
(HERE / "page.html").write_text(page)
print(f"wrote {HERE / 'page.html'} ({len(page.encode())} bytes)")
