from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import subprocess, os, math
CAV='/home/user/Claude/designs/polices/Caveat-600.woff'
cav=lambda s: ImageFont.truetype(CAV,s)
W,H=1080,1920
os.makedirs('hdf',exist_ok=True)
# (fichier, durée, centre horizontal du recadrage, textes)
S=[
 (1,2.4,1.0,None),
 (2,2.2,0.5,dict(lines=["Personnalisez","avec vos prénoms,","une date, un message…"],x=690,y=1420,size=86,rot=6,arrow=True)),
 (3,2.2,0.5,dict(lines=["Des designs","doux et élégants"],x=720,y=1500,size=94,rot=6,heart=True)),
 (4,2.2,0.5,None),
 (5,2.2,0.5,dict(lines=["Des médaillons","de qualité"],x=730,y=1510,size=94,rot=6,heart=True)),
 (6,2.8,0.5,dict(lines=["Le cadeau parfait","pour toute la famille"],x=700,y=1540,size=90,rot=6,heart=True)),
 (7,2.8,0.5,dict(icons=True)),
 (8,2.8,0.5,dict(lines=["Personnalisez","votre médaillon de Noël"],x=540,y=1500,size=108,rot=4,heart=True,flourish=True)),
 (9,3.2,0.5,None),
]
def cover(im,cx):
    s=H/im.height; im=im.resize((round(im.width*s),H),Image.LANCZOS)
    off=round((im.width-W)*cx); return im.crop((off,0,off+W,H)).filter(ImageFilter.UnsharpMask(1.0,35,2))
def heart(d,x,y,s,w=5,fill=None):
    pts=[]
    for k in range(100):
        t=2*math.pi*k/100
        pts.append((x+s*16*math.sin(t)**3/17, y-s*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/17))
    d.line(pts+[pts[0]],fill='white',width=w,joint='curve') if not fill else d.polygon(pts,fill=fill)
def textlayer(spec):
    L=Image.new('RGBA',(W,H),(0,0,0,0))
    if spec.get('icons'):
        d=ImageDraw.Draw(L); f=cav(66); cols=[(200,'Cadeau','unique'),(540,'Décoration','élégante'),(880,'Souvenir','pour toujours')]
        y0=1555
        heart(d,200,y0+40,46,6)
        d.polygon([(540,y0),(500,y0+50),(520,y0+50),(490,y0+90),(590,y0+90),(560,y0+50),(580,y0+50)],outline='white',width=6); d.line([(540,y0+90),(540,y0+110)],fill='white',width=6)
        d.rectangle([840,y0+35,920,y0+105],outline='white',width=6); d.rectangle([832,y0+20,928,y0+40],outline='white',width=6); d.line([(880,y0+20),(880,y0+105)],fill='white',width=6)
        d.arc([846,y0-8,880,y0+24],200,20,fill='white',width=6); d.arc([880,y0-8,914,y0+24],160,340,fill='white',width=6)
        for x,a,b in cols:
            for j,t in enumerate((a,b)):
                w=d.textlength(t,font=f); d.text((x-w/2,y0+130+j*62),t,font=f,fill='white')
    else:
        T=Image.new('RGBA',(W,700),(0,0,0,0)); d=ImageDraw.Draw(T); f=cav(spec['size']); lh=int(spec['size']*1.05)
        cx=W//2
        for j,t in enumerate(spec['lines']):
            w=d.textlength(t,font=f); d.text((cx-w/2,20+j*lh),t,font=f,fill='white')
        yb=20+len(spec['lines'])*lh+20
        if spec.get('flourish'):
            d.line([(cx-230,yb+25),(cx-60,yb+18)],fill='white',width=6); d.line([(cx+60,yb+18),(cx+230,yb+25)],fill='white',width=6)
        if spec.get('heart'): heart(d,cx,yb+30,40,6)
        T=T.rotate(spec['rot'],resample=Image.BICUBIC,center=(cx,200))
        L.alpha_composite(T,(spec['x']-cx,spec['y']-20))
        if spec.get('arrow'):
            A=ImageDraw.Draw(L); pts=[(spec['x']-130+int(60*math.cos(t/20*math.pi/1.6)), spec['y']-30-int(150*t/20)) for t in range(21)]
            pts=[]; 
            for k in range(30):
                t=k/29; x=spec['x']-40-160*t+40*math.sin(t*math.pi); y=spec['y']-20-170*t
                pts.append((x,y))
            A.line(pts,fill='white',width=7,joint='curve'); ex,ey=pts[-1]; A.line([(ex,ey),(ex+38,ey+10)],fill='white',width=7); A.line([(ex,ey),(ex+8,ey+38)],fill='white',width=7)
    # ombre douce pour la lisibilité
    a=L.split()[3]; sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v:min(255,int(v*1.1))))
    sh2=Image.new('RGBA',(W,H),(20,10,5,0)); sh2.putalpha(sh.split()[3].point(lambda v:int(v*.75)))
    out=Image.new('RGBA',(W,H),(0,0,0,0)); out.alpha_composite(sh2,(3,5)); out.alpha_composite(L); return out
FPS=30; TR=0.5
args=['ffmpeg','-y']; fc=[]; idx=0; vids=[]
for n,(k,dur,cx,spec) in enumerate(S):
    base=cover(Image.open(f'hd/{k}.png').convert('RGB'),cx); bp=f'hdf/b{k}.png'; base.save(bp)
    N=int((dur+TR)*FPS); args+=['-i',bp]; bi=idx; idx+=1
    z=f"1+0.045*on/{N}" if n%2==0 else f"1.045-0.045*on/{N}"
    fc.append(f"[{bi}:v]scale=3240:5760:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s={W}x{H}:fps={FPS},setsar=1[b{n}]")
    if spec:
        tp=f'hdf/t{k}.png'; textlayer(spec).save(tp); args+=['-loop','1','-framerate',str(FPS),'-t',f'{dur+TR:.2f}','-i',tp]; ti=idx; idx+=1
        fc.append(f"[{ti}:v]format=rgba,fade=t=in:st=0.35:d=0.45:alpha=1[t{n}]")
        fc.append(f"[b{n}][t{n}]overlay=0:0:shortest=1,format=yuv420p[v{n}]")
    else:
        fc.append(f"[b{n}]format=yuv420p[v{n}]")
prev='v0'; off=S[0][1]
for n in range(1,len(S)):
    fc.append(f"[{prev}][v{n}]xfade=transition=fade:duration={TR}:offset={off-TR/2:.2f}[x{n}]"); prev=f'x{n}'; off+=S[n][1]
total=sum(s[1] for s in S)
fc.append(f"[{prev}]fade=t=out:st={total-0.7:.2f}:d=0.7[out]")
args+=['-filter_complex',';'.join(fc),'-map','[out]','-t',f'{total:.2f}','-r',str(FPS),'-c:v','libx264','-preset','slow','-profile:v','high','-level','4.2','-pix_fmt','yuv420p','-crf','14','-movflags','+faststart','sapin-et-lin-pub-hd.mp4']
r=subprocess.run(args,capture_output=True,text=True); print(r.returncode, r.stderr[-1500:] if r.returncode else 'ok')
