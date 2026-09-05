# HYPHA ORIGINS · 01 — MARÍA SABINA

Build folder for episode 01, worked from the master brief v6 (05 Sep 2026).
Nothing is generated except the map graphic (brief section 6). Cards, labels
and lower thirds are made in Premiere, not here.

```
maria-sabina/
  refs/map/            Harris style frames (ref_harris_NN.png), never distributed; empty, see premiere-notes
  assets/              sourced originals, untouched (HO01_[shot]_[type]_[slug].[ext])
  assets/SOURCES.csv   filename, shot, source_url, publication, date, rights_holder, licence, retrieved
  work/                masks, cutouts, treated versions
  exports/map/         HO01_02_MAP_start.png, HO01_03_MAP_end.png, HO01_02-03_MAP_zoom.mp4, OPENART_LOG.csv
  exports/satellite/   Google Earth Studio frame sequence (shot 04)
  exports/contact-sheet.png
  exports/premiere-notes.md
  build/tools/         contact-sheet.py, fetch-assets.sh (helpers; not deliverables)
```

Types: `PHOTO`, `DOC`, `MAP`, `SAT`, `STOCK`, `TXT`, `PTC`. No species name in
any filename, slug, folder or log entry.

```
python3 maria-sabina/build/tools/contact-sheet.py       # rebuild exports/contact-sheet.png from SOURCES.csv
./maria-sabina/build/tools/fetch-assets.sh              # pull the OpenArt map files; list NEEDS_MANUAL items
python3 maria-sabina/build/tools/highlight-element.py   # highlighter swipe + box elements -> exports/elements/
python3 maria-sabina/build/tools/treat.py --help        # document / photo treatments from a fetched still
python3 maria-sabina/build/tools/label-map.py --help    # labels on the map clip (parked)
```

`exports/elements/` holds drop-on highlight layers (ProRes 4444 alpha) ready for Premiere.

Start with `exports/premiere-notes.md`: rights decisions, the map QA state and
every item that still needs a hand.
