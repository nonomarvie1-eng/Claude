from PIL import Image, ImageDraw, ImageFont
import subprocess, os
P='/home/user/Claude/designs/photos-3d/'
F='/home/user/Claude/designs/polices/'
BG=(238,237,235); G=(31,61,44); RED=(163,49,47); GOLD=(184,137,58)
sans=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
cinzel=lambda s: ImageFont.truetype(F+'Cinzel.ttf', s)
script=lambda s: ImageFont.truetype(F+'PinyonScript.ttf', s)
slides=[
 (P+'prenom-couronne/1-face.jpg',  ["Le cadeau de Noël","qu'ils garderont","toute leur vie"]),
 (P+'prenom-couronne/6-prenoms.jpg',["Avec SON prénom"]),
 (P+'premier-noel-bebe/1-face.jpg',["Son tout","premier Noël"]),
 (P+'notre-premier-noel/1-face.jpg',["Votre premier","Noël à deux"]),
 (P+'famille/1-face.jpg',          ["Pour toute","la famille"]),
 (P+'medaillon-animal/1-face.jpg', ["Et même","pour le chien"]),
]
def caption(d, lines, y0):
    f=sans(78)
    for i,t in enumerate(lines):
        w=d.textlength(t,font=f); x=(1080-w)/2; y=y0+i*96
        d.text((x,y),t,font=f,fill='white',stroke_width=10,stroke_fill=G)
out=[]
for i,(img,lines) in enumerate(slides):
    c=Image.new('RGB',(1080,1920),BG)
    im=Image.open(img).convert('RGB').resize((1080,1080))
    c.paste(im,(0,520))
    d=ImageDraw.Draw(c)
    caption(d,lines,190 if len(lines)>2 else 250)
    p=f'frames/s{i}.png'; c.save(p); out.append(p)
# end card
c=Image.new('RGB',(1080,1920),G); d=ImageDraw.Draw(c)
logo=Image.open('/home/user/Claude/designs/logo/favicon.png').convert('RGBA').resize((300,300)); c.paste(logo,(390,420),logo)
def ctr(t,f,y,fill):
    w=d.textlength(t,font=f); d.text(((1080-w)/2,y),t,font=f,fill=fill)
ctr('SAPIN & LIN',cinzel(96),800,(245,239,228))
ctr('Personnalisé au prénom',script(110),950,(217,178,95))
ctr('Imprimé en Europe',sans(48),1160,(245,239,228))
ctr('Livré avant Noël',sans(48),1230,(245,239,228))
ctr('Lien dans la bio',sans(62),1420,'white')
c.save('frames/s6.png'); out.append('frames/s6.png')
# video: each slide 2.3s with slow zoom, crossfades 0.4s
D=2.3; FPS=30; T=0.4
args=['ffmpeg','-y']
for p in out: args+=['-i',p]
fc=[]
for i in range(len(out)):
    fc.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(D*FPS)}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]")
prev='v0'; off=D-T
for i in range(1,len(out)):
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={T}:offset={off:.2f}[x{i}]"); prev=f'x{i}'; off+=D-T
args+=['-filter_complex',';'.join(fc),'-map',f'[{prev}]','-r',str(FPS),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart','sapin-et-lin-tiktok.mp4']
subprocess.run(args,check=True,capture_output=True)
print('ok')
