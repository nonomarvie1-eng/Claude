const { chromium } = require('playwright'); const fs = require('fs');
const D = '/home/user/Claude/designs/';
const b64 = (f, t = 'jpeg') => `data:image/${t};base64,` + fs.readFileSync(f).toString('base64');
const IMG = {
  medBebe: b64(D + 'photos-3d/premier-noel-bebe/1-face.jpg'), medJoy: b64(D + 'photos-3d/prenom-couronne/1-face.jpg'),
  medFam: b64(D + 'photos-3d/famille/1-face.jpg'),
  mugG: b64(D + 'mugs-premium/photo-guirlande-1-droite.jpg'), mugR: b64(D + 'mugs-premium/photo-pull-rouge-1-droite.jpg'),
  sweat: b64(D + 'sweat-famille/sweat-famille-v2.png', 'png'), body: b64(D + 'body-bebe/body-petit-renne.png', 'png')
};
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,600&family=Figtree:wght@500;600&display=swap" rel="stylesheet">`;
// vêtements à plat (SVG) avec le design posé dessus
const sweatSVG = (w) => `<svg viewBox="0 0 600 560" width="${w}" style="filter:drop-shadow(0 18px 22px rgba(60,40,20,.28))">
  <defs><clipPath id="sw"><path d="M215 40 Q300 75 385 40 L515 90 Q560 120 575 200 L598 470 L532 482 L490 250 L482 540 L118 540 L110 250 L68 482 L2 470 L25 200 Q40 120 85 90 Z"/></clipPath>
  <linearGradient id="swS" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient></defs>
  <g clip-path="url(#sw)"><rect width="600" height="560" fill="#b01f28"/><rect y="508" width="600" height="32" fill="#9a1a22"/><path d="M0 452 L66 464 L62 490 L0 480Z M600 452 L534 464 L538 490 L600 480Z" fill="#9a1a22"/>
  <image href="${IMG.sweat}" x="170" y="120" width="260" height="295"/><rect width="600" height="560" fill="url(#swS)"/></g>
  <path d="M215 40 Q300 75 385 40 Q300 105 215 40Z" fill="#8a161d"/></svg>`;
const bodySVG = (w) => `<svg viewBox="0 0 420 470" width="${w}" style="filter:drop-shadow(0 16px 20px rgba(60,40,20,.25))">
  <defs><clipPath id="bd"><path d="M150 20 Q210 55 270 20 L360 60 L410 190 L355 205 L330 150 L330 330 Q330 380 280 410 L262 455 L158 455 L140 410 Q90 380 90 330 L90 150 L65 205 L10 190 L60 60 Z"/></clipPath></defs>
  <g clip-path="url(#bd)"><rect width="420" height="470" fill="#fbfaf7"/><image href="${IMG.body}" x="128" y="90" width="164" height="200"/>
  <rect width="420" height="470" fill="#000" opacity=".03"/></g>
  <path d="M150 20 Q210 55 270 20 Q210 80 150 20Z" fill="#e6e1d8"/><circle cx="185" cy="445" r="4" fill="#ccc"/><circle cx="210" cy="445" r="4" fill="#ccc"/><circle cx="235" cy="445" r="4" fill="#ccc"/></svg>`;
const ph = (src, x, y, s, crop = 1) => `<div class="ph" style="left:${x}px;top:${y}px;width:${s}px;height:${s}px;background-image:url(${src});background-size:${crop * 100}%"></div>`;
function page(W, H, layout, text) { return `<html><head>${FONTS}<style>
  body{margin:0;width:${W}px;height:${H}px;background:#ecebe8;position:relative;overflow:hidden;font-family:Figtree}
  .ph{position:absolute;background-position:center;-webkit-mask-image:radial-gradient(closest-side,#000 72%,transparent 100%)}
  .it{position:absolute}
  .t{position:absolute;left:0;right:0;top:${text.top}px;text-align:center}
  .k{font-size:${text.k}px;letter-spacing:.3em;text-transform:uppercase;color:#8d6748;font-weight:600;margin-bottom:${text.k * .5}px}
  h1{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:${text.t}px;line-height:1;color:#24402f;margin:0}
  h1 em{color:#a3312f} p{font-size:${text.s}px;color:#5f5d57;margin:${text.s * .55}px 0 0}
  </style></head><body>${layout}
  <div class="t"><div class="k">Cadeaux de Noël personnalisés</div><h1>Le souvenir de Noël <em>à votre nom</em></h1><p>Décorations · Mugs · Bébé · Famille — imprimés en Europe</p></div></body></html>`; }
const desktop = page(2400, 1200,
  ph(IMG.medBebe, -40, -40, 700) + `<div class="it" style="left:600px;top:250px;transform:rotate(-5deg)">${sweatSVG(470)}</div>` +
  ph(IMG.mugG, 1010, 220, 600, 1.25) + `<div class="it" style="left:1560px;top:330px;transform:rotate(5deg)">${bodySVG(320)}</div>` +
  ph(IMG.medFam, 1740, -40, 700),
  { top: 940, t: 108, s: 38, k: 26 });
const mobile = page(1200, 1500,
  ph(IMG.medBebe, -80, -150, 640) + ph(IMG.medFam, 640, -150, 640) +
  `<div class="it" style="left:50px;top:420px;transform:rotate(-5deg)">${sweatSVG(430)}</div>` +
  ph(IMG.mugG, 470, 380, 520, 1.25) + `<div class="it" style="left:880px;top:470px;transform:rotate(6deg)">${bodySVG(300)}</div>`,
  { top: 1170, t: 82, s: 32, k: 22 });
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  for (const [n, html, w, h] of [['banniere-gamme-ordinateur', desktop, 2400, 1200], ['banniere-gamme-mobile', mobile, 1200, 1500]]) {
    await p.setViewportSize({ width: w, height: h }); await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    await p.screenshot({ path: D + 'photos-3d/' + n + '.jpg', type: 'jpeg', quality: 90 }); }
  await b.close(); })();
