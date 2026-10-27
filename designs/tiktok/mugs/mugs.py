from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import subprocess, os
W,H=1080,1920; FPS=30; TR=0.45
os.makedirs('f',exist_ok=True)
def sharpen(im): return im.filter(ImageFilter.UnsharpMask(1.0,35,2))
def cover(im, box=None):
    if box: im=im.crop(box)
    s=max(W/im.width,H/im.height); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; return sharpen(im.crop((x,y,x+W,y+H)))
def blurbg(im):
    b=cover(im).filter(ImageFilter.GaussianBlur(35)); return ImageEnhance.Brightness(b).enhance(.6)
def feather(img, f=70):
    m=Image.new('L',img.size,255); d=ImageDraw.Draw(m)
    for k in range(f):
        v=int(255*k/f); d.line([(0,k),(img.width,k)],fill=v); d.line([(0,img.height-1-k),(img.width,img.height-1-k)],fill=v)
    return m
src={i:Image.open(f'clean/{i}.png').convert('RGB') for i in range(1,9)}
frames=[]
# 0. accroche : gros plan sur les 3 mugs + question
c=ImageEnhance.Brightness(cover(src[1]).filter(ImageFilter.GaussianBlur(45))).enhance(.5); mug=src[5].crop((40,540,984,1150)); s=1180/mug.width; mug=sharpen(mug.resize((W,round(mug.height*s)),Image.LANCZOS))
mug=mug.crop((50,0,1130,mug.height)); y=1080-mug.height//2; c.paste(mug,(0,y),feather(mug,60))
d=ImageDraw.Draw(c); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',96)
for j,t in enumerate(["Ton prénom","sur ton mug","de Noël ?"]):
    w=d.textlength(t,font=f); d.text(((W-w)/2,230+j*118),t,font=f,fill='white',stroke_width=9,stroke_fill=(120,20,25))
frames.append((c,1.6,'punch'))
# 1. ambiance : recadré pour sortir l'étiquette du cadre et garder tout le texte
frames.append((cover(src[1],(140,112,940,1536)),2.4,'in'))
for i,d_ in [(2,3.3),(3,3.3),(4,3.3),(5,3.6),(6,3.3),(7,3.3)]:
    if i==5:  # 3 mugs : on garde les 3 en entier
        c=blurbg(src[5]); im=src[5]; s=1180/im.width; im=im.resize((1180,round(im.height*s)),Image.LANCZOS).crop((50,0,1130,round(1536*1180/1024)))
        c.paste(sharpen(im),(0,(H-im.height)//2),feather(im,50)); frames.append((c,d_,'in'))
    else: frames.append((cover(src[i]),d_,'in' if i%2 else 'out'))
# 8. fin (image horizontale)
im=src[8]; s=1.18; im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS); cx=round(725*s); im=im.crop((cx-540,0,cx+540,im.height))
c=blurbg(src[8]); c.paste(sharpen(im),(0,(H-im.height)//2),feather(im,90)); frames.append((c,3.6,'in'))
args=['ffmpeg','-y']; fc=[]
for n,(img,dur,mode) in enumerate(frames):
    p=f'f/s{n}.png'; img.save(p); args+=['-i',p]; N=int((dur+TR)*FPS)
    z={'punch':"if(lt(on,10),1.18-0.16*on/10,1.02+0.03*(on-10)/%d)"%N,'in':f"1+0.045*on/{N}",'out':f"1.045-0.045*on/{N}"}[mode]
    fc.append(f"[{n}:v]scale=3240:5760:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p[v{n}]")
prev='v0'; off=frames[0][1]
for n in range(1,len(frames)):
    tr='fade' if n>1 else 'fadeblack'
    fc.append(f"[{prev}][v{n}]xfade=transition={tr}:duration={TR}:offset={off-TR/2:.2f}[x{n}]"); prev=f'x{n}'; off+=frames[n][1]
total=sum(f[1] for f in frames)
fc.append(f"[{prev}]fade=t=out:st={total-0.7:.2f}:d=0.7[out]")
args+=['-filter_complex',';'.join(fc),'-map','[out]','-t',f'{total:.2f}','-r',str(FPS),'-c:v','libx264','-preset','slow','-profile:v','high','-level','4.2','-pix_fmt','yuv420p','-crf','14','-movflags','+faststart','sapin-et-lin-mugs.mp4']
r=subprocess.run(args,capture_output=True,text=True); print(r.returncode, r.stderr[-1200:] if r.returncode else 'ok', total)
