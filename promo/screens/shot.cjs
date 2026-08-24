const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  for (const n of ['courses','profile']) {
    const p = await b.newPage({ viewport:{width:780,height:1660}, deviceScaleFactor:2 });
    await p.goto('file://' + process.cwd() + '/' + n + '.html');
    await p.waitForTimeout(700);
    await p.screenshot({ path: n + '.png' });
    console.log(n, 'ok');
  }
  await b.close();
})();
