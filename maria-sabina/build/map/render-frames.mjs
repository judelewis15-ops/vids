// Exports shots 02-04 as a PNG frame sequence at 60 fps (never a screen
// recording): each frame is rendered, waited on until every tile is in, then
// screenshotted, so the result is deterministic and re-renderable.
//
//   node maria-sabina/build/map/render-frames.mjs                # all 480 frames
//   node maria-sabina/build/map/render-frames.mjs --frames 0,120,300,479
//   node maria-sabina/build/map/render-frames.mjs --start 0 --end 480 --step 4
//   node maria-sabina/build/map/render-frames.mjs --encode        # also make the MP4 + ProRes
//   node maria-sabina/build/map/render-frames.mjs --basemap carto # CARTO Dark Matter basemap
//
// Output: maria-sabina/exports/map-sequence/HO01_02-04_MAP_ny-to-huautla_####.png
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { chromium } from "playwright";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const args = Object.fromEntries(
  process.argv.slice(2).map((a, i, arr) => {
    if (!a.startsWith("--")) return [];
    const k = a.slice(2);
    const v = arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : "1";
    return [k, v];
  }).filter((e) => e.length),
);

const WIDTH = +(args.width || 1080), HEIGHT = +(args.height || 1920); // design canvas (CSS px)
const SCALE = +(args.scale || 2);                                       // 2 -> 2160 x 3840 export
const OUT = path.resolve(ROOT, args.out || "maria-sabina/exports/map-sequence");
const BASENAME = args.name || "HO01_map";
const EXTRA = ["textScale", "lineScale", "arcBow"].filter((k) => args[k]).map((k) => `&${k}=${args[k]}`).join("");
const CACHE = path.join(HERE, "data", "tile-cache");
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(CACHE, { recursive: true });

// ---- tiny static server: page, vendor maplibre, fonts, clipped data ----
const MOUNTS = [
  ["/vendor/", path.join(ROOT, "node_modules/maplibre-gl/dist")],
  ["/fonts/", path.join(ROOT, "public/fonts")],
  ["/data/", path.join(HERE, "data")],
  ["/", HERE],
];
const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
               ".geojson": "application/geo+json", ".ttf": "font/ttf", ".png": "image/png" };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  for (const [prefix, dir] of MOUNTS) {
    if (!url.startsWith(prefix)) continue;
    const file = path.join(dir, url.slice(prefix.length));
    if (fs.existsSync(file) && fs.statSync(file).isFile()) {
      res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
      fs.createReadStream(file).pipe(res);
      return;
    }
  }
  res.writeHead(404); res.end("not found " + url);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

// ---- frame list ----
let frames;
if (args.frames) frames = args.frames.split(",").map(Number);
else {
  const start = +(args.start || 0), end = +(args.end || 480), step = +(args.step || 1);
  frames = []; for (let f = start; f < end; f += step) frames.push(f);
}

const browser = await chromium.launch({
  headless: true,
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
         "--disable-gpu-vsync", "--font-render-hinting=none"],
});
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: SCALE });
page.on("pageerror", (e) => console.error("page error:", e.message));
page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning" || args.verbose) console.log(`[browser ${m.type()}]`, m.text()); });

// Terrain tiles are cached on disk so re-renders are instant and offline.
await page.route(/elevation-tiles-prod\/terrarium\/(\d+)\/(\d+)\/(\d+)\.png/, async (route, req) => {
  const m = req.url().match(/terrarium\/(\d+)\/(\d+)\/(\d+)\.png/);
  const file = path.join(CACHE, `${m[1]}-${m[2]}-${m[3]}.png`);
  if (fs.existsSync(file)) return route.fulfill({ status: 200, contentType: "image/png", body: fs.readFileSync(file) });
  try {
    const res = await route.fetch();
    const body = await res.body();
    if (res.status() === 200) fs.writeFileSync(file, body);
    return route.fulfill({ response: res, body });
  } catch (e) {
    console.error("tile fetch failed", req.url(), e.message);
    return route.abort();
  }
});

await page.goto(`http://127.0.0.1:${port}/index.html?w=${WIDTH}&h=${HEIGHT}${EXTRA}`);
await page.waitForFunction(() => window.__ms && window.__ms.loaded, null, { timeout: 120000 });
await page.evaluate(() => document.fonts.ready);

const t0 = Date.now();
for (let i = 0; i < frames.length; i++) {
  const f = frames[i];
  const cam = await page.evaluate((f) => window.__ms.renderFrame(f), f);
  const file = path.join(OUT, `${BASENAME}_${String(f + 1).padStart(5, "0")}.png`);
  await page.screenshot({ path: file, type: "png", timeout: 0, clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT } });
  if (i % 20 === 0 || i === frames.length - 1) {
    const el = (Date.now() - t0) / 1000, per = el / (i + 1);
    console.log(`frame ${String(f + 1).padStart(5, "0")}  z=${cam.zoom.toFixed(2)} pitch=${cam.pitch.toFixed(0)} brg=${cam.bearing.toFixed(0)}  ${(i + 1)}/${frames.length}  ${per.toFixed(1)}s/frame  eta ${(per * (frames.length - i - 1) / 60).toFixed(1)} min`);
  }
}
await browser.close();
server.close();

if (args.encode) {
  const ffmpeg = [path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), "ffmpeg"].find((p) => p === "ffmpeg" || fs.existsSync(p));
  const pattern = path.join(OUT, `${BASENAME}_%05d.png`);
  const exportsDir = path.resolve(ROOT, "maria-sabina/exports");
  const mp4 = path.join(exportsDir, `${BASENAME}.mp4`);
  const mov = path.join(exportsDir, `${BASENAME}_prores422hq.mov`);
  const run = (a) => { const r = spawnSync(ffmpeg, a, { stdio: "inherit" }); if (r.status) throw new Error("ffmpeg failed"); };
  run(["-y", "-framerate", "60", "-start_number", "1", "-i", pattern, "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4]);
  run(["-y", "-framerate", "60", "-start_number", "1", "-i", pattern, "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", mov]);
  console.log("encoded", mp4, mov);
}
console.log("done");
