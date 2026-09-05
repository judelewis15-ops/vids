#!/usr/bin/env bash
# Downloads the Natural Earth 10m layers the map style needs (GitHub mirror of
# naturalearthdata.com, public domain) into build/map/data/raw/ne, then clips
# them with prepare-data.mjs. Only needed if build/map/data/*.geojson is missing.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$HERE/data/raw/ne"
mkdir -p "$RAW"
BASE="https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
for f in ne_10m_admin_0_countries ne_10m_admin_0_boundary_lines_land \
         ne_10m_admin_1_states_provinces_lines ne_10m_admin_1_states_provinces \
         ne_10m_lakes ne_10m_ocean; do
  if [ ! -s "$RAW/$f.geojson" ]; then
    echo "fetching $f"
    curl -sSL --retry 3 -o "$RAW/$f.geojson" "$BASE/$f.geojson"
  fi
done
node "$HERE/prepare-data.mjs" "$RAW" "$HERE/data"
