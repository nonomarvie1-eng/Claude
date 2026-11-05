"""Visuel publicitaire 1080x1350 (format 4:5 Meta) : plaque principale + bandeau + 3 variantes.

Usage : python3 tools/make_ad_visual.py principale.png var1.png var2.png var3.png sortie.png ["texte du badge"]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).parent / "fonts"
W, H = 1080, 1350


def shadowed(img, size, angle=0):
    p = img.convert("RGBA")
    p.thumbnail(size, Image.LANCZOS)
    p = p.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (p.width + 60, p.height + 60), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 120), (30, 40), p.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    sh.paste(p, (30, 30), p)
    return sh


def main(main_img, v1, v2, v3, out, badge="LE PRÉNOM, LA RACE ET LA PHRASE SONT PERSONNALISABLES"):
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):  # dégradé chaud
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(214 - 40 * t), int(186 - 45 * t), int(150 - 50 * t)))
    for x in range(0, W, 135):  # lames de bois discrètes
        d.line([(x, 0), (x, H)], fill=(150, 120, 90), width=3)

    big = shadowed(Image.open(main_img), (560, 820), angle=-2)
    bg.paste(big, ((W - big.width) // 2, 110), big)

    f = ImageFont.truetype(str(FONTS / "BebasNeue-Regular.ttf"), 34)
    tw = d.textlength(badge, font=f)
    d.rounded_rectangle([40, 40, 40 + tw + 50, 100], radius=14, fill=(250, 196, 60))
    d.text((40 + 25, 70), badge, font=f, fill=(120, 30, 20), anchor="lm")

    xs = [120, 425, 730]
    for x, v in zip(xs, [v1, v2, v3]):
        t = shadowed(Image.open(v), (200, 300))
        bg.paste(t, (x, H - t.height - 10), t)

    bg.save(out, quality=92)
    print("OK :", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
