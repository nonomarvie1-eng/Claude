#!/usr/bin/env python3
"""Photos PROVISOIRES des maquettes de préproduction (non commercialisables).
Visage, corps et aliments : pixels d'origine, corrections globales seulement.
Opérations de décor (signalées sur les maquettes) :
  A1 : prolongement du plafond au-dessus de la tête (miroir flou des lignes supérieures réelles), pour simuler
       l'air que la photo définitive aura naturellement. Aucune génération.
  B1 : « brûlage » local (assombrissement en lumière linéaire) du set en vannerie hors de l'assiette, masque
       elliptique protégeant l'assiette ; même prolongement miroir en haut.
"""
import os, sys, numpy as np, cv2
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retouche
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); O=os.path.join(R,'03_photos_retouchees/maquettes')
A4=303/216
def lin(a): return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def srgb(a): a=np.clip(a,0,1); return np.where(a<=.0031308,a*12.92,1.055*a**(1/2.4)-.055)
def extend_top(img,E,feather=40,blur=10,dark=.85,src_rows=None):
    """Ajoute E lignes en haut : miroir « aller-retour » des src_rows premières lignes réelles (décor seulement),
    flouté et légèrement assombri."""
    a=np.asarray(img,np.float32)/255; h,w,_=a.shape; S=src_rows or E
    idx=[]; k=0
    while len(idx)<E:
        seq=list(range(S)) if k%2==0 else list(range(S-1,-1,-1)); idx+=seq; k+=1
    m=a[idx[:E]][::-1].copy(); m=cv2.GaussianBlur(m,(0,0),blur)*dark
    g=np.linspace(.75,1,E)[:,None,None]; m=m*g        # léger dégradé vers le haut
    out=np.concatenate([m,a],0)
    # fondu à la jonction sur 'feather' lignes (côté réel : plafond/fond uniquement)
    f=np.linspace(0,1,feather)[:,None,None]
    blend=cv2.GaussianBlur(a[:feather],(0,0),blur)*dark
    out[E:E+feather]=blend*(1-f)+a[:feather]*f
    # grain identique à la photo pour éviter un aplat lisse
    noise=np.random.default_rng(7).normal(0,.012,(E+feather,w,1)).astype(np.float32)
    out[:E+feather]+=noise
    return Image.fromarray((np.clip(out,0,1)*255+.5).astype(np.uint8))
def up(img,s,fn):
    o=img.resize((round(img.width*s),round(img.height*s)),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4,35,3)); o.save(os.path.join(O,fn)); print(fn,o.size)
# ---- A1 : P1 (cuisine, foutou) ; extension 150 px, lignes réelles 0..1113
p1=Image.open(os.path.join(R,'03_photos_retouchees/P1_portrait_cuisine_foutou__retouche_1x.png')).convert('RGB')
H=round(900*A4); E=112
a1=extend_top(p1,E).crop((0,0,900,H)); up(a1,2.84,'A1_P1_extension_haut.png')
# ---- A2 : P2 (plateau généreux) ; retouche globale + recadrage
p2,g=retouche.retouch(Image.open(os.path.join(R,'00_originaux/P2_portrait_riz_sauce_gombo.jpg')),.30,1.03,1.04,.95)
y0=20; a2=p2.crop((0,y0,900,y0+H)); up(a2,2.84,'A2_P2_recadre.png')
# ---- B1 : P6 ; brûlage hors assiette + extension haute
p6=Image.open(os.path.join(R,'03_photos_retouchees/P6_plat_poulet_yassa_thiere__retouche_1x.png')).convert('RGB')
m,ell=retouche.plate_alpha(os.path.join(R,'00_originaux/P6_plat_poulet_yassa_thiere.png'))
m=cv2.GaussianBlur((m>.5).astype(np.float32),(0,0),5)            # transition douce, à l'extérieur du bord
m=np.maximum(m,(retouche.plate_alpha(os.path.join(R,'00_originaux/P6_plat_poulet_yassa_thiere.png'))[0]>.5))  # assiette = 1 strict
a=np.asarray(p6,np.float32)/255; L=lin(a)
lum=(L*[.2126,.7152,.0722]).sum(2,keepdims=True); L2=lum+(L-lum)*.75          # désaturation douce du décor
burn=(L2*.075)                                                                # ≈ -3,7 IL
out=srgb(L*m[...,None]+burn*(1-m[...,None]))
p6b=Image.fromarray((out*255+.5).astype(np.uint8))
W=1086; HB=round(W*A4); EB=300
b1=extend_top(p6b,EB,blur=8,dark=1.0,src_rows=170).crop((0,0,W,HB)); up(b1,2.35,'B1_P6_brule_extension.png')
np.save(os.path.join(O,'B1_masque_assiette.npy'),m)
print('ellipse',ell)
# ---- B1 (suite) : décalage de 126 px vers la droite (assiette coupée à droite, comme S2-5) ;
#      bande gauche = prolongement du bord gauche du set assombri (moyenne par ligne, floutée, grain).
b=np.asarray(Image.open(os.path.join(O,'B1_P6_brule_extension.png')).resize((W,HB),Image.LANCZOS),np.float32)/255
SH=126; edge=b[:, :24].mean(1,keepdims=True); edge=cv2.GaussianBlur(edge,(0,0),9)
ext=np.repeat(edge,SH,1)*np.linspace(.85,1,SH)[None,:,None]
ext+=np.random.default_rng(3).normal(0,.012,ext.shape).astype(np.float32)
nb=np.concatenate([ext,b[:, :W-SH]],1)
f=np.linspace(0,1,110)[None,:,None]**1.5; nb[:,SH:SH+110]=ext[:, -1:]*(1-f)+b[:, :110]*f
up(Image.fromarray((np.clip(nb,0,1)*255+.5).astype(np.uint8)),2.35,'B1_P6_brule_extension_decale.png')
