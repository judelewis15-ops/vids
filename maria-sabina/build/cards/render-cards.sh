#!/usr/bin/env bash
# Renders the four TXT assets from the Remotion compositions in src/MariaSabina.
# Bundles once, then renders everything from that bundle.
# Cards: H.264 MP4 + PNG still. Overlays (eyebrow, lower third): ProRes 4444
# with alpha so they drop straight over the footage, plus a PNG still.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
BROWSER="${REMOTION_BROWSER:-}"
FLAGS=(--log=error --gl=swiftshader)
[ -n "$BROWSER" ] && FLAGS+=(--browser-executable="$BROWSER")
A=maria-sabina/assets; E=maria-sabina/exports; B=maria-sabina/build/cards/bundle
mkdir -p "$A" "$E"
rm -rf "$B"
npx remotion bundle src/index.ts --out-dir "$B" --log=error
npx remotion render "$B" HO01-08-TXT-date-card "$E/HO01_08_TXT_date-card.mp4" --codec=h264 --crf=12 "${FLAGS[@]}"
npx remotion still  "$B" HO01-08-TXT-date-card "$A/HO01_08_TXT_date-card.png" --frame=90 "${FLAGS[@]}"
npx remotion render "$B" HO01-18-TXT-end-card  "$E/HO01_18_TXT_end-card.mp4" --codec=h264 --crf=12 "${FLAGS[@]}"
npx remotion still  "$B" HO01-18-TXT-end-card  "$A/HO01_18_TXT_end-card.png" --frame=90 "${FLAGS[@]}"
npx remotion render "$B" HO01-01-TXT-eyebrow   "$E/HO01_01_TXT_eyebrow_alpha.mov" --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png "${FLAGS[@]}"
npx remotion still  "$B" HO01-01-TXT-eyebrow   "$A/HO01_01_TXT_eyebrow.png" --frame=180 --image-format=png "${FLAGS[@]}"
npx remotion render "$B" HO01-17-TXT-lower-third "$E/HO01_17_TXT_lower-third_alpha.mov" --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png "${FLAGS[@]}"
npx remotion still  "$B" HO01-17-TXT-lower-third "$A/HO01_17_TXT_lower-third.png" --frame=240 --image-format=png "${FLAGS[@]}"
rm -rf "$B"
echo "cards done"
