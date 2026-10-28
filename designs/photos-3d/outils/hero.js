const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const [name, w, h, d] of [['banniere-mobile', 1200, 1500, 21.5]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto(`http://127.0.0.1:8765/render.html?k=famille&s=hero&w=${w}&h=${h}&d=${d}`); await p.waitForFunction(() => window.done, null, { timeout: 180000 });
    await p.locator('canvas').screenshot({ path: `/home/user/Claude/designs/photos-3d/${name}.jpg`, type: 'jpeg', quality: 90 }); await p.close(); }
  await b.close(); })();
