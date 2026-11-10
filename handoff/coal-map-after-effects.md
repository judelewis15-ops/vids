# Handoff: coal and the vote, map-led reel in After Effects

This is a brief for a Claude session running on the PC that has After Effects installed. It was written in a cloud session that cannot reach that PC. Everything you need is here or in this repository; the person you are working with has seen none of the build yet.

## 1. What to make

A vertical reel, about 85 seconds, that shows the map of Britain's coalfields and the map of how Britain votes are close to the same map.

- Script and beat sheet: `scripts/05-coal-and-the-vote.md` in this repository (branch `claude/clever-hawking-qenq6t`). Read it first.
- Output: 1080 × 1920, 24 fps (the reference is 23.976), H.264, with burned-in captions. Also export a version without captions.
- Voice-over has not been recorded. Build to the beat sheet timings and leave the picture easy to retime: one pre-composition per beat.

## 2. First step: prove the claim on a still frame

Do this before any animation. The whole video depends on one overlay looking convincing with real data.

1. Draw the coalfield outlines on a plain map of Great Britain.
2. Draw the 2010 general election result by constituency on top.
3. Dim the big conurbations (Greater London, Birmingham, Manchester, Liverpool, Leeds, Sheffield, Newcastle, Glasgow, Edinburgh, Cardiff, Bristol, Nottingham).
4. Count it: of the Labour seats outside those conurbations, what share intersect a coalfield? Of the constituencies that intersect a coalfield, what share were Labour?

Show the person the still and the two numbers. If the match is weak, say so plainly and try 1983 (Labour's worst modern result) or soften the script line "It's the same map." Do not make the picture look more convincing than the data is: no moving, trimming or selectively hiding constituencies beyond the stated city dimming.

## 3. The look

Reference: Johnny Harris, "How the Nile created a civilization", https://www.instagram.com/p/DfaOC6qnHIv/ (67 seconds). Watch it if you can. This description comes from going through it at two frames a second.

**The map**
- A tilted 3D relief map, not a flat one. Real elevation, exaggerated enough that hills cast shadows. Camera looks down at roughly 35 to 55 degrees.
- Photographic land texture: warm ochre and sand for dry ground, saturated green for vegetation, deep navy sea with a faint wave or bathymetry texture. Low golden sunlight from one side.
- Shallow depth of field. The near and far edges of the map fall out of focus, like a tabletop model.
- Atmospheric haze toward the horizon; in low-angle shots a pale sky is visible at the top of frame.
- Volumetric-looking clouds floating above the terrain with soft shadows on the ground. In the reference they build and billow over a region to show rain. Here they are dressing: scattered cloud over Britain, thicker over the hills, drifting slowly.
- City lights as small warm glowing points, visible even in daylight.
- Place labels in an old-atlas serif, capitals, widely tracked, laid flat on the terrain as if printed on it, slightly worn. For example "DURHAM", "SOUTH WALES".

**Motion**
- The camera never stops. Every map shot is a slow push-in, drift or orbit held for 5 to 12 seconds. No fast whip moves. Ease in and out.
- One new element per beat. Nothing appears that the voice is not talking about.
- Lines and fills animate on; they never pop. In the reference the river draws on as a glowing line, then becomes a pulsing dashed line showing flow. A pulsing concentric-ring marker shows a location. Small tiles pin onto the map with a thin leader line.

**Other footage**
- Archive film or photos sit in a rounded-corner frame, centred, on pure black, with captions beneath. Use this for beat 4.
- The presenter appears only briefly in the reference (about 9 of 67 seconds). This video can run with none.

**Captions**
- Small white monospace text on a mid-grey box at about 60% opacity, centred, in the lower third, one phrase at a time, at most two lines. They change with the phrase, not word by word.

**What to carry over, and what not to copy**
- Carry over: the relief map, light, haze, depth of field, clouds, serif labels, slow camera, caption style, one-element-per-beat discipline.
- Do not copy the Nile's specific devices (the electric blue river line, the element tiles). This video has its own, below.

## 4. This video's own elements

- **Coal seams as embers.** The coalfield areas glow from beneath the surface: dark charcoal with an orange-red inner glow and a slow flicker. In beat 2 the land surface fades or peels to reveal them; afterwards they stay faintly visible through the terrain for the rest of the video.
- **Pit lights.** One small warm point of light per colliery, switching on in order of opening date and off in order of closing date. A small year counter in the caption font runs alongside.
- **Constituency blocks.** Each constituency is a low extruded block rising out of the map, coloured by winning party, slightly translucent so the ember glow shows through at the edges. Suggested colours: Labour #E4003B, Conservative #0087DC, Reform UK #12B6CF. Put every other party in one neutral stone grey so the eye stays on the comparison.
- **Flips.** A block changing hands rotates or pulses once and changes colour. In beat 7 they flip in sequence along the seam, not all at once.
- **City dimming.** On "take away the big cities", the conurbation blocks sink and desaturate. They do not disappear.
- **Exceptions stay visible.** Kent's small coalfield under blue seats is part of the honest picture. Do not hide it.

## 5. Data

The cloud session found some of this and could not reach the rest. Check licences before publishing and add a credits line.

| Need | Source | Notes |
|---|---|---|
| Constituency boundaries, 2010 to 2019 | `martinjc/UK-GeoJSON` on GitHub, `json/electoral/gb/topo_wpc.json` (confirmed to exist, about 2.4 MB TopoJSON, Great Britain) | The official source is the Office for National Statistics Open Geography Portal. 2010 and 2019 use the same boundaries, which is why those two elections were chosen |
| 2010 results | `eelcodevlieger/mapimage` on GitHub, `src/main/resources/election_data/2010/electoral_commission/GE2010-constituency-results-website.xls` (confirmed to exist) | Electoral Commission data. The House of Commons Library also publishes constituency results |
| 2019 results | `alpha-spatial/2305-ge-results` on GitHub, `data/2019GeneralElection_3.js` (confirmed: GeoJSON with fields `pcon22nm`, `2019 Res_3` for the winning party) | Files for 2015 and 2017 are alongside. Strip the leading `var … =` to parse |
| 2024 results | House of Commons Library | 2024 used new boundaries. For beat 8 either map 2024 winners onto the old shapes by best overlap and say so in the credits, or show 2024 as a brief colour wash, not block by block |
| 2025 county councils | Council control after the May 2025 elections, from the BBC or the House of Commons Library; county boundaries from the Open Geography Portal | Only four counties are named in the script |
| Coalfield outlines | Not found yet. Try the British Geological Survey's 1:625,000 bedrock geology (free, Open Government Licence) filtered to the Coal Measures groups, or the Coal Authority's (now Mining Remediation Authority) coalfield or coal mining reporting area open data | This is the layer the claim rests on, so use a published dataset, not a hand-drawn shape |
| Colliery locations and dates | Not found yet. The Northern Mine Research Society publishes colliery lists by coalfield; the Coal Authority publishes mine entry data | Check the terms of use. If dates are patchy, animate pit lights by coalfield, not by individual pit, and say "about" |
| Elevation | Ordnance Survey Terrain 50 (free, OS OpenData) or Copernicus 90 m | Exaggerate vertically by 3 to 6 times; Britain is flat compared with the Nile valley |
| Land texture | Sentinel-2 cloudless mosaic (EOX), Natural Earth II, or NASA Blue Marble; multiply a hillshade made from the elevation over it | Grade toward the reference palette: warm, slightly golden |
| Night lights | NASA Black Marble | Add as a glow layer for city lights |

## 6. How to build it

Start by asking the person, or checking the machine, for: the After Effects version, and whether any of these are installed: GEOlayers 3, Element 3D, Trapcode, Red Giant, Video Copilot Optical Flares, Blender, Cinema 4D (the Lite version ships with After Effects). The route depends on the answer.

**Route A, recommended if Blender is available or can be installed (it is free).**
Blender makes the relief, clouds and light; After Effects does everything else. This gets closest to the reference, and Blender can be driven entirely by Python scripts from the command line.
1. In Blender: build the terrain from the elevation data as a displaced plane with the land texture; add a sun lamp low in the west or south-west; add volumetric clouds (a volume shader with noise, or a few cloud volume objects); set a camera with depth of field.
2. Render each camera move as an image sequence with these passes: beauty, depth, cloud alpha, and a flat "position" reference so overlays can be matched. Export the camera to After Effects (Blender's After Effects export add-on writes a `.jsx`).
3. In After Effects: import the sequences and the camera. Put coal, pit lights, constituency blocks, labels and markers on 3D layers on the ground plane so they track the camera. Use the depth pass for depth of field and haze.

**Route B, After Effects only.**
1. Generate a terrain mesh as a `.glb` file from the elevation data with a script, textured with the graded land image. After Effects 2024 and later import 3D models and light them with the Advanced 3D renderer.
2. Or, without a mesh: use the graded, hillshaded land image as a large 3D layer tilted back, with a second displaced copy for parallax. This is flatter but fast.
3. Clouds: stock cloud elements or fractal-noise clouds on 3D layers a little above the ground, with a blurred, darkened, offset copy on the ground as shadow.
4. Depth of field from the After Effects camera, or a gradient-driven camera lens blur at top and bottom of frame.

**Route C, if GEOlayers 3 is installed.**
It imports real map tiles, elevation and GeoJSON straight into After Effects and extrudes shapes, which covers the terrain, the coalfield polygons and the constituency blocks in one tool. Use it for the map and add clouds, glow and grade as in Route B.

**For all routes**
- Convert every geographic layer to the same projection (British National Grid, EPSG:27700) before it reaches After Effects, and export the vector layers as SVG or as shape-layer paths generated by script at a fixed scale, so everything registers.
- Drive After Effects with ExtendScript files run from the command line, and render with `aerender`. Keep the scripts in the repository under `ae/` so the build is repeatable.
- One pre-composition per beat, named `01_hook` to `10_close`, assembled in a master composition. Captions in their own composition, driven from a text file of phrases and timings so they can be retimed to the voice-over.
- Constituency colours must come from the results data by script, never be set by hand.
- Grade last: warm highlights, slightly lifted blacks, gentle vignette, fine film grain.

## 7. Order of work

1. The still-frame test in section 2, shown to the person with the two numbers.
2. One finished look frame of beat 2 (embers under the terrain, with clouds and labels), shown for approval of the style.
3. Beat 5, the reveal, as a 12-second animation. It is the shot the video lives on.
4. The remaining beats, then captions, then grade.
5. Retime to the voice-over when it exists.

## 8. What is settled and what is open

Settled: the topic, the script draft, the reference style, the use of 2010 and 2019, the beat order.

Open, for the person to decide:
- Whether they appear on camera for beat 9 or it stays on the map.
- Whether beat 4 uses archive material, and where that comes from (check rights).
- Music and sound. The reference analysis did not cover audio.

Not verified: every fact in the script is from memory; the list is in `scripts/05-coal-and-the-vote.md`. Two datasets, coalfield outlines and colliery locations, have not been located.

## 9. Other scripts in this repository

`scripts/01` to `04` are earlier scripts in a different, talking-head format, plus one map-led script on private military contractors (`04-guns-for-hire-wagner-to-haiti.md`) that could reuse everything built here: the relief map, clouds, labels, markers and captions.
