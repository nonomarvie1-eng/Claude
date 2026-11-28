#!/usr/bin/env python3
"""Série 2 : agrandissements Lanczos des détourages (alpha prémultiplié, pour éviter tout liseré)
et des photos pleines. Aucune génération : interpolation mathématique + accentuation douce."""
import os, numpy as np
from PIL import Image, ImageFilter
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D=os.path.join(R,'03_photos_retouchees/serie2')
def up_rgba(src,s,dst):
    im=Image.open(src).convert('RGBA'); a=np.asarray(im,float)/255
    pm=np.dstack([a[...,:3]*a[...,3:],a[...,3:]])
    W,H=round(im.width*s),round(im.height*s)
    ch=[np.asarray(Image.fromarray((pm[...,i]*65535).astype(np.uint16)).resize((W,H),Image.LANCZOS) if False else Image.fromarray(pm[...,i].astype(np.float32),'F').resize((W,H),Image.LANCZOS)) for i in range(4)]
    al=np.clip(ch[3],0,1); rgb=np.dstack([np.clip(ch[i],0,None) for i in range(3)])/np.maximum(al,1e-4)[...,None]
    rgb=np.clip(rgb,0,1)
    out=Image.fromarray((np.dstack([rgb,al])*255+.5).astype(np.uint8),'RGBA')
    r,g,b,A=out.split(); rgbim=Image.merge('RGB',(r,g,b)).filter(ImageFilter.UnsharpMask(1.4,35,3))
    rgbim.putalpha(A); rgbim.save(dst); print(os.path.basename(dst),rgbim.size)
def up_rgb(src,s,dst):
    im=Image.open(src).convert('RGB'); o=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4,35,3)); o.save(dst); print(os.path.basename(dst),o.size)
for k in ['P1','P7','P8']: up_rgba(f'{D}/{k}_detoure_1x.png',2.6,f'{D}/{k}_detoure_x2.60.png')
up_rgb(f'{D}/P8_portrait_sourire__retouche_1x.png',3.03,f'{D}/P8_portrait_sourire__retouche_x3.03.png')
up_rgb(os.path.join(R,'03_photos_retouchees/P1_portrait_cuisine_foutou__retouche_1x.png'),2.84,f'{D}/P1_retouche_x2.84.png')
up_rgba(os.path.join(R,'03_photos_retouchees/P6_plat_poulet_yassa_thiere__assiette_detouree_x1.92.png'),1.3,f'{D}/P6_assiette_detouree_x2.50.png')
