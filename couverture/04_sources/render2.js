// Série 2 : rendu PNG 300 dpi (2551 x 3579 px) + PDF 216 x 303 mm. Usage : node render2.js [1 2 ...] [--guides]
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const DIR = path.join(__dirname, 'serie2'), OUT = path.resolve(__dirname, '../05_couvertures_HD/serie2');
const sel = process.argv.slice(2).filter(a => !a.startsWith('--')); const guides = process.argv.includes('--guides');
const files = fs.readdirSync(DIR).filter(f => /^S2-\d_.*\.html$/.test(f)).filter(f => !sel.length || sel.includes(f[3]));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 817, height: 1146 }, deviceScaleFactor: 3.125 });
  for (const f of files) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.join(DIR, f));
    if (guides) await p.evaluate(() => document.documentElement.classList.add('guides'));
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    const bad = await p.evaluate(() => [...document.fonts].filter(x => x.status === 'error').map(x => x.family));
    if (bad.length) console.log(f, 'FONT ERRORS', bad);
    const stem = f.replace('.html', '') + (guides ? '_REPERES' : '');
    await (await p.$('.cover')).screenshot({ path: path.join(OUT, stem + '.png') });
    if (!guides) await p.pdf({ path: path.join(OUT, stem + '.pdf'), width: '216mm', height: '303mm', printBackground: true, pageRanges: '1' });
    console.log('ok', stem); await p.close();
  }
  await b.close();
})();
