# Hypha — Instagram promo assets

## Screens (`screens/`)

Rebuilt app screens rendered from HTML via Playwright. No AI generation — exact type
and layout, and editable by changing the HTML and re-rendering.

    node shot.cjs        # writes courses.png, profile.png at 1560x3320

- `courses.html` — 8 Week DIY Grow course card
- `profile.html` — grower profile
- `common.css` — shared device frame + bottom nav
- `g.css` + `f*.woff2` — self-hosted Anton / Montserrat

### Decisions baked in

- Bottom nav standardised to 5 tabs (Home, Courses, Feed, Add, Profile) across both
  screens, matching the live app. The earlier mockups had a 4-tab bar.
- Course details come from the real DIY Course in Notion: 9 sections plus a
  contamination bonus (10 modules), ~30 min runtime, designed to run over 8 weeks.
- Placeholder content removed: "OATS / How to make Oats / joe" and "Sarah Chen".

## Brand

| | |
|---|---|
| Accent | `#7B3FF2` |
| Page | `#F7F5F0` |
| Heading | Anton |
| Body/UI | Montserrat 500–800 |
| Logo | black `hypha` wordmark, 1752x373 transparent PNG |

Voice: first person, lowercase, no hype.

## Offer

Annual signup gets a free kit for the first 500 users. One kit grows 1kg.
Pitch: everything needed to start cultivating — the course, the community, and 1-1
access to expert growers. Roughly £8 a kilo against ~£25 retail.

## Promo cut (9:16, ~12s)

| Beat | On screen |
|---|---|
| 0-3s | hand lifts phone over a fruiting tub — "supermarket mushrooms are £25 a kilo" |
| 3-6s | feed scrolling — "mine cost me £8" |
| 6-9s | Courses, then a 1-1 thread — "the course, the community, the growers who've done it" |
| 9-12s | logo on cream — "first 500 annual = free kit. 1kg." |

All mushrooms render as pioppinis (brown caps, slender clustered stems).

## Generation budget

Higgsfield Plus, no unlimited allowance.

| Step | Model | Each | Qty | Total |
|---|---|---|---|---|
| Hero frames | `nano_banana_pro` | 2 | 4 | 8 |
| Clips (5s, 9:16, silent) | `kling3_0` std | 7.5 | 4 | 30 |
| Assembly + captions | ffmpeg | 0 | | 0 |
