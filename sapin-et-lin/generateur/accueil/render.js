const { chromium } = require('playwright'); const path = require('path');
(async () => { const d = process.argv[2]; const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2320, height: 1740 } });
  await p.goto('file://' + path.join(d, 'hero.html')); await p.waitForTimeout(500);
  await p.locator('.s').screenshot({ path: path.join(d, 'accueil-sapin-et-lin.png') }); await b.close(); })();
