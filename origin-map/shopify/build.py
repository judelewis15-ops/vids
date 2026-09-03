#!/usr/bin/env python3
"""Build a single HTML fragment that embeds the Origin Map inside a Shopify page.

Reads ../index.html, ../app.js, ../styles.css and ../data/*.json and writes
page.html next to this script. Paste page.html into the page body in the
Shopify admin (Online Store > Pages > Add page > "<>" HTML view), or pass it
to the Admin API as the page body.

The map runs inside a #origin-map container, a fixed-height stage of
100vh minus the site header, so the theme header and footer stay where they
are. The theme's own page title is hidden: the globe is the content.
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
borders = json.loads((ROOT / "data/borders.json").read_text())


# ---------- Borders: each line as an encoded polyline string ----------
# Google's polyline algorithm at 1e2 precision: deltas as base-32 varints
# offset by 63 so every char is printable. The one awkward char in that
# alphabet, backslash, is swapped for "!" so the blob needs no JSON escaping.
# Decoded in the page; verified below.
def encode_polyline(line, factor=100):
    out = []
    px = py = 0
    for x, y in line:
        for v, pv in ((round(y * factor), py), (round(x * factor), px)):
            d = v - pv
            d = ~(d << 1) if d < 0 else d << 1
            while d >= 0x20:
                out.append(chr((0x20 | (d & 0x1F)) + 63))
                d >>= 5
            out.append(chr(d + 63))
        px, py = round(x * factor), round(y * factor)
    return "".join(out).replace("\\", "!")


def decode_polyline(text, factor=100):
    pts, i, x, y = [], 0, 0, 0
    while i < len(text):
        for axis in ("y", "x"):
            shift = result = 0
            while True:
                c = ord(text[i])
                b = (92 if c == 33 else c) - 63
                i += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            d = ~(result >> 1) if result & 1 else result >> 1
            if axis == "y":
                y += d
            else:
                x += d
        pts.append([x / factor, y / factor])
    return pts


def encode_borders(feature):
    lines = feature["geometry"]["coordinates"]
    encoded = [encode_polyline(line) for line in lines]
    for text, line in zip(encoded, lines):
        assert decode_polyline(text) == [[round(x, 2), round(y, 2)] for x, y in line]
    return encoded


BORDERS_DECODER = """const rows = JSON.parse(
      document.getElementById("origin-map-borders").textContent,
    );
    const decode = (text) => {
      const pts = [];
      let i = 0;
      let x = 0;
      let y = 0;
      while (i < text.length) {
        for (const axis of ["y", "x"]) {
          let shift = 0;
          let result = 0;
          let b;
          do {
            const c = text.charCodeAt(i++);
            b = (c === 33 ? 92 : c) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
          } while (b >= 0x20);
          const d = result & 1 ? ~(result >> 1) : result >> 1;
          if (axis === "y") y += d;
          else x += d;
        }
        pts.push([x / 100, y / 100]);
      }
      return pts;
    };
    return {
      type: "Feature",
      properties: {},
      geometry: { type: "MultiLineString", coordinates: rows.map(decode) },
    };"""


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
packed_borders = encode_borders(borders)


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

# The theme's page template wraps page content in
# section.page-content > .container > h1.page-title + .page-body. The globe is
# the content, so the title goes, the column padding goes, and the stage is a
# fixed-height block under the site header: 100vh minus HEADER_ALLOWANCE.
# :has() does the job in current browsers; the loader adds .origin-map-host as
# a fallback for older ones.
HEADER_ALLOWANCE = "140px"
host_css = f"""
.page-content:has({PREFIX}), .page-content.origin-map-host {{
  max-width: none;
  padding: 0;
  margin: 0;
}}
.page-content:has({PREFIX}) > .container, .page-content.origin-map-host > .container {{
  max-width: none;
  padding: 0;
  margin: 0;
}}
.page-content:has({PREFIX}) .page-title, .page-content.origin-map-host .page-title {{
  display: none;
}}
.page-content:has({PREFIX}) .page-body, .page-content.origin-map-host .page-body {{
  font-size: 16px;
  line-height: 1.5;
}}
"""

scoped_css = reset_css + scope_css(css) + host_css + f"""
{PREFIX} {{
  position: relative;
  /* Fill the width even if the theme still pads its column. */
  width: 100vw;
  margin-left: calc(50% - 50vw);
  /* Fixed-height stage: what is left below the site header. */
  height: calc(100vh - {HEADER_ALLOWANCE});
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
app_js, n = re.subn(
    r"  // \[borders-loader\][\s\S]*?// \[/borders-loader\]\n",
    "  const loadBorders = () =>\n    Promise.resolve().then(() => {\n    " + BORDERS_DECODER + "\n    });\n",
    app_js,
)
assert n == 1, "borders loader not found"
assert "document.body" not in app_js

loader = f"""(function () {{
  var host = document.getElementById("origin-map");
  var section = host && host.closest(".page-content");
  if (section) section.classList.add("origin-map-host");
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
borders_json = json.dumps(packed_borders, separators=(",", ":")).replace("</", "<\\/")

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
<script type="application/json" id="origin-map-borders">{borders_json}</script>
<script>
{loader}
</script>
"""
(HERE / "page.html").write_text(page)
print(f"wrote {HERE / 'page.html'} ({len(page.encode())} bytes)")
