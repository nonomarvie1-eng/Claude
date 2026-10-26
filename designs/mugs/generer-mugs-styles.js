const { chromium } = require('playwright'); const fs = require('fs');
const OUT = '/home/user/Claude/designs/mugs/'; 
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@600;700&family=Fraunces:ital,wght@0,700;0,900;1,600&family=Caveat:wght@600;700&display=swap" rel="stylesheet">`;
const VW = 1425, VH = 600, SIDES = [VW * .25, VW * .75];
let seed = 3; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280; const R = (a, b) => a + rnd() * (b - a);
const RED = '#c0282d', DRED = '#8e1a1f', GREEN = '#24502f', CREAM = '#fbf6ec', BROWN = '#b5713c', DBROWN = '#6b3a1c', GOLD = '#c9a04a';
const fitS = (n, b) => !n ? b : n.length > 9 ? b * .64 : n.length > 6 ? b * .8 : b;
const flake = (x, y, r, c, w = 3) => { let d = ''; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3, m = .55; d += `M${x} ${y}L${x + Math.cos(a) * r} ${y + Math.sin(a) * r}M${x + Math.cos(a) * r * m} ${y + Math.sin(a) * r * m}l${Math.cos(a + .75) * r * .32} ${Math.sin(a + .75) * r * .32}M${x + Math.cos(a) * r * m} ${y + Math.sin(a) * r * m}l${Math.cos(a - .75) * r * .32} ${Math.sin(a - .75) * r * .32}`; } return `<path d="${d}" stroke="${c}" stroke-width="${w}" stroke-linecap="round" fill="none"/>`; };
const heart = (x, y, s, c) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 6C-8-2-16 2-12 10c3 5 12 10 12 10s9-5 12-10C16 2 8-2 0 6z" fill="${c}"/>`;
const star = (x, y, r, c) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(1) + ' ' + (y + Math.sin(a) * rr).toFixed(1); } return `<path d="${d}Z" fill="${c}"/>`; };
const scatter = (n, avoid, fn) => { let s = ''; let k = 0; while (k < n) { const x = R(20, VW - 20), y = R(30, VH - 30); if (avoid(x, y)) continue; s += fn(x, y, k); k++; } return s; };
const nearSides = (x, y, rx = 220, ry = 260) => SIDES.some(c => Math.abs(x - c) < rx && Math.abs(y - 300) < ry);

// --- personnages ---
function reindeer(cx, cy, s = 1) { return `<g transform="translate(${cx} ${cy}) scale(${s})">
  <path d="M-38-70c-20-30-10-55 5-70M-30-100c-14 0-22-8-26-18M-12-118c-4-12 0-20 6-26" stroke="${DBROWN}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <path d="M38-70c20-30 10-55-5-70M30-100c14 0 22-8 26-18M12-118c4-12 0-20-6-26" stroke="${DBROWN}" stroke-width="9" stroke-linecap="round" fill="none"/>
  <ellipse cx="-62" cy="-48" rx="24" ry="12" fill="${BROWN}" transform="rotate(-25 -62 -48)"/><ellipse cx="62" cy="-48" rx="24" ry="12" fill="${BROWN}" transform="rotate(25 62 -48)"/>
  <path d="M-55-40c0-50 110-50 110 0 0 40-20 90-55 100-35-10-55-60-55-100z" fill="${BROWN}"/>
  <ellipse cx="0" cy="35" rx="34" ry="28" fill="#e8c7a1"/><circle cx="0" cy="22" r="17" fill="${RED}"/><circle cx="-6" cy="16" r="5" fill="#fff" opacity=".7"/>
  <circle cx="-22" cy="-22" r="8" fill="#2a1a12"/><circle cx="22" cy="-22" r="8" fill="#2a1a12"/><circle cx="-19" cy="-25" r="3" fill="#fff"/><circle cx="25" cy="-25" r="3" fill="#fff"/>
  <ellipse cx="-34" cy="2" rx="9" ry="6" fill="#e88a8a" opacity=".6"/><ellipse cx="34" cy="2" rx="9" ry="6" fill="#e88a8a" opacity=".6"/>
  <path d="M-50 62c30 18 70 18 100 0l-6 22c-30 12-58 12-88 0z" fill="${RED}"/><path d="M28 70l14 46h-26z" fill="${RED}"/>
  ${[-36, -16, 4, 24].map(x => `<path d="M${x} 66v14" stroke="#fff" stroke-width="4" opacity=".7"/>`).join('')}</g>`; }
function gingerbread(cx, cy, s = 1) { return `<g transform="translate(${cx} ${cy}) scale(${s})">
  <path d="M0-120a42 42 0 1 1-.1 0zM-30-50h60c14 0 22 8 40 10 22 2 22 34 0 34h-30v40l26 56c8 18-20 28-28 10L0 40l-28 60c-8 18-36 8-28-10l26-56V-6h-30c-22 0-22-32 0-34 18-2 26-10 40-10z" fill="${BROWN}"/>
  <path d="M-30-6h60" stroke="${CREAM}" stroke-width="0" />
  <path d="M-62-30q8 6 0 12M62-30q-8 6 0 12M-36 82q10 -6 14 6M36 82q-10 -6 -14 6" stroke="${CREAM}" stroke-width="5" stroke-linecap="round" fill="none"/>
  <circle cx="-15" cy="-88" r="6" fill="#2a1a12"/><circle cx="15" cy="-88" r="6" fill="#2a1a12"/><path d="M-18-68q18 14 36 0" stroke="${CREAM}" stroke-width="5" stroke-linecap="round" fill="none"/>
  <ellipse cx="-26" cy="-72" rx="8" ry="5" fill="#e88a8a" opacity=".6"/><ellipse cx="26" cy="-72" rx="8" ry="5" fill="#e88a8a" opacity=".6"/>
  <path d="M-14-46l14 8 14-8v16l-14-8-14 8z" fill="${RED}"/>
  <circle cx="0" cy="-8" r="6" fill="${RED}"/><circle cx="0" cy="12" r="6" fill="${GREEN}"/><circle cx="0" cy="32" r="6" fill="${RED}"/></g>`; }

const D = {
  // 1. Renne mignon — enfants
  'renne': n => { seed = 7; let s = scatter(46, (x, y) => nearSides(x, y, 230, 250), (x, y, k) => k % 3 === 0 ? flake(x, y, R(10, 16), '#9fc3d6', 2.6) : k % 3 === 1 ? heart(x, y, R(.7, 1), RED) : star(x, y, R(5, 8), GOLD));
    for (const c of SIDES) s += `<text x="${c}" y="86" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="54" fill="${GREEN}">Le chocolat chaud de</text>
      ${reindeer(c, 290, 1.25)}<text x="${c}" y="${n ? 528 : 528}" text-anchor="middle" font-family="Fraunces" font-weight="900" font-size="${fitS(n, 92)}" fill="${RED}">${n}</text>`;
    return s; },
  // 2. Pain d'épices gourmand
  'pain-epices': n => { seed = 11; let s = scatter(40, (x, y) => nearSides(x, y, 230, 260), (x, y, k) => k % 2 ? flake(x, y, R(10, 15), BROWN, 2.6) : `<circle cx="${x}" cy="${y}" r="${R(5, 8)}" fill="${k % 4 ? RED : GREEN}"/>`);
    for (const c of SIDES) s += `<text x="${c}" y="92" text-anchor="middle" font-family="Pinyon Script" font-size="62" fill="${DBROWN}">Les petites douceurs de</text>
      ${gingerbread(c, 300, 1.05)}<text x="${c}" y="552" text-anchor="middle" font-family="Pinyon Script" font-size="${fitS(n, 112)}" fill="${RED}">${n}</text>`;
    return s; },
  // 3. Carreaux rouges (buffalo plaid) — moderne
  'carreaux': n => { let pl = `<defs><pattern id="pl" width="90" height="90" patternUnits="userSpaceOnUse"><rect width="90" height="90" fill="${RED}"/><rect width="45" height="90" fill="#1d1d1b" opacity=".55"/><rect width="90" height="45" fill="#1d1d1b" opacity=".55"/></pattern></defs>`;
    let s = pl + `<rect width="${VW}" height="${VH}" fill="url(#pl)"/>`;
    for (const c of SIDES) s += `<rect x="${c - 250}" y="110" width="500" height="380" rx="26" fill="${CREAM}"/><rect x="${c - 236}" y="124" width="472" height="352" rx="18" fill="none" stroke="${GREEN}" stroke-width="3" stroke-dasharray="10 8"/>
      <text x="${c}" y="200" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="9" fill="${GREEN}">JOYEUX NOËL</text>
      <text x="${c}" y="${n ? 320 : 320}" text-anchor="middle" font-family="Fraunces" font-style="italic" font-weight="600" font-size="${fitS(n, 110)}" fill="${RED}">${n}</text>
      ${star(c, 390, 14, GOLD)}<path d="M${c - 120} 390h90M${c + 30} 390h90" stroke="${GOLD}" stroke-width="3"/>
      <text x="${c}" y="446" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="24" letter-spacing="8" fill="${GREEN}">2026</text>`;
    return s; }
};

function mockup(data) { const W = 1200, mw = 640, mh = 700, x0 = 230, y0 = 260, sw = 2850 * .44, face = .25;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${W}" width="${W}" height="${W}">
    <defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#efe9df"/><stop offset="1" stop-color="#e2d9cb"/></linearGradient>
      <linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".28"/><stop offset=".14" stop-color="#000" stop-opacity=".06"/><stop offset=".42" stop-color="#fff" stop-opacity=".18"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset=".88" stop-color="#000" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient>
      <clipPath id="body"><path d="M${x0} ${y0} H${x0 + mw} V${y0 + mh - 40} Q${x0 + mw} ${y0 + mh} ${x0 + mw - 40} ${y0 + mh} H${x0 + 40} Q${x0} ${y0 + mh} ${x0} ${y0 + mh - 40} Z"/></clipPath><filter id="sh"><feGaussianBlur stdDeviation="18"/></filter></defs>
    <rect width="${W}" height="${W}" fill="url(#bg)"/><ellipse cx="${x0 + mw / 2 + 60}" cy="${y0 + mh + 10}" rx="${mw * .62}" ry="34" fill="#000" opacity=".22" filter="url(#sh)"/>
    <path d="M${x0 + mw - 6} ${y0 + 150} C ${x0 + mw + 210} ${y0 + 140} ${x0 + mw + 210} ${y0 + 470} ${x0 + mw - 6} ${y0 + 470}" stroke="#f4f2ee" stroke-width="58" fill="none"/>
    <path d="M${x0 + mw - 6} ${y0 + 150} C ${x0 + mw + 210} ${y0 + 140} ${x0 + mw + 210} ${y0 + 470} ${x0 + mw - 6} ${y0 + 470}" stroke="#000" stroke-opacity=".08" stroke-width="58" fill="none"/>
    <g clip-path="url(#body)"><rect x="${x0}" y="${y0}" width="${mw}" height="${mh}" fill="#f7f5f1"/>
      <image href="${data}" x="${x0 + mw / 2 - 2850 * face * (mw / sw)}" y="${y0 + 80}" width="${2850 * mw / sw}" height="${1200 * mw / sw}" preserveAspectRatio="none"/>
      <rect x="${x0}" y="${y0}" width="${mw}" height="${mh}" fill="url(#shade)"/></g>
    <ellipse cx="${x0 + mw / 2}" cy="${y0}" rx="${mw / 2}" ry="40" fill="#e9e5df"/><ellipse cx="${x0 + mw / 2}" cy="${y0 + 4}" rx="${mw / 2 - 18}" ry="30" fill="#d8d2c8"/></svg>`; }

(async () => { const b = await chromium.launch(); const p = await b.newPage();
  const sets = { 'renne': 'Lucas', 'pain-epices': 'Nathan', 'carreaux': 'Chloé' };
  for (const [k, name] of Object.entries(sets)) {
    for (const [suf, n] of [['', name], ['-sans-prenom', '']]) {
      await p.setViewportSize({ width: 2850, height: 1200 });
      await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${VH}" width="2850" height="1200">${D[k](n)}</svg></body></html>`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
      await p.locator('svg').screenshot({ path: `${OUT}mug-${k}${suf}.png`, omitBackground: true });
    }
    const data = 'data:image/png;base64,' + fs.readFileSync(`${OUT}mug-${k}.png`).toString('base64');
    await p.setViewportSize({ width: 1200, height: 1200 }); await p.setContent(`<body style="margin:0">${mockup(data)}</body>`); await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: `${OUT}apercu-mug-${k}.jpg`, type: 'jpeg', quality: 88 });
  }
  await b.close(); })();
