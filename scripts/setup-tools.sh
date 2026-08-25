#!/usr/bin/env bash
# Installs the media tooling this project uses:
#   - playwright (browser automation, for driving the Remotion studio / capturing pages)
#   - yt-dlp     (video downloader)
#   - ffmpeg     (frame extraction, transcoding)
#
# Idempotent: already-present tools are left alone. Safe to run on every session start.
set -uo pipefail

log() { printf '[setup-tools] %s\n' "$*"; }

have() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------- ffmpeg ----
install_ffmpeg() {
  if have ffmpeg && have ffprobe; then
    log "ffmpeg present: $(ffmpeg -version | head -1)"
    return
  fi
  log "installing ffmpeg"
  if have brew; then
    brew install ffmpeg
  elif have apt-get; then
    ${SUDO:-} apt-get update -qq || true
    ${SUDO:-} apt-get install -y --no-install-recommends ffmpeg
  else
    log "no supported package manager for ffmpeg; install it manually"
    return 1
  fi
}

# ----------------------------------------------------------------- yt-dlp ---
install_ytdlp() {
  if have yt-dlp; then
    log "yt-dlp present: $(yt-dlp --version)"
    return
  fi
  log "installing yt-dlp"
  if have brew; then
    brew install yt-dlp
  else
    "${PYTHON:-python3}" -m pip install --break-system-packages -U yt-dlp \
      || "${PYTHON:-python3}" -m pip install -U yt-dlp
  fi
}

# ------------------------------------------------------------- playwright ---
# The sandbox images ship Chromium under PLAYWRIGHT_BROWSERS_PATH and block
# `playwright install`. The pip default is whatever is newest, which expects a
# newer Chromium build than the one on disk, so pin the playwright release whose
# bundled Chromium revision matches what is already installed.
install_playwright() {
  local py="${PYTHON:-python3}"

  if ! "$py" -c 'import playwright' 2>/dev/null; then
    log "installing playwright"
    "$py" -m pip install --break-system-packages playwright \
      || "$py" -m pip install playwright
  fi

  local browsers_path="${PLAYWRIGHT_BROWSERS_PATH:-}"
  if [ -z "$browsers_path" ] || [ ! -d "$browsers_path" ]; then
    # No preinstalled browsers: fetch them the normal way.
    log "downloading chromium via playwright"
    "$py" -m playwright install chromium
    return
  fi

  # Preinstalled browsers exist. Find the on-disk chromium revision and, if the
  # installed playwright expects a different one, pin playwright to match.
  local on_disk expected
  on_disk="$(ls -d "$browsers_path"/chromium-* 2>/dev/null | head -1)"
  on_disk="${on_disk##*chromium-}"
  expected="$("$py" - <<'PY' 2>/dev/null
import json, pathlib, playwright
p = pathlib.Path(playwright.__file__).parent / "driver" / "package" / "browsers.json"
d = json.loads(p.read_text())
print(next(b["revision"] for b in d["browsers"] if b["name"] == "chromium"))
PY
)"

  if [ -z "$on_disk" ]; then
    log "no chromium under $browsers_path; downloading"
    "$py" -m playwright install chromium
    return
  fi

  if [ "$on_disk" = "$expected" ]; then
    log "playwright chromium revision $on_disk matches preinstalled browser"
    return
  fi

  log "playwright wants chromium $expected but $on_disk is installed; pinning playwright"
  local ver
  for ver in 1.56.0 1.55.0 1.54.0 1.53.0; do
    "$py" -m pip install --break-system-packages "playwright==$ver" >/dev/null 2>&1 \
      || "$py" -m pip install "playwright==$ver" >/dev/null 2>&1 || continue
    expected="$("$py" - <<'PY' 2>/dev/null
import json, pathlib, playwright
p = pathlib.Path(playwright.__file__).parent / "driver" / "package" / "browsers.json"
d = json.loads(p.read_text())
print(next(b["revision"] for b in d["browsers"] if b["name"] == "chromium"))
PY
)"
    if [ "$expected" = "$on_disk" ]; then
      log "pinned playwright==$ver (chromium $on_disk)"
      return
    fi
  done
  log "could not match a playwright release to chromium $on_disk;"
  log "launch with executable_path='$browsers_path/chromium' instead"
}

if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
  SUDO=sudo
else
  SUDO=
fi

rc=0
install_ffmpeg     || rc=1
install_ytdlp      || rc=1
install_playwright || rc=1

log "done"
exit "$rc"
