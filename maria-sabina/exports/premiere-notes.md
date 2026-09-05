# HO01 María Sabina · Premiere notes

Master 9:16, 2160x3840, 60 fps. All generated clips are 720p and scale up under the grain plate. UK English in every string. No em dashes. No end card, no logo, no outro: the video ends on the line.

## Status

No shots generated yet. See `cost-gate-report.md` for the three blockers and the decisions needed. Per-shot notes below are ready for when clips exist.

## Per-shot

| Shot | Time | In Premiere |
|---|---|---|
| 01 | 0:00 to 0:07 | Eyebrow `HYPHA ORIGINS · 01` in at 0:01. Camera favours the banker for five seconds. Time the head turn so the cut to 02 lands on "woman" at 0:06. |
| 02 to 03 | 0:07 to 0:12 | Map. Labels `NEW YORK` and `HUAUTLA DE JIMÉNEZ` added here, JetBrains Mono, uppercase, tracked, violet. Lower thirds for Wasson and Sabina on the settle. Clip is generated without any labels. |
| 04 | 0:12 to 0:15 | Match cut from the map pin into the Sierra Mazateca wide. No narration under it. |
| 05 | 0:15 to 0:21 | Straight cut. |
| 06 | 0:21 to 0:25 | Window shifts aubergine to dawn inside the clip. |
| 07 | 0:25 to 0:28 | Typewriter beat continues "wrote it up". |
| 08 | 0:28 to 0:31 | Model renders `LIFE` and `MAY 13, 1957`. Check both at 1080 width before accepting. Highlighter swipe is in the clip. |
| 09 | 0:31 to 0:34 | Model renders `Seeking the Magic Mushroom` and `Eva Mendez`. Body copy must read as grey lines only. |
| 10 | 0:34 to 0:37 | Model renders `Huautla de Jiménez`. Hold the last second. This is the turn. |
| 11 | 0:37 to 0:42 | Tourists lengthen down the road. |
| 12 | 0:42 to 0:44 | 2s. If generated at 3s, trim head. |
| 13 | 0:44 to 0:51 | Three clips A (2s), B (2s), C (3s) cut in sequence. |
| 14 | 0:51 to 0:56 | Her quote typed in over the static shot, cream JetBrains Mono, with attribution to Estrada, Vida de María Sabina (1977). Not rendered by the model. Quote text to be supplied by Jude verbatim from the book. |
| 15 | 0:56 to 0:59 | Slow pull back. |
| 16 | 0:59 to 1:03 | `Mazateca` is the only legible word on the screen. Nothing of Hypha's in frame. |
| 17 | 1:03 to 1:05 | Hard cut to black on the last syllable of "why". Nothing after. |

## Post over everything

Grain plate, gate weave, flicker and vignette per the earlier film emulation spec. Sound: paper rustle on every prop move, candle, footsteps as soft card taps.

## Unresolved

- BUDGET_TOTAL not set.
- Per-job cap of 120 is below the quoted price of the map (400) and several other jobs. See the cost gate report.
- Shot 12 cannot run at 2s on Gemini Omni or Kling. Proposed: Wan at 2s.
- Generated media cannot be saved into the repo from this environment because cdn.openart.ai is blocked by egress policy.
- Reference frame `ref_map_sa.png` not saved locally for the same reason. Hosted URL and a ready visualReference object are in `style/ref_map_sa_source.json`.
- Her quote for shot 14 is not in the brief. Jude to supply verbatim.
