// Shoots the two still frames for the series intro: the fitted globe and the
// episode pin at END_ZOOM. Usage:
//   PIN=natal-super-strength END_ZOOM=4 node scripts/shoot-intro.mjs
// Needs playwright (npm i -D playwright) and a Chromium (CHROME=/path to reuse one).
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
// A copy of the site with maplibre-gl served from ./vendor (the CDN is not
// needed): see README, "Shooting the series intro".
const site = process.env.SITE || path.join(here, "..");
const out = process.env.OUT || path.join(here, "..", "shots", "frames");
import { mkdirSync } from "node:fs";
mkdirSync(out, { recursive: true });
const PIN = process.env.PIN || "natal-super-strength";
const END_ZOOM = Number(process.env.END_ZOOM || 5.2);
const PORT = 8765;

const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: site, stdio: "ignore" });
await new Promise((r) => setTimeout(r, 800));

const browser = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text()); });
await page.goto(`http://127.0.0.1:${PORT}/index.html?fly=${PIN}`, { waitUntil: "networkidle" });
await page.waitForSelector('body[data-cinematic-ready="1"]', { timeout: 60000 });
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => window.__origin.idle());
await page.waitForTimeout(500);
await page.screenshot({ path: path.join(out, "start.png") });
console.log("start frame:", await page.evaluate(() => { const c = window.__origin.map.getCenter(); return [c.lng.toFixed(2), c.lat.toFixed(2), window.__origin.map.getZoom().toFixed(2)]; }));

// A mid frame: globe rotated so the pin is centred, still at globe zoom. Useful as a second keyframe.
await page.evaluate((id) => { const m = window.__origin.map; const c = window.__origin.coordsOf(id); m.jumpTo({ center: c, zoom: m.getZoom() }); }, PIN);
await page.evaluate(() => window.__origin.idle());
await page.waitForTimeout(300);
await page.screenshot({ path: path.join(out, "mid.png") });

const ok = await page.evaluate(([id, z]) => window.__origin.view(id, z), [PIN, END_ZOOM]);
if (!ok) throw new Error("pin not found: " + PIN);
await page.evaluate(() => window.__origin.idle());
await page.waitForTimeout(500);
await page.screenshot({ path: path.join(out, process.env.END_NAME || "end.png") });
console.log("end frame:", await page.evaluate(() => { const c = window.__origin.map.getCenter(); return [c.lng.toFixed(2), c.lat.toFixed(2), window.__origin.map.getZoom().toFixed(2)]; }));

await browser.close();
server.kill();
