const { chromium } = require('playwright'); const fs = require('fs');
const SRC = fs.readFileSync('/home/user/Claude/designs/nouveaux/generer.js', 'utf8');
eval(SRC.slice(SRC.indexOf('const b64'), SRC.indexOf('// guirlande en arc')).replace(/^(const|let) /gm, 'var ').replace(/; const /g, '; var '));
const OUT = __dirname + '/';
const VW = 1425, VH = 600, A = VW * .25, B = VW * .75;   // A = face prénom, B = face « Joyeux Noël »
const GOLD = '#c9a24e', RED = '#b3262c', GREEN = '#1d4a32', CREAM = '#f7efe1';
const caps = (x, y, t, s, f, ls = .32) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="${s}" letter-spacing="${s * ls}" fill="${f}">${t}</text>`;
const scr = (x, y, t, s, f) => t ? `<text x="${x}" y="${y}" text-anchor="middle" font-family="Pinyon Script" font-size="${s}" fill="${f}">${t}</text>` : '';
const fit = (n, b) => !n ? b : n.length > 9 ? b * .66 : n.length > 6 ? b * .82 : b;

// frise jacquard (flocons + losanges) sur toute la largeur
function fairIsle(y, fg, acc) {
  const px = 7, flake = ['....X....','..X.X.X..','...XXX...','X.XX.XX.X','.XXX.XXX.','X.XX.XX.X','...XXX...','..X.X.X..','....X....'];
  let s = '';
  for (let x = 0; x < VW; x += px * 2) { s += `<rect x="${x}" y="${y}" width="${px - 1}" height="${px - 1}" fill="${fg}"/><rect x="${x + px}" y="${y + px}" width="${px - 1}" height="${px - 1}" fill="${fg}"/>`; }
  let col = 0, i = 0;
  while (col * px < VW + 20) { for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) if (flake[r][c] === 'X') s += `<rect x="${(col + c) * px}" y="${y + (r + 3) * px}" width="${px - 1}" height="${px - 1}" fill="${fg}"/>`;
    // petit losange doré entre deux flocons
    const dx = (col + 11) * px, dy = y + 7 * px; s += `<path d="M${dx} ${dy - 14}l10 14l-10 14l-10 -14z" fill="${acc}"/>`; col += 22; i++; }
  const yb = y + 13 * px; for (let x = 0; x < VW; x += px * 2) s += `<rect x="${x}" y="${yb}" width="${px - 1}" height="${px - 1}" fill="${fg}"/><rect x="${x + px}" y="${yb + px}" width="${px - 1}" height="${px - 1}" fill="${fg}"/>`;
  return s + `<rect x="0" y="${yb + px * 2 + 6}" width="${VW}" height="3" fill="${fg}"/>`;
}
const tinyTree = (x, y, s, f) => `<path d="M${x} ${y - 14 * s}l${7 * s} ${10 * s}h${-3 * s}l${6 * s} ${9 * s}h${-20 * s}l${6 * s} ${-9 * s}h${-3 * s}z" fill="${f}"/>`;

const D = {
  'pull-rouge': n => { seed = 3; let sp = ''; for (let i = 0; i < 70; i++) { const x = R(20, VW - 20), y = R(165, 435); if (Math.min(Math.abs(x - A), Math.abs(x - B)) > 150 || y < 190 || y > 410) sp += pick([sparkle(x, y, R(4, 7), GOLD), tinyTree(x, y + 6, .8, GOLD)]); }
    return `<defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c22d33"/><stop offset="1" stop-color="#9e1f25"/></linearGradient></defs>
    <rect width="${VW}" height="${VH}" fill="url(#rg)"/>${fairIsle(22, '#fbf3e6', GOLD)}${fairIsle(VH - 140, '#fbf3e6', GOLD)}${sp}
    ${caps(A, 240, 'JOYEUX NOËL', 30, GOLD)}${scr(A, 355, n, fit(n, 130), '#fbf3e6')}${caps(A, 410, '2026', 30, GOLD, .4)}
    ${scr(B, 330, 'Joyeux Noël', 110, '#fbf3e6')}${caps(B, 400, '2026', 30, GOLD, .4)}`; },
  'sapin-vert': n => { seed = 5; let bg = ''; for (let i = 0; i < 150; i++) { const x = R(10, VW - 10), y = R(15, VH - 15); if (Math.min(Math.hypot(x - A, y - 300), Math.hypot(x - B, y - 300)) > 225) bg += rnd() > .45 ? tinyTree(x, y + 8, R(.9, 1.3), GOLD) : sparkle(x, y, R(4, 7), GOLD); }
    const medal = (cx, inner) => `<circle cx="${cx}" cy="300" r="212" fill="#f4ead6"/><circle cx="${cx}" cy="300" r="198" fill="none" stroke="${GOLD}" stroke-width="2.5"/><circle cx="${cx}" cy="300" r="190" fill="none" stroke="${GOLD}" stroke-width="1" opacity=".7"/>
      ${holly(cx - 18, 168, 22, -60, '#2f6b45')}${holly(cx + 18, 168, 22, 60, '#2f6b45')}${berries(cx, 168, 3, 6)}${sparkle(cx, 455, 9, GOLD)}${inner}`;
    return `<rect width="${VW}" height="${VH}" fill="${GREEN}"/><rect width="${VW}" height="${VH}" filter="url(#grain)" opacity=".5"/>${bg}
    ${medal(A, caps(A, 245, 'JOYEUX NOËL', 26, '#8a6a35') + scr(A, 345, n, fit(n, 116), GREEN) + caps(A, 405, '2026', 26, GOLD, .4))}
    ${medal(B, scr(B, 318, 'Joyeux Noël', 70, GREEN) + caps(B, 390, '2026', 26, GOLD, .4))}`; },
  'guirlande-creme': n => { seed = 9; let top = '', bot = '', sp = '';
    for (let x = -30; x < VW + 30; x += 34) { const y = 40 + Math.sin(x / 70) * 8; top += holly(x, y, 30, R(-70, 70), pick(['#24503a', '#2f6b45', '#3d7a52'])) + (rnd() > .5 ? berries(x + 10, y + 10, 2, 6) : ''); }
    top += `<path d="M0 52 ${Array.from({ length: 30 }, (_, i) => `Q${i * 50 + 25} ${70} ${i * 50 + 50} 52`).join(' ')}" fill="none" stroke="#b3262c" stroke-width="3"/>`;
    for (let x = 60; x < VW; x += 150) top += `<path d="M${x} 60V${100 + (x % 300 ? 20 : 0)}" stroke="${GOLD}" stroke-width="1.5"/><ellipse cx="${x}" cy="${118 + (x % 300 ? 20 : 0)}" rx="9" ry="14" fill="none" stroke="${GOLD}" stroke-width="2.5"/>`;
    for (let x = -20; x < VW + 20; x += 46) { const y = VH - 30 + Math.sin(x / 60) * 5; bot += holly(x, y, 22, R(-80, 80), pick(['#24503a', '#2f6b45'])) + (rnd() > .6 ? berries(x + 8, y - 6, 2, 5) : ''); }
    for (let i = 0; i < 60; i++) { const x = R(20, VW - 20), y = R(170, 520); if (Math.min(Math.abs(x - A), Math.abs(x - B)) > 170 || y < 200 || y > 470) sp += sparkle(x, y, R(3, 7), GOLD); }
    return `<rect width="${VW}" height="${VH}" fill="${CREAM}"/><rect width="${VW}" height="${VH}" filter="url(#grain)"/>${top}${bot}${sp}
    ${caps(A, 245, 'JOYEUX NOËL', 30, '#a7833f')}${scr(A, 365, n, fit(n, 138), '#1f4a33')}${caps(A, 425, '2026', 30, '#a7833f', .4)}
    ${scr(B, 335, 'Joyeux Noël', 112, '#1f4a33')}${caps(B, 405, '2026', 30, '#a7833f', .4)}`; },
};
const NAMES = { 'pull-rouge': 'Alice', 'sapin-vert': 'Louis', 'guirlande-creme': 'Emma' };
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2850, height: 1200 } });
  for (const [k, f] of Object.entries(D)) for (const [suf, n] of [['', NAMES[k]], ['-sans-prenom', '']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${VH}" width="2850" height="1200">${DEFS}${f(n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    await p.locator('svg').screenshot({ path: `${OUT}mug-${k}${suf}.png` }); console.log(k, suf); }
  await b.close(); })();
