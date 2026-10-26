const { chromium } = require('playwright'); const fs = require('fs');
const D = '/home/user/Claude/designs/photos-3d/';
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,600&family=Figtree:wght@500;600&display=swap" rel="stylesheet">`;
const jobs = [
  { src: 'banniere-ordinateur-haute.jpg', out: 'banniere-ordinateur-texte.jpg', w: 2400, h: 1620, top: 1290, t: 110, s: 40, k: 27 },
  { src: 'banniere-mobile.jpg', out: 'banniere-mobile-texte.jpg', w: 1200, h: 1500, top: 1090, t: 82, s: 34, k: 23 }
];
(async () => { const b = await chromium.launch();
  for (const j of jobs) { const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
    const img = 'data:image/jpeg;base64,' + fs.readFileSync(D + j.src).toString('base64');
    await p.setContent(`<html><head>${FONTS}<style>
      body{margin:0;width:${j.w}px;height:${j.h}px;background:url(${img}) top center/100% auto no-repeat #efede9;position:relative;font-family:Figtree,sans-serif}
      .t{position:absolute;left:0;right:0;top:${j.top}px;transform:translateY(-50%);text-align:center}
      .k{font-size:${j.k}px;letter-spacing:.32em;text-transform:uppercase;color:#8d6748;font-weight:600;margin-bottom:${j.k * .6}px}
      h1{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:${j.t}px;line-height:1;color:#24402f;margin:0}
      h1 em{color:#a3312f}
      p{font-size:${j.s}px;color:#5f5d57;margin:${j.s * .6}px 0 0}
    </style></head><body><div class="t"><div class="k">Médaillons de Noël personnalisés</div><h1>Le souvenir de Noël <em>à votre nom</em></h1><p>Céramique · imprimé en Europe · dès 12,90 €</p></div></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    await p.screenshot({ path: D + j.out, type: 'jpeg', quality: 90 }); await p.close(); }
  await b.close(); })();
