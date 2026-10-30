import sys, math
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
d = Image.open(src).convert('RGBA')
W, H = d.size
white = Image.new('RGBA', d.size, (255, 255, 255, 255)); white.alpha_composite(d); d = white
# cylindre : on voit la moitie avant du mug, centree sur la face gauche du motif
R = int(25.8 / 20.4 * W / (2 * math.pi))      # rayon en pixels source
cx = int(W * 0.25)
bw = 2 * R
body = Image.new('RGB', (bw, H))
px, bp = d.load(), body.load()
for x in range(bw):
    u = (x - R + 0.5) / R
    a = math.asin(max(-1, min(1, u)))
    sx = int(cx + a * R) % W
    shade = 0.80 + 0.20 * math.cos(a) ** 0.6       # bords plus sombres
    hl = max(0, 1 - abs(u + 0.45) / 0.10) * 0.10      # reflet
    for y in range(H):
        r, g, b, _ = px[sx, y]
        bp[x, y] = tuple(min(255, int(c * shade + 255 * hl)) for c in (r, g, b))
s = 0.62
body = body.resize((int(bw * s), int(H * s)))
cw, ch = 1500, 1150
canvas = Image.new('RGB', (cw, ch), (238, 233, 224))
bx, by = 330, 230
# ombre portee
sh = Image.new('L', (cw, ch), 0)
ImageDraw.Draw(sh).ellipse([bx - 20, by + body.height - 30, bx + body.width + 120, by + body.height + 45], fill=110)
canvas.paste((150, 140, 125), (0, 0), sh.filter(ImageFilter.GaussianBlur(25)))
# anse a droite
hd = ImageDraw.Draw(canvas)
hx = bx + body.width - 30
hd.rounded_rectangle([hx, by + 120, hx + 230, by + body.height - 150], radius=110, outline=(205, 200, 192), width=52)
hd.rounded_rectangle([hx + 8, by + 128, hx + 222, by + body.height - 158], radius=105, outline=(244, 242, 238), width=36)
canvas.paste(body, (bx, by))
# bords haut / bas
hd.ellipse([bx, by - 34, bx + body.width, by + 34], fill=(248, 247, 244), outline=(214, 210, 203), width=4)
hd.ellipse([bx + 14, by - 22, bx + body.width - 14, by + 22], fill=(226, 222, 215))
canvas.save(out, quality=90)
