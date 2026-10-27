const { chromium } = require('playwright');
const fs = require('fs');
const OUT = '/home/user/Claude/designs/nouveaux/';
fs.mkdirSync(OUT, { recursive: true });
const b64 = f => fs.readFileSync('/home/user/Claude/designs/polices/' + f).toString('base64');
const FONTS = `<style>@font-face{font-family:'Pinyon Script';src:url(data:font/ttf;base64,${b64('PinyonScript.ttf')})}@font-face{font-family:Cinzel;font-weight:100 900;src:url(data:font/ttf;base64,${b64('Cinzel.ttf')})}</style>`;

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
const paper = (bg) => `<rect width="600" height="600" fill="${bg}"/><rect width="600" height="600" filter="url(#grain)"/>`;


const paw = (x, y, s, fill) => `<g transform="translate(${x} ${y}) scale(${s})" fill="${fill}"><ellipse cx="0" cy="8" rx="13" ry="11"/><ellipse cx="-15" cy="-8" rx="5.5" ry="7" transform="rotate(-20 -15 -8)"/><ellipse cx="-5.5" cy="-15" rx="5.5" ry="7.5"/><ellipse cx="5.5" cy="-15" rx="5.5" ry="7.5"/><ellipse cx="15" cy="-8" rx="5.5" ry="7" transform="rotate(20 15 -8)"/></g>`;
const DESIGNS = {
  'medaillon-animal': { name: 'Rocky', f: n => { seed = 41;
    const C = '#f6efe2';
    let snow = ''; for (let i = 0; i < 60; i++) { const x = R(40, 560), y = R(40, 560); if (Math.hypot(x - 300, y - 300) < 250 && !(y > 250 && y < 400) && !(y < 215 && Math.hypot(x - 300, y - 300) > 170) && !(y > 440) && Math.hypot(x - 300, y - 95) > 50 && !(y < 215 && Math.hypot(x - 300, y - 300) > 120)) snow += `<circle cx="${x}" cy="${y}" r="${R(1.5, 3.4)}" fill="#fff" opacity="${R(.35, .85)}"/>`; }
    // traces de pattes qui traversent en arc
    let trail = ''; for (let i = 0; i < 5; i++) { const t = i / 4, x = 200 + t * 200, y = 500 + Math.sin(t * Math.PI) * 12 + (i % 2 ? 9 : -9); trail += `<g transform="rotate(90 ${x} ${y})">${paw(x, y, .5, C + 'd9')}</g>`; }
    // os : barre + 4 boules
    const bx = 300, by = 325, hw = 138, hh = 44, r = 36;
    const bone = `<g filter="url(#bsh)">
      <rect x="${bx - hw}" y="${by - hh}" width="${hw * 2}" height="${hh * 2}" fill="${C}"/>
      <circle cx="${bx - hw}" cy="${by - r * .78}" r="${r}" fill="${C}"/><circle cx="${bx - hw}" cy="${by + r * .78}" r="${r}" fill="${C}"/>
      <circle cx="${bx + hw}" cy="${by - r * .78}" r="${r}" fill="${C}"/><circle cx="${bx + hw}" cy="${by + r * .78}" r="${r}" fill="${C}"/></g>
      <rect x="${bx - hw + 6}" y="${by - hh + 8}" width="${hw * 2 - 12}" height="${hh * 2 - 16}" rx="10" fill="none" stroke="url(#gold)" stroke-width="2"/>`;
    // bonnet posé sur la boule gauche du haut
    const hat = `<g transform="translate(${bx - hw + 2} ${by - r * .78 - 26}) rotate(-12) scale(.85)">
      <path d="M-40 4 C -34 -30 -6 -52 24 -48 C 44 -44 56 -28 60 -8 C 62 2 54 6 50 -2 C 44 -18 34 -28 22 -28 C 4 -26 -18 -16 -40 4 Z" fill="#2f6a48" stroke="${C}" stroke-width="2"/>
      <path d="M-48 2 C -16 -10 16 -12 46 -2 C 52 0 52 12 46 12 C 16 4 -16 4 -48 14 C -54 16 -56 4 -48 2 Z" fill="#fff"/>
      <circle cx="54" cy="0" r="10" fill="#fff"/></g>`;
    const sprig = `${holly(bx + hw + 10, by - r * .78 - 30, 22, 30, '#2f6a48')}${holly(bx + hw + 30, by - r * .78 - 18, 20, 75, '#2f6a48')}${berries(bx + hw + 16, by - r * .78 - 18, 3, 6)}`;
    return `<defs><radialGradient id="vel" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#b5363b"/><stop offset=".7" stop-color="#86202a"/><stop offset="1" stop-color="#5e141c"/></radialGradient>
      <filter id="bsh" x="-20%" y="-40%" width="140%" height="180%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#3a0a10" flood-opacity=".45"/></filter></defs>
    <rect width="600" height="600" fill="url(#vel)"/><rect width="600" height="600" filter="url(#grain)" opacity=".6"/>
    <circle cx="300" cy="300" r="262" fill="none" stroke="url(#gold)" stroke-width="3"/><circle cx="300" cy="300" r="252" fill="none" stroke="url(#gold)" stroke-width="1" opacity=".6"/>
    ${snow}
    ${T.arc('a1', 150, true, 300)}${T.arcText('a1', 'JOYEUX NOËL', 23, C, .32)}
    ${trail}
    ${bone}${hat}${sprig}
    ${T.script(300, 342, n, scriptSize(n, 84), '#1f3d2c')}
    ${T.caps(300, 448, '2026', 26, 'url(#gold)', .5)}
    ${sparkle(222, 440, 8)}${sparkle(378, 440, 8)}
    ${flake(150, 420, 11, C, 2)}${flake(450, 420, 11, C, 2)}`; } },
};

// plaid 50x60 pouces, portrait
function knitBand(y, w, rows, fg, bg) {
  // bande jacquard : sapins + flocons en pixels
  const px = 10; let s = `<rect x="0" y="${y}" width="${w}" height="${rows * px}" fill="${bg}"/>`;
  const tree = ['....X....','...XXX...','..XXXXX..','...XXX...','..XXXXX..','.XXXXXXX.','XXXXXXXXX','....X....','....X....'];
  const flk = ['X...X...X','.X..X..X.','..X.X.X..','...XXX...','XXXX.XXXX','...XXX...','..X.X.X..','.X..X..X.','X...X...X'];
  const motifs = [tree, flk]; let col = 0, i = 0;
  while (col * px < w) { const m = motifs[i % 2]; for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) if (m[r][c] === 'X') s += `<rect x="${(col + c) * px}" y="${y + (r + 2) * px}" width="${px - 1.5}" height="${px - 1.5}" rx="2" fill="${fg}"/>`; col += 13; i++; }
  for (let c = 0; c * px < w; c += 2) { s += `<rect x="${c * px}" y="${y}" width="${px - 1.5}" height="${px - 1.5}" rx="2" fill="${fg}"/><rect x="${c * px}" y="${y + (rows - 1) * px}" width="${px - 1.5}" height="${px - 1.5}" rx="2" fill="${fg}"/>`; }
  return s;
}
const PLAID = n => { seed = 61; const W = 1000, H = 1200, G = '#1f3d2c', C = '#f3ead8';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="__W__" height="__H__">${DEFS}
  <rect width="${W}" height="${H}" fill="${G}"/>
  ${knitBand(60, W, 13, C, G)}${knitBand(H - 190, W, 13, C, G)}
  <rect x="0" y="230" width="${W}" height="3" fill="${C}" opacity=".5"/><rect x="0" y="${H - 222}" width="${W}" height="3" fill="${C}" opacity=".5"/>
  ${(() => { let s = ''; for (let i = 0; i < 60; i++) { const x = R(30, W - 30), y = R(280, H - 270); if (Math.abs(y - 600) > 190 || Math.abs(x - 500) > 400) s += `<circle cx="${x}" cy="${y}" r="${R(2, 4.5)}" fill="${C}" opacity="${R(.35, .8)}"/>`; } return s; })()}
  ${star(500, 400, 26)}
  <text x="500" y="485" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="46" letter-spacing="20" fill="${C}">LA FAMILLE</text>
  ${n ? `<text x="500" y="690" text-anchor="middle" font-family="Pinyon Script" font-size="${n.length > 9 ? 170 : 220}" fill="url(#gold)">${n}</text>` : ''}
  <text x="500" y="800" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="40" letter-spacing="18" fill="${C}">NOËL 2026</text>
  ${sparkle(290, 787, 12)}${sparkle(710, 787, 12)}
  </svg>`; };


// tote bag : 2 faces carrées — style colis du Père Noël
const TOTE = (n, face) => { seed = 71; const W = 1000, K = '#d8bf96', RED = '#a3312f', G = '#1f3d2c', INK = '#3a2a1c';
  // texture kraft
  let fib = ''; for (let i = 0; i < 260; i++) { const x = R(0, W), y = R(0, W), l = R(8, 30), a = R(0, Math.PI); fib += `<path d="M${x} ${y}l${Math.cos(a) * l} ${Math.sin(a) * l}" stroke="${rnd() > .5 ? '#c2a679' : '#e6d2ae'}" stroke-width="${R(1, 2.2)}" opacity=".55"/>`; }
  const ring = (cx, cy, r, txt, col, rot) => `<g transform="rotate(${rot} ${cx} ${cy})" opacity=".88">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${col}" stroke-width="7"/><circle cx="${cx}" cy="${cy}" r="${r - 16}" fill="none" stroke="${col}" stroke-width="3"/>
    <path id="rg${cx}" d="M${cx} ${cy + r - 38}A${r - 38} ${r - 38} 0 1 1 ${cx} ${cy - r + 38}A${r - 38} ${r - 38} 0 1 1 ${cx} ${cy + r - 38}" fill="none"/>
    <text font-family="Cinzel" font-weight="700" font-size="${r > 170 ? 30 : 24}" letter-spacing="${r > 170 ? 7 : 4}" fill="${col}"><textPath href="#rg${cx}" startOffset="50%" text-anchor="middle">${txt}</textPath></text>
    ${star(cx, cy + 6, 34, col)}<text x="${cx}" y="${cy + 80}" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="30" letter-spacing="6" fill="${col}">2026</text></g>`;
  const stripe = (y) => { let s = ''; for (let x = -40; x < W + 40; x += 56) s += `<path d="M${x} ${y}l28 0l-24 26l-28 0z" fill="${Math.round((x + 40) / 56) % 2 ? RED : G}"/>`; return s; };
  const frame = `${stripe(40)}${stripe(W - 66)}`;
  const center = face === 'face' ? `
    ${ring(250, 250, 150, 'PÔLE NORD · PÔLE NORD · PÔLE NORD ·', RED, -14)}
    <text x="455" y="225" font-family="Cinzel" font-weight="700" font-size="54" letter-spacing="4" fill="${G}">SAC OFFICIEL</text>
    <text x="455" y="292" font-family="Cinzel" font-weight="700" font-size="44" letter-spacing="5" fill="${G}">DU PÈRE NOËL</text>
    <rect x="455" y="322" width="420" height="5" fill="${RED}"/>
    <text x="500" y="520" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="38" letter-spacing="12" fill="${RED}">LIVRAISON SPÉCIALE POUR</text>
    <path d="M150 720 H850" stroke="${INK}" stroke-width="3" stroke-dasharray="10 9" opacity=".7"/>
    ${n ? `<text x="500" y="690" text-anchor="middle" font-family="Pinyon Script" font-size="${n.length > 9 ? 150 : 180}" fill="${G}">${n}</text>` : ''}
    <g transform="rotate(-6 780 840)"><rect x="650" y="790" width="280" height="96" rx="8" fill="none" stroke="${RED}" stroke-width="6"/><text x="790" y="852" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="34" letter-spacing="5" fill="${RED}">FRAGILE</text></g>
    <text x="100" y="855" font-family="Cinzel" font-weight="600" font-size="24" letter-spacing="5" fill="${INK}" opacity=".75">EXP. : ATELIER DES LUTINS</text>`
  : `
    ${ring(500, 330, 190, '· PÔLE NORD · LIVRAISON EXPRESS · PÔLE NORD ', RED, 8)}
    <text x="500" y="640" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="50" letter-spacing="8" fill="${G}">NE PAS OUVRIR</text>
    <text x="500" y="710" text-anchor="middle" font-family="Cinzel" font-weight="700" font-size="50" letter-spacing="8" fill="${G}">AVANT LE</text>
    <text x="500" y="830" text-anchor="middle" font-family="Pinyon Script" font-size="120" fill="${RED}">25 décembre</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${W}" width="__W__" height="__W__">${DEFS}
  <rect width="${W}" height="${W}" fill="${K}"/>${fib}<rect width="${W}" height="${W}" filter="url(#grain)"/>
  ${frame}${center}</svg>`; };

(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [k, d] of (process.env.TOTE ? [] : Object.entries(DESIGNS))) for (const [suffix, n] of [['', d.name], ['-sans-prenom', '']]) {
    await p.setViewportSize({ width: 3000, height: 3000 });
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="3000" height="3000">${DEFS}${d.f(n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    await p.locator('svg').screenshot({ path: `${OUT}${k}${suffix}.png`, omitBackground: true });
  }
  for (const [suffix, n] of (process.env.PLAID ? [['', 'Martin'], ['-sans-prenom', '']] : [])) {
    await p.setViewportSize({ width: 6000, height: 7200 });
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0}</style></head><body>${PLAID(n).replace('__W__', 6000).replace('__H__', 7200)}</body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
    await p.locator('svg').screenshot({ path: `${OUT}plaid-famille${suffix}.png` });
  }
  for (const [file, n, face] of (process.env.TOTE ? [['tote-face', 'Léo', 'face'], ['tote-face-sans-prenom', '', 'face'], ['tote-dos', '', 'dos']] : [])) {
    await p.setViewportSize({ width: 5000, height: 5000 });
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0}</style></head><body>${TOTE(n, face).replace(/__W__/g, 5000)}</body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
    await p.locator('svg').screenshot({ path: `${OUT}${file}.png` });
  }
  await b.close();
})();
