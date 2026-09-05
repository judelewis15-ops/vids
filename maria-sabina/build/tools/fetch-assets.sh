#!/usr/bin/env bash
# Pulls what the build container could not: the OpenArt map frames and clip
# listed in assets/SOURCES.csv (cdn.openart.ai rows) into exports/map, and
# prints the NEEDS_MANUAL items with their URLs. Run on a machine with normal
# internet access.
#   ./maria-sabina/build/tools/fetch-assets.sh        # map files + manual list
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
MS="$ROOT/maria-sabina"
CSV="$MS/assets/SOURCES.csv"
mkdir -p "$MS/exports/map" "$MS/assets"
python3 - "$CSV" <<'PY' | while IFS=$'\t' read -r name url; do
import csv, sys
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    if r["source_url"].startswith("https://cdn.openart.ai/"):
        print(r["filename"] + "\t" + r["source_url"])
PY
  case "$name" in *_MAP_*) dst="$MS/exports/map/$name" ;; *) dst="$MS/assets/$name" ;; esac
  if [ -s "$dst" ]; then echo "have $name"; else echo "get  $name"; curl -sSL --retry 3 -o "$dst" "$url"; fi
done
echo
echo "== NEEDS_MANUAL (from SOURCES.csv) =="
python3 - "$CSV" <<'PY'
import csv, sys
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    if r["retrieved"].startswith("NEEDS_MANUAL"):
        print(f"- shot {r['shot']:<8} {r['filename']}\n    {r['source_url']}\n    {r['retrieved']}")
PY
