import sys,re;sys.path.insert(0,'.')
from sections import home_sections
html="".join(v for _,v in home_sections())
loc={"C01B7A47":"mises_en_situation/petit_toutou_salon.png","0525FFD2":"mises_en_situation/avenue_porte.png","57B2D92B":"mises_en_situation/chateau_cuisine.png","33728BC1":"mises_en_situation/noel_cheminee.png","5CCB3C6A":"collection_fr/petit_toutou_v2_photo_presse.png","04579DE4":"collection_fr/avenue_v3_plate.png","2AFE91A5":"collection_fr/chateau_v4_final.png","2610AB4E":"collection_fr/noel_lettre_v1.png"}
def rep(m):
    for k,v in loc.items():
        if k in m.group(0): return "file:///home/user/Claude/designs/"+v
    return m.group(0)
html=re.sub(r'https://cdn\.shopify\.com[^"]+',rep,html)
hdr='<div style="background:#1b2a4a;color:#fff;font:500 13px DM Sans,sans-serif;text-align:center;padding:10px">Livraison offerte · Aperçu avant impression</div><div style="display:flex;justify-content:space-between;padding:14px 18px;font:700 20px Poppins,sans-serif;color:#1b2a4a;background:#f7f0e3">Gâté Pourri<span>☰</span></div>'
open(sys.argv[1],'w').write('<html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"></head><body style="margin:0">'+hdr+html+'</body></html>')
