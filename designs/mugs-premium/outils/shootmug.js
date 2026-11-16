const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/mugs-premium/';
const KEYS = (process.argv[2] || 'guirlande,foret,nuit-doree').split(','), VIEWS = (process.argv[3] || 'droite,gauche,face,dessus').split(',');
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 1600 } }); p.on('pageerror', e => console.log('PE', e.message));
  for (const k of KEYS) for (const [i, v] of VIEWS.entries()) { await p.goto(`http://127.0.0.1:8765/mug.html?k=${k}&v=${v}`); await p.waitForFunction(() => window.done, null, { timeout: 180000 });
    await p.locator('canvas').screenshot({ path: `${OUT}photo-${k}-${i + 1}-${v}.jpg`, type: 'jpeg', quality: 90 }); console.log(k, v); }
  await b.close(); })();
