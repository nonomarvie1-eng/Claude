from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import subprocess, os
src=Image.open('planche.png').convert('RGB')
X=[(0,397),(405,809),(817,1214)]; Y=[(0,433),(441,838),(846,1295)]
DUR=[2,2,2,2,2,3,3,3,3]
os.makedirs('f',exist_ok=True)
paths=[]
for r in range(3):
    for c in range(3):
        i=r*3+c; x0,x1=X[c]; y0,y1=Y[r]
        p=src.crop((x0,y0,x1,y1))
        # effacer l'étiquette de temps (coin haut gauche) avec le fond voisin flouté
        p=p.crop((0,46,p.width,p.height))
        # agrandissement en 2 étapes + netteté
        W=1080; H=round(p.height*W/p.width)
        big=p.resize((p.width*2,p.height*2),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2,60,2))
        big=big.resize((W,H),Image.LANCZOS).filter(ImageFilter.UnsharpMask(2.0,70,3))
        # fond vertical : même image, agrandie et floutée
        bg=p.resize((round(p.width*1920/p.height),1920),Image.LANCZOS)
        bx=(bg.width-1080)//2; bg=bg.crop((bx,0,bx+1080,1920)).filter(ImageFilter.GaussianBlur(40))
        bg=ImageEnhance.Brightness(bg).enhance(.55)
        canvas=bg.copy(); yy=(1920-H)//2
        # fondu doux haut/bas de l'image centrale
        mask=Image.new('L',(W,H),255); d=ImageDraw.Draw(mask)
        for k in range(60): 
            v=int(255*k/60); d.line([(0,k),(W,k)],fill=v); d.line([(0,H-1-k),(W,H-1-k)],fill=v)
        canvas.paste(big,(0,yy),mask)
        fp=f'f/p{i}.png'; canvas.save(fp); paths.append(fp)
FPS=30; T=0.45
args=['ffmpeg','-y']
for p in paths: args+=['-i',p]
fc=[]
for i,p in enumerate(paths):
    N=int((DUR[i]+T)*FPS)
    zin = i%2==0
    z = f"1+0.05*on/{N}" if zin else f"1.05-0.05*on/{N}"
    fc.append(f"[{i}:v]scale=4320:7680:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]")
prev='v0'; off=DUR[0]
for i in range(1,len(paths)):
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={T}:offset={off-T/2:.2f}[x{i}]"); prev=f'x{i}'; off+=DUR[i]
fc.append(f"[{prev}]fade=t=out:st={sum(DUR)-0.6}:d=0.6[out]")
args+=['-filter_complex',';'.join(fc),'-map','[out]','-t',str(sum(DUR)),'-r',str(FPS),'-c:v','libx264','-preset','slow','-profile:v','high','-pix_fmt','yuv420p','-crf','14','-movflags','+faststart','sapin-et-lin-pub.mp4']
subprocess.run(args,check=True,capture_output=True); print('ok')
