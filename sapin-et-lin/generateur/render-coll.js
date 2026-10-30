const { chromium } = require('playwright');
const path = require('path');
const designs = [
  ['bebe',    'MON PREMIER NOËL',   'star',  '2026',      'Léo'],
  ['couple',  'NOTRE PREMIER NOËL', 'heart', '2026',      'Léa & Tom'],
  ['famille', 'LA FAMILLE',         'house', 'NOËL 2026', 'Martin'],
  ['chien',   'JOYEUX NOËL',        'paw',   '2026',      'Rocky'],
];
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2000, height: 2000 } });
  for (const [slug, title, icon, year, ex] of designs)
    for (const theme of ['blanc', 'vert'])
      for (const [name, kind] of [[ex, 'apercu'], ['', 'IMPRESSION']]) {
        const qs = new URLSearchParams({ theme, name, title, icon, year }).toString();
        await p.goto('file://' + path.join(dir, 'ornament2.html') + '?' + qs);
        await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
        await p.locator('svg').screenshot({ path: path.join(dir, 'coll', `boule-${slug}-${theme}-${kind}.png`), omitBackground: true });
      }
  await b.close();
})();
