# ShroomRoom course B-roll — production log

Live record of approved assets, spend, and batch state. Updated as the run proceeds.

## World

- **Style / world master** (uploaded ref): `voBNtSWY4cpDVZzY07uT`
  Flat paper-cutout, thick cream-white outlines, paper grain, deep aubergine + violet LED.
  Same reference the `grow_` reel series was built on. Passed into every image job.

## Approved masters

| Asset | Status | OpenArt id | Notes |
|---|---|---|---|
| ~~M1 — character sheet~~ | **SUPERSEDED** | ~~`YwA3E4EhrbbuBiv9921W`~~ | Withdrawn. Jude chose the existing reel character instead. 180 credits sunk. |
| **CHARACTER** | **APPROVED** | `HINzQfJak0hyVgxhxtD0` | `grow_shot07_v3` from the reel series — standing, facing camera, full body. Curly dark brown hair, light stubble, **slate grey hoodie, dark grey joggers, white socks**. Passed into every shot with a person in it. |
| M2 — kitchen setting | pending review | — | history `J8MiUzulA7Z3mNwCO6Zk` — no people, unaffected by the character change |
| M5 — tub prop | pending review | — | history `WNh6ddJs4lklNzCCmqWR` — plain undrilled tub, bare substrate. Colonised / fruiting / spent states derive from it |
| M3 — whiteboard setting | pending review (v2) | — | v1 `0qV3r4YFuoA3F840MTjk` **void** (wrong character). v2 `xkeaNJu0eJLNdp7Vq8DS` |
| M4 — grow bedroom | reuse, already exists | (from `grow_` series) | shelf / desk / cupboard / grow-space scenes |

## Reference stack (every image job)

1. Style / world master — always
2. M1 character sheet — any shot with a person
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
| **Running total** | **468** |

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

## Decisions

- **Character is the existing reel character**, not a new sheet. `grow_shot07_v3`. Wardrobe
  across all 160 shots is therefore slate grey hoodie / dark grey joggers / white socks,
  not the navy crew-neck the shot list originally described.
- **Violet world, not warm kitchen.** Jude's call. The course lives in the same aubergine /
  violet-LED world as the `grow_` reels rather than the warm brown/cream General palette.
- **Drafts per shot.** 2 as standard. Review after batch 2 — if the plain DEMO shots come back
  clean first time, drop to 1 draft on those and keep 2 on the Pro diagram shots (~1,700 saved).
