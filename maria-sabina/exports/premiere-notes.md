# HYPHA ORIGINS · 01 — MARÍA SABINA
## Premiere notes · built against master brief v6 (05 Sep 2026)

Master 9:16, 2160×3840, 60 fps. Modes per brief section 4: FULL BLEED, STACKED (16:9 asset upper two thirds, presenter lower third), PTC FULL. Everything below is for the edit; nothing here was cut in.

### Status at handoff

| Deliverable | State |
|---|---|
| `assets/SOURCES.csv` | 23 rows, every shot covered. 20 rows are `NEEDS_MANUAL`: the build container has no route to archive.org, Wikimedia Commons, INAH, LoC, Getty, Pexels, Google Earth Studio or the OpenArt CDN. Each row carries the exact URL or archive to check. |
| `exports/map/HO01_02_MAP_start.png` | Generated and accepted (OpenArt, Nano Banana Pro image2image, 4K). Lives in the OpenArt library until `build/tools/fetch-assets.sh` pulls it. |
| `exports/map/HO01_03_MAP_end.png` | Generated and accepted at thumbnail scale (see Map, below). Same fetch. |
| `exports/map/HO01_02-03_MAP_zoom.mp4` | Round 1 complete on Seedance 2.0 (historyId `Q4tluhdUnLoln0exkPm4`): two outputs, 3840×2160, 6.04 s, 24 fps, no audio. Both open on the start frame with no visible text. The 6.3 motion checks still need a viewer; pick one in the OpenArt library and save it under this name. |
| `exports/contact-sheet.png` | Built from the v6 shot list. Every shot has a tile; unsourced tiles carry the NEEDS_MANUAL reason and URL. |
| `exports/map/OPENART_LOG.csv` | Every historyId, model, mode and outcome. |

### Rights decisions (brief section 10)

- **Life, 13 May 1957** (shots 06, 07, 08, 09, 10). In copyright: cover, spread, Allan Richardson's photographs. Rights holder Dotdash Meredith, licensable through the LIFE Picture Collection. Editorial use on a monetised shop account is not a safe assumption. Decision for the edit: default to a period-accurate recreation of the spread for 09 and 10 (drifts across a page cut identically), and treat 06, 07 and 08 as licence-or-drop. Nothing was recreated in this build (brief section 0: "never a recreation" for a shot that cannot be sourced applies to photographs; the section 10 recreation of the spread is a rights route the edit still has to choose).
- **Portraits of María Sabina** (01, 14, 15). Best archive portraits are INAH / Fototeca Nacional (Nacho López, c.1975-80) under CC BY-NC-ND, which excludes commercial use without an INAH licence. The Commons category has 5 files with mixed provenance; check photographer and licence on each file page. The only fully cleared route is a LIFE Picture Collection licence of a 1955 Richardson frame.
- **Echevarría film stills** (14). Frame grabs from *María Sabina, mujer espíritu* (1979) need permission from the rights holder (Filmoteca UNAM / Nicolás Echevarría).
- **Estrada quotation** (15). Short verbatim quotation with attribution from *María Sabina: Her Life and Chants* (1981, Henry Munn's translation of *Vida de María Sabina*, 1977). Her words about the foreigners are commonly reproduced in English as the line beginning "From the moment the foreigners arrived..."; copy it exactly from the book page, not from this note, and put the page number in SOURCES.csv.
- **The strain name** (17). Appears once, only inside real third-party screenshots, with vendor names, prices and any species name blurred before the timeline. Nothing of Jude's or Hypha's in frame with it. The sources log carries no search terms for this shot by design.
- **Faces.** Every image of her is a real photograph with a logged source. Nothing generated.

### Map (shots 02-03, brief section 6)

- **Style references.** Harris YouTube frames could not be captured: YouTube is blocked from the build container, and this OpenArt connector does not expose `openart_upload_sign`, so no local file can be uploaded as a reference. Substitute used: two OpenArt-generated dark map plates (historyIds `hsoLidT5UiBjqRh2oSCX`, `Dcwyv09S28zSnahOLF57`) as `visualReferences` labelled "style reference". `refs/map/` is empty. If the Harris frames matter, upload them from a desktop OpenArt session and re-run 6.1 and 6.2.
- **Motion reference.** historyId `IDbmkGjjxF87lxxCQFgl` returns "History not found" on this account; it is not in the visible generation history either. The South Africa clip could not be used as the yardstick. Re-check the id.
- **Start frame.** `Lq2IzDydQO1wFBCxSY8D`, candidate D (`e82Vw6pkMZOZhY567Czv`). Accepted: no visible text, ocean darker than land, Mexico and New York in frame, no HUD.
- **End frame.** `Vjj0MnwMAyeB5xJfZ4sG`, candidate B (`9NfdJaenQxYaHbRAihJ6`). Accepted: one cream ring marker at the arc's end, arc enters from the top right, Oaxaca fills the middle, palette within a stop of the start frame.
- **QA caveat.** The build container cannot download from cdn.openart.ai, so both frames were checked on relayed 512 px thumbnails, not at 4K. Text at label size would not be visible at that scale. Confirm zero text on both frames at 4K in the OpenArt library before the clip is cut in; if either frame carries text, regenerate per 6.1 / 6.2 and re-run 6.3.
- **Video.** Round 1 of 3 on Seedance 2.0: historyId `Q4tluhdUnLoln0exkPm4`, two outputs, 16:9, 4K, 6.04 s, 24 fps, no audio, seed -1. Output 1 `J5EnKJlGedqGPaP7yMIu`, output 2 `JNFwHl3vUNgcbZDmAatC` (URLs in `OPENART_LOG.csv`). What could be checked from the build container: the first frame of each matches the start frame (wide map, New York marker, no text, no HUD). What could not: the 6.3 motion list. Judge both in the OpenArt library against it: no text at any point, no HUD, one constant-speed push with a soft settle, no rotation or wobble, marker fades in rather than drops, final frame matches the end frame. Save the accepted one as `exports/map/HO01_02-03_MAP_zoom.mp4`. If both fail, rounds 2 and 3 vary only the seed and run at 1080p (Jude's direction, 2,400 credits per round of two); then one round on `kling-3-omni`; then stop.
- **Polling.** `openart_creation_wait` is not exposed by this connector; `openart_creation_get` was used instead.
- **Labels on the clip (Jude's direction, 05 Sep: "text is used throughout").** `build/tools/label-map.py` burns the labels into the clip with real type instead of the model: it colour-tracks the violet New York marker in the opening frames and the cream ring in the closing frames, sets `NEW YORK` (follows the marker, gone by 2 s), `HUAUTLA DE JIMÉNEZ` then `SIERRA MAZATECA` (land in the final second, staggered 200 ms) and `OAXACA` (lower in the lit state, 60%) in JetBrains Mono, uppercase, 0.18 em tracking, cream, shadow `0 1px 6px rgba(0,0,0,0.9)`, fade plus 6 px slide over 300 ms, and writes a labelled MP4 plus an optional ProRes 4444 alpha overlay. Tested on a synthetic push built from the real start frame. Run it once the clip is fetched:

  ```
  ./maria-sabina/build/tools/fetch-assets.sh
  python3 maria-sabina/build/tools/label-map.py --in maria-sabina/exports/map/HO01_02-03_MAP_zoom.mp4 \
      --out maria-sabina/exports/map/HO01_02-03_MAP_zoom_labelled.mp4 \
      --overlay maria-sabina/exports/map/HO01_02-03_MAP_labels.mov
  ```

  `--text-scale 1` gives the brief's literal 11 px / 9 px sizes; the default 2.0 keeps them legible after the STACKED scale-down. `--ny-until`, `--land-at` and `--no-oaxaca` adjust timing and content.
- **AI-labelled stills (same direction).** Nano Banana Pro added labels to the accepted frames for static use: end frame with `HUAUTLA DE JIMÉNEZ` / `SIERRA MAZATECA` / `OAXACA` (historyId `ve00eL0C4nioQOpAjyEQ`, two outputs) and start frame with `NEW YORK` / `MEXICO` (`sDisSB6YOo5s1a8jucGZ`, two outputs). Labels are present; spelling and the accent could only be checked at thumbnail scale, so confirm at full size before use. AI text is not used on the moving clip: it warps during the zoom, which is why the brief kept it out of the model.
- **In Premiere.** Marker pulse and film emulation per section 8. If the labelled clip is used, the Premiere label layers for 02-03 are not needed; shot 04's labels still land in Premiere on the satellite settle.

### Per-shot notes

- **01** Portrait, 2.5D (subject 100→108%, background 100→104%), eyebrow `HYPHA ORIGINS · 01` at 0:01 top left, source label bottom right. Source: NEEDS_MANUAL (INAH o-302990 preferred; licence required).
- **02-03** Map clip, STACKED, 16:9 in the upper two thirds. PTC 1 below from 0:07.
- **04** Google Earth Studio satellite zoom on Huautla, exported as a 60 fps frame sequence at 2160×3840 into `exports/satellite/`. Match the framing of the map's final frame for the cut. NEEDS_MANUAL (interactive tool).
- **05** Real drone, Sierra Mazateca or Oaxaca highlands, slow lateral move, graded to archive. NEEDS_MANUAL (Pexels / Artgrid / Storyblocks searches in SOURCES.csv).
- **06** Richardson ceremony photographs from the Life scan, slow push, source label `LIFE · 13 MAY 1957`. Rights: see above.
- **07** Cover on the dark surface, whip zoom from black, one white frame on impact, 2-4° rotation, soft shadow, parallax.
- **08** Tight on the masthead date, yellow highlighter swipe (`#F5D90A` at 55%, Multiply, rough-edged, 400 ms left to right). The date comes from the document, not a card.
- **09** Spread punched into one column, drift down, yellow box highlight (35%) on the false-name passage, outside dims to 40%.
- **10** Tight on the printed village name, yellow swipe, hold a beat too long.
- **11** Five or six clippings fan out on the dark surface, torn edges, one pulls forward, snap to headline. Sources: HNDM search plus the retrospectives listed in SOURCES.csv.
- **12** Archive photo of visitors, 2.5D push. If nothing clears, a second clipping pulls forward.
- **13** Army / police clipping, snap to headline, highlight the relevant word in the original language.
- **14** Three later-life stills, 2.5D, barely moving, held long, source label on each.
- **15** Last still dimmed to 30%, her words typewriter in at ~14 chars/s in JetBrains Mono cream, attribution `MARÍA SABINA · TO ÁLVARO ESTRADA · 1977` at 60% beneath, book cover small in the corner.
- **16** PTC full frame, death line, no graphics, hold a beat.
- **17** Screenshots fan out, camera snaps between three instances, yellow highlighter on the word each time. Blur names, prices, species. Source labels generic (`VENDOR LISTING`, `FORUM · 2023`).
- **18** PTC. Hard cut to black on the last syllable. Nothing after.

### Deviations from the brief and why

00. **Text on the map (user direction, 05 Sep 2026).** Brief 6.4 kept every label out of the model and in Premiere. Jude asked for the regions to be named on the map itself. Done deterministically with `label-map.py` (real type), plus AI-labelled stills for static use. Section 12's "no text in generation prompts" was set aside for those two stills only.
0. **Resolution (user direction, 05 Sep 2026).** Jude asked mid-run for 1080p instead of 4K and for no expensive models where a cheaper one will do. Round 1 of the video had already been submitted at 4K (brief 6.3) and could not be cancelled; every further map round runs at 1080p on Seedance 2.0, and kling-3-omni stays the single fallback round only.

1. Harris style references replaced by OpenArt-generated plates (no upload route, YouTube blocked). See Map.
2. Motion reference historyId not found on this account.
3. Frame and video QA done on relayed thumbnails, not at 4K. Confirm in the OpenArt library.
4. `openart_creation_get` used for polling instead of `openart_creation_wait` (not exposed).
5. Stale assets from earlier briefs (AI clips, 9:16 MapLibre map, Remotion cards) were removed from the repository. The AI clips and test stills still exist in the OpenArt library (see the earlier historyIds in git history); ignore them.
6. Sourcing is logged, not downloaded: no route from the build container to the archives. `build/tools/fetch-assets.sh` pulls the map files and prints the manual list.

### Definition of done check (brief section 13)

- Every shot 01-18 has a tile: yes.
- Every sourced asset logged with URL and rights holder: yes (23 rows).
- Map clip passes every 6.3 check or the failure is documented with historyIds: round 1 produced two candidates; first-frame checks pass, motion checks are yours to run in a viewer; every id is in `OPENART_LOG.csv`.
- This file lists rights decisions, NEEDS_MANUAL items and deviations: yes.
