const { chromium } = require('playwright');
const path = require('path');
const themes = [
  ['joyeux-noel', 'JOYEUX NOËL',        'diamond', '2026',      'Emma'],
  ['bebe',        'MON PREMIER NOËL',   'star',    '2026',      'Léo'],
  ['couple',      'NOTRE PREMIER NOËL', 'heart',   '2026',      'Léa & Tom'],
  ['famille',     'LA FAMILLE',         'house',   'NOËL 2026', 'Martin'],
  ['chien',       'JOYEUX NOËL',        'paw',     '2026',      'Rocky'],
];
(async () => {
  const dir = process.argv[2], out = path.join(dir, 'final');
  const b = await chromium.launch();
  const jobs = [];
  for (const st of ['rouge', 'nuit']) {
    for (const [slug, title, icon, year, ex] of themes)
      for (const [name, kind] of [[ex, 'apercu'], ['', 'IMPRESSION']])
        jobs.push(['boule', st, slug, title, icon, year, name, kind]);
    for (const [name, kind] of [['Emma', 'apercu'], ['', 'IMPRESSION']])
      jobs.push(['mug', st, 'joyeux-noel', 'JOYEUX NOËL', 'diamond', '2026', name, kind]);
  }
  for (const [fmt, st, slug, title, icon, year, name, kind] of jobs) {
    const p = await b.newPage({ viewport: fmt === 'mug' ? { width: 2409, height: 1169 } : { width: 2000, height: 2000 } });
    await p.goto('file://' + path.join(dir, 'styles2.html') + '?' + new URLSearchParams({ fmt, style: st, title, icon, year, name }));
    await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(250);
    await p.locator('svg').screenshot({ path: path.join(out, `${fmt}-${slug}-${st}-${kind}.png`) });
    await p.close();
  }
  await b.close();
})();
