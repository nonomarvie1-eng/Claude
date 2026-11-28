// Rendu des maquettes : chaque maquette x 3 polices -> PNG 300 dpi (2551 x 3579). Usage : node render_maquettes.js [A1 A2 B1]
const { chromium } = require('playwright'); const path=require('path'), fs=require('fs');
const DIR=path.join(__dirname,'maquettes'), OUT=path.resolve(__dirname,'../05_couvertures_HD/maquettes');
const sel=process.argv.slice(2); const fonts=['bodoni','playfair','cormorant'];
const files=fs.readdirSync(DIR).filter(f=>/^(A1|A2|B1)_.*\.html$/.test(f)).filter(f=>!sel.length||sel.includes(f.slice(0,2)));
(async()=>{ const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:817,height:1146},deviceScaleFactor:3.125});
 for(const f of files) for(const ft of fonts){ const p=await ctx.newPage();
   await p.goto('file://'+path.join(DIR,f)+'?f='+ft); await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
   const bad=await p.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family)); if(bad.length) console.log('FONT ERR',bad);
   await (await p.$('.cover')).screenshot({path:path.join(OUT,f.slice(0,2)+'_'+ft+'.png')}); console.log('ok',f.slice(0,2),ft); await p.close(); }
 await b.close(); })();
