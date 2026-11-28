#!/usr/bin/env python3
"""Planches : comparative, miniatures (vitrine en ligne / téléphone), contrôle. Usage : python3 04_sources/planches.py [sortie_suffixe]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H=os.path.join(R,'05_couvertures_HD'); P=os.path.join(R,'06_planches')
os.makedirs(P,exist_ok=True)
names=[('A_portrait_autrice','A — Portrait d’autrice'),('B_transmission','B — Transmission'),('C_gastronomie','C — Gastronomie africaine'),('D_afrique_contemporaine','D — Afrique contemporaine'),('E_edition_prestige','E — Édition de prestige')]
font=lambda s,b=False: ImageFont.truetype(os.path.join(R,'04_sources/polices',[f for f in os.listdir(os.path.join(R,'04_sources/polices')) if f.startswith('mem8YaGs126MiZpBA')][0]) if False else '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
ims=[Image.open(os.path.join(H,n+'.png')).convert('RGB') for n,_ in names]
# Trim (sans fond perdu) : 3 mm = 35.4 px
trim=[im.crop((35,35,im.width-35,im.height-35)) for im in ims]
def sheet(h,gap,fn,label=True,bg=(236,233,228)):
    t=[x.resize((round(x.width*h/x.height),h),Image.LANCZOS) for x in trim]
    W=sum(x.width for x in t)+gap*(len(t)+1); Hh=h+gap*2+(60 if label else 0)
    S=Image.new('RGB',(W,Hh),bg); d=ImageDraw.Draw(S); x=gap
    for im,(n,l) in zip(t,names):
        S.paste(im,(x,gap))
        if label: d.text((x,gap+h+18),l,fill=(48,37,31),font=font(24))
        x+=im.width+gap
    S.save(os.path.join(P,fn),quality=92); return S
suf=sys.argv[1] if len(sys.argv)>1 else ''
sheet(1100,60,f'planche_comparative{suf}.jpg')
# Miniatures : 160 px de haut (vignette librairie en ligne), 90 px (liste mobile)
t160=[x.resize((round(x.width*240/x.height),240),Image.LANCZOS) for x in trim]
t90=[x.resize((round(x.width*90/x.height),90),Image.LANCZOS) for x in trim]
t60=[x.resize((round(x.width*60/x.height),60),Image.LANCZOS) for x in trim]
W=60+sum(x.width+40 for x in t160); S=Image.new('RGB',(W,560),(255,255,255)); d=ImageDraw.Draw(S)
d.text((30,14),'Miniatures à taille réelle d’écran : 240 px (fiche produit), 90 px (liste mobile), 60 px (résultat de recherche)',fill=(60,60,60),font=font(18))
x=30
for a,b,c,(n,l) in zip(t160,t90,t60,names):
    S.paste(a,(x,50)); S.paste(b,(x,310)); S.paste(c,(x+b.width+16,310)); d.text((x,420),l.split(' — ')[0],fill=(60,60,60),font=font(22,True)); x+=a.width+40
# Version gris (contraste en N&B / liseuse)
x=30
for a in t90:
    S.paste(a.convert('L').convert('RGB'),(x,460)) if False else None
S.save(os.path.join(P,f'planche_miniatures{suf}.png'))
# Mise en situation téléphone : fiche produit 390 pt de large
ph=Image.new('RGB',(1170,2532),(250,248,245)); d=ImageDraw.Draw(ph)
for i,im in enumerate(trim):
    w=330; h=round(im.height*w/im.width); col=i%3; row=i//3
    ph.paste(im.resize((w,h),Image.LANCZOS),(45+col*375,140+row*(h+120)))
    d.text((45+col*375,140+row*(h+120)+h+14),names[i][1].split(' — ')[0]+' · L’Afrique dans mon assiette',fill=(40,40,40),font=font(22))
d.text((45,50),'Simulation boutique mobile (iPhone, 1170 px de large)',fill=(90,90,90),font=font(30,True))
ph.save(os.path.join(P,f'simulation_telephone{suf}.jpg'),quality=90)
print('ok')
