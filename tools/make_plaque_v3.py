"""Plaque 20x30 cm (300 dpi), style « plaque émaillée » inspiré du design ChatGPT retenu.

Usage :
  python3 tools/make_plaque_v3.py illustration.png "Max" "Chien gentil|mais très bavard" sortie.png [titre]
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from make_plaque import remove_white_bg  # noqa: E402

FONTS = Path(__file__).parent / "fonts"
SLAB = str(FONTS / "AlfaSlabOne-Regular.ttf")
SCRIPT = str(FONTS / "Pacifico-Regular.ttf")
SERIF = str(FONTS / "DMSerifDisplay-Regular.ttf")

W, H = 2362, 3543
NAVY = (27, 52, 92)
CREAM = (251, 242, 222)
TERRA = (178, 64, 38)
GOLD = (196, 150, 70)


def fit(draw, text, path, max_w, start, min_size=40):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 6
    return ImageFont.truetype(path, min_size)


def paw(d, cx, cy, s, color):
    d.ellipse([cx - s, cy - 0.55 * s, cx + s, cy + 1.05 * s], fill=color)
    for dx, dy in [(-1.15, -1.0), (-0.42, -1.55), (0.42, -1.55), (1.15, -1.0)]:
        r = 0.37 * s
        x, y = cx + dx * s, cy + dy * s
        d.ellipse([x - r, y - r * 1.25, x + r, y + r * 1.25], fill=color)


def rivet(d, x, y, r=34):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 85, 35))
    d.ellipse([x - r + 6, y - r + 6, x + r - 6, y + r - 6], fill=GOLD)
    d.ellipse([x - r / 2.5, y - r / 1.6, x + r / 6, y - r / 6], fill=(245, 225, 170))


def curved_banner(img, text, cy, half_w, R=2600, thick=330):
    """Bandeau terracotta en arc avec le texte suivant la courbe."""
    d = ImageDraw.Draw(img)
    cx, ccy = W / 2, cy + R
    a = math.asin(half_w / R)
    outer, inner = R + thick / 2, R - thick / 2
    pts = [(cx + outer * math.sin(t), ccy - outer * math.cos(t)) for t in [(-a + 2 * a * i / 80) for i in range(81)]]
    pts += [(cx + inner * math.sin(t), ccy - inner * math.cos(t)) for t in [(a - 2 * a * i / 80) for i in range(81)]]
    d.polygon(pts, fill=TERRA)
    # extrémités en queue d'aronde
    for sgn in (-1, 1):
        t = sgn * a
        ox, oy = cx + outer * math.sin(t), ccy - outer * math.cos(t)
        ix, iy = cx + inner * math.sin(t), ccy - inner * math.cos(t)
        mx, my = cx + R * math.sin(t) + sgn * 70, ccy - R * math.cos(t) + 40
        d.polygon([(ox, oy), (ox + sgn * 140, oy + 120), (mx, my), (ix + sgn * 140, iy + 120), (ix, iy)], fill=(140, 48, 28))
    # texte lettre par lettre sur l'arc
    f = fit(d, text, SLAB, 2 * half_w * 0.86, 300)
    total = d.textlength(text, font=f)
    theta = -total / 2 / R
    for ch in text:
        w = d.textlength(ch, font=f)
        t = theta + w / 2 / R
        x, y = cx + R * math.sin(t), ccy - R * math.cos(t)
        glyph = Image.new("RGBA", (int(w) + 60, f.size + 120), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((glyph.width / 2, glyph.height / 2), ch, font=f, fill=CREAM, anchor="mm")
        glyph = glyph.rotate(-math.degrees(t), resample=Image.BICUBIC, expand=True)
        img.paste(glyph, (int(x - glyph.width / 2), int(y - glyph.height / 2)), glyph)
        theta += w / R


def name_badge(d, cx, cy, nom, w=1180, h=380):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    n = 70
    shape = [(x0 + n, y0), (x1 - n, y0), (x1, y0 + n), (x1, y1 - n), (x1 - n, y1), (x0 + n, y1), (x0, y1 - n), (x0, y0 + n)]
    big = [(x + (18 if x > cx else -18), y + (18 if y > cy else -18)) for x, y in shape]
    d.polygon(big, fill=TERRA)
    d.polygon(shape, fill=NAVY)
    inner = [(x + (-22 if x > cx else 22), y + (-22 if y > cy else 22)) for x, y in shape]
    d.line(inner + [inner[0]], fill=CREAM, width=6)
    for sx in (x0 + 55, x1 - 55):
        d.ellipse([sx - 16, cy - 16, sx + 16, cy + 16], fill=CREAM)
    f = fit(d, nom, SCRIPT, w - 260, 230)
    d.text((cx, cy - 15), nom, font=f, fill=CREAM, anchor="mm")


def bottom_ribbon(d, cy, lignes, half_w=840, h=470):
    x0, x1 = W / 2 - half_w, W / 2 + half_w
    y0, y1 = cy - h / 2, cy + h / 2
    d.polygon([(x0 - 120, y0 + 30), (x0 + 60, y0 + 30), (x0 + 60, y1 + 30), (x0 - 120, y1 + 30), (x0 - 30, (y0 + y1) / 2 + 30)], fill=(16, 34, 64))
    d.polygon([(x1 + 120, y0 + 30), (x1 - 60, y0 + 30), (x1 - 60, y1 + 30), (x1 + 120, y1 + 30), (x1 + 30, (y0 + y1) / 2 + 30)], fill=(16, 34, 64))
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    y = cy - (len(lignes) - 1) * 105
    for ligne in lignes[:2]:
        f = fit(d, ligne, SERIF, 2 * half_w - 160, 200)
        d.text((W / 2, y), ligne, font=f, fill=CREAM, anchor="mm")
        y += 210


def main(illu, nom, phrase, out, titre="ATTENTION"):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # bordures
    d.rounded_rectangle([20, 20, W - 20, H - 20], radius=130, outline=NAVY, width=70)
    d.rounded_rectangle([150, 150, W - 150, H - 150], radius=60, outline=TERRA, width=12)
    for x, y in [(115, 115), (W - 115, 115), (115, H - 115), (W - 115, H - 115)]:
        rivet(d, x, y)

    curved_banner(img, titre, cy=470, half_w=880)
    d = ImageDraw.Draw(img)

    # animal
    art_top, art_h = 760, 1840
    if illu != "-":
        art = remove_white_bg(Image.open(illu).convert("RGBA"))
        art = art.crop(art.getbbox())
        s = min(1550 / art.width, art_h / art.height)
        art = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS)
        img.paste(art, ((W - art.width) // 2, art_top), art)

    # traits d'expression et empreintes latérales
    for sgn in (-1, 1):
        bx = W / 2 + sgn * 640
        for ang, ln in [(-50, 120), (-20, 150), (10, 120)]:
            a = math.radians(ang)
            x0, y0 = bx + sgn * 40 * math.cos(a), 1050 + 140 * math.sin(a)
            d.line([(x0, y0), (x0 + sgn * ln * math.cos(a), y0 + ln * math.sin(a))], fill=NAVY, width=22)
        paw(d, W / 2 + sgn * 860, 1500, 70, TERRA)

    name_badge(d, W / 2, art_top + int(art_h * 0.49), nom)

    # séparateurs + ruban de la phrase
    sep_y = H - 820
    d.line([(420, sep_y), (1020, sep_y)], fill=TERRA, width=10)
    d.line([(W - 1020, sep_y), (W - 420, sep_y)], fill=TERRA, width=10)
    paw(d, W / 2, sep_y, 40, TERRA)
    bottom_ribbon(d, H - 480, [l.strip() for l in phrase.split("|")])
    paw(d, W / 2, H - 205, 32, TERRA)

    img.save(out, dpi=(300, 300))
    print(f"OK : {out}")


if __name__ == "__main__":
    if len(sys.argv) not in (5, 6):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
