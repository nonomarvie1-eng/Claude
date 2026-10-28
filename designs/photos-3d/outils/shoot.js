const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/photos-3d/';
const KEYS = (process.argv[2] || 'prenom-couronne,premier-noel-bebe,notre-premier-noel,famille').split(',');
const SHOTS = ['face', 'trois-quarts', 'recto-verso', 'detail', 'a-plat', 'prenoms'];
(async () => { const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 1600 } }); p.on('console', m => m.type() === 'error' && console.log('ERR', m.text())); p.on('pageerror', e => console.log('PE', e.message));
  for (const k of KEYS) { fs.mkdirSync(OUT + k, { recursive: true });
    for (const [i, s] of SHOTS.entries()) { await p.goto(`http://127.0.0.1:8765/render.html?k=${k}&s=${s}`); await p.waitForFunction(() => window.done, null, { timeout: 120000 });
      await p.locator('canvas').screenshot({ path: `${OUT}${k}/${i + 1}-${s}.jpg`, type: 'jpeg', quality: 90 }); console.log(k, s); } }
  await b.close(); })();
