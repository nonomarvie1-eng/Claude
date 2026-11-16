const { chromium } = require('playwright');
const OUT = '/home/user/Claude/designs/';
const font = `<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,600;1,700&family=Figtree:wght@600;700&display=swap" rel="stylesheet">`;
const P = '#1f3d2c', P2 = '#2f5c40', P3 = '#4d8060', P4 = '#7fae8a', R = '#b3282d', R2 = '#d9474b', GOLD = '#c9a04a', CREAM = '#fbf6ec';

// pseudo-aléatoire stable
let seed = 7; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;

function wreath(cx, cy, rad, opts = {}) {
  const { leaves = 110, berries = 14, stars = 0, greens = [P, P2, P3, P4] } = opts;
  let s = '';
  for (let i = 0; i < leaves; i++) {
    const a = i / leaves * Math.PI * 2 + rnd() * .05;
    const rr = rad + (rnd() - .5) * 22;
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr;
    const ang = a * 180 / Math.PI + 90 + (rnd() - .5) * 80;
    const len = 16 + rnd() * 12;
    s += `<ellipse cx="${x}" cy="${y}" rx="${len}" ry="${4 + rnd() * 2.5}" fill="${greens[Math.floor(rnd() * greens.length)]}" transform="rotate(${ang} ${x} ${y})"/>`;
  }
  // brins d'aiguilles fins
  for (let i = 0; i < 60; i++) {
    const a = rnd() * Math.PI * 2, rr = rad + (rnd() - .5) * 26, x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr, ang = rnd() * 360;
    s += `<path d="M${x} ${y}l${Math.cos(ang) * 12} ${Math.sin(ang) * 12}" stroke="${P4}" stroke-width="1.4" stroke-linecap="round" opacity=".8"/>`;
  }
  for (let i = 0; i < berries; i++) {
    const a = (i / berries) * Math.PI * 2 + rnd() * .3, rr = rad + (rnd() - .5) * 14, x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr;
    for (let k = 0; k < 3; k++) { const bx = x + (rnd() - .5) * 12, by = y + (rnd() - .5) * 12; s += `<circle cx="${bx}" cy="${by}" r="${4 + rnd() * 1.5}" fill="${k ? R : R2}"/><circle cx="${bx - 1.4}" cy="${by - 1.4}" r="1.2" fill="#fff" opacity=".55"/>`; }
  }
  for (let i = 0; i < stars; i++) { const a = rnd() * Math.PI * 2, rr = rad + (rnd() - .5) * 30; s += star(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr, 5 + rnd() * 3, GOLD); }
  return s;
}
const star = (x, y, r, c) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(2) + ' ' + (y + Math.sin(a) * rr).toFixed(2); } return `<path d="${d}Z" fill="${c}"/>`; };
const snowflake = (x, y, r, c, w = 2) => { let s = ''; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3, ex = x + Math.cos(a) * r, ey = y + Math.sin(a) * r, mx = x + Math.cos(a) * r * .55, my = y + Math.sin(a) * r * .55;
  s += `<path d="M${x} ${y}L${ex} ${ey}M${mx} ${my}l${Math.cos(a + .7) * r * .3} ${Math.sin(a + .7) * r * .3}M${mx} ${my}l${Math.cos(a - .7) * r * .3} ${Math.sin(a - .7) * r * .3}"/>`; }
  return `<g stroke="${c}" stroke-width="${w}" stroke-linecap="round" fill="none">${s}</g>`; };
const arc = (id, cx, cy, r, top) => top
  ? `<path id="${id}" d="M${cx - r} ${cy}A${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none"/>`
  : `<path id="${id}" d="M${cx - r} ${cy}A${r} ${r} 0 0 0 ${cx + r} ${cy}" fill="none"/>`;
const arcText = (id, txt, size, fill, spacing = .32) => `<text font-family="Figtree" font-weight="700" font-size="${size}" letter-spacing="${size * spacing}" fill="${fill}"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${txt}</textPath></text>`;
const name = (n, y, size, fill) => n ? `<text x="300" y="${y}" text-anchor="middle" font-family="Cormorant Garamond" font-style="italic" font-weight="700" font-size="${size}" fill="${fill}">${n}</text>` : '';

const D = {
  // A — Couronne : fond crème, couronne de sapin et baies, texte en arc
  couronne: n => `<circle cx="300" cy="300" r="300" fill="${CREAM}"/>
    ${(seed = 7, wreath(300, 300, 228, { stars: 10 }))}
    ${arc('t1', 300, 300, 168, true)}${arcText('t1', 'JOYEUX NOËL', 26, R)}
    ${arc('b1', 300, 300, 176, false)}${arcText('b1', '2026', 24, P2, .5)}
    ${name(n, 336, 112, P)}
    ${star(300, 400, 9, GOLD)}`,
  // B — Nuit étoilée : fond vert sapin, flocons, prénom doré
  nuit: n => `<circle cx="300" cy="300" r="300" fill="${P}"/>
    <circle cx="300" cy="300" r="276" fill="none" stroke="${GOLD}" stroke-width="3"/><circle cx="300" cy="300" r="264" fill="none" stroke="${GOLD}" stroke-width="1" opacity=".6"/>
    ${(() => { seed = 3; let s = ''; for (let i = 0; i < 26; i++) { const a = rnd() * Math.PI * 2, r = 120 + rnd() * 130, x = 300 + Math.cos(a) * r, y = 300 + Math.sin(a) * r; if (Math.abs(y - 320) < 70 && Math.abs(x - 300) < 200) continue; s += rnd() > .5 ? snowflake(x, y, 9 + rnd() * 10, CREAM, 2) : star(x, y, 4 + rnd() * 4, GOLD); } return s; })()}
    <text x="300" y="214" text-anchor="middle" font-family="Figtree" font-weight="700" font-size="24" letter-spacing="8" fill="${GOLD}">NOËL 2026</text>
    ${name(n, 340, 120, CREAM)}
    <path d="M220 384h160" stroke="${GOLD}" stroke-width="2"/>${star(300, 384, 10, GOLD)}`,
  // C — Scandinave : fond rouge, frise de flocons et sapins blancs
  scandi: n => `<circle cx="300" cy="300" r="300" fill="${R}"/>
    <circle cx="300" cy="300" r="250" fill="${CREAM}"/>
    ${(() => { let s = ''; for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, x = 300 + Math.cos(a) * 275, y = 300 + Math.sin(a) * 275; s += i % 2 ? snowflake(x, y, 13, CREAM, 2.4) : `<path d="M${x} ${y - 14}l10 14h-5l8 12h-26l8-12h-5z" fill="${CREAM}" transform="rotate(${a * 180 / Math.PI + 90} ${x} ${y})"/>`; } return s; })()}
    <path d="M300 112l34 50h-16l26 40h-88l26-40h-16z" fill="${P2}"/><rect x="292" y="202" width="16" height="12" fill="#8d6748"/>${star(300, 108, 10, GOLD)}
    ${name(n, 350, 110, P)}
    <text x="300" y="420" text-anchor="middle" font-family="Figtree" font-weight="700" font-size="22" letter-spacing="7" fill="${R}">NOËL 2026</text>`
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setViewportSize({ width: 3000, height: 3000 });
  for (const [k, f] of Object.entries(D)) for (const [suffix, n] of [['', 'Emma'], ['-sans-prenom', '']]) {
    await p.setContent(`<html><head>${font}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="3000" height="3000">${f(n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: `${OUT}medaillon-${k}${suffix}.png`, omitBackground: true });
  }
  await p.setViewportSize({ width: 1200, height: 470 });
  const fig = (k, label) => `<figure style="margin:0;display:grid;gap:14px;justify-items:center"><img src="data:image/png;base64,${require('fs').readFileSync(OUT + 'medaillon-' + k + '.png').toString('base64')}" style="width:330px;height:330px;filter:drop-shadow(0 10px 18px rgba(0,0,0,.18))"><figcaption style="font:600 18px Figtree;color:#22261f">${label}</figcaption></figure>`;
  await p.setContent(`<html><head>${font}</head><body style="margin:0;background:#efe8dc;padding:34px;display:grid;grid-template-columns:repeat(3,1fr);gap:20px">${fig('couronne', 'A · Couronne')}${fig('nuit', 'B · Nuit étoilée')}${fig('scandi', 'C · Scandinave')}</body></html>`);
  await p.waitForTimeout(800); await p.screenshot({ path: OUT + 'apercu-medaillons.png' });
  await b.close();
})();
