#!/usr/bin/env bash
# Pulls the sourced and generated assets listed in assets/SOURCES.csv into
# maria-sabina/assets. Run this on a machine with normal internet access: the
# build container that produced this repo could not reach cdn.openart.ai,
# archive.org, Wikimedia Commons or INAH.
#
#   ./maria-sabina/build/tools/fetch-assets.sh          # everything below
#   ./maria-sabina/build/tools/fetch-assets.sh ai       # only the OpenArt clips
#   ./maria-sabina/build/tools/fetch-assets.sh life     # only the 1957 issue scan
#   ./maria-sabina/build/tools/fetch-assets.sh commons  # Commons candidates for review
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
A="$ROOT/maria-sabina/assets"
CAND="$A/_candidates"
mkdir -p "$A" "$CAND"
WHAT="${1:-all}"

fetch_ai() {
  echo "== OpenArt generations (Hypha account) =="
  # filename<TAB>url, straight from SOURCES.csv
  python3 - "$ROOT/maria-sabina/assets/SOURCES.csv" <<'PY' | while IFS=$'\t' read -r name url; do
import csv, sys
for r in csv.DictReader(open(sys.argv[1], encoding="utf-8")):
    if r["source URL"].startswith("https://cdn.openart.ai/"):
        print(r["filename"] + "\t" + r["source URL"])
PY
    dest="$A"
    case "$name" in HO01_0[23]_MAP_*|HO01_02-03_MAP_*) dest="$ROOT/maria-sabina/exports/map" ;; esac  # OpenArt map pipeline outputs
    mkdir -p "$dest"
    if [ -s "$dest/$name" ]; then echo "have $name"; continue; fi
    echo "get  $name"; curl -sSL --retry 3 -o "$dest/$name" "$url"
  done
}

fetch_life() {
  echo "== LIFE 13 May 1957 (Internet Archive scan; in copyright, see SOURCES.csv) =="
  ITEM="Life-1957-05-13-Vol-42-No-19"
  META="$(curl -sSL "https://archive.org/metadata/$ITEM")"
  PDF="$(printf '%s' "$META" | python3 -c '
import json,sys
m=json.load(sys.stdin)
fs=[f for f in m.get("files",[]) if f.get("name","").lower().endswith(".pdf")]
fs.sort(key=lambda f:int(f.get("size",0)), reverse=True)
print(fs[0]["name"] if fs else "")')"
  if [ -z "$PDF" ]; then echo "no PDF listed for $ITEM; open https://archive.org/details/$ITEM"; return; fi
  [ -s "$CAND/LIFE-1957-05-13.pdf" ] || curl -sSL --retry 3 -o "$CAND/LIFE-1957-05-13.pdf" "https://archive.org/download/$ITEM/$PDF"
  echo "saved $CAND/LIFE-1957-05-13.pdf"
  echo "cover  -> crop page 1 to HO01_07_ARC_life-cover.jpg"
  echo "spread -> the Great Adventures III pages (around pp. 100-120) to HO01_09_ARC_life-spread.jpg / HO01_10_ARC_life-spread-village.jpg"
  echo "e.g. pdftoppm -r 300 -f 1 -l 1 -jpeg \"$CAND/LIFE-1957-05-13.pdf\" \"$CAND/life-p\""
}

fetch_commons() {
  echo "== Wikimedia Commons candidates (review licences on each file page before use) =="
  for CAT in "Category:María_Sabina" "Category:Huautla_de_Jiménez"; do
    curl -sSL "https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=categorymembers&gcmtitle=$CAT&gcmtype=file&gcmlimit=50&prop=imageinfo&iiprop=url|user|extmetadata&iiextmetadatafilter=Artist|LicenseShortName|DateTimeOriginal|Credit" \
      | python3 -c '
import json,sys,urllib.parse
d=json.load(sys.stdin)
for p in d.get("query",{}).get("pages",{}).values():
    ii=p["imageinfo"][0]; m=ii.get("extmetadata",{})
    print("\t".join([p["title"], ii["url"], m.get("Artist",{}).get("value","?")[:80], m.get("LicenseShortName",{}).get("value","?"), m.get("DateTimeOriginal",{}).get("value","?")]))' \
      | while IFS=$'\t' read -r title url artist lic date; do
          f="$CAND/$(printf '%s' "$title" | sed 's/^File://; s#/#_#g')"
          echo "$title | $artist | $lic | $date"
          [ -s "$f" ] || curl -sSL -o "$f" "$url"
        done
  done
  echo "INAH portraits (need a licence for commercial use):"
  echo "  https://repositorio.inah.gob.mx/o-302990  (Maria Sabina, retrato, Nacho Lopez c.1975)"
  echo "  https://repositorio.inah.gob.mx/o-305512"
  echo "LoC, 1967 counterculture (public domain): https://www.loc.gov/pictures/item/2024640601/"
}

case "$WHAT" in
  ai) fetch_ai ;;
  life) fetch_life ;;
  commons) fetch_commons ;;
  all) fetch_ai; fetch_life; fetch_commons ;;
  *) echo "usage: $0 [all|ai|life|commons]"; exit 1 ;;
esac
