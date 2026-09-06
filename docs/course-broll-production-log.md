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

## Prompting lesson — DO NOT NAME WHAT MUST NOT BE SEEN

The still air box tape failed twice because both prompts described **a hole covered by tape**.
Naming the hole makes the model draw a hole, and it then renders it as partly visible so that
both things it was told about are present. Negatives did not counteract it.

v3 never mentions a hole at all: the front face is described as an unbroken sheet of plastic
with two solid grey rectangles stuck onto it. The opening is implied, never drawn.

**General rule: describe only what should be visible.** For anything that must be hidden,
occluded or absent, describe the covering object as solid and the surface as continuous, and
put the hidden thing in the negatives only.

## Video failure policy — applied

0.9's video failed twice: v1 hallucinated, v2 animated the polyfill plugs as cotton balls being
thrown into the tub. **Stopped at two attempts per the standing rule** rather than spending a
third time.

Diagnosis: the shot has two near-identical objects plus small detachable-looking details
(polyfill), and PixVerse treats those as things to animate. Freezing them by name did not help;
naming them at all appears to invite motion.

**Resolution: 0.9 ships as a still**, with any drift added in the editor. No further spend.
Apply the same judgement to other shots whose only "motion" is a hand settling — a static
4 seconds under voiceover reads fine and cannot fail.

## Camera rule — LOCKED OFF BY DEFAULT

**PixVerse over-drives any camera instruction.** "One very slow, smooth camera push in" came
back on 0.8 as a hard zoom, far too close. From here the default is a **completely locked-off
camera**, stated explicitly and at length:

`THE CAMERA IS COMPLETELY LOCKED OFF AND DOES NOT MOVE AT ALL — no push in, no pull back,
no zoom, no pan, no tilt, no drift, no parallax.`

Only ask for camera movement where the shot genuinely needs it, and expect to have to fight it.

## Motion rule — TREAT IT AS A STILL

Also from 0.9: naming two similar objects in a scene invites the model to invent, swap or
duplicate them. Motion prompts must now **freeze every object explicitly by name**, state what
must not appear (holes, duplicates, transformations), and describe the shot as
"a still image with one micro-movement" rather than as an animation.

## Whiteboard rule — HE IS NOT DRAWING

The board shows a **completed** diagram, so he must not be mid-stroke on it. Posing him with a
marker touching the board reads as him drawing something that is already finished.

**Correct poses for a WB shot** — back three-quarter to camera, facing the board, and one of:
- open palm presenting the diagram
- one finger pointing at a single element
- arms folded, considering it

The marker is **capped and held down at his side, or resting in the board's tray**. His hand
never touches the board and never holds a marker against it.

**Affected shots** (prompted as "marker touching / near the board"): 0.5 roadmap, 1.2 tree,
1.7 race, 1.14 FAE.
- **1.14** regenerated (v2) and re-videoed. v1 still and video void.
- **0.5** fixed. Approved still `FcORuftLIK7KJTjL5Iie` (v3), replacement video
  `uN7huOM1urEE9fbg5Aq6`. Board and all nine icons preserved by editing pose only.
- **1.2 and 1.7** keep the drawing pose by Jude's decision — each appears once in its own
  section. Note 1.2 is also reused in §2, so the objection would recur there.

Unaffected (already correct): 0.2 pointing, 0.3 presenting, 0.10 arms folded, 1.4 pointing,
1.5 open hand.

## Character rule — NO LIP MOVEMENT (structural, from batch 4)

"No jaw movement, no lip movement" in the motion prompt does not reliably hold on PixVerse.
As with the tape: a negative cannot suppress what the composition invites. If the mouth is
visible and facing camera, the video model may animate it.

**So the rule is applied at the STILL stage, by composition:**

| Shot type | Default framing from batch 4 |
|---|---|
| DEMO | Hands and the object. Face out of frame, or in profile looking down at the task |
| WB | Back three-quarter to camera, facing the board. Mouth not visible |
| SCENE | Profile, or the figure small enough in frame that the mouth is a few pixels |

Mouth facing camera only where the shot genuinely needs it — and those shots **ship as stills**,
no video. Motion prompts keep the no-jaw / no-lip wording as belt-and-braces, but the
composition is what actually prevents it.

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
| ~~M6 v1 — still air box~~ | **DEFECTIVE** | ~~`YT4ROcuLkrCB59f2weLH`~~ | Tape patches did not fully cover the arm holes. Flaw would propagate to every SAB shot |
| ~~M6 v2 — still air box~~ | **DEFECTIVE** | — | Tape still did not cover. Enlarging the tape did not work because the prompt still named the hole |
| **M6 v3 — still air box** | **APPROVED** | `qegFfiC5DsBfsCL1o2k2` | Prompt never mentions a hole — unbroken plastic face with two solid tape rectangles. Third attempt; the rewrite worked |
| **M8 — jar (base, empty, two-piece lid)** | **APPROVED** | `E4tbdBbKwvnYhlZpkP7S` | Recurs in ~25 shots across §1–§4; states (¾ full, foiled, colonising, white) derive from it |
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
| Batch 2 videos — 5 × PixVerse 720p 4s | 250 |
| M6 v2 SAB master, tape fix (Pro ×2, 2K) | 72 |
| 0.9 video retry (locked-off) | 50 |
| M6 v3 SAB master, rewritten prompt (Pro ×2, 2K) | 72 |
| 0.8 v2 redo on M6 v3 (Lite ×2) | 28 |
| Batch 3 stills — 1.1, 1.3, 1.4, 1.5 (Lite ×2 each) | 112 |
| Batch 3 stills — 1.2 tree/mycelium (Pro ×2, 2K) | 72 |
| Batch 3 videos + 0.8 redo video — 6 × PixVerse 720p 4s | 300 |
| Jar master M8 (Pro ×2, 2K) | 72 |
| Batch 4 stills — 1.6, 1.8 start, 1.9, 1.10 (Lite ×2 each) | 112 |
| Batch 4 stills — 1.7 race board (Pro ×2, 2K) | 72 |
| 1.8 end frame (Lite ×2) | 28 |
| Batch 4 videos — 1.6, 1.7, 1.9, 1.10 | 200 |
| Batch 5 stills — 1.11, 1.12, 1.14, 1.15 (Lite ×2), 1.13 (Pro ×2, 2K) | 184 |
| 1.12 v2 reframe — body in shot (Lite ×2) | 28 |
| 1.12 + 1.14 v2 videos | 100 |
| 0.5 v3 replacement video | 50 |
| Batch 7 stills — 1.16, 1.18, 1.19, 1.20 (Lite ×2), 1.17 pot cutaway (Pro ×2, 2K) | 184 |
| 1.17 v2 — water line corrected (Pro ×2, 2K) | 72 |
| **Running total** | **3,504** |

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
**Batch 7 = §1 shots 1.16–1.20. Stills submitted — completes section 1.**

| Shot | Tag | History |
|---|---|---|
| 1.16 foil over the lids | DEMO | `RPkfvLHOLOEevfUNbCOW` |
| 1.17 pot cutaway — trivet, water line, 4 jars | DEMO | v1 `zbgj2ytQ4I3val1MIdqw` **void** — water drawn at jar-shoulder height, i.e. a water bath. v2 `wY1oR0YCX0zNhAKB0oXW` |
| 1.18 rolling boil vs gentle simmer | DEMO | `ShDyFJYrREXgSDlJjTwC` |
| 1.19 jars cooling overnight | SCENE | `UchKAorNOgx6Bv0DOYEt` |
| 1.20 warm jar kills spores board | WB | `VHyXi35vxDEmV1vE2aqj` |

1.17 is the section's key teaching diagram. **Correct geometry, per Jude:** a shallow layer of
water on the pot base, the trivet standing in it with its platform DRY above the waterline, and
the jars on the dry trivet with a clear air gap beneath them. The jars are in steam, never in
water. v1 was wrong — it put the water at jar-shoulder height, which is a water bath.

**Script ambiguity worth fixing before filming.** §1 step 7 reads "fill with water up to about
where the jars will sit", which a student can easily read as filling up around the jars. The
next line ("we don't want them boiling in a bath") corrects it, but the first line is what
people act on. Suggest tightening to something like "fill with water to just below the trivet —
the jars should sit above the water, not in it".
1.18 and 1.19 have no people and no hands. 1.20 uses the corrected presenting pose.

**Next: §2 inoculation, batches 8–9 (2.1–2.14).** Almost entirely hands-in-the-SAB; the SAB and
jar masters both exist. 2.7 (needle flamed until glowing) should be a start→end transition —
fire is the one thing that must genuinely move, and the likeliest to be hallucinated.

**Batch 5 = §1 shots 1.11–1.15.**

| Shot | Tag | Approved still |
|---|---|---|
| 1.11 rice steaming off | DEMO | `6jfuc94FP6frwAymCBZO` — video `IMZvyA04i1LhEuuzLykv` |
| 1.12 fill jar to ¾ | DEMO | `QBmHvlkJ7TuMVQm1V5vU` (v2) — video `3wpx3aJgwjJkZFolqUOQ` |
| 1.13 two lid types | DEMO | `1oMpOfMghePwpaIndRsf` — **ships as a still**, no video: two near-identical objects, 0.9's failure signature, and no natural motion in shot |
| 1.14 FAE / jar breathing board | WB | `IqJxddQ8WhEIbj07yEO3` (v2, presenting pose) — video `ISalpfBQmaTixSqzR1KF`. v1 still + its video void (drawing pose) |
| 1.15 sealed cupboard gag | SCENE | `JIUa3FGT7dNF9zfcQBWY` — video `JGi6WLknq9dce12JeS8K` |

**Hands-only framing needs a hard crop.** "Face not in frame" is not enough — 1.12 v1 drew a
full torso and an arm arcing over the top. v2 specifies arms cut by the frame edge at
mid-forearm and lists torso, shoulders, elbows, neck and head in the negatives.

**Batch 4 = §1 shots 1.6–1.10, plus the jar master. Stills submitted — first batch under the no-face-to-camera framing.**

| Shot | Tag | Approved still | Video |
|---|---|---|---|
| 1.6 factory rice pouch | SCENE | `LgEpv2nm2vLoDflqcXGp` | `u7uLsPEhcgARZHZTTHeL` |
| 1.7 the race board | WB | `v1SH2G1PHqke2FKQE9s9` | `3Ty87QlJrpBUPoJXuPkY` |
| 1.8 rinse — START (cloudy) | DEMO | `SINWX3zHKrVbZPZSD2YN` | end frame `jTgznBKQlKbWLvo8xDGl`, then transition |
| 1.9 simmer + timer | DEMO | `neU6U5iJG9EmN9ffD9tz` | `2kuBva6jF054gT8toDu3` |
| 1.10 cold rinse | DEMO | `YIRKUN5qtjyWXDb0oBNy` | `H8648OKEU9NHuuwvW5hR` |

1.8's END frame (clear water) is derived from the picked start frame — 1 Lite draft, next turn.
Videos after picks. 1.8 is the batch's one start→end transition (PixVerse with endFrame).

**Batch 3 = §1 shots 1.1–1.5, plus the 0.8 redo on the corrected SAB master. Stills approved, videos submitted.**

| Shot | Tag | Approved still | Video history |
|---|---|---|---|
| 0.8 still air box (v2, on M6 v3) | DEMO | `RD6HkWnUWNgUCgvVdcIq` | `bYIzJpK8Xsl0LbllXSkf` |
| 1.1 bag of brown rice | DEMO | `aJTo5LfQ6jSO6LUMOjXM` | `QSiZIN37zO5Wy54XcZoI` |
| 1.2 tree = mycelium, fruit = mushroom | WB | `VfxUOfgWKSbrFvkAVAS3` | `RvCYaBVIgY8hgY4owQuu` |
| 1.3 forest floor cross-section | SCENE | `n5S58lk8Nn2jA7tk7AW2` | `yfTD0SadSx3qHGUJCjvx` |
| 1.4 mushroom 90% water | WB | `hUPO35Nka7hRxRx8qRFt` | `87wxmKComo4a5OGAC7x1` |
| 1.5 water balance seesaw | WB | `cyLql2ar7gJJwZAam0vV` | `cxjN0eONTMfxh6i3Rb81` |

All six videos under the new rules: camera locked off at length, every object frozen by name,
described as a still with one micro-movement, no jaw or lip movement. Jude chose video for all
six over stills-for-boards.

**Next: batch 4 = 1.6–1.10** (rice pouch factory, the race board, rinse transition, simmer pot,
cold rinse). 1.8 is the first start→end transition shot. **Jar master still recommended before
1.9–1.12**, where jars start recurring.


**Batch 1 = shots 0.1–0.5. Stills all approved, videos submitted.**

| Shot | Tag | Approved still | Video history |
|---|---|---|---|
| 0.1 opener — beside the fruiting tub | SCENE | `yEQ9eYOKvFb9FuEr76tf` | `nyK6LDcmAKrVk4ADRQLc` |
| 0.2 dried vs fresh piles | WB | `fnCmh4UoAbCfuvs5wz3j` | `Q28wsgObryyETlvnT4T9` |
| 0.3 the loop | WB | `NuP1ljnZKHyysTyQV9sn` | `xPhKWK9Y3NxtqByzUweK` |
| 0.4 legal shrug | DEMO | `t1mH6KsJVPaqwIc8AvyK` | `tBSBiHZ3fpI7FY50BxW5` |
| 0.5 roadmap (9 step icons) | WB | `BmdI1IpXEAEnY3JVSXdA` | `ncKNtPZDxQPnlpgZo2KA` |

All videos: PixVerse V6 image2video, 720p, 4s, silent, 50 credits each.

**Batch 2 = shots 0.6–0.10. Complete — stills approved, videos submitted.**

| Shot | Tag | Approved still | Video |
|---|---|---|---|
| 0.6 consumer → producer | SCENE | `fcU4HyToBSeV7P7FKl7T` (v2) | `s7QoA3SC0JbugqXpDCYB` |
| 0.7 kit flat-lay | DEMO | `ll5xJ3BZDRckTWSbiEOV` | `lbUkPL01xEuxYuYv1LkO` |
| 0.8 still air box | DEMO | v2 rendering on M6 v3 | after still approval |
| 0.9 drilled vs plain tub | DEMO | `aqqNOMBNehqhDHS1iQsM` | **ships as a still.** Two video attempts failed; stopped per policy |
| 0.10 don't-need board | WB | `lraBsHlEUxIMBKQ6poCU` | `6TyXPLo5fNfwBgsPn75A` |

**Section 0 shot, with 0.8 to redo and 0.9's video retried.**
**Batch 3 = §1 shots 1.1–1.5. Stills submitted. Videos held until all five stills are reviewed.**

| Shot | Tag | Still |
|---|---|---|
| 1.1 rice bag | DEMO | rendering |
| 1.2 tree / mycelium board (reused §2) | WB, Pro 2K | rendering |
| 1.3 forest floor cross-section | SCENE | rendering |
| 1.4 mushroom filled ~90% with water (reused §5 §8) | WB | rendering |
| 1.5 seesaw — droplet vs mould, balanced | WB | rendering |

No jar in 1.1–1.5. **Jar master needed before 1.12** (first jar shot); jars recur in ~25 shots
across §1–§4.

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
