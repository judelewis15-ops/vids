const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const FPS = 30, DUR = 12, N = FPS * DUR;
(async () => {
  fs.rmSync('frames', { recursive: true, force: true });
  fs.mkdirSync('frames');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/film.html');
  await p.waitForLoadState('networkidle');
  await p.waitForTimeout(600);
  for (let i = 0; i < N; i++) {
    await p.evaluate((t) => window.setTime(t), i / FPS);
    await p.screenshot({ path: `frames/f${String(i).padStart(4,'0')}.jpg`, type: 'jpeg', quality: 95 });
    if (i % 60 === 0) console.log('frame', i, '/', N);
  }
  await b.close();
  console.log('frames done');
})();
