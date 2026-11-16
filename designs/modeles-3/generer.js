const { chromium } = require('playwright'); const fs = require('fs');
const SRC = fs.readFileSync('/home/user/Claude/designs/nouveaux/generer.js', 'utf8');
eval(SRC.slice(SRC.indexOf('const b64'), SRC.indexOf('// guirlande en arc')).replace(/^(const|let) /gm, 'var ').replace(/; const /g, '; var '));
const CAV = fs.readFileSync('/home/user/Claude/designs/polices/Caveat-600.woff').toString('base64');
const FONTS2 = FONTS.replace('</style>', `@font-face{font-family:Caveat;src:url(data:font/woff;base64,${CAV})}</style>`);
const OUT = __dirname + '/';
const paper = (bg) => `<rect width="600" height="600" fill="${bg}"/><rect width="600" height="600" filter="url(#grain)"/>`;
const GOLD = '#c9a24e', DG = '#a7833f', RED = '#b3262c', GREEN = '#1d4a32', CREAM = '#f7efe1', BROWN = '#8a5a3b';
const caps = (x, y, t, s, f, ls = .32) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="${s}" letter-spacing="${s * ls}" fill="${f}">${t}</text>`;
const scr = (x, y, t, s, f) => t ? `<text x="${x}" y="${y}" text-anchor="middle" font-family="Pinyon Script" font-size="${s}" fill="${f}">${t}</text>` : '';
const fit = (n, b) => !n ? b : n.length > 9 ? b * .66 : n.length > 6 ? b * .82 : b;
const arc = (id, cx, cy, r) => `<path id="${id}" d="M${cx - r} ${cy}A${r} ${r} 0 0 1 ${cx + r} ${cy}" fill="none"/>`;
const arcT = (id, t, s, f) => `<text font-family="Cinzel" font-weight="600" font-size="${s}" letter-spacing="${s * .3}" fill="${f}"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${t}</textPath></text>`;

// tête de renne mignonne, centrée en (0,0), ~ 200 px de large
const antler = (m) => `<g transform="scale(${m} 1)" fill="none" stroke="${BROWN}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">
  <path d="M38 -62 C 52 -96 66 -120 92 -138"/><path d="M58 -98 C 78 -102 96 -96 110 -84"/><path d="M76 -122 C 74 -142 80 -158 92 -168"/><path d="M48 -80 C 34 -98 30 -116 34 -132"/></g>`;
const reindeer = (cx, cy, s, scarf = true) => `<g transform="translate(${cx} ${cy}) scale(${s})">
  ${antler(1)}${antler(-1)}
  <ellipse cx="-68" cy="-40" rx="30" ry="15" transform="rotate(-30 -68 -40)" fill="#b07a52"/><ellipse cx="68" cy="-40" rx="30" ry="15" transform="rotate(30 68 -40)" fill="#b07a52"/>
  <ellipse cx="-66" cy="-40" rx="16" ry="7" transform="rotate(-30 -66 -40)" fill="#f2c9b8"/><ellipse cx="66" cy="-40" rx="16" ry="7" transform="rotate(30 66 -40)" fill="#f2c9b8"/>
  <path d="M0 -78 C 46 -78 62 -42 58 -6 C 54 34 34 66 0 70 C -34 66 -54 34 -58 -6 C -62 -42 -46 -78 0 -78 Z" fill="#b07a52"/>
  <path d="M0 12 C 30 12 42 30 40 46 C 36 66 18 74 0 74 C -18 74 -36 66 -40 46 C -42 30 -30 12 0 12 Z" fill="#e8c9a6"/>
  <ellipse cx="-24" cy="-18" rx="7.5" ry="9.5" fill="#2b1a12"/><ellipse cx="24" cy="-18" rx="7.5" ry="9.5" fill="#2b1a12"/>
  <circle cx="-21" cy="-22" r="2.6" fill="#fff"/><circle cx="27" cy="-22" r="2.6" fill="#fff"/>
  <ellipse cx="-38" cy="8" rx="9" ry="5" fill="#e98f8a" opacity=".6"/><ellipse cx="38" cy="8" rx="9" ry="5" fill="#e98f8a" opacity=".6"/>
  <circle cx="0" cy="28" r="17" fill="#d6363c"/><circle cx="-5" cy="22" r="5" fill="#fff" opacity=".7"/>
  <path d="M-10 52 Q 0 60 10 52" stroke="#5a3a28" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  ${scarf ? `<path d="M-50 70 C -20 86 20 86 50 70 L 54 86 C 20 102 -20 102 -54 86 Z" fill="${RED}"/><path d="M22 90 L 30 132 L 46 128 L 40 88 Z" fill="${RED}"/><path d="M-42 79 h 6 M-26 86 h6 M-10 89 h6 M6 89 h6 M22 86 h6" stroke="#f7efe1" stroke-width="3"/>` : ''}
</g>`;

// 1. Médaillon « Renne enchanté » (viewBox 600, trou du ruban en haut ≈ y 45)
const MED = n => { seed = 13; let sp = '';
  for (let i = 0; i < 40; i++) { const x = R(70, 530), y = R(110, 520); if (Math.hypot(x - 300, y - 300) < 240 && Math.hypot(x - 300, y - 250) > 140 && !(y > 330 && x > 110 && x < 490)) sp += rnd() > .5 ? sparkle(x, y, R(4, 8), GOLD) : `<circle cx="${x}" cy="${y}" r="${R(2, 3.5)}" fill="${GOLD}" opacity=".7"/>`; }
  return `${paper('#fbf5ec')}<circle cx="300" cy="300" r="268" fill="none" stroke="${GOLD}" stroke-width="3"/><circle cx="300" cy="300" r="258" fill="none" stroke="${GOLD}" stroke-width="1" opacity=".6"/>
  ${sp}${reindeer(300, 222, .82)}
  ${caps(300, 378, 'MON PREMIER NOËL', 22, GREEN, .3)}
  ${scr(300, 452, n, fit(n, 92), GREEN)}${caps(300, 500, '2026', 24, DG, .45)}
  ${holly(270, 535, 16, -70, '#2f6b45')}${holly(330, 535, 16, 70, '#2f6b45')}${berries(300, 537, 3, 5)}`; };

// 2. Mug « Esprit de Noël » (tour complet 1425×600 ; A = prénom, B = « Joyeux Noël »)
const VW = 1425, VH = 600, A = VW * .25, B = VW * .75;
const stag = (cx, cy, s) => `<g transform="translate(${cx} ${cy}) scale(${s})">
  <path d="M0 -52 C 24 -52 36 -38 34 -16 C 32 6 22 22 18 40 C 15 56 10 70 0 72 C -10 70 -15 56 -18 40 C -22 22 -32 6 -34 -16 C -36 -38 -24 -52 0 -52 Z" fill="${GOLD}"/><ellipse cx="-13" cy="-14" rx="4" ry="5" fill="${GREEN}"/><ellipse cx="13" cy="-14" rx="4" ry="5" fill="${GREEN}"/><ellipse cx="0" cy="62" rx="9" ry="6" fill="${GREEN}" opacity=".5"/>
  <ellipse cx="-50" cy="-32" rx="26" ry="11" transform="rotate(-22 -50 -32)" fill="${GOLD}"/><ellipse cx="50" cy="-32" rx="26" ry="11" transform="rotate(22 50 -32)" fill="${GOLD}"/>
  <g fill="none" stroke="${GOLD}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
   <path d="M-12 -50 C -22 -80 -40 -104 -66 -124 C -80 -136 -88 -150 -90 -168"/><path d="M-30 -92 C -26 -112 -28 -130 -36 -146"/><path d="M-52 -114 C -52 -134 -58 -150 -68 -162"/><path d="M-66 -124 C -84 -124 -100 -118 -112 -106"/>
   <path d="M12 -50 C 22 -80 40 -104 66 -124 C 80 -136 88 -150 90 -168"/><path d="M30 -92 C 26 -112 28 -130 36 -146"/><path d="M52 -114 C 52 -134 58 -150 68 -162"/><path d="M66 -124 C 84 -124 100 -118 112 -106"/></g></g>`;
const laurel = (cx, cy, r, side) => { let s = '', pts = [];
  for (let i = 0; i <= 8; i++) { const a = (90 + side * (28 + i * 13)) * Math.PI / 180; pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r, a]); }
  s += `<path d="M${pts.map(p => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' L')}" stroke="${GOLD}" stroke-width="3" fill="none"/>`;
  pts.slice(1).forEach(([x, y, a], i) => { const t = a * 180 / Math.PI + (side > 0 ? 90 : -90);
    for (const o of [-1, 1]) { const ang = t + o * 35; const lx = x + Math.cos((ang - 90) * Math.PI / 180) * 0, ly = y;
      s += `<ellipse cx="${x + Math.cos(ang * Math.PI / 180) * 14}" cy="${y + Math.sin(ang * Math.PI / 180) * 14}" rx="14" ry="5.5" fill="${GOLD}" transform="rotate(${ang} ${x + Math.cos(ang * Math.PI / 180) * 14} ${y + Math.sin(ang * Math.PI / 180) * 14})"/>`; } });
  return s; };
const MUG = n => { seed = 21; let bg = '';
  for (let i = 0; i < 120; i++) { const x = R(10, VW - 10), y = R(15, VH - 15); if (Math.min(Math.hypot(x - A, y - 290), Math.hypot(x - B, y - 290)) > 230) bg += rnd() > .5 ? sparkle(x, y, R(3, 7), GOLD) : `<circle cx="${x}" cy="${y}" r="${R(1.5, 3)}" fill="${GOLD}" opacity=".6"/>`; }
  const face = (cx, top, bottom) => `${laurel(cx, 300, 215, -1)}${laurel(cx, 300, 215, 1)}${stag(cx, 230, .74)}${top}${bottom}`;
  return `<rect width="${VW}" height="${VH}" fill="${GREEN}"/><rect width="${VW}" height="${VH}" filter="url(#grain)" opacity=".45"/>${bg}
  ${face(A, scr(A, 395, n, fit(n, 112), GOLD), caps(A, 452, '2026', 28, GOLD, .45))}
  ${face(B, scr(B, 388, 'Joyeux Noël', 66, GOLD), caps(B, 452, '2026', 28, GOLD, .45))}`; };

// 3. Body « Pain d'épices » (fond transparent, 1000×1100)
const ginger = (cx, cy, s) => `<g transform="translate(${cx} ${cy}) scale(${s})">
  <path d="M0 -150 C 44 -150 66 -122 66 -92 C 66 -70 56 -56 44 -48 L 110 -40 C 140 -36 142 0 112 2 L 58 2 L 74 100 C 80 130 46 142 34 116 L 0 52 L -34 116 C -46 142 -80 130 -74 100 L -58 2 L -112 2 C -142 0 -140 -36 -110 -40 L -44 -48 C -56 -56 -66 -70 -66 -92 C -66 -122 -44 -150 0 -150 Z" fill="#c07a3e"/>
  <path d="M-96 -20 q 8 -10 16 0 q 8 10 16 0 M64 -20 q 8 -10 16 0 q 8 10 16 0 M-62 96 q 8 -8 16 0 M46 96 q 8 -8 16 0" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>
  <circle cx="-20" cy="-100" r="7" fill="#3a2214"/><circle cx="20" cy="-100" r="7" fill="#3a2214"/>
  <path d="M-20 -76 Q 0 -60 20 -76" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>
  <ellipse cx="-36" cy="-82" rx="9" ry="6" fill="#e98f8a" opacity=".7"/><ellipse cx="36" cy="-82" rx="9" ry="6" fill="#e98f8a" opacity=".7"/>
  <path d="M-30 -44 L 0 -30 L 30 -44 L 30 -20 L 0 -30 L -30 -20 Z" fill="${RED}"/><circle cx="0" cy="-30" r="7" fill="${RED}"/>
  <circle cx="0" cy="0" r="8" fill="#3d7a52"/><circle cx="0" cy="30" r="8" fill="${RED}"/></g>`;
const cane = (x, y, s, r) => `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})"><path d="M0 120 V 0 A 26 26 0 0 1 52 0" stroke="#fff" stroke-width="18" fill="none" stroke-linecap="round"/><path d="M0 120 V 0 A 26 26 0 0 1 52 0" stroke="${RED}" stroke-width="18" fill="none" stroke-dasharray="14 14" stroke-linecap="butt"/></g>`;
const BODY = n => { seed = 31; let sp = ''; for (let i = 0; i < 14; i++) { const x = R(180, 820), y = R(260, 640); if (Math.hypot(x - 500, y - 430) > 220) sp += sparkle(x, y, R(7, 12), GOLD); }
  return `${sp}
  <path id="ab" d="M260 330 A 260 260 0 0 1 740 330" fill="none"/><text font-family="Caveat" font-size="78" fill="${GREEN}"><textPath href="#ab" startOffset="50%" text-anchor="middle">Mon premier Noël</textPath></text>
  ${ginger(500, 520, 1.15)}${cane(250, 560, .9, -18)}${cane(700, 560, .9, 18)}
  ${n ? `<text x="500" y="850" text-anchor="middle" font-family="Caveat" font-size="${n.length > 8 ? 120 : 150}" fill="${GREEN}">${n}</text>` : ''}
  ${caps(500, 935, '2026', 40, DG, .45)}`; };

(async () => { const b = await chromium.launch(); const p = await b.newPage();
  const shot = async (file, vb, w, h, body, transparent) => { await p.setViewportSize({ width: w, height: h });
    await p.setContent(`<html><head>${FONTS2}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${h}">${DEFS}${body}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    await p.locator('svg').screenshot({ path: OUT + file, omitBackground: !!transparent }); console.log(file); };
  for (const [suf, n] of [['', 'Arthur'], ['-sans-prenom', '']]) await shot(`medaillon-renne${suf}.png`, '0 0 600 600', 3000, 3000, MED(n), true);
  for (const [suf, n] of [['', 'Léa'], ['-sans-prenom', '']]) await shot(`mug-esprit-de-noel${suf}.png`, `0 0 ${VW} ${VH}`, 2850, 1200, MUG(n));
  for (const [suf, n] of [['', 'Jade'], ['-sans-prenom', '']]) await shot(`body-pain-epices${suf}.png`, '0 0 1000 1000', 3000, 3000, BODY(n), true);
  await b.close(); })();
