#!/usr/bin/env python3
"""Planches série 2 : comparative, miniatures, téléphone, et comparaison avec la série 1. Usage : python3 04_sources/planches2.py [suffixe]"""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H=os.path.join(R,'05_couvertures_HD/serie2'); P=os.path.join(R,'06_planches/serie2'); os.makedirs(P,exist_ok=True)
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
files=sorted(f for f in glob.glob(H+'/S2-*.png') if 'REPERES' not in f)
lab=[os.path.basename(f)[:4]+' '+os.path.basename(f)[5:-4].replace('_',' ') for f in files]
bl=round(3/25.4*300)
trim=[Image.open(f).convert('RGB').crop((bl,bl,2551-bl,3579-bl)) for f in files]
suf=sys.argv[1] if len(sys.argv)>1 else ''
def sheet(h,gap,fn,cols=6):
    t=[x.resize((round(x.width*h/x.height),h),Image.LANCZOS) for x in trim]; rows=(len(t)+cols-1)//cols
    W=cols*(t[0].width+gap)+gap; S=Image.new('RGB',(W,rows*(h+gap+50)+gap),(236,233,228)); d=ImageDraw.Draw(S)
    for i,(im,l) in enumerate(zip(t,lab)):
        x=gap+(i%cols)*(im.width+gap); y=gap+(i//cols)*(h+gap+50); S.paste(im,(x,y)); d.text((x,y+h+12),l,fill=(48,37,31),font=F(22))
    S.save(os.path.join(P,fn),quality=92)
sheet(1000,50,f'planche_comparative_serie2{suf}.jpg')
# miniatures : 240 / 120 / 64 px de haut
S=Image.new('RGB',(1500,620),'white'); d=ImageDraw.Draw(S); d.text((24,14),'Miniatures : 240 px (fiche produit), 120 px (grille mobile), 64 px (résultat de recherche) — taille réelle',fill=(60,60,60),font=F(18)); x=24
for im,l in zip(trim,lab):
    a=im.resize((round(im.width*240/im.height),240),Image.LANCZOS); b=im.resize((round(im.width*120/im.height),120),Image.LANCZOS); c=im.resize((round(im.width*64/im.height),64),Image.LANCZOS)
    S.paste(a,(x,50)); S.paste(b,(x,310)); S.paste(c,(x+b.width+12,310)); d.text((x,450),l[:4],fill=(40,40,40),font=F(22,True)); x+=a.width+40
S.crop((0,0,x,500)).save(os.path.join(P,f'planche_miniatures_serie2{suf}.png'))
# téléphone
ph=Image.new('RGB',(1170,2532),(250,248,245)); d=ImageDraw.Draw(ph); d.text((45,50),'Simulation boutique mobile (1170 px de large)',fill=(90,90,90),font=F(30,True))
for i,im in enumerate(trim):
    w=520; h=round(im.height*w/im.width); col=i%2; row=i//2
    ph.paste(im.resize((w,h),Image.LANCZOS),(45+col*560,130+row*(h+90))); d.text((45+col*560,130+row*(h+90)+h+12),lab[i][:4]+' · L’Afrique dans mon assiette',fill=(40,40,40),font=F(22))
ph.save(os.path.join(P,f'simulation_telephone_serie2{suf}.jpg'),quality=90)
print('ok',len(trim))
