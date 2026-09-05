# HYPHA ORIGINS · 01 — MARÍA SABINA

Build folder for the ~62 s Reel (1080 × 1920, 60 fps). Johnny Harris grammar:
archive stills with slow push-ins, one continuous map move, hard cuts on the
turn. Single violet accent (`#7C3AED`) on the map and the text cards only.
Type: Bebas Neue cards, JetBrains Mono eyebrows. Cream `#FAF7F2` on aubergine
`#1A0B2E`. The map follows the HO01 map art direction: near-black water, slate
relief lit from the north-west, one spotlit subject (Mexico, then Oaxaca, then
the Sierra Mazateca), a violet arc that draws on from New York, terrain that
rises into frame as the camera tilts to 58 degrees. Grain, vignette, chromatic
aberration and the 2% drift are added in Premiere, not in the export.

## Layout

```
maria-sabina/
  assets/            source assets, one file per shot, HO01_[shot]_[type]_[slug].[ext]
  assets/SOURCES.csv every asset: filename, shot, source URL, rights holder, licence, date, notes
  exports/           rendered deliverables (map MP4, cards, contact sheet)
  exports/map-sequence/  480 PNG frames of shots 02-04 (rebuilt, not committed)
  build/map/         MapLibre page + frame exporter for shots 02-04
  build/cards/       render script for the four TXT assets (Remotion comps live in src/MariaSabina)
  build/tools/       fetch-assets.sh (pull sourced/generated files), contact-sheet.py
```

Types: `ARC` archive, `MAP`, `AI`, `BRL` own footage, `TXT` text card or overlay.

## Commands

```
npm install
npm run ho01:map        # shots 02-04: 480 frames at 2160x3840 (HO01_map_00001.png on) + HO01_map.mp4 (+ ProRes 422 HQ)
npm run ho01:cards      # shots 01, 08, 17, 18: cards as MP4 + PNG, overlays as ProRes 4444 alpha + PNG
./maria-sabina/build/tools/fetch-assets.sh   # OpenArt clips, the 1957 issue scan, Commons candidates
npm run ho01:sheet      # exports/HO01_contact-sheet.png, every asset against its shot number
```

The map exporter runs headless Chromium through Playwright (already a dev
dependency): it steps the camera per frame, waits for the map to idle, and
captures the canvas, so the sequence is deterministic. Terrain tiles are cached
under `build/map/data/tile-cache` after the first pass. Useful flags on
`build/map/render-frames.mjs`: `--frames 0,239,479` (frame 1, midpoint, final
for the brightness check), `--scale 1` (1080x1920 preview), `--textScale 1
--lineScale 1` (the literal 11px / 9px / 2px sizes from the art direction
instead of the phone-legible defaults), `--arcBow 0` (pure great circle).

If Remotion cannot find a browser, point it at one:
`REMOTION_BROWSER=/path/to/chrome npm run ho01:cards`.

## What is built here and what is not

Built in this repo: the map sequence (02-04), the eyebrow overlay (01), the
date card (08), the lower third (17), the end card (18), the contact sheet, and
the AI clips for 05, 06, 11, 12, 13, 14a-c (generated on the Hypha OpenArt
account, Gemini Omni 1.1 Flash, 9:16 1080p, 3 s each, 5 s for 05; the files
live in the OpenArt library until `fetch-assets.sh ai` pulls them down).

Not built here, by design: every frame of her and every frame of the magazine.
Shots 01, 07, 09, 10 and 15 are real archive only. Shot 17 is own footage only.
`SOURCES.csv` lists the candidates and their rights position; nothing goes in
the timeline until the licence column is settled.

## Rights, read before cutting

- **LIFE, 13 May 1957** (cover, spread, Allan Richardson's photographs): in
  copyright, Dotdash Meredith. Editorial use on a monetised shop account is
  not a safe assumption. Licence through the LIFE Picture Collection or accept
  the risk knowingly. The Internet Archive scan is only there so the edit can
  be laid out.
- **Portraits of María Sabina**: the best archive portraits (Nacho López,
  c.1975-80) are held by INAH / Fototeca Nacional under CC BY-NC-ND, which
  excludes commercial use without a licence. Check photographer and date on any
  Commons file before it goes in.
- **Natural Earth** (map data) is public domain. **Terrain tiles** are open data
  (credit "Mapzen Terrain Tiles"). All fonts are OFL.

## Do not

- Name any species in assets, filenames, on-screen text, or the search terms
  logged in `SOURCES.csv`.
- Generate her face or the magazine. AI is for landscape and period colour
  only, and each AI clip is logged with its prompt source and history id.
