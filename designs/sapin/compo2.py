from PIL import Image, ImageFilter, ImageEnhance
import sys
S='/tmp/claude-0/-home-user-Claude/c8fa17df-e4a2-5d0d-a391-7cc709b1d3bc/scratchpad/'
bg=Image.open(__import__('os').environ['BG']).convert('RGB')
K=int(__import__('os').environ.get('K','3')); bg=bg.resize((bg.width*K,bg.height*K),Image.LANCZOS).filter(ImageFilter.GaussianBlur(.6))
def med(name, width, ribbon_px):
    m=Image.open(S+'three/tr-'+name+'.png').convert('RGBA'); bb=m.getbbox(); m=m.crop(bb)
    # garde seulement 'ribbon_px' de ruban au-dessus du disque
    import numpy as np
    al=np.asarray(m.split()[3]); w,h=m.size
    rows=(al>20).sum(1); disc_top=int(np.argmax(rows>w*.5))
    top=max(0,int(disc_top-ribbon_px*w/width))
    m=m.crop((0,top,w,h)); s=width/m.width; m=m.resize((int(m.width*s),int(m.height*s)),Image.LANCZOS)
    rgb=m.convert('RGB'); a=m.split()[3]
    rgb=ImageEnhance.Brightness(rgb).enhance(float(__import__('os').environ.get('BRI','.74'))); rgb=ImageEnhance.Contrast(rgb).enhance(1.0); rgb=ImageEnhance.Color(rgb).enhance(1.05)
    r,g,b=rgb.split(); r=r.point(lambda v:min(255,v*1.06)); b=b.point(lambda v:v*.88); rgb=Image.merge('RGB',(r,g,b))
    import numpy as np
    arr=np.asarray(rgb).astype(float); H,W=arr.shape[:2]
    yy,xx=np.mgrid[0:H,0:W]; grad=1.05-0.12*(xx/W)-0.12*(yy/H)   # lumière chaude venant d'en haut à gauche
    warm=np.stack([grad*1.03,grad*1.0,grad*.95],-1)
    arr=np.clip(arr*warm,0,255).astype('uint8'); rgb=Image.fromarray(arr)
    rgb=rgb.filter(ImageFilter.GaussianBlur(.7)); m=rgb.convert('RGBA'); m.putalpha(a); return m
def put(m,x,y):
    sh=Image.new('RGBA',m.size,(0,0,0,0)); sh.putalpha(m.split()[3].point(lambda v:v*.45)); sh=sh.filter(ImageFilter.GaussianBlur(14))
    bg.paste((10,15,8),(x+10,y+16),sh); bg.paste(m,(x,y),m)
for spec in sys.argv[2:]:
    n,w,r,x,y=spec.split(':'); mm=med(n,int(w),int(r)); put(mm,int(x)-mm.width//2,int(y)-mm.height+mm.width//2)
bg.save(S+sys.argv[1],quality=90)
