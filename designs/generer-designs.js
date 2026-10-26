const { chromium } = require('playwright');
const fs = require('fs');
const OUT = '/home/user/Claude/designs/';
const P = '#24402f', P2 = '#3d6b4f', R = '#a3312f', GOLD = '#b8893a';
const font = `<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,600&family=Figtree:wght@600&display=swap" rel="stylesheet">`;
const sprig = (x, y, s, c = P2) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${c}" stroke-width="1.6" fill="none" stroke-linecap="round"><path d="M-18 0h34"/><path d="M-6 0c-3-5-8-6-11-6M-6 0c-3 5-8 6-11 6M6 0c-3-5-8-6-11-6M6 0c-3 5-8 6-11 6"/><circle cx="17" cy="0" r="2.6" fill="${R}" stroke="none"/></g>`;
const script = (x, y, t, s, c = P) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cormorant Garamond" font-style="italic" font-weight="600" font-size="${s}" fill="${c}">${t}</text>`;
const caps = (x, y, t, s, c = GOLD) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Figtree" font-weight="600" font-size="${s}" letter-spacing="${s * .3}" fill="${c}">${t}</text>`;
const star = (x, y, s, c) => `<g transform="translate(${x} ${y}) scale(${s / 30})"><path d="M0-30l8.8 18 19.7 2.9-14.3 13.9 3.4 19.7L0 15.2l-17.6 9.3 3.4-19.7L-28.5-9.1l19.7-2.9z" fill="${c}"/></g>`;
const tree = (x, y, s, c) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0-14l7 10h-3l5 8H-9l5-8h-3z" fill="${c}"/>`;

const designs = {
  // 1. Boule au prénom (rond, fond transparent)
  'boule-prenom': { w: 200, h: 200, px: 3000, svg: `
    ${caps(100, 70, 'NOËL 2026', 10)}
    ${script(100, 116, 'Emma', 46)}
    ${sprig(100, 140, 1.5)}` },
  // 2. Famille (pull, coussin, affiche)
  'famille-noel': { w: 240, h: 200, px: 4000, svg: `
    ${caps(120, 52, 'FAMILLE', 14)}
    ${script(120, 112, 'Martin', 62)}
    ${sprig(120, 138, 1.8)}
    ${caps(120, 170, 'NOËL 2026', 9, P2)}` },
  // 3. Motif répété (plaid, tote bag, mug) — fond vert sapin
  'motif-sapins': { w: 200, h: 200, px: 4000, bg: P, svg: (() => {
    let s = '';
    for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) {
      const x = 20 + c * 40 + (r % 2) * 20, y = 20 + r * 40, k = (r * 5 + c) % 3;
      for (const xx of (x >= 180 ? [x, x - 200] : [x])) s += k === 0 ? tree(xx, y, 1.3, '#f3eee6') : k === 1 ? star(xx, y, 5, GOLD) : sprig(xx, y, .55, '#8fb39b');
    }
    return s; })() }
};

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [name, d] of Object.entries(designs)) {
    const html = `<!doctype html><html><head>${font}<style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d.w} ${d.h}" width="${d.px}" height="${d.px * d.h / d.w}">${d.bg ? `<rect width="100%" height="100%" fill="${d.bg}"/>` : ''}${d.svg}</svg></body></html>`;
    await p.setViewportSize({ width: d.px, height: Math.round(d.px * d.h / d.w) });
    await p.setContent(html); await p.waitForLoadState('networkidle'); await p.evaluate(() => document.fonts.ready);
    await p.locator('svg').screenshot({ path: OUT + name + '.png', omitBackground: true });
    fs.writeFileSync(OUT + name + '.svg', `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d.w} ${d.h}">${d.bg ? `<rect width="100%" height="100%" fill="${d.bg}"/>` : ''}${d.svg}</svg>`);
  }
  // planche d'aperçu
  const tile = (n, bg, label) => `<figure style="margin:0;background:${bg};border-radius:20px;padding:24px;display:grid;place-items:center;gap:12px"><img src="${OUT + n}.png" style="width:100%;max-height:300px;object-fit:contain"><figcaption style="font:600 18px Figtree;color:#22261f">${label}</figcaption></figure>`;
  await p.setViewportSize({ width: 1200, height: 520 });
  await p.goto('file:///dev/null').catch(()=>{});
  await p.setContent(`<html><head>${font}</head><body style="margin:0;background:#f3eee6;padding:30px;display:grid;grid-template-columns:repeat(3,1fr);gap:24px;font-family:Figtree">
    ${tile('boule-prenom', '#fdfbf7', '1 · Boule au prénom')}${tile('famille-noel', '#fdfbf7', '2 · Famille (pull, coussin, affiche)')}${tile('motif-sapins', '#fdfbf7', '3 · Motif (plaid, tote, mug)')}</body></html>`);
  await p.waitForTimeout(800);
  await p.screenshot({ path: OUT + 'apercu-designs.png' });
  await b.close();
})();
