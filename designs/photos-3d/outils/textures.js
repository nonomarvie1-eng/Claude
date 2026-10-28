// rend les designs (avec différents prénoms) en PNG pour les textures 3D
const { chromium } = require('playwright'); const fs = require('fs'), vm = require('vm');
const SRC = fs.readFileSync(__dirname + '/../premium.js', 'utf8');
const lib = SRC.slice(SRC.indexOf('let seed'), SRC.indexOf('// mise en situation'));
const ctx = { Math }; vm.createContext(ctx);
vm.runInContext(lib + ';this.L={DEFS,DESIGNS};', ctx);
const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Cinzel:wght@500;600;700&display=swap" rel="stylesheet">`;
const SET = { 'prenom-couronne': ['Emma', 'Lucas', 'Chloé'], 'premier-noel-bebe': ['Emma', 'Jules', 'Léna'], 'notre-premier-noel': ['Léa & Tom', 'Sarah & Hugo', 'Inès & Max'], 'famille': ['Martin', 'Dubois', 'Bernard'] };
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2048, height: 2048 } });
  for (const [k, names] of Object.entries(SET)) for (let i = 0; i < names.length; i++) {
    await p.setContent(`<html><head>${FONTS}<style>html,body{margin:0}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="2048" height="2048">${ctx.L.DEFS}${ctx.L.DESIGNS[k].f(names[i])}</svg></body></html>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.locator('svg').screenshot({ path: `${__dirname}/tex/${k}-${i}.png` });
  } await b.close(); })();
