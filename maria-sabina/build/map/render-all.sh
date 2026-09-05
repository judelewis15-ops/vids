#!/usr/bin/env bash
# Full 480-frame export split across N worker browsers, then encode.
# Usage: ./render-all.sh [workers=2] [extra render-frames args...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/../../.."
N="${1:-2}"; shift || true
TOTAL=480
PER=$(( (TOTAL + N - 1) / N ))
pids=()
for ((i=0; i<N; i++)); do
  s=$(( i * PER )); e=$(( s + PER )); [ $e -gt $TOTAL ] && e=$TOTAL
  node "$HERE/render-frames.mjs" --start $s --end $e "$@" > "$HERE/data/render-worker-$i.log" 2>&1 &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
node "$HERE/render-frames.mjs" --frames 479 --encode "$@"
