const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/sweat-famille/';
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">`;
const C = '#fbf3e4', G = '#2f6b4a', KC = 10;
// renne pixel (14 x 14), regardant à droite
const DEER = [
 'X.X.X.........',
 'XXXXX.........',
 '.XXX..........',
 '..XXX.........',
 '.XXXXX........',
 'XXXX.XXXXXXXX.',
 '..XXXXXXXXXXXX',
 '...XXXXXXXXXX.',
 '...XXXXXXXXXX.',
 '...X.X....X.X.',
 '...X.X....X.X.',
 '...X.X....X.X.'];
const SNOW = ['X..X..X', '.X.X.X.', '..XXX..', 'XXX.XXX', '..XXX..', '.X.X.X.', 'X..X..X'];
const TREE = ['...X...', '..XXX..', '.XXXXX.', '..XXX..', '.XXXXX.', 'XXXXXXX', '...X...'];
const HEART = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
const cell = (x, y, col) => `<rect x="${x + 1}" y="${y + 1}" width="${KC - 2}" height="${KC - 2}" rx="3" fill="${col}"/>`;
const grid = (g, x0, y0, col, flip) => { let s = ''; g.forEach((row, r) => [...row].forEach((ch, c) => { if (ch === 'X') s += cell(x0 + (flip ? row.length - 1 - c : c) * KC, y0 + r * KC, col); })); return s; };
const line = (y, f, col = C) => { let s = ''; for (let c = 0; c < 60; c++) if (f(c)) s += cell(c * KC, y, col); return s; };
function band(y) { let s = line(y, () => true) + line(y + 20, c => c % 4 === 0) + line(y + 30, c => c % 4 === 1 || c % 4 === 3);
  for (let i = 0; i < 4; i++) { const x = i * 150 + 4 * KC; s += grid(SNOW, x, y + 50, C) + grid(TREE, x + 80, y + 50, G === '' ? C : C); }
  s += line(y + 130, c => c % 4 === 1 || c % 4 === 3) + line(y + 140, c => c % 4 === 0) + line(y + 160, () => true); return s; }
function design(role, fam) { let s = band(0);
  // rennes face à face + coeur
  s += grid(DEER, 40, 210, C, true) + grid(DEER, 420, 210, C, false) + grid(HEART, 265, 250, '#e8b04a');
  for (const [x, y] of [[20, 190], [570, 190], [200, 205], [380, 205]]) s += cell(x, y, C);
  if (role) s += `<text x="300" y="${role.length > 7 ? 412 : 418}" text-anchor="middle" font-family="Pinyon Script" font-size="${role.length > 7 ? 92 : 112}" fill="${C}">${role}</text>`;
  if (fam) s += `<text x="300" y="470" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="28" letter-spacing="9" fill="${C}">${fam}</text>`;
  s += band(510); return s; }
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3600, height: 4200 } });
  for (const [suf, r, f, bg] of [['', 'Papa', 'FAMILLE MARTIN', ''], ['-sans-texte', '', '', ''], ['-apercu', 'Papa', 'FAMILLE MARTIN', '#b01f28'], ['-apercu-vert', 'Maman', 'FAMILLE MARTIN', '#1f4430']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 680" width="3600" height="4080">${bg ? `<rect x="-20" y="-20" width="640" height="720" fill="${bg}"/>` : ''}${design(r, f)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}sweat-famille-v2${suf}.png`, omitBackground: !bg }); }
  await b.close(); })();
