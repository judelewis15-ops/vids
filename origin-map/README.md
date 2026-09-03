# Origin Map

A standalone single-page site: an interactive world map of pins. Each pin is one catalogue entry with a name, location, short story, photo, optional article link and optional Instagram reel. Tapping a pin opens a detail panel. Pins cluster when zoomed out and split apart when zoomed in.

No framework, no build step. Four files plus this README:

```
index.html       page shell
app.js           map, panel, search, chips, hash links
styles.css       visual system
data/pins.json   the catalogue (GeoJSON)
```

Map rendering is [MapLibre GL JS](https://maplibre.org/) from a CDN, drawn as a globe. There is no tile server: land is a dot matrix generated once from Natural Earth 1:110m polygons into `data/land-dots.json`, so the map needs no API key and makes no map-data requests at view time. Fonts come from Google Fonts. Photos live in a Cloudflare R2 bucket. The site is deployed on Cloudflare Pages.

## Run it locally

Any static file server works. The page fetches `data/pins.json`, so opening `index.html` straight from disk will not load pins in most browsers.

```
cd origin-map
python3 -m http.server 8080
# then open http://localhost:8080
```

## How to add a pin

Add one Feature to the `features` array in `data/pins.json`:

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [LNG, LAT] },
  "properties": {
    "id": "slug-for-this-pin",
    "name": "Display Name",
    "latin": "Psilocybe cubensis",
    "region": "Region or city",
    "country": "Country",
    "summary": "Two sentences. That is enough for the panel.",
    "image": "https://YOUR_R2_PUBLIC_DOMAIN/slug-for-this-pin.jpg",
    "article_url": "https://example.com/the-longer-article",
    "reel_id": "C1a2B3c4D5e",
    "tags": ["cacao", "single-origin"]
  }
}
```

Rules:

- **Coordinates are `[longitude, latitude]`**, GeoJSON order. Longitude first. A quick sanity check: longitude is between -180 and 180, latitude between -90 and 90, and for most of Europe, Africa and Asia longitude is the smaller number.
- `id` must be unique. It becomes the shareable link (`https://your-domain/#slug-for-this-pin`), so use lowercase letters, digits and hyphens only.
- `latin` is optional. When set it appears in italics directly under the name (use it for a scientific name). Leave it out or set it to `""` to hide the line.
- `article_url` and `reel_id` may be empty strings (`""`). The panel hides the button and the reel when they are empty.
- `image` should be the full public URL of the photo. If it is empty or fails to load the panel shows a plain gradient block instead, so nothing breaks.
- `tags` is an array of strings. Every unique tag across all pins becomes a filter chip, so keep tags short and consistent (`"cacao"`, not `"Cacao "` in one place and `"cocoa"` in another).
- Keep the file valid JSON: commas between features, no trailing comma after the last one. Paste it into any JSON validator if the map comes up empty.

The file ships with three strain pins (Leucistic Cambodian, Golden Teacher, Amazonian) with empty `image`, `article_url` and `reel_id` fields. Fill those in as the photos, articles and reels are ready.

## How to upload an image to R2

1. Export the photo as a JPEG, landscape, at least 1600 px wide. The panel crops it to 16:9 with the middle of the picture kept, so leave the subject near the centre.
2. Name the file after the pin's `id`, e.g. `slug-for-this-pin.jpg`.
3. In the Cloudflare dashboard go to **R2 → your bucket → Upload** and upload the file. Or from the command line with Wrangler:

   ```
   npx wrangler r2 object put YOUR_BUCKET_NAME/slug-for-this-pin.jpg --file ./slug-for-this-pin.jpg
   ```

4. The bucket needs a public domain (R2 → bucket → Settings → Public access → Custom Domains). Once that is set, the photo is at `https://YOUR_R2_PUBLIC_DOMAIN/slug-for-this-pin.jpg`. Put that full URL in the pin's `image` field.

## How to find an Instagram reel ID

1. Open the reel on instagram.com (or tap **Share → Copy link** in the app).
2. The URL looks like `https://www.instagram.com/reel/C1a2B3c4D5e/`. The reel ID is the part between `/reel/` and the next slash: `C1a2B3c4D5e`.
3. Put that string in the pin's `reel_id` field. The site builds the embed URL itself (`https://www.instagram.com/reel/ID/embed/`).

The reel is only loaded into the page when its panel is open and is removed when the panel closes, so nothing keeps playing in the background. The account must be public for the embed to work.

## How to deploy

The site is static, so Cloudflare Pages serves the repo as-is.

1. Push this folder to a Git repo on the `main` branch. If this folder is the root of the repo, the layout above is the repo root.
2. In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**, pick the repo and the `main` branch.
3. Build settings: framework preset **None**, build command **empty**, build output directory **`/`** (if the site lives in a subfolder of the repo, put that folder name instead, e.g. `origin-map`).
4. Save and deploy. Every push to `main` redeploys.
5. Custom domain: in the Pages project go to **Custom domains → Set up a custom domain**, enter your map domain. If the domain's DNS is already on Cloudflare, the CNAME record is created for you. Otherwise add a CNAME from the domain to `your-project.pages.dev`.
6. HTTPS is automatic once the domain is active.

To preview a change before it lands on `main`, push a branch: Pages builds a preview URL for it.

## Embedding in a Shopify page

`shopify/build.py` turns the four source files into one HTML fragment, `shopify/page.html`, that runs inside a Shopify page body. The map is a fixed-height stage of `100vh - 140px` (the site header allowance, `HEADER_ALLOWANCE` in the script) so the globe fills what is left below the header with no page scroll; the theme's own page title is hidden because the globe is the content; all styles are scoped to `#origin-map`. Rebuild after any change to the source files:

```
python3 shopify/build.py
```

Then paste `shopify/page.html` into the page body (Online Store > Pages > the page > `<>` HTML view) or send it as the `body` in a `pageCreate` / `pageUpdate` Admin API call. Pins are embedded in the fragment, so `data/pins.json` edits need a rebuild and re-paste too.

## Regenerating the land dots

`data/land-dots.json` is committed, so you only need this if you change the spacing or want fresh Natural Earth data.

```
cd origin-map
npm install
npm run build:dots            # 0.9° lattice, longitude spacing scaled by 1/cos(lat)
node scripts/build-dots.js --no-cos   # plain lattice, denser towards the poles
node scripts/build-dots.js --spacing 0.7
```

The script downloads Natural Earth 110m land as GeoJSON (falling back to the same data from the `world-atlas` npm package if the download fails), keeps lattice points that fall on land, rounds to two decimals and writes a GeoJSON FeatureCollection with a `lat` property on each point. The Shopify build packs the lattice as row runs so the page body stays small.

## Shooting the series intro

`index.html?fly=<pin id>` is cinematic mode: no controls, no attribution, no panel, pitch allowed, and `window.__origin` on the page with `view(id, zoom)` (cut to a pin), `fly(id, zoom, ms)` (ease into it), `props(id)` and `idle()` (resolves after the next render).

`shots/intro-shot.js` is the series intro as a pure function of time (`window.__shot.setTime(seconds)`): hold on the globe, whip into the episode pin with the camera tilting, fill the region outline, pulse the pin, pop the label, then tilt down over the land. Region outlines live in `data/regions/` (KwaZulu-Natal is cut from Natural Earth 10m admin-1). Render it with:

```
npm i -D playwright                      # once; CHROME=/path/to/chrome reuses an installed browser
PIN=natal-super-strength REGION=data/regions/kwazulu-natal.json node scripts/shoot-intro.mjs
ffmpeg -framerate 60 -i shots/frames/f%04d.jpg \
  -vf "tmix=frames=3:weights='1 2 1',fps=30,format=yuv420p" \
  -c:v libx264 -crf 17 -movflags +faststart shots/episode-01/intro.mp4
```

`KEYS="0,1.25,4"` saves stills at those seconds instead, for checking a new pin's framing before a full render. The render is resumable: frames already on disk are skipped. Finished clips and key frames live in `shots/<episode>/`.

## Settings you might want to change

All in `app.js`, near the top:

| Constant | Default | What it does |
| --- | --- | --- |
| `INITIAL_CENTER`, `INITIAL_ZOOM` | `[10, 20]`, `1.6` | Starting view. The map renders as a globe. |
| `LIMB_CLEARANCE` | `40` | On load the zoom is adjusted so the globe sits fully visible with this many pixels between its edge and the nearest stage edge. Set to `0` to keep `INITIAL_ZOOM` as is. |
| `MIN_ZOOM`, `MAX_ZOOM` | `1`, `12` | Zoom limits. |
| `OPEN_ZOOM` | `5` | Zoom the map eases to when a pin is opened from a link or the list. |
| `TAG_MATCH` | `'any'` | With several chips selected, `'any'` shows pins that have at least one of them, `'all'` shows only pins that have every one. Search text always combines with the chips using AND. |

Globe colours live at the top of `app.js`: `GLOBE` (space, ocean, sky), `DOT_COLOR` and `DOT_RADIUS` (the land dots) and `PIN`. The gloss highlight is the `.gloss` rule in `styles.css`.

## Mobile notes

- Under 768px the panel is a bottom sheet. Drag the handle, or swipe anywhere on the sheet: pull down from the top of the content to shrink or close it, push up to expand it. Once the content is scrolled, swiping scrolls the content as normal.
- Layout respects the phone's safe areas (notch, home indicator) via `env(safe-area-inset-*)`.
- The search field is 16px so iOS Safari does not zoom the page when it is focused.

## Accessibility notes

- The panel is a `role="dialog"` with `aria-modal="true"`. Focus moves into it when it opens and back to where it came from when it closes. Escape closes it.
- Map pins are not keyboard reachable in MapLibre, so a list of every pin is rendered below the map for screen readers and keyboard users. It is visually hidden until it receives focus (Tab past the map, or use the "Skip to list of pins" link that appears on the first Tab press).
- All colours are the three brand colours at various opacities, and the text contrast passes WCAG AA.
