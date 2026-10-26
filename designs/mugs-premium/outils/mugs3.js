const { chromium } = require('playwright'); const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync(__dirname + '/premium.js', 'utf8');
const lib = SRC.slice(SRC.indexOf('let seed'), SRC.indexOf('// mise en situation'));
const ctx = { Math }; vm.createContext(ctx);
vm.runInContext(lib + ';this.L={DEFS,pine,eucalyptus,holly,berries,sparkle,star,flake,setSeed:s=>{seed=s},R:(a,b)=>R(a,b),pick};', ctx);
const L = ctx.L;
const OUT = '/home/user/Claude/designs/mugs-premium/'; fs.mkdirSync(OUT, { recursive: true });
const TEX = __dirname + '/three/tex/';
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@500;600;700&display=swap" rel="stylesheet">`;
const VW = 1425, VH = 600, SIDES = [VW * .25, VW * .75];
const fit = (n, b) => !n ? b : n.length > 9 ? b * .66 : n.length > 6 ? b * .82 : b;
const script = (x, y, t, s, f) => t ? `<text x="${x}" y="${y}" text-anchor="middle" font-family="Pinyon Script" font-size="${s}" fill="${f}">${t}</text>` : '';
const caps = (x, y, t, s, f, ls = .4) => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Cinzel" font-weight="600" font-size="${s}" letter-spacing="${s * ls}" fill="${f}">${t}</text>`;
const EXTRA = `<defs>
 <radialGradient id="bRed" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#f08a84"/><stop offset=".45" stop-color="#c0282d"/><stop offset="1" stop-color="#6e1013"/></radialGradient>
 <radialGradient id="bGreen" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#7fb894"/><stop offset=".45" stop-color="#2f6b4a"/><stop offset="1" stop-color="#143524"/></radialGradient>
 <radialGradient id="bGold" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fbe9b0"/><stop offset=".45" stop-color="#c9a04a"/><stop offset="1" stop-color="#7a5a1c"/></radialGradient>
 <radialGradient id="bCream" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#efe6d6"/><stop offset="1" stop-color="#b8a98f"/></radialGradient>
</defs>`;
const bauble = (x, y, r, fill, len) => `<path d="M${x} ${y - len}V${y - r}" stroke="#a3312f" stroke-width="3"/><rect x="${x - r * .28}" y="${y - r - r * .3}" width="${r * .56}" height="${r * .34}" rx="2" fill="url(#gold)"/><circle cx="${x}" cy="${y}" r="${r}" fill="url(#${fill})"/><ellipse cx="${x - r * .35}" cy="${y - r * .38}" rx="${r * .22}" ry="${r * .13}" fill="#fff" opacity=".75" transform="rotate(-30 ${x - r * .35} ${y - r * .38})"/>`;

// guirlande continue sur toute la largeur (raccord aux bords)
function garlandBand(y, amp) { let s = ''; const pts = x => y + Math.sin(x / VW * Math.PI * 4) * amp;
  for (let x = -60; x <= VW + 60; x += 26) { const yy = pts(x);
    s += L.pine(x, yy, L.R(44, 62), L.R(-150, -110)) + L.pine(x, yy, L.R(40, 58), L.R(-70, -30));
    if (L.R(0, 1) > .55) s += L.pine(x, yy, L.R(36, 50), L.R(60, 120));
    if (L.R(0, 1) > .62) s += L.eucalyptus(x, yy, L.R(38, 52), L.pick([-130, -50, 70, 110]) + L.R(-10, 10)); }
  for (let x = 30; x <= VW; x += 95) { const yy = pts(x); s += L.holly(x - 9, yy + 4, 20, 30) + L.holly(x + 9, yy + 4, 18, -30) + L.berries(x, yy, 3, 6.5); }
  return s; }
// sapin aquarelle fait de branches
function fir(x, base, h) { const tiers = 4, greens = ['#1f4a33', '#2a5c40', '#346b4b', '#24503a']; let g = `<rect x="${x - h * .035}" y="${base - h * .14}" width="${h * .07}" height="${h * .14}" fill="#5a3d28"/>`;
  for (let i = 0; i < tiers; i++) { const t = i / tiers, top = base - h * .1 - h * .9 * (t + 1 / tiers) - h * .06, bot = base - h * .1 - h * .9 * t, w = h * .4 * (1 - t * .72);
    let edge = ''; const teeth = 5; for (let k = 0; k <= teeth; k++) { const xx = x + w - (2 * w) * k / teeth; edge += `L${xx} ${bot + (k % 2 ? -h * .03 : 0)}`; }
    g += `<path d="M${x} ${top}L${x + w} ${bot}${edge}Z" fill="${greens[(i + Math.round(x)) % 4]}"/>`;
    g += `<path d="M${x - w * .78} ${bot - h * .015}Q${x - w * .3} ${bot - h * .07} ${x} ${bot - h * .04}T${x + w * .78} ${bot - h * .015}" stroke="#fff" stroke-width="${h * .03}" stroke-linecap="round" fill="none"/>`; }
  g += `<path d="M${x} ${base - h * 1.02}l${h * .05} ${h * .07}h${-h * .1}z" fill="#fff"/>`;
  return `<g filter="url(#wc)">${g}</g>`; }

const D = {
  // A — Guirlande de sapin et boules suspendues tout autour du haut du mug
  'guirlande': n => { L.setSeed(21); let s = EXTRA + garlandBand(70, 18);
    const fills = ['bRed', 'bGold', 'bGreen', 'bCream'];
    for (let x = 60, i = 0; x < VW; x += 118, i++) { if (SIDES.some(c => Math.abs(x - c) < 150)) continue; const len = L.R(40, 130); s += bauble(x, 70 + Math.sin(x / VW * Math.PI * 4) * 18 + len, L.R(16, 24), fills[i % 4], len); }
    for (const c of SIDES) s += caps(c, 300, 'JOYEUX NOËL', 26, '#a3312f', .45) + script(c, 420, n, fit(n, 140), '#1f4430') + caps(c, 492, '2026', 24, 'url(#gold)', .55) + L.sparkle(c - 62, 484, 7) + L.sparkle(c + 62, 484, 7);
    return s; },
  // B — Forêt enneigée en aquarelle tout le long du bas, flocons qui tombent
  'foret': n => { L.setSeed(42); let s = EXTRA;
    for (let i = 0; i < 70; i++) { const x = L.R(10, VW - 10), y = L.R(20, 380); if (SIDES.some(c => Math.abs(x - c) < 250 && y > 90 && y < 330)) continue; s += i % 3 ? `<circle cx="${x}" cy="${y}" r="${L.R(2, 4)}" fill="#a9c6d6" opacity=".8"/>` : L.flake(x, y, L.R(8, 13), '#a9c6d6', 2); }
    const trees = []; for (let x = -30; x < VW + 40; x += L.R(48, 74)) trees.push([x, L.R(110, 190)]);
    trees.sort((a, b) => b[1] - a[1]).forEach(([x, h]) => s += fir(x, 586, h));
    s += `<path d="M0 578 C 300 566 600 590 ${VW / 2} 576 S 1200 566 ${VW} 578 V${VH} H0Z" fill="#fff"/>`;
    for (const c of SIDES) s += L.star(c, 92, 13) + caps(c, 152, 'JOYEUX NOËL', 24, '#2f5c40', .45) + script(c, 262, n, fit(n, 138), '#a3312f') + caps(c, 316, '2026', 22, 'url(#gold)', .55);
    return s; },
  // C — Nuit verte et branches dorées, étiquette crème
  'nuit-doree': n => { L.setSeed(9); let s = EXTRA + `<rect width="${VW}" height="${VH}" fill="#173a29"/><rect width="${VW}" height="${VH}" filter="url(#grain)" opacity=".6"/>`;
    for (let x = 0; x < VW; x += 95) for (let y = 30, r = 0; y < VH; y += 95, r++) { const xx = x + (r % 2) * 47; if (SIDES.some(c => Math.abs(xx - c) < 215 && Math.abs(y - 300) < 205)) continue;
      const k = (x / 95 + r) % 3; s += k === 0 ? L.pine(xx - 18, y + 8, 38, -40, { dark: '#c9a04a', light: '#e9cb78', w: 1.4 }) : k === 1 ? L.star(xx, y, 7) : L.sparkle(xx, y, 9); }
    for (const c of SIDES) s += `<ellipse cx="${c}" cy="300" rx="196" ry="182" fill="#fbf6ec"/><ellipse cx="${c}" cy="300" rx="182" ry="168" fill="none" stroke="url(#gold)" stroke-width="3"/>
      ${L.pine(c - 6, 170, 46, 200, { w: 1.6 })}${L.pine(c + 6, 170, 46, -20, { w: 1.6 })}${L.berries(c, 168, 3, 6)}
      ${caps(c, 232, 'JOYEUX NOËL', 22, '#a3312f', .42)}${script(c, 338, n, fit(n, 116), '#1f4430')}${caps(c, 402, '2026', 22, 'url(#gold)', .55)}`;
    return s; }
};
const NAMES = { 'guirlande': 'Emma', 'foret': 'Lucas', 'nuit-doree': 'Chloé' };
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2850, height: 1200 } });
  for (const [k, name] of Object.entries(NAMES)) for (const [suf, n] of [['', name], ['-sans-prenom', '']]) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0;background:transparent}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VW} ${VH}" width="2850" height="1200">${L.DEFS}${D[k](n)}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.locator('svg').screenshot({ path: `${OUT}mug-${k}${suf}.png`, omitBackground: true });
    if (!suf) fs.copyFileSync(`${OUT}mug-${k}.png`, `${TEX}mug-${k}.png`);
  } await b.close(); })();
