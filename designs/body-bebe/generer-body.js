const { chromium } = require('playwright'); const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync(__dirname + '/premium.js', 'utf8');
const lib = SRC.slice(SRC.indexOf('let seed'), SRC.indexOf('// mise en situation'));
const ctx = { Math }; vm.createContext(ctx);
vm.runInContext(lib + ';this.L={DEFS,garland,sparkle,T,setSeed:s=>{seed=s}};', ctx);
const L = ctx.L; const OUT = '/home/user/Claude/designs/body-bebe/'; fs.mkdirSync(OUT, { recursive: true });
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">`;
const d = n => { L.setSeed(11); return `${L.garland(300, 300, 212, 28, 152, 13)}
  ${L.T.arc('a1', 168, true, 318)}${L.T.arcText('a1', 'MON PREMIER NOËL', 26, '#3c5a46')}
  ${L.sparkle(300, 196, 12)}${L.sparkle(266, 212, 6)}${L.sparkle(334, 212, 6)}
  ${n ? `<text x="300" y="322" text-anchor="middle" font-family="Pinyon Script" font-size="${n.length > 7 ? 104 : 132}" fill="#2c4a37">${n}</text>` : ''}
  ${L.T.caps(300, 392, '2026', 30, 'url(#gold)', .45)}`; };
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3000, height: 2800 } });
  for (const [suf, n] of [['', 'Emma'], ['-sans-prenom', '']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="40 110 520 480" width="3000" height="2769">${L.DEFS}${d(n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}body-premier-noel${suf}.png`, omitBackground: true }); }
  await b.close(); })();
