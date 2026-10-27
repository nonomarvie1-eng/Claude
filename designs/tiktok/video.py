# usage: python3 video.py sortie.mp4 slides.json
from PIL import Image, ImageDraw, ImageFont, ImageOps
import subprocess, json, sys, os
F='/home/user/Claude/designs/polices/'
BG=(238,237,235); G=(31,61,44)
sans=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
cinzel=lambda s: ImageFont.truetype(F+'Cinzel.ttf', s)
script=lambda s: ImageFont.truetype(F+'PinyonScript.ttf', s)
out_mp4, spec = sys.argv[1], json.load(open(sys.argv[2]))
tmp='frames-'+os.path.splitext(os.path.basename(out_mp4))[0]; os.makedirs(tmp, exist_ok=True)
def caption(d, lines, y0, size=78):
    f=sans(size)
    for i,t in enumerate(lines):
        w=d.textlength(t,font=f); d.text(((1080-w)/2,y0+i*int(size*1.23)),t,font=f,fill='white',stroke_width=10,stroke_fill=G)
paths=[]
for i,s in enumerate(spec['slides']):
    if s.get('end'):
        c=Image.new('RGB',(1080,1920),G); d=ImageDraw.Draw(c)
        logo=Image.open('/home/user/Claude/designs/logo/favicon.png').convert('RGBA').resize((300,300)); c.paste(logo,(390,420),logo)
        def ctr(t,f,y,fill):
            w=d.textlength(t,font=f); d.text(((1080-w)/2,y),t,font=f,fill=fill)
        ctr('SAPIN & LIN',cinzel(96),800,(245,239,228)); ctr(s.get('script','Personnalisé au prénom'),script(104),950,(217,178,95))
        for j,t in enumerate(s.get('lines',['Imprimé en Europe','Livré avant Noël'])): ctr(t,sans(48),1160+j*70,(245,239,228))
        ctr('Lien dans la bio',sans(62),1420,'white')
    else:
        im=Image.open(s['img']).convert('RGB')
        if s.get('cover'):
            c=ImageOps.fit(im,(1080,1920),Image.LANCZOS,centering=tuple(s.get('center',[.5,.5])))
        else:
            c=Image.new('RGB',(1080,1920),tuple(s.get('bg',BG))); c.paste(im.resize((1080,1080),Image.LANCZOS),(0,520))
        d=ImageDraw.Draw(c); caption(d,s['text'],s.get('y',220),s.get('size',78))
    p=f'{tmp}/s{i}.png'; c.save(p); paths.append(p)
D=spec.get('dur',2.3); FPS=30; T=0.4
args=['ffmpeg','-y']
for p in paths: args+=['-i',p]
fc=[]
for i in range(len(paths)):
    fc.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(D*FPS)}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]")
prev='v0'; off=D-T
for i in range(1,len(paths)):
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={T}:offset={off:.2f}[x{i}]"); prev=f'x{i}'; off+=D-T
args+=['-filter_complex',';'.join(fc),'-map',f'[{prev}]','-r',str(FPS),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out_mp4]
subprocess.run(args,check=True,capture_output=True); print('ok', out_mp4)
