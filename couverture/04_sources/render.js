// Rendu : PNG 300 dpi (2079 x 2906 px), JPEG et PDF vectoriel (texte + polices embarquées).
// Usage : node render.js [A B C D E] [--guides]
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.resolve(__dirname, '../05_couvertures_HD');
const concepts = process.argv.slice(2).filter(a => !a.startsWith('--'));
const guides = process.argv.includes('--guides');
const files = fs.readdirSync(path.join(__dirname, 'concepts')).filter(f => /^[A-E]_.*\.html$/.test(f))
  .filter(f => !concepts.length || concepts.includes(f[0]));
(async () => {
  const b = await chromium.launch();
  // 176 mm à 96 css-px/in = 665.2 px ; DSF = 300/96 = 3.125 -> 2079 px
  const ctx = await b.newContext({ viewport: { width: 666, height: 930 }, deviceScaleFactor: 3.125 });
  for (const f of files) {
    const p = await ctx.newPage();
    await p.goto('file://' + path.join(__dirname, 'concepts', f) + (guides ? '?guides' : ''));
    if (guides) await p.evaluate(() => document.documentElement.classList.add('guides'));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    const missing = await p.evaluate(() => [...document.fonts].filter(x => x.status === 'error').map(x => x.family));
    if (missing.length) console.log(f, 'FONT ERRORS', missing);
    const el = await p.$('.cover');
    const stem = f.replace('.html', '') + (guides ? '_REPERES' : '');
    await el.screenshot({ path: path.join(OUT, stem + '.png') });
    if (!guides) await p.pdf({ path: path.join(OUT, stem + '.pdf'), width: '176mm', height: '246mm', printBackground: true, pageRanges: '1' });
    console.log('ok', stem);
    await p.close();
  }
  await b.close();
})();
