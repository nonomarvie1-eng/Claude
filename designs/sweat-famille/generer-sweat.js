const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/sweat-famille/'; fs.mkdirSync(OUT, { recursive: true });
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">`;
const C = '#fbf3e4', W = 600, KC = 10, COLS = 60;
const SNOW = ['X..X..X', '.X.X.X.', '..XXX..', 'XXX.XXX', '..XXX..', '.X.X.X.', 'X..X..X'];
const TREE = ['...X...', '..XXX..', '.XXXXX.', '..XXX..', '.XXXXX.', 'XXXXXXX', '...X...'];
function band(y0) { let s = ''; const cell = (c, r) => `<rect x="${c * KC + 1}" y="${y0 + r * KC + 1}" width="${KC - 2}" height="${KC - 2}" rx="3" fill="${C}"/>`;
  const rows = [c => true, c => false, c => c % 4 === 0, c => c % 4 === 1 || c % 4 === 3, c => false];
  for (let r = 0; r < 7; r++) rows.push(c => { const m = (c + 4) % 15; if (m < 7) return SNOW[r][m] === 'X'; if (m === 7) return false; return TREE[r][m - 8] === 'X'; });
  rows.push(c => false, c => c % 4 === 1 || c % 4 === 3, c => c % 4 === 0, c => false, c => true);
  rows.forEach((f, r) => { for (let c = 0; c < COLS; c++) if (f(c)) s += cell(c, r); }); return s; }
const star = (x, y, r) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .42 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(1) + ' ' + (y + Math.sin(a) * rr).toFixed(1); } return `<path d="${d}Z" fill="${C}"/>`; };
function design(role, fam) { let s = band(0) + band(470);
  s += star(300, 210, 9) + `<path d="M190 210h90M320 210h90" stroke="${C}" stroke-width="2"/>`;
  if (role) s += `<text x="300" y="340" text-anchor="middle" font-family="Pinyon Script" font-size="${role.length > 7 ? 104 : 128}" fill="${C}">${role}</text>`;
  if (fam) s += `<text x="300" y="420" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="10" fill="${C}">${fam}</text>`;
  return s; }
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3600, height: 3900 } });
  for (const [suf, r, f, bg] of [['', 'Papa', 'FAMILLE MARTIN', ''], ['-sans-texte', '', '', ''], ['-apercu', 'Papa', 'FAMILLE MARTIN', '#b01f28']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 640" width="3600" height="3840">${bg ? `<rect x="-20" y="-20" width="640" height="680" fill="${bg}"/>` : ''}${design(r, f)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}sweat-famille${suf}.png`, omitBackground: !bg }); }
  await b.close(); })();
