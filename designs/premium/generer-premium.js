const { chromium } = require('playwright');
const fs = require('fs');
const OUT = '/home/user/Claude/designs/premium/';
fs.mkdirSync(OUT, { recursive: true });
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@500;600;700&display=swap" rel="stylesheet">`;

let seed = 1; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
const R = (a, b) => a + rnd() * (b - a);
const pick = a => a[Math.floor(rnd() * a.length)];

const DEFS = `<defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#8a6420"/><stop offset=".22" stop-color="#e9cb78"/><stop offset=".45" stop-color="#b8892e"/>
    <stop offset=".7" stop-color="#f5df9a"/><stop offset="1" stop-color="#94701f"/></linearGradient>
  <radialGradient id="berry" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#ef6a62"/><stop offset=".55" stop-color="#b8262b"/><stop offset="1" stop-color="#7d1418"/></radialGradient>
  <radialGradient id="euca" cx=".4" cy=".4" r=".8"><stop offset="0" stop-color="#b7cdb8"/><stop offset="1" stop-color="#7d9c86"/></radialGradient>
  <filter id="wc" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="3"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .38  0 0 0 0 .3  0 0 0 .09 0"/></filter>
  <filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter>
  <clipPath id="disc"><circle cx="300" cy="300" r="300"/></clipPath>
</defs>`;

/* ---------- éléments botaniques ---------- */
function pine(x, y, len, ang, opts = {}) {
  const { dark = '#1f4430', light = '#3f7354', w = 2.1, density = 1 } = opts;
  const a = ang * Math.PI / 180, bend = R(-.25, .25);
  let s = `<g filter="url(#wc)">`;
  const pts = [];
  for (let i = 0; i <= 24; i++) { const t = i / 24, aa = a + bend * t; pts.push([x + Math.cos(aa) * len * t, y + Math.sin(aa) * len * t, aa]); }
  s += `<path d="M${pts.map(p => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join('L')}" stroke="#5a3d28" stroke-width="${w * 1.1}" fill="none" stroke-linecap="round"/>`;
  const n = Math.round(len / 2.6 * density);
  for (let i = 2; i < n; i++) {
    const t = i / n, p = pts[Math.min(24, Math.round(t * 24))], taper = 1 - t * .55;
    for (const side of [-1, 1]) {
      const na = p[2] + side * R(.55, .95), nl = R(13, 19) * taper;
      s += `<path d="M${p[0].toFixed(1)} ${p[1].toFixed(1)}l${(Math.cos(na) * nl).toFixed(1)} ${(Math.sin(na) * nl).toFixed(1)}" stroke="${rnd() > .45 ? dark : light}" stroke-width="${w}" stroke-linecap="round"/>`;
    }
  }
  return s + `</g>`;
}
function eucalyptus(x, y, len, ang) {
  const a = ang * Math.PI / 180; let s = `<g filter="url(#wc)" opacity=".92">`;
  s += `<path d="M${x} ${y}q${Math.cos(a + .3) * len / 2} ${Math.sin(a + .3) * len / 2} ${Math.cos(a) * len} ${Math.sin(a) * len}" stroke="#8a7a68" stroke-width="1.6" fill="none"/>`;
  for (let i = 1; i <= 6; i++) {
    const t = i / 6.5, px = x + Math.cos(a) * len * t, py = y + Math.sin(a) * len * t, side = i % 2 ? 1 : -1, r = 13 - i * 1.1;
    const lx = px + Math.cos(a + side * 1.3) * r * .9, ly = py + Math.sin(a + side * 1.3) * r * .9;
    s += `<ellipse cx="${lx}" cy="${ly}" rx="${r}" ry="${r * .82}" fill="url(#euca)" transform="rotate(${ang} ${lx} ${ly})"/>`;
  }
  return s + `</g>`;
}
function holly(x, y, size, ang, fill = '#24503a') {
  const d = 'M0 -1 C .18 -.78 .42 -.8 .38 -.55 C .62 -.5 .7 -.3 .5 -.12 C .72 0 .7 .25 .45 .3 C .55 .55 .35 .75 .18 .62 C .12 .85 0 1 0 1 C 0 1 -.12 .85 -.18 .62 C -.35 .75 -.55 .55 -.45 .3 C -.7 .25 -.72 0 -.5 -.12 C -.7 -.3 -.62 -.5 -.38 -.55 C -.42 -.8 -.18 -.78 0 -1 Z';
  return `<g transform="translate(${x} ${y}) rotate(${ang}) scale(${size * .55} ${size})" filter="url(#wc)"><path d="${d}" fill="${fill}"/><path d="M0 -.9 V .9" stroke="#6f9a7c" stroke-width=".04" fill="none"/></g>`;
}
const berries = (x, y, n = 3, r = 7) => { let s = ''; for (let i = 0; i < n; i++) { const bx = x + R(-r, r) * 1.1, by = y + R(-r, r) * 1.1; s += `<circle cx="${bx}" cy="${by}" r="${r * R(.85, 1.1)}" fill="url(#berry)"/><circle cx="${bx - r * .3}" cy="${by - r * .35}" r="${r * .22}" fill="#fff" opacity=".7"/>`; } return s; };
const star = (x, y, r, fill = 'url(#gold)') => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .42 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(2) + ' ' + (y + Math.sin(a) * rr).toFixed(2); } return `<path d="${d}Z" fill="${fill}"/>`; };
const sparkle = (x, y, r, fill = 'url(#gold)') => `<path d="M${x} ${y - r}Q${x} ${y} ${x + r} ${y}Q${x} ${y} ${x} ${y + r}Q${x} ${y} ${x - r} ${y}Q${x} ${y} ${x} ${y - r}Z" fill="${fill}"/>`;
const flake = (x, y, r, c, w) => { let s = ''; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3, m = .55; s += `M${x} ${y}L${x + Math.cos(a) * r} ${y + Math.sin(a) * r}M${x + Math.cos(a) * r * m} ${y + Math.sin(a) * r * m}l${Math.cos(a + .75) * r * .32} ${Math.sin(a + .75) * r * .32}M${x + Math.cos(a) * r * m} ${y + Math.sin(a) * r * m}l${Math.cos(a - .75) * r * .32} ${Math.sin(a - .75) * r * .32}`; } return `<path d="${s}" stroke="${c}" stroke-width="${w}" stroke-linecap="round" fill="none"/>`; };

// guirlande en arc : angles en degrés (0 = droite, 90 = bas)
function garland(cx, cy, rad, from, to, step) {
  let s = '';
  for (let d = from; d <= to; d += step) {
    const a = d * Math.PI / 180, x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad, tang = d + 90;
    s += pine(x, y, R(46, 64), tang + R(-25, 5));
    s += pine(x, y, R(40, 56), tang + 180 + R(-5, 25));
    if (rnd() > .45) s += eucalyptus(x, y, R(40, 54), tang + pick([-40, 140]) + R(-10, 10));
  }
  for (let d = from + step / 2; d <= to; d += step * 1.6) {
    const a = d * Math.PI / 180, x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad;
    s += holly(x - 8, y, 20, d + 40) + holly(x + 8, y, 18, d - 40) + berries(x, y, 3, 6.5);
  }
  return s;
}
const T = {
  caps: (x, y, t, size, fill, ls = .35) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="${size}" letter-spacing="${size * ls}" fill="${fill}">${t}</text>`,
  script: (x, y, t, size, fill) => t ? `<text x="${x}" y="${y}" text-anchor="middle" font-family="Pinyon Script" font-size="${size}" fill="${fill}">${t}</text>` : '',
  arc: (id, r, top, cy = 300) => `<path id="${id}" d="M${300 - r} ${cy}A${r} ${r} 0 0 ${top ? 1 : 0} ${300 + r} ${cy}" fill="none"/>`,
  arcText: (id, t, size, fill, ls = .3) => `<text font-family="Cinzel" font-weight="600" font-size="${size}" letter-spacing="${size * ls}" fill="${fill}"><textPath href="#${id}" startOffset="50%" text-anchor="middle">${t}</textPath></text>`
};
const scriptSize = (n, base) => !n ? base : n.length > 10 ? base * .62 : n.length > 7 ? base * .78 : base;
const paper = (bg) => `<circle cx="300" cy="300" r="300" fill="${bg}"/><rect width="600" height="600" filter="url(#grain)" clip-path="url(#disc)"/>`;

const DESIGNS = {
  // 1. Bébé
  'premier-noel-bebe': { name: 'Emma', f: n => { seed = 11; return `${paper('#fbf5ee')}
    <circle cx="300" cy="300" r="282" fill="none" stroke="url(#gold)" stroke-width="2.5"/>
    ${garland(300, 300, 236, 25, 155, 13)}
    ${T.arc('a1', 205, true)}${T.arcText('a1', 'MON PREMIER NOËL', 27, '#3c5a46')}
    ${sparkle(300, 150, 13)}${sparkle(262, 170, 6)}${sparkle(338, 170, 6)}
    ${T.script(300, 318, n, scriptSize(n, 150), '#2c4a37')}
    ${T.caps(300, 392, '2026', 30, 'url(#gold)', .4)}`; } },
  // 2. Couple
  'notre-premier-noel': { name: 'Léa & Tom', f: n => { seed = 23; return `
    <defs><radialGradient id="night" cx=".5" cy=".42" r=".65"><stop offset="0" stop-color="#2d5a40"/><stop offset="1" stop-color="#132a1c"/></radialGradient></defs>
    <circle cx="300" cy="300" r="300" fill="url(#night)"/><rect width="600" height="600" filter="url(#grain)" clip-path="url(#disc)" opacity=".7"/>
    <circle cx="300" cy="300" r="276" fill="none" stroke="url(#gold)" stroke-width="3"/><circle cx="300" cy="300" r="266" fill="none" stroke="url(#gold)" stroke-width="1" opacity=".7"/>
    ${pine(300, 92, 92, 200, { dark: '#4f8a63', light: '#83b892' })}${pine(300, 92, 92, -20, { dark: '#4f8a63', light: '#83b892' })}
    ${holly(282, 104, 26, -35, '#3d7a55')}${holly(318, 104, 26, 35, '#3d7a55')}${berries(300, 98, 4, 8)}
    ${T.caps(300, 196, 'NOTRE PREMIER NOËL', 22, 'url(#gold)', .32)}
    ${T.script(300, 318, n, scriptSize(n, 118), '#fbf3e4')}
    <path d="M300 372c-14-14-30-4-22 10 5 9 22 18 22 18s17-9 22-18c8-14-8-24-22-10z" fill="url(#gold)"/>
    ${T.caps(300, 446, '2026', 28, 'url(#gold)', .45)}
    ${[[140,220],[460,230],[170,420],[430,410],[120,320],[480,330]].map(([x,y]) => sparkle(x, y, R(5, 9))).join('')}`; } },
  // 3. Famille
  'famille': { name: 'Martin', f: n => { seed = 31; let houses = '';
    const H = [[120, 470, 70, 66], [196, 448, 64, 88], [268, 462, 74, 70], [348, 444, 66, 92], [420, 466, 72, 66]];
    for (const [x, y, w, h] of H) { houses += `<rect x="${x}" y="${y - h + 20}" width="${w}" height="${h}" fill="#1c3a52"/><path d="M${x - 6} ${y - h + 22}L${x + w / 2} ${y - h - 14}L${x + w + 6} ${y - h + 22}Z" fill="#162f43"/><path d="M${x - 6} ${y - h + 22}L${x + w / 2} ${y - h - 14}L${x + w + 6} ${y - h + 22}" stroke="#f6f1e6" stroke-width="5" fill="none" stroke-linejoin="round"/>`;
      for (let k = 0; k < 2; k++) houses += `<rect x="${x + 12 + k * (w - 34)}" y="${y - h + 40}" width="11" height="14" rx="1" fill="#ffd27a"/><rect x="${x + 7 + k * (w - 34)}" y="${y - h + 35}" width="21" height="24" fill="#ffd27a" opacity=".22"/>`; }
    let trees = ''; for (const [x, s] of [[96, 1.1], [478, 1.2], [520, .8], [70, .8]]) trees += `<path d="M${x} ${470 - 90 * s}l${28 * s} ${44 * s}h${-12 * s}l${22 * s} ${36 * s}h${-76 * s}l${22 * s} ${-36 * s}h${-12 * s}z" fill="#163526"/><path d="M${x} ${470 - 90 * s}l${10 * s} ${16 * s}h${-20 * s}z" fill="#f6f1e6"/>`;
    let snow = ''; for (let i = 0; i < 70; i++) { const x = R(40, 560), y = R(40, 400); if (Math.hypot(x - 300, y - 300) < 290 && !(y > 200 && y < 330 && x > 110 && x < 490)) snow += `<circle cx="${x}" cy="${y}" r="${R(1.2, 3)}" fill="#fff" opacity="${R(.5, 1)}"/>`; }
    return `<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f2236"/><stop offset=".7" stop-color="#284a63"/><stop offset="1" stop-color="#3f6680"/></linearGradient></defs>
    <circle cx="300" cy="300" r="300" fill="url(#sky)"/>
    <circle cx="456" cy="142" r="26" fill="#f6efd8"/><circle cx="468" cy="134" r="24" fill="url(#sky)" opacity=".001"/>
    ${snow}${trees}${houses}
    <path d="M0 470 C 120 444 220 486 320 466 S 520 448 600 470 V600 H0Z" fill="#f6f1e6"/><path d="M0 500 C 150 486 300 512 600 492 V600 H0Z" fill="#e7ecef"/>
    <circle cx="300" cy="300" r="284" fill="none" stroke="url(#gold)" stroke-width="3"/>
    ${T.caps(300, 196, 'LA FAMILLE', 26, '#f6f1e6', .45)}
    ${T.script(300, 300, n, scriptSize(n, 130), 'url(#gold)')}
    ${T.caps(300, 548, 'NOËL 2026', 22, '#3f6680', .4)}`; } },
  // 4. Prénom classique
  'prenom-couronne': { name: 'Emma', f: n => { seed = 5; return `${paper('#fbf6ec')}
    ${garland(300, 300, 238, -90, 268, 12)}
    ${T.caps(300, 232, 'JOYEUX NOËL', 24, '#a3312f', .38)}
    ${T.script(300, 336, n, scriptSize(n, 140), '#24432f')}
    ${T.caps(300, 400, '2026', 26, 'url(#gold)', .45)}
    ${sparkle(236, 392, 7)}${sparkle(364, 392, 7)}`; } }
};

// mise en situation : médaillon accroché, lumières floues
function mockup(dataUrl) {
  seed = 77; let bokeh = '';
  for (let i = 0; i < 46; i++) bokeh += `<circle cx="${R(0, 1200)}" cy="${R(0, 1200)}" r="${R(14, 60)}" fill="${pick(['#ffd27a', '#ffe6a8', '#ffb85c', '#fff3d6'])}" opacity="${R(.18, .6)}"/>`;
  let branches = '';
  for (const [x, y, a] of [[-20, 120, 20], [-30, 260, -10], [1220, 140, 160], [1230, 300, 190], [-10, 1040, -30], [1210, 1060, 210], [200, -20, 70], [1000, -20, 110]]) branches += pine(x, y, 260, a, { w: 5, density: .55, dark: '#163a26', light: '#2c5c3d' });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" width="1200" height="1200">${DEFS}
    <defs><radialGradient id="bg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#2a3d2c"/><stop offset="1" stop-color="#0d1810"/></radialGradient>
      <filter id="bk"><feGaussianBlur stdDeviation="14"/></filter><filter id="bb"><feGaussianBlur stdDeviation="5"/></filter>
      <filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="26" stdDeviation="24" flood-color="#000" flood-opacity=".55"/></filter>
      <linearGradient id="rib" x1="0" x2="1"><stop offset="0" stop-color="#7d1418"/><stop offset=".45" stop-color="#d33a3f"/><stop offset="1" stop-color="#8e1a1f"/></linearGradient>
      <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".35" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
      <clipPath id="orn"><circle cx="600" cy="660" r="360"/></clipPath></defs>
    <rect width="1200" height="1200" fill="url(#bg)"/>
    <g filter="url(#bk)">${bokeh}</g><g filter="url(#bb)" opacity=".9">${branches}</g>
    <path d="M572 0 C 560 140 590 220 588 300" stroke="url(#rib)" stroke-width="26" fill="none"/><path d="M628 0 C 640 140 612 220 612 300" stroke="url(#rib)" stroke-width="26" fill="none"/>
    <g filter="url(#sh)"><circle cx="600" cy="660" r="364" fill="#efe9df"/>
      <image href="${dataUrl}" x="240" y="300" width="720" height="720" clip-path="url(#orn)"/>
      <circle cx="600" cy="660" r="360" fill="url(#gloss)"/>
      <circle cx="600" cy="660" r="362" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="5"/></g>
    <circle cx="600" cy="332" r="15" fill="#2a2a2a" opacity=".55"/>
    <path d="M588 300 C 586 316 590 330 600 334 C 610 330 614 316 612 300" stroke="url(#rib)" stroke-width="12" fill="none"/>
  </svg>`;
}

(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const shots = {};
  for (const [k, d] of Object.entries(DESIGNS)) {
    for (const [suffix, n] of [['', d.name], ['-sans-prenom', '']]) {
      await p.setViewportSize({ width: 3000, height: 3000 });
      await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="3000" height="3000">${DEFS}<g clip-path="url(#disc)">${d.f(n)}</g></svg></body></html>`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
      const file = `${OUT}${k}${suffix}.png`;
      await p.locator('svg').screenshot({ path: file, omitBackground: true });
      if (!suffix) shots[k] = file;
    }
    // mise en situation
    const data = 'data:image/png;base64,' + fs.readFileSync(shots[k]).toString('base64');
    await p.setViewportSize({ width: 1200, height: 1200 });
    await p.setContent(`<html><body style="margin:0">${mockup(data)}</body></html>`); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}photo-${k}.jpg`, type: 'jpeg', quality: 88 });
  }
  // planche
  const keys = Object.keys(DESIGNS), labels = { 'premier-noel-bebe': 'Mon premier Noël', 'notre-premier-noel': 'Notre premier Noël', 'famille': 'La famille', 'prenom-couronne': 'Prénom · couronne' };
  const img = f => 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');
  await p.setViewportSize({ width: 1200, height: 1270 });
  await p.setContent(`<html><head><link href="https://fonts.googleapis.com/css2?family=Figtree:wght@600&display=swap" rel="stylesheet"></head><body style="margin:0;background:#efe8dc;padding:30px;display:grid;grid-template-columns:1fr 1fr;gap:24px;font:600 20px Figtree">
    ${keys.map(k => `<figure style="margin:0;display:grid;gap:10px"><img src="${img(OUT + 'photo-' + k + '.jpg')}" style="width:100%;border-radius:18px"><figcaption style="text-align:center;color:#22261f">${labels[k]}</figcaption></figure>`).join('')}</body></html>`);
  await p.waitForTimeout(600); await p.screenshot({ path: OUT + 'apercu.jpg', type: 'jpeg', quality: 85, fullPage: true });
  await b.close();
})();
