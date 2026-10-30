const { chromium } = require('playwright'); const path = require('path');
(async () => { const d = process.argv[2]; const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 2320, height: 1740 } });
  await p.goto('file://' + path.join(d, 'hero.html')); await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(800);
  await p.locator('svg').screenshot({ path: path.join(d, 'hero.png') }); await b.close(); })();
