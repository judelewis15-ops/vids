#!/usr/bin/env bash
# One-command Hypha launch simulation: set up MiroFish (pinned + Claude patch),
# check keys and network, run the pipeline, write the report to launch-sim/out/.
#
#   bash launch-sim/run.sh [--rounds N]
#
# Needs LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME and ZEP_API_KEY in the
# environment, and network access to api.getzep.com (see README.md).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MF="${MIROFISH_DIR:-$HOME/mirofish}"
MF_COMMIT=7657031ac01184afe2cb220f5ee3545573b5e843

echo "== Checking configuration"
missing=0
for v in LLM_API_KEY LLM_BASE_URL LLM_MODEL_NAME ZEP_API_KEY; do
  if [ -z "${!v:-}" ]; then echo "   missing environment variable: $v"; missing=1; fi
done
[ "$missing" = 0 ] || { echo "Set these in the environment settings, then start a new session."; exit 1; }

for host in "https://api.getzep.com" "${LLM_BASE_URL%/}/models"; do
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' "$host" || true)
  if [ "$code" = "000" ]; then
    echo "   cannot reach $host (add it under Allowed domains)"; exit 1
  fi
done
echo "   keys set, network ok"

echo "== Setting up MiroFish in $MF"
if [ ! -d "$MF/.git" ]; then
  git init -q "$MF"
  git -C "$MF" remote add origin https://github.com/666ghj/MiroFish
  GIT_LFS_SKIP_SMUDGE=1 git -C "$MF" fetch -q --depth 1 origin "$MF_COMMIT"
  git -C "$MF" checkout -q FETCH_HEAD
fi
if git -C "$MF" apply --reverse --check "$HERE/mirofish-claude.patch" 2>/dev/null; then
  echo "   Claude patch already applied"
else
  git -C "$MF" apply "$HERE/mirofish-claude.patch"
  echo "   Claude patch applied"
fi
(cd "$MF/backend" && uv sync -q --python 3.12)

echo "== Testing the model key with one small request"
(cd "$MF/backend" && .venv/bin/python -c '
from app.utils.llm_client import LLMClient
print("   model replied:", LLMClient().chat([{"role": "user", "content": "Reply with the single word OK."}], max_tokens=20)[:40])
')

echo "== Starting MiroFish backend"
(cd "$MF/backend" && .venv/bin/python run.py > "$HERE/backend.log" 2>&1) &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null || true' EXIT
for _ in $(seq 1 60); do
  curl -s -o /dev/null localhost:5001/api/graph/project/list && break
  sleep 1
done

python3 "$HERE/run_mirofish.py" \
  --seed "$HERE/seed/hypha-app-launch.md" \
  --question "$HERE/question.txt" \
  --out "$HERE/out" \
  "$@"
