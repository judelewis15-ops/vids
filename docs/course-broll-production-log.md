# ShroomRoom course B-roll — production log

Live record of approved assets, spend, and batch state. Updated as the run proceeds.

## Project

All generations from this point land in the OpenArt project
**ShroomRoom DIY Course — B-roll** — `QsNx6KDWHkO0Mw2Cj1TB`.

**Limitation:** the OpenArt MCP has no move or re-assign tool — a generation's project is fixed
at submission time. The 14 jobs made before the project existed (M1 v1–v3, M2, M3 v1–v2, M5,
M5b, and batch 1 shots 0.2–0.5 v1) are in **Personal Project** and cannot be moved. They still
work as references, since references are by asset id, not by folder. Only remedy is to
regenerate them into the course project, which costs credits and risks drift — not recommended.

## Style tags

No tagging API exists either, so the tag is carried in the **prompt slug**, which is visible
and searchable in OpenArt's history. Convention from here:

`course_<TAG>_<section>-<shot>_<name>_v<n>`  e.g. `course_WB_0-5_roadmap_v2`

| Tag | Meaning |
|---|---|
| `MASTER` | Reusable master asset — character, setting, prop |
| `WB` | Whiteboard shot — he explains at the board |
| `DEMO` | He performs the step, hands visible |
| `SCENE` | Set piece / metaphor, no procedure |
| `MAP` | Uses the Maps style reference, not General |

## Character rule — NO TALKING

From batch 2 on, the character **never speaks or addresses camera** in B-roll. This footage sits
under Jude's own talking-head voice; a second Jude mouthing words on screen fights it.

**Every prompt with the character must carry:** mouth closed, lips together, not speaking, not
addressing the camera; attention on the task or the board rather than the lens.
**Negative:** `talking, speaking, mouth open, open mouth, mid-speech, addressing camera`.

Expressions still allowed: neutral, focused, a small closed-mouth smile, raised eyebrows.
Applies to stills and to video motion prompts — no jaw or lip movement in the animation either.

## World

- **Style / world master** (uploaded ref): `voBNtSWY4cpDVZzY07uT`
  Flat paper-cutout, thick cream-white outlines, paper grain, deep aubergine + violet LED.
  Same reference the `grow_` reel series was built on. Passed into every image job.

## Approved masters

| Asset | Status | OpenArt id | Notes |
|---|---|---|---|
| ~~M1 — character sheet~~ | **SUPERSEDED** | ~~`YwA3E4EhrbbuBiv9921W`~~ | Withdrawn. Jude chose the existing reel character instead. 180 credits sunk. |
| CHARACTER (origin) | superseded by M7 | `HINzQfJak0hyVgxhxtD0` | `grow_shot07_v3` from the reel series. Defined the likeness; too busy to serve as a reference. Used for shots 0.1–0.10 and to derive M7. |
| **M2 — kitchen setting** | **APPROVED** | `5FSHm4tNka40DLIvvksR` | empty violet kitchen, counter + hob, clear centre and lower third |
| **M5 — tub prop (base)** | **APPROVED** | `ewGam1wDW2bU1k5Mp9sm` | plain undrilled tub, bare substrate, lid leaning at its right |
| M5b — tub, fruiting state | pending review | — | history `K3mwkEbZqLGxJF59D5nO`. Derived from M5. Needed by 0.1 and all §7/§8 tub shots |
| M5c — tub, colonised state | not yet made | — | needed at §6. Derive from M5 when §6 comes up |
| M5d — tub, spent state | not yet made | — | needed at §9. Derive from M5 when §9 comes up |
| **M6 — still air box** | **APPROVED** | `YT4ROcuLkrCB59f2weLH` | upside-down clear tub, two taped arm holes with slits. Recurs through §2 and the SAB companion |
| **M7 — character sheet** | **APPROVED — canonical** | `VMzzkzSYH3prW0hFOpAh` | Four clean views on plain aubergine. **This is the character reference on every shot from 0.8 onward**, replacing the scene image `HINzQfJak0hyVgxhxtD0`. |
| **M3 — whiteboard setting** | **APPROVED** | `xfKOBc3z06AxeyC7BW4h` | blank board left two-thirds, character right. v1 void — wrong character |
| M4 — grow bedroom | reuse, already exists | (from `grow_` series) | shelf / desk / cupboard / grow-space scenes |

## Reference stack (every image job)

1. Style / world master — always
2. **M7 character sheet** (`VMzzkzSYH3prW0hFOpAh`) — any shot with a person
3. Setting master — M2 kitchen, M3 whiteboard, or M4 bedroom
4. Prop master — where an established prop recurs (tub, jars, bag)

## Working method

Batches of 5 shots. Per batch: generate all images → **stop for approval** → generate videos for
approved stills → **stop**. Next batch does not start until the previous is cleared.

## Spend

| Item | Credits |
|---|---|
| M1 v1 (2 drafts) | 72 |
| M1 v2 (2 drafts, called off) | 72 |
| M1 v3 (recolour, approved) | 36 |
| M2 kitchen (2 drafts) | 72 |
| M3 whiteboard v1 — void, wrong character | 72 |
| M5 tub (2 drafts) | 72 |
| M3 whiteboard v2 (2 drafts, 2K) | 72 |
| M5b fruiting tub (2 drafts, 2K) | 72 |
| Batch 1 images — 0.2, 0.3, 0.4 (Lite ×2 each) | 84 |
| Batch 1 images — 0.5 roadmap v1 (Pro ×2, 2K) — **void**, empty circles | 72 |
| Batch 1 images — 0.5 roadmap v2 (Pro ×2, 2K) — step icons | 72 |
| Batch 1 images — 0.1 opener (Lite ×2) | 28 |
| Batch 1 videos — 5 × PixVerse 720p 4s | 250 |
| Batch 2 images — SAB master, 0.6, 0.7, 0.9, 0.10 | 228 |
| 0.6 v2 character correction (Pro ×2, 2K) | 72 |
| M7 character sheet (Pro ×2, 2K) | 72 |
| 0.8 still air box (Lite ×2) | 28 |
| **Running total** | **1,446** |

Opening balance 99,608. Project estimate 16,197 incl. 15% contingency.
M1 came in 36 over its 144 budget; absorbed by contingency.

## Whiteboard rule — DIAGRAM ONLY

Boards are generated carrying the **visual logic only**: shapes, arrows, icons, columns,
paths, clock faces, comparisons. **All digits and multi-word labels are added in the editor.**

Reason: in-image text is unreliable, digits worst of all, and 17 of the 57 board shots carry
numbers that are load-bearing instructions (90 min sterilise, 21–24°C, 18°C, day ranges, the
9-stop roadmap). A wrong number in a paid cultivation course is a failed grow, not a typo.
Compounding it, the OpenArt CDN is blocked from this session, so generated text cannot be
proofread here — only Jude can see it.

**Every board prompt must therefore carry:**
`NO TEXT ANYWHERE — no letters, no words, no numbers, no labels` in the body, and
`text, letters, words, numbers, labels, writing, doodles, smudges` in the negative.
Leave clean flat space where each label will sit, so the editor overlay has somewhere to go.

Short, low-risk single words (TREE, FRUIT, MOULD) may be generated where they are decorative
rather than instructional — specified verbatim and kept off the frame edges.

## Resolution

Nano Banana Pro at **2K costs the same 36 credits as 1K** (only 4K doubles, to 72).
All Pro shots run at 2K from here.

## Batch state

**Batch 1 = shots 0.1–0.5. Stills all approved, videos submitted.**

| Shot | Tag | Approved still | Video history |
|---|---|---|---|
| 0.1 opener — beside the fruiting tub | SCENE | `yEQ9eYOKvFb9FuEr76tf` | `nyK6LDcmAKrVk4ADRQLc` |
| 0.2 dried vs fresh piles | WB | `fnCmh4UoAbCfuvs5wz3j` | `Q28wsgObryyETlvnT4T9` |
| 0.3 the loop | WB | `NuP1ljnZKHyysTyQV9sn` | `xPhKWK9Y3NxtqByzUweK` |
| 0.4 legal shrug | DEMO | `t1mH6KsJVPaqwIc8AvyK` | `tBSBiHZ3fpI7FY50BxW5` |
| 0.5 roadmap (9 step icons) | WB | `BmdI1IpXEAEnY3JVSXdA` | `ncKNtPZDxQPnlpgZo2KA` |

All videos: PixVerse V6 image2video, 720p, 4s, silent, 50 credits each.

**Batch 2 = shots 0.6–0.10.** Stills mostly approved.

| Shot | Tag | Approved still |
|---|---|---|
| 0.6 consumer → producer | SCENE | v2 done `MpPLxuReEBACDlTlAcA4` — layout kept, character corrected. Awaiting pick |
| 0.7 kit flat-lay | DEMO | `ll5xJ3BZDRckTWSbiEOV` |
| 0.8 still air box | DEMO | rendering `995XMg8SkWZO2wibJlyM` — first shot built on M7 |
| 0.9 drilled vs plain tub | DEMO | `aqqNOMBNehqhDHS1iQsM` |
| 0.10 don't-need board | WB | `lraBsHlEUxIMBKQ6poCU` |

## Character drift — root cause and fix

0.6 v1 came back with the wrong face. Cause: the character reference in use
(`HINzQfJak0hyVgxhxtD0`) is a full bedroom scene, not a character sheet — the model has to
locate the man inside a busy frame and invent unseen angles. 0.6 needed him twice, in two
lighting states, in poses absent from the reference, so it invented.

Fix: **M7**, a clean four-view sheet derived from that image. Once approved it becomes the
character reference on every shot. The `grow_` series prompts reference a proper "CHARACTER
sheet" upload, so one exists in Jude's uploads — it could not be identified from this session
(uploads are unviewable here and three candidates are unlabelled), hence deriving a new one.

Batch 1's five shots were single-figure and close to the reference pose, so they are probably
unaffected; reissue against M7 if any look off.

## Decisions

- **Character is the existing reel character**, not a new sheet. `grow_shot07_v3`. Wardrobe
  across all 160 shots is therefore slate grey hoodie / dark grey joggers / white socks,
  not the navy crew-neck the shot list originally described.
- **Violet world, not warm kitchen.** Jude's call. The course lives in the same aubergine /
  violet-LED world as the `grow_` reels rather than the warm brown/cream General palette.
- **Drafts per shot.** 2 as standard. Review after batch 2 — if the plain DEMO shots come back
  clean first time, drop to 1 draft on those and keep 2 on the Pro diagram shots (~1,700 saved).
