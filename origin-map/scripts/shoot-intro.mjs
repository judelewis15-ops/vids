// Renders the series intro shot (shots/intro-shot.js) frame by frame.
//
//   PIN=natal-super-strength REGION=data/regions/kwazulu-natal.json node scripts/shoot-intro.mjs
//
// KEYS="0,0.4,1.25,4" saves those seconds as stills instead of a full render.
// FPS (default 60) and DUR (default 4) set the render; OUT the frames folder.
// SITE points at a copy of the site whose index.html loads maplibre-gl from a
// local ./vendor folder when the CDN is unreachable. CHROME reuses a browser.
// Needs playwright. Encode afterwards with ffmpeg (see README).
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = process.env.SITE || path.join(here, "..");
const out = process.env.OUT || path.join(here, "..", "shots", "frames");
const PIN = process.env.PIN || "natal-super-strength";
const REGION = process.env.REGION || "";
const FPS = Number(process.env.FPS || 60);
const DUR = Number(process.env.DUR || 4);
const KEYS = process.env.KEYS ? process.env.KEYS.split(",").map(Number) : null;
const PORT = Number(process.env.PORT || 8765);
mkdirSync(out, { recursive: true });

const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: site, stdio: "ignore" });
await new Promise((r) => setTimeout(r, 800));

const browser = await chromium.launch({
  executablePath: process.env.CHROME || undefined,
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.log("pageerror:", e.message));
await page.goto(`http://127.0.0.1:${PORT}/index.html?fly=${PIN}`, { waitUntil: "networkidle" });
await page.waitForSelector('body[data-cinematic-ready="1"]', { timeout: 60000 });
await page.evaluate(() => window.__origin.idle());
await page.evaluate((cfg) => { window.__shotConfig = cfg; }, { pin: PIN, region: REGION || null });
await page.addScriptTag({ content: readFileSync(path.join(here, "..", "shots", "intro-shot.js"), "utf8") });
await page.waitForSelector('body[data-shot-ready="1"][data-shot-region="1"]', { timeout: 30000 });
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => window.__shot.setTime(0));
await page.evaluate(() => window.__origin.idle());

async function frame(t, file) {
  await page.evaluate((t) => window.__shot.setTime(t), t);
  await page.evaluate(() => window.__origin.idle());
  await page.screenshot({ path: file, type: file.endsWith(".jpg") ? "jpeg" : "png", quality: file.endsWith(".jpg") ? 94 : undefined });
}

if (KEYS) {
  for (const t of KEYS) await frame(t, path.join(out, `key-${t.toFixed(2)}.png`));
  console.log("stills:", KEYS.join(", "));
} else {
  const n = Math.round(FPS * DUR);
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const file = path.join(out, `f${String(i).padStart(4, "0")}.jpg`);
    if (existsSync(file)) continue; // resume an interrupted render
    await frame(i / FPS, file);
  }
  console.log(`${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close();
server.kill();
