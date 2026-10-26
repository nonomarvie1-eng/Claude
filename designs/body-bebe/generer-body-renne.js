const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/body-bebe/';
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Pinyon+Script&display=swap" rel="stylesheet">`;
const BR = '#a8714a', DBR = '#6b4329', LBR = '#e9cfae', RED = '#c8343a', GREEN = '#2f6b4a', CREAM = '#fbf3e4', GOLD = '#d4a64a';
const star = (x, y, r, c) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(1) + ' ' + (y + Math.sin(a) * rr).toFixed(1); } return `<path d="${d}Z" fill="${c}" stroke="${c}" stroke-width="${r * .18}" stroke-linejoin="round"/>`; };
const heart = (x, y, s, c) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 6C-8-2-16 2-12 10c3 5 12 10 12 10s9-5 12-10C16 2 8-2 0 6z" fill="${c}"/>`;
const flake = (x, y, r, c) => { let d = ''; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; d += `M${x} ${y}L${x + Math.cos(a) * r} ${y + Math.sin(a) * r}M${x + Math.cos(a) * r * .55} ${y + Math.sin(a) * r * .55}l${Math.cos(a + .75) * r * .3} ${Math.sin(a + .75) * r * .3}M${x + Math.cos(a) * r * .55} ${y + Math.sin(a) * r * .55}l${Math.cos(a - .75) * r * .3} ${Math.sin(a - .75) * r * .3}`; } return `<path d="${d}" stroke="${c}" stroke-width="${r * .16}" stroke-linecap="round" fill="none"/>`; };
function reindeer(cx, cy) { return `<g transform="translate(${cx} ${cy})">
  <!-- bois -->
  <g stroke="${DBR}" stroke-width="13" stroke-linecap="round" fill="none">
    <path d="M-48-82C-62-120-58-150-40-176"/><path d="M-52-112c-22-4-36-16-42-34"/><path d="M-46-146c-14-6-20-18-20-30"/>
    <path d="M48-82C62-120 58-150 40-176"/><path d="M52-112c22-4 36-16 42-34"/><path d="M46-146c14-6 20-18 20-30"/></g>
  <!-- bonnet de Noël sur un bois -->
  <g transform="translate(34 -150) rotate(28)"><path d="M-30 18 C-24-20 4-48 40-46 C20-30 18 0 30 18Z" fill="${RED}"/><rect x="-36" y="12" width="74" height="18" rx="9" fill="#fff"/><circle cx="42" cy="-46" r="11" fill="#fff"/></g>
  <!-- oreilles -->
  <ellipse cx="-86" cy="-46" rx="34" ry="17" fill="${BR}" transform="rotate(-24 -86 -46)"/><ellipse cx="-86" cy="-46" rx="20" ry="8" fill="${LBR}" transform="rotate(-24 -86 -46)"/>
  <ellipse cx="86" cy="-46" rx="34" ry="17" fill="${BR}" transform="rotate(24 86 -46)"/><ellipse cx="86" cy="-46" rx="20" ry="8" fill="${LBR}" transform="rotate(24 86 -46)"/>
  <!-- tête -->
  <path d="M-74-40C-74-110 74-110 74-40C74 20 44 76 0 84C-44 76-74 20-74-40Z" fill="${BR}"/>
  <ellipse cx="0" cy="44" rx="48" ry="38" fill="${LBR}"/>
  <!-- yeux fermés souriants -->
  <path d="M-42-12q14-14 28 0M14-12q14-14 28 0" stroke="#3a2418" stroke-width="7" stroke-linecap="round" fill="none"/>
  <path d="M-46-20l-8-6M46-20l8-6" stroke="#3a2418" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="-52" cy="14" rx="13" ry="8" fill="#f08b8b" opacity=".75"/><ellipse cx="52" cy="14" rx="13" ry="8" fill="#f08b8b" opacity=".75"/>
  <!-- nez -->
  <circle cx="0" cy="26" r="22" fill="${RED}"/><ellipse cx="-7" cy="18" rx="7" ry="5" fill="#fff" opacity=".7"/>
  <path d="M-14 58q14 12 28 0" stroke="#3a2418" stroke-width="5" stroke-linecap="round" fill="none"/>
  <!-- écharpe -->
  <path d="M-62 76c38 22 86 22 124 0l-6 26c-38 16-74 16-112 0z" fill="${GREEN}"/><path d="M34 90l20 64h-34z" fill="${GREEN}"/>
  ${[-44, -20, 4, 28].map(x => `<path d="M${x} 86v16" stroke="${CREAM}" stroke-width="6" opacity=".9"/>`).join('')}
  <path d="M22 148h34" stroke="${CREAM}" stroke-width="6"/>
</g>`; }
function design(n) {
  let s = reindeer(300, 300);
  const deco = [[110, 150, 's', 13], [492, 170, 'f', 18], [86, 290, 'f', 14], [516, 300, 's', 10], [140, 410, 'h', 1], [470, 420, 'h', .9], [478, 96, 's', 8], [120, 90, 'f', 12]];
  for (const [x, y, k, r] of deco) s += k === 's' ? star(x, y, r, GOLD) : k === 'f' ? flake(x, y, r, '#9cc0d4') : heart(x, y, r, RED);
  s += `<text x="300" y="530" text-anchor="middle" font-family="Fredoka" font-weight="600" font-size="38" letter-spacing="3" fill="${GREEN}">Mon premier Noël</text>`;
  if (n) s += `<text x="300" y="${n.length > 7 ? 612 : 622}" text-anchor="middle" font-family="Fredoka" font-weight="700" font-size="${n.length > 7 ? 74 : 92}" fill="${RED}" stroke="#fff" stroke-width="2">${n}</text>`;
  s += star(160, 600, 9, GOLD) + star(440, 600, 9, GOLD);
  return s; }
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3000, height: 3300 } });
  for (const [suf, n] of [['', 'Léo'], ['-sans-prenom', '']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="50 40 500 610" width="3000" height="3660">${design(n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}body-petit-renne${suf}.png`, omitBackground: true }); }
  await b.close(); })();
