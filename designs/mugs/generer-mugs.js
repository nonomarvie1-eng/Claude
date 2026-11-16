const { chromium } = require('playwright'); const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync(__dirname + '/premium.js', 'utf8');
const lib = SRC.slice(SRC.indexOf('let seed'), SRC.indexOf('// mise en situation'));
const ctx = { Math }; vm.createContext(ctx);
vm.runInContext(lib + ';this.L={DEFS,garland,pine,holly,berries,sparkle,star,T,setSeed:s=>{seed=s},R:(a,b)=>R(a,b)};', ctx);
const L = ctx.L;
const OUT = '/home/user/Claude/designs/mugs/'; fs.mkdirSync(OUT, { recursive: true });
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@500;600;700&display=swap" rel="stylesheet">`;
const VW = 1425, VH = 600, SIDES = [VW * .25, VW * .75];
const fit = (n, base) => !n ? base : n.length > 10 ? base * .62 : n.length > 7 ? base * .78 : base;
const script = (x, y, t, s, f) => t ? `<text x="${x}" y="${y}" text-anchor="middle" font-family="Pinyon Script" font-size="${s}" fill="${f}">${t}</text>` : '';
const caps = (x, y, t, s, f, ls = .38) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="${s}" letter-spacing="${s * ls}" fill="${f}">${t}</text>`;

const D = {
  // A — couronne de houx sur fond blanc (fond transparent : le mug est blanc)
  'joyeux-noel': n => SIDES.map((cx, i) => { L.setSeed(5 + i); return `
    <g transform="translate(${cx - 300 * .86} ${300 - 300 * .86}) scale(.86)">${L.garland(300, 300, 228, -60, 240, 12)}</g>
    ${caps(cx, 236, 'JOYEUX NOËL', 24, '#a3312f')}
    ${script(cx, 330, n, fit(n, 128), '#24432f')}
    ${caps(cx, 392, '2026', 24, 'url(#gold)', .5)}${L.sparkle(cx - 62, 384, 7)}${L.sparkle(cx + 62, 384, 7)}`; }).join('')
    + `<g opacity=".9">${L.sparkle(VW / 2, 270, 12)}${L.sparkle(VW / 2 - 30, 320, 6)}${L.sparkle(VW / 2 + 28, 340, 7)}</g>`,
  // B — nuit étoilée et village enneigé, tout autour du mug
  'la-famille': n => { L.setSeed(31); let s = `<defs><linearGradient id="skyM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f2236"/><stop offset=".75" stop-color="#284a63"/><stop offset="1" stop-color="#3f6680"/></linearGradient></defs>
      <rect width="${VW}" height="${VH}" fill="url(#skyM)"/>`;
    for (let i = 0; i < 160; i++) { const x = L.R(0, VW), y = L.R(10, 430); if (SIDES.some(c => Math.abs(x - c) < 230 && y > 150 && y < 360)) continue; s += `<circle cx="${x}" cy="${y}" r="${L.R(1.2, 3.2)}" fill="#fff" opacity="${L.R(.45, 1)}"/>`; }
    s += `<circle cx="${VW * .5}" cy="110" r="34" fill="#f6efd8"/>`;
    // village
    let x = -20; while (x < VW + 20) { const w = L.R(58, 84), h = L.R(60, 100), y = 512;
      if (L.R(0, 1) < .22) { const t = L.R(.8, 1.3); s += `<path d="M${x + 30} ${y - 96 * t}l${30 * t} ${48 * t}h${-13 * t}l${24 * t} ${40 * t}h${-82 * t}l${24 * t} ${-40 * t}h${-13 * t}z" fill="#163526"/><path d="M${x + 30} ${y - 96 * t}l${11 * t} ${18 * t}h${-22 * t}z" fill="#f6f1e6"/>`; x += 62 * t; continue; }
      s += `<rect x="${x}" y="${y - h}" width="${w}" height="${h + 20}" fill="#1c3a52"/><path d="M${x - 7} ${y - h + 2}L${x + w / 2} ${y - h - 36}L${x + w + 7} ${y - h + 2}Z" fill="#162f43"/><path d="M${x - 7} ${y - h + 2}L${x + w / 2} ${y - h - 36}L${x + w + 7} ${y - h + 2}" stroke="#f6f1e6" stroke-width="6" fill="none" stroke-linejoin="round"/>`;
      for (let k = 0; k < 2; k++) s += `<rect x="${x + 12 + k * (w - 36)}" y="${y - h + 22}" width="12" height="15" rx="1" fill="#ffd27a"/><rect x="${x + 7 + k * (w - 36)}" y="${y - h + 17}" width="22" height="25" fill="#ffd27a" opacity=".22"/>`;
      x += w + L.R(8, 22); }
    s += `<path d="M0 512 C 200 490 400 530 712 508 S 1200 494 ${VW} 512 V${VH} H0Z" fill="#f6f1e6"/><path d="M0 548 C 300 534 700 560 ${VW} 540 V${VH} H0Z" fill="#e7ecef"/>`;
    for (const cx of SIDES) s += caps(cx, 196, 'LA FAMILLE', 28, '#f6f1e6', .45) + script(cx, 312, n, fit(n, 132), 'url(#gold)') + caps(cx, 574, 'NOËL 2026', 20, '#3f6680', .4);
    return s; }
};

function mockup(data, face) { // mug simple vu de face, poignée à droite ; face = 0.25 ou 0.75 de la zone
  const W = 1200, mw = 640, mh = 700, x0 = 230, y0 = 260, sw = 2850 * .44;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${W}" width="${W}" height="${W}">
    <defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#efe9df"/><stop offset="1" stop-color="#e2d9cb"/></linearGradient>
      <linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".28"/><stop offset=".14" stop-color="#000" stop-opacity=".06"/><stop offset=".42" stop-color="#fff" stop-opacity=".18"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset=".88" stop-color="#000" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient>
      <clipPath id="body"><path d="M${x0} ${y0} H${x0 + mw} V${y0 + mh - 40} Q${x0 + mw} ${y0 + mh} ${x0 + mw - 40} ${y0 + mh} H${x0 + 40} Q${x0} ${y0 + mh} ${x0} ${y0 + mh - 40} Z"/></clipPath>
      <filter id="sh"><feGaussianBlur stdDeviation="18"/></filter></defs>
    <rect width="${W}" height="${W}" fill="url(#bg)"/>
    <ellipse cx="${x0 + mw / 2 + 60}" cy="${y0 + mh + 10}" rx="${mw * .62}" ry="34" fill="#000" opacity=".22" filter="url(#sh)"/>
    <path d="M${x0 + mw - 6} ${y0 + 150} C ${x0 + mw + 210} ${y0 + 140} ${x0 + mw + 210} ${y0 + 470} ${x0 + mw - 6} ${y0 + 470}" stroke="#f4f2ee" stroke-width="58" fill="none"/>
    <path d="M${x0 + mw - 6} ${y0 + 150} C ${x0 + mw + 210} ${y0 + 140} ${x0 + mw + 210} ${y0 + 470} ${x0 + mw - 6} ${y0 + 470}" stroke="#000" stroke-opacity=".08" stroke-width="58" fill="none"/>
    <g clip-path="url(#body)"><rect x="${x0}" y="${y0}" width="${mw}" height="${mh}" fill="#f7f5f1"/>
      <image href="${data}" x="${x0 + mw / 2 - 2850 * face * (mw / sw)}" y="${y0 + 80}" width="${2850 * mw / sw}" height="${1200 * mw / sw}" preserveAspectRatio="none"/>
      <rect x="${x0}" y="${y0}" width="${mw}" height="${mh}" fill="url(#shade)"/></g>
    <ellipse cx="${x0 + mw / 2}" cy="${y0}" rx="${mw / 2}" ry="40" fill="#e9e5df"/><ellipse cx="${x0 + mw / 2}" cy="${y0 + 4}" rx="${mw / 2 - 18}" ry="30" fill="#d8d2c8"/>
  </svg>`;
}

(async () => { const b = await chromium.launch(); const p = await b.newPage();
  const sets = { 'joyeux-noel': 'Emma', 'la-famille': 'Martin' };
  for (const [k, name] of Object.entries(sets)) {
    for (const [suf, n] of [['', name], ['-sans-prenom', '']]) {
      await p.setViewportSize({ width: 2850, height: 1200 });
      await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${VH}" width="2850" height="1200">${L.DEFS}${D[k](n)}</svg></body></html>`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
      await p.locator('svg').screenshot({ path: `${OUT}mug-${k}${suf}.png`, omitBackground: true });
    }
    const data = 'data:image/png;base64,' + fs.readFileSync(`${OUT}mug-${k}.png`).toString('base64');
    await p.setViewportSize({ width: 1200, height: 1200 }); await p.setContent(`<body style="margin:0">${mockup(data, .25)}</body>`); await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: `${OUT}apercu-mug-${k}.jpg`, type: 'jpeg', quality: 88 });
  }
  await b.close(); })();
