// Usage : node shopify/catalogue/generer-catalogue.js index.html shopify/catalogue
// Construit le catalogue Shopify à partir du tableau P0 de index.html.
const fs=require('fs'),vm=require('vm');
const [,,html,outDir]=process.argv;
const t=fs.readFileSync(html,'utf8');
const src=t.match(/const P0=(\[[\s\S]*?\n\]);/)[1];
const P0=vm.runInNewContext('('+src+')');
const RAW='https://raw.githubusercontent.com/nonomarvie1-eng/Claude/claude/shopify-fofana/shopify/images/';
const IM={p1:'plateau-afrique-1-compartiment',p2:'plateau-afrique-2-compartiments',p3:'plateau-afrique-dessus',cm1:'plateau-cote-divoire-moyen-1',cm2:'plateau-cote-divoire-moyen-2',c1:'plateau-cote-divoire-grand-1',c3:'plateau-cote-divoire-grand-2',t1:'talier-pilon-1',t2:'talier-pilon-2',m1:'mortier-bois-1',m2:'mortier-bois-2',mr2:'mortier-sculpte-1',mr1:'mortier-sculpte-2',gm1:'grand-mortier-1',gm2:'grand-mortier-2',gm3:'grand-mortier-3',mm1:'mortier-massif-1',mm2:'mortier-massif-2',mm3:'mortier-massif-3'};
const img=k=>({file:IM[k]+'.jpg',url:RAW+IM[k]+'.jpg'});
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const base=n=>n.replace(/ \(.*\)$/,'');
// Regroupe les fiches « g » (variantes) en un seul produit Shopify.
const groups={};const out=[];
for(const x of P0){
  const variant={sku:x.id,option:x.vk||null,price:x.p.toFixed(2),weight_g:x.w||0,stock:x.s,images:x.gal.map(img)};
  if(x.g){
    if(!groups[x.g]){groups[x.g]={handle:x.id,title:base(x.n),status:'ACTIVE',product_type:x.cat,collection:x.cat,vendor:'La Boutique de Mme Fofana',description_html:'<p>'+esc(x.d)+'</p>',option_name:x.gl,caracteristiques:[],variants:[]};out.push(groups[x.g])}
    groups[x.g].variants.push(Object.assign(variant,{caracteristiques:x.l}));
  }else{
    out.push({handle:x.id,title:x.n,status:x.hide?'DRAFT':'ACTIVE',product_type:x.cat,collection:x.cat,vendor:'La Boutique de Mme Fofana',description_html:'<p>'+esc(x.d)+'</p>',option_name:null,caracteristiques:x.l,variants:[variant]});
  }
}
// Caractéristiques des produits à variantes : communes + ce qui distingue les variantes.
const EXTRA={'plateau-afrique':['Compartiments : 1 ou 2'],'assiette-cote-divoire':['Tailles : moyenne et grande','Dimensions (moyenne) : 26 × 24 cm']};
for(const g of Object.values(groups)){
  const common=g.variants[0].caracteristiques.filter(l=>g.variants.every(v=>v.caracteristiques.includes(l)));
  g.caracteristiques=[...common,...(EXTRA[g.handle]||[])];
  g.variants.forEach(v=>delete v.caracteristiques);
}
fs.writeFileSync(outDir+'/products.json',JSON.stringify(out,null,2)+'\n');
// CSV au format d'import Shopify.
const H=['Handle','Title','Body (HTML)','Vendor','Product Category','Type','Tags','Published','Option1 Name','Option1 Value','Variant SKU','Variant Grams','Variant Inventory Tracker','Variant Inventory Qty','Variant Inventory Policy','Variant Fulfillment Service','Variant Price','Variant Requires Shipping','Variant Taxable','Variant Weight Unit','Image Src','Image Position','Image Alt Text','Variant Image','Status','Caractéristiques (product.metafields.custom.caracteristiques)'];
const q=v=>{v=v==null?'':String(v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v};
const rows=[H];
for(const p of out){
  const imgs=[];p.variants.forEach(v=>v.images.forEach(i=>{if(!imgs.find(a=>a.url===i.url))imgs.push(i)}));
  const n=Math.max(p.variants.length,imgs.length);
  for(let i=0;i<n;i++){
    const v=p.variants[i],im=imgs[i],first=i===0;
    rows.push([p.handle,first?p.title:'',first?p.description_html:'',first?p.vendor:'','',first?p.product_type:'',first?p.collection:'',first?(p.status==='ACTIVE'?'TRUE':'FALSE'):'',first?(p.option_name||'Title'):'',v?(v.option||'Default Title'):'',v?v.sku:'',v?v.weight_g:'',v?'shopify':'',v?v.stock:'',v?'deny':'',v?'manual':'',v?v.price:'',v?'TRUE':'',v?'FALSE':'',v?'g':'',im?im.url:'',im?i+1:'',im?(p.title):'',v?v.images[0].url:'',first?p.status.toLowerCase():'',first?p.caracteristiques.join('\n'):''].map(q));
  }
}
fs.writeFileSync(outDir+'/products.csv',rows.map(r=>r.join(',')).join('\n')+'\n');
for(const p of out)console.log(p.status.padEnd(6),p.handle.padEnd(24),p.variants.map(v=>`${v.option||'-'} ${v.price}€ ${v.weight_g}g stock ${v.stock}`).join(' | '));
