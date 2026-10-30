import sys
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
d = Image.open(src).convert('RGBA')
white = Image.new('RGBA', d.size, (255,255,255,255)); white.alpha_composite(d); d = white
D = 900
d = d.resize((D, D), Image.LANCZOS)
cw, ch = 1400, 1400
c = Image.new('RGBA', (cw, ch), (236, 231, 222, 255))
ox, oy = (cw - D)//2, 330
sh = Image.new('L', (cw, ch), 0)
ImageDraw.Draw(sh).ellipse([ox+25, oy+45, ox+D+25, oy+D+45], fill=120)
c.paste((160,150,135,255), (0,0), sh.filter(ImageFilter.GaussianBlur(30)))
m = Image.new('L', (D, D), 0); ImageDraw.Draw(m).ellipse([0,0,D-1,D-1], fill=255)
c.paste(d, (ox, oy), m)
dr = ImageDraw.Draw(c)
dr.ellipse([ox, oy, ox+D-1, oy+D-1], outline=(215,208,196,255), width=5)
hx, hy = cw//2, oy+48
dr.rectangle([hx-11, 0, hx+11, hy], fill=(163,49,47,255))
dr.ellipse([hx-20, hy-20, hx+20, hy+20], fill=(236,231,222,255), outline=(200,193,182,255), width=4)
c.convert('RGB').save(out, quality=90)
