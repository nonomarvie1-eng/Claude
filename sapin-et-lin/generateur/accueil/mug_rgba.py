# Mug 3D simple sur fond transparent, a partir du fichier a plat du mug
import sys, math
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
d = Image.open(src).convert('RGBA')
W, H = d.size
white = Image.new('RGBA', d.size, (255, 255, 255, 255)); white.alpha_composite(d); d = white
R = int(25.8 / 20.4 * W / (2 * math.pi)); cx = int(W * 0.25); bw = 2 * R
body = Image.new('RGBA', (bw, H)); px, bp = d.load(), body.load()
for x in range(bw):
    u = (x - R + 0.5) / R; a = math.asin(max(-1, min(1, u)))
    sx = int(cx + a * R) % W
    shade = 0.78 + 0.22 * math.cos(a) ** 0.7
    hl = max(0, 1 - abs(u + 0.5) / 0.09) * 0.12
    for y in range(H):
        r, g, b, _ = px[sx, y]
        bp[x, y] = tuple(min(255, int(c * shade + 255 * hl)) for c in (r, g, b)) + (255,)
pad_top, pad_bot = 60, 40
k = 4  # sur-echantillonnage pour des bords lisses
cw, ch = bw + 560, H + pad_top + pad_bot
big = Image.new('RGBA', (cw * k, ch * k), (0, 0, 0, 0)); dr = ImageDraw.Draw(big)
# anse
hx, hy0, hy1 = (bw - 40) * k, (pad_top + 170) * k, (pad_top + H - 230) * k
dr.rounded_rectangle([hx, hy0, hx + 380 * k, hy1], radius=170 * k, outline=(232, 229, 223, 255), width=86 * k)
dr.rounded_rectangle([hx + 10 * k, hy0 + 10 * k, hx + 370 * k, hy1 - 10 * k], radius=160 * k, outline=(250, 249, 246, 255), width=58 * k)
mask = Image.new('L', (bw * k, H * k), 255)
big.paste(body.resize((bw * k, H * k), Image.LANCZOS), (0, pad_top * k))
# bord haut (ellipse) et bas arrondi
dr.ellipse([0, (pad_top - 52) * k, bw * k, (pad_top + 52) * k], fill=(250, 249, 246, 255), outline=(215, 211, 204, 255), width=5 * k)
dr.ellipse([18 * k, (pad_top - 36) * k, (bw - 18) * k, (pad_top + 36) * k], fill=(222, 218, 211, 255))
dr.ellipse([0, (pad_top + H - 34) * k, bw * k, (pad_top + H + 34) * k], fill=(214, 210, 203, 255))
big.paste(body.crop((0, H - 40, bw, H)).resize((bw * k, 40 * k)), (0, (pad_top + H - 40) * k))
big.resize((cw, ch), Image.LANCZOS).save(out)
