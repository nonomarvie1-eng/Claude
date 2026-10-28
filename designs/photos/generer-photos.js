const { chromium } = require('playwright');
const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync(__dirname + '/premium.js', 'utf8');
// on réutilise les dessins de premium.js (tout ce qui précède la mise en situation)
const lib = SRC.slice(SRC.indexOf('let seed'), SRC.indexOf('// mise en situation'));
const ctx = { Math, fs, require };
vm.createContext(ctx);
vm.runInContext(lib + '\n;this.L = { DEFS, DESIGNS, pine, holly, berries, sparkle, star, R: (a,b)=>R(a,b), setSeed: s => { seed = s; } };', ctx);
const L = ctx.L;
const OUT = '/home/user/Claude/designs/photos/';
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@500;600;700&family=Figtree:wght@500;600&display=swap" rel="stylesheet">`;

const PRODUCTS = {
  'prenom-couronne':     { names: ['Emma', 'Lucas', 'Chloé'] },
  'premier-noel-bebe':   { names: ['Emma', 'Jules', 'Léna'] },
  'notre-premier-noel':  { names: ['Léa & Tom', 'Sarah & Hugo', 'Inès & Max'] },
  'famille':             { names: ['Martin', 'Dubois', 'Bernard'] }
};

/* ---------- briques de décor ---------- */
const DEF2 = `<defs>
  <filter id="drop" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#3a2a18" flood-opacity=".35"/></filter>
  <filter id="dropDark" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="24" stdDeviation="22" flood-color="#000" flood-opacity=".55"/></filter>
  <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter><filter id="blur14"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="linen" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9 .04" numOctaves="2" seed="5"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .47  0 0 0 0 .36  0 0 0 .13 0"/></filter>
  <filter id="wood" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".004 .09" numOctaves="3" seed="8"/><feColorMatrix values="0 0 0 0 .25  0 0 0 0 .14  0 0 0 0 .07  0 0 0 .55 0"/></filter>
  <linearGradient id="rib" x1="0" x2="1"><stop offset="0" stop-color="#7d1418"/><stop offset=".45" stop-color="#d33a3f"/><stop offset="1" stop-color="#8e1a1f"/></linearGradient>
  <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".35" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>`;
let cid = 0;
// médaillon : data = image du design ; ribbon 'up' | 'loose' | 'none' ; tilt < 1 = vu de biais
function orn(data, cx, cy, r, { rot = 0, tilt = 1, ribbon = 'up', dark = false } = {}) {
  const id = 'c' + (++cid), hy = -r * .86, hr = r * .055;
  let rb = '';
  if (ribbon === 'up') rb = `<path d="M${-hr * .9} ${hy} C ${-hr * 1.6} ${hy - r * .5} ${-hr * 3} ${-cy - 40} ${-hr * 3} ${-cy - 60}" stroke="url(#rib)" stroke-width="${r * .07}" fill="none"/><path d="M${hr * .9} ${hy} C ${hr * 1.6} ${hy - r * .5} ${hr * 3} ${-cy - 40} ${hr * 3} ${-cy - 60}" stroke="url(#rib)" stroke-width="${r * .07}" fill="none"/>`;
  if (ribbon === 'loose') rb = `<path d="M0 ${hy} C ${r * .25} ${hy - r * .45} ${r * .75} ${hy - r * .55} ${r * .6} ${hy - r * .25} C ${r * .5} ${hy - r * .05} ${r * .2} ${hy - r * .15} 0 ${hy}" stroke="url(#rib)" stroke-width="${r * .065}" fill="none"/><path d="M0 ${hy} C ${-r * .2} ${hy - r * .3} ${-r * .55} ${hy - r * .35} ${-r * .8} ${hy - r * .2}" stroke="url(#rib)" stroke-width="${r * .065}" fill="none" stroke-linecap="round"/>`;
  const edge = tilt < 1 ? `<ellipse cx="${r * (1 - tilt) * .16}" cy="0" rx="${r * tilt}" ry="${r}" fill="#cfc6b8"/>` : '';
  return `<g transform="translate(${cx} ${cy}) rotate(${rot})">
    <g filter="url(#${dark ? 'dropDark' : 'drop'})">${edge}
      <g transform="scale(${tilt} 1)">
        <clipPath id="${id}"><circle r="${r}"/></clipPath>
        <circle r="${r + 2}" fill="#efe9df"/>
        <image href="${data}" x="${-r}" y="${-r}" width="${r * 2}" height="${r * 2}" clip-path="url(#${id})"/>
        <circle r="${r}" fill="url(#gloss)"/><circle r="${r - 1}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="3"/>
        <circle cx="0" cy="${hy}" r="${hr}" fill="#6b625a" opacity=".55"/>
      </g></g>${rb}</g>`;
}
const linenBg = c => `<rect width="1200" height="1200" fill="${c}"/><rect width="1200" height="1200" filter="url(#linen)"/>`;
function sprigs(list) { return list.map(([x, y, len, a, s]) => (L.setSeed(s), L.pine(x, y, len, a, { w: 3.4, density: .8 }))).join(''); }
const caption = (t, y = 1130, fill = '#2c4a37') => `<text x="600" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="34" letter-spacing="7" fill="${fill}">${t}</text>`;
const small = (t, y, fill = '#6e6c64') => `<text x="600" y="${y}" text-anchor="middle" font-family="Figtree" font-weight="500" font-size="28" fill="${fill}">${t}</text>`;

/* ---------- scènes ---------- */
const SCENES = {
  '1-sapin': d => { L.setSeed(77); let bokeh = ''; for (let i = 0; i < 46; i++) bokeh += `<circle cx="${L.R(0, 1200)}" cy="${L.R(0, 1200)}" r="${L.R(14, 60)}" fill="${['#ffd27a', '#ffe6a8', '#ffb85c', '#fff3d6'][i % 4]}" opacity="${L.R(.18, .6)}"/>`;
    return `<defs><radialGradient id="bgN" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#2a3d2c"/><stop offset="1" stop-color="#0d1810"/></radialGradient></defs>
      <rect width="1200" height="1200" fill="url(#bgN)"/><g filter="url(#blur14)">${bokeh}</g>
      <g filter="url(#blur6)" opacity=".9">${sprigs([[-20, 120, 300, 20, 1], [1220, 160, 300, 160, 2], [-10, 1040, 280, -30, 3], [1210, 1060, 280, 210, 4], [200, -20, 260, 70, 5], [1000, -20, 260, 110, 6]])}</g>
      ${orn(d.main, 600, 650, 370, { dark: true })}`; },
  '2-a-plat': d => `${linenBg('#f1e9dc')}
      ${sprigs([[-30, 160, 330, 15, 11], [-20, 230, 260, -12, 12], [1230, 980, 340, 200, 13], [1220, 1060, 260, 170, 14], [980, -30, 220, 115, 15]])}
      ${L.berries(230, 200, 4, 13)}${L.berries(980, 1010, 4, 13)}${L.holly(250, 250, 46, 30)}${L.holly(950, 960, 46, -150)}
      ${L.sparkle(900, 220, 16)}${L.sparkle(950, 300, 9)}${L.sparkle(260, 980, 14)}${L.sparkle(330, 1040, 8)}
      ${orn(d.main, 600, 640, 360, { rot: -7, ribbon: 'loose' })}`,
  '3-recto-verso': d => `${linenBg('#f4ede2')}
      <path d="M0 150 C 300 120 900 120 1200 150" stroke="#8d6748" stroke-width="5" fill="none"/>
      ${sprigs([[40, 140, 240, -8, 21], [1160, 140, 240, 188, 22]])}
      <g transform="translate(0 150)">${orn(d.main, 400, 470, 255, { rot: -4 }).replace(/-cy - 60/g, '0')}</g>
      <g transform="translate(0 150)">${orn(d.main, 840, 440, 255, { rot: 5, tilt: .58 })}</g>
      ${caption('IMPRIMÉ RECTO VERSO', 1090)}${small('Le même design des deux côtés', 1140)}`,
  '4-taille': d => `${linenBg('#f6f1e8')}
      ${orn(d.main, 600, 560, 330, { ribbon: 'loose' })}
      <g stroke="#2c4a37" stroke-width="3" fill="none"><path d="M270 960H930"/><path d="M270 940v40M930 940v40"/><path d="M290 948l-20 12 20 12M910 948l20 12-20 12"/></g>
      <rect x="490" y="932" width="220" height="56" rx="28" fill="#f6f1e8"/>
      <text x="600" y="972" text-anchor="middle" font-family="Figtree" font-weight="600" font-size="34" fill="#2c4a37">≈ 7,5 cm</text>
      ${caption('CÉRAMIQUE · RUBAN INCLUS', 1090)}${small('Prêt à accrocher au sapin', 1140)}`,
  '5-prenoms': d => `${linenBg('#f2eadf')}
      ${sprigs([[-40, 150, 640, -4, 31], [1240, 150, 640, 184, 32]])}${L.berries(600, 140, 5, 14)}${L.holly(570, 150, 50, -40)}${L.holly(632, 150, 50, 40)}
      ${[[230, 560, -5], [600, 640, 2], [970, 560, 6]].map(([x, y, r], i) => orn(d.alts[i], x, y, 185, { rot: r })).join('')}
      ${caption('VOTRE PRÉNOM, VOTRE MÉDAILLON', 1060)}${small('Personnalisation offerte', 1112)}`,
  '6-cadeaux': d => { const gift = (x, y, w, h, c, rc, a) => `<g transform="rotate(${a} ${x + w / 2} ${y + h / 2})"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="${c}"/><rect x="${x + w / 2 - 14}" y="${y}" width="28" height="${h}" fill="${rc}"/><rect x="${x}" y="${y + h / 2 - 14}" width="${w}" height="28" fill="${rc}"/></g>`;
    return `<rect width="1200" height="1200" fill="#8a5a36"/><rect width="1200" height="1200" filter="url(#wood)"/>
      ${[200, 420, 640, 860, 1080].map(y => `<path d="M0 ${y}H1200" stroke="#5e3a20" stroke-width="3" opacity=".5"/>`).join('')}
      <g filter="url(#blur6)">${gift(-60, -40, 420, 300, '#b3282d', '#d9b45c', -8)}${gift(860, -60, 400, 330, '#1f3d2c', '#d9b45c', 10)}${gift(940, 900, 360, 360, '#efe4d0', '#b3282d', -12)}</g>
      ${sprigs([[-20, 1000, 320, -25, 41], [40, 1120, 260, -40, 42]])}${L.berries(170, 990, 4, 14)}
      ${L.sparkle(760, 980, 14)}${L.sparkle(820, 1040, 8)}${L.sparkle(380, 260, 12)}
      ${orn(d.main, 600, 610, 350, { rot: 8, ribbon: 'loose' })}`; }
};

(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const renderDesign = async (key, name) => {
    await p.setViewportSize({ width: 1200, height: 1200 });
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="1200" height="1200">${L.DEFS}${L.DESIGNS[key].f(name)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    return 'data:image/png;base64,' + (await p.locator('svg').screenshot()).toString('base64');
  };
  const sheet = [];
  for (const [key, P] of Object.entries(PRODUCTS)) {
    fs.mkdirSync(OUT + key, { recursive: true });
    const alts = []; for (const n of P.names) alts.push(await renderDesign(key, n));
    const d = { main: alts[0], alts };
    for (const [sname, fn] of Object.entries(SCENES)) {
      await p.setViewportSize({ width: 1200, height: 1200 });
      await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" width="1200" height="1200">${L.DEFS}${DEF2}${fn(d)}</svg></body></html>`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
      const f = `${OUT}${key}/${sname}.jpg`;
      await p.locator('svg').screenshot({ path: f, type: 'jpeg', quality: 88 });
      sheet.push(f);
    }
  }
  // planche d'aperçu pour un produit
  const img = f => 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');
  for (const key of Object.keys(PRODUCTS)) {
    const files = Object.keys(SCENES).map(s => `${OUT}${key}/${s}.jpg`);
    await p.setViewportSize({ width: 1200, height: 800 });
    await p.setContent(`<body style="margin:0;background:#efe8dc;padding:16px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px">${files.map(f => `<img src="${img(f)}" style="width:100%;border-radius:12px">`).join('')}</body>`);
    await p.waitForTimeout(300); await p.screenshot({ path: `${OUT}apercu-${key}.jpg`, type: 'jpeg', quality: 82, fullPage: true });
  }
  await b.close();
})();
