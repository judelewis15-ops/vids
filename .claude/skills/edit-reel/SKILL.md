---
name: edit-reel
description: Cut a raw talking-head recording (silences, retakes) to best takes, drop in OpenArt b-roll, and render a 1080x1920 Instagram reel with word captions. Use when the user gives you footage plus a script and asks for the edit.
---

# Edit a reel

Inputs you need before starting:
1. The raw footage on disk. Chat attachments land in `/root/.claude/uploads/<session>/`; copy it to `raw/`. Google Drive links and most CDNs are unreachable from web sessions, so ask for a chat attachment or run locally.
2. The script, one spoken beat per line, at `scripts/<video>/script.txt`.
3. A b-roll manifest at `scripts/<video>/broll.json` (see `scripts/02-ochra/broll.json`). Each clip has `src` (under `public/`), `url`, `keywords` and optionally `line` (0-based script line) and `mode` (`cutaway` full-frame, or `split` b-roll top / face bottom).
4. A word-timestamped transcript if speech-to-text is available: `--whisper small` (needs faster-whisper and model weights) or `--transcript words.json` from any tool. Without one, takes are kept in order and you pick by hand from the take sheet.

Steps:
1. `pip install imageio-ffmpeg` if `ffmpeg` is missing. `npm i` if `node_modules` is missing.
2. `python3 pipeline/fetch_broll.py scripts/<video>/broll.json` to pull the clips into `public/broll/`. If the CDN is blocked the edit can still reference the `url` directly, but the render machine must be able to reach it.
3. `python3 pipeline/cut.py raw/<file> --script scripts/<video>/script.txt --broll scripts/<video>/broll.json --whisper small`
   - Tune `--noise` (dB, default -35) and `--min-silence` (s, default 0.6) if takes merge or fragment.
   - `--focus x,y` moves the portrait crop for landscape sources (percent, default 50,40 keeps a centred face).
4. Read `public/edit/takes.md` and look at `public/edit/thumbs/take_XX.jpg`. Check every chosen take and any `missing` script lines. Override by editing `public/edit/edit.json` (segments, b-roll `segment`/`offset`/`duration`) and show the user the take sheet before rendering.
5. Preview timing without a full render: `npx remotion still src/index.ts Reel out/frame.png --frame=<n>`.
6. Render: `npx remotion render src/index.ts Reel out/<video>.mp4 --codec=h264 --crf=18` (add `--browser-executable=/opt/pw-browsers/chromium` in the web sandbox). Output is 1080x1920, 30 fps, H.264 + AAC, captions inside the Reels safe zone, punch-in on every other cut.
7. Check the result: duration, that b-roll lands on the right beats, and that the reel is under 90 s. Send `out/<video>.mp4` to the user.

Instagram Reels targets: 9:16 at 1080x1920, 30 fps, H.264/AAC, keep text out of the top 220 px and bottom 320 px, aim for under 90 s.
