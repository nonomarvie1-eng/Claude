"""Plaque 20x30 cm (300 dpi), style « plaque émaillée vintage ».

Usage :
  python3 tools/make_plaque_v2.py illustration.png "Max" "CHIEN GENTIL|MAIS TRÈS BAVARD" sortie.png [titre]
Le caractère | sépare les lignes de la phrase. Titre par défaut : ATTENTION.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from make_plaque import remove_white_bg  # noqa: E402

FONTS = Path(__file__).parent / "fonts"
BEBAS = str(FONTS / "BebasNeue-Regular.ttf")
SCRIPT = str(FONTS / "Pacifico-Regular.ttf")

W, H = 2362, 3543
NAVY = (28, 54, 70)
CREAM = (248, 239, 222)
SAGE = (196, 220, 208)
TERRA = (196, 92, 62)
TERRA_DARK = (150, 64, 42)


def font_fit(draw, text, path, max_w, start, min_size=40):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 6
    return ImageFont.truetype(path, min_size)


def paw(d, cx, cy, s, color):
    d.ellipse([cx - s, cy - 0.6 * s, cx + s, cy + 1.1 * s], fill=color)
    for dx, dy in [(-1.15, -1.05), (-0.42, -1.6), (0.42, -1.6), (1.15, -1.05)]:
        r = 0.38 * s
        x, y = cx + dx * s, cy + dy * s
        d.ellipse([x - r, y - r * 1.2, x + r, y + r * 1.2], fill=color)


def main(illu, nom, phrase, out, titre="ATTENTION"):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # filets et « rivets » de plaque émaillée
    m = 110
    d.rounded_rectangle([m, m, W - m, H - m], radius=80, outline=CREAM, width=10)
    for x, y in [(m + 90, m + 90), (W - m - 90, m + 90), (m + 90, H - m - 90), (W - m - 90, H - m - 90)]:
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=CREAM)

    # titre
    f_t = font_fit(d, titre, BEBAS, W - 2 * m - 420, 420)
    d.text((W / 2, 400), titre, font=f_t, fill=CREAM, anchor="mm")

    # panneau crème en arche
    px0, px1 = 260, W - 260
    top, bottom = 640, H - 330
    r = (px1 - px0) // 2
    d.rectangle([px0, top + r, px1, bottom], fill=CREAM)
    d.ellipse([px0, top, px1, top + 2 * r], fill=CREAM)

    # soleil moutarde derrière l'animal
    cx, cy, sr = W // 2, 1450, 700
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=SAGE)

    # animal
    if illu != "-":
        art = remove_white_bg(Image.open(illu).convert("RGBA"))
        art = art.crop(art.getbbox())
        box_w, box_h = 2 * sr + 300, 1300
        s = min(box_w / art.width, box_h / art.height)
        art = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS)
        # ombre portée douce
        shadow = Image.new("RGBA", art.size, (0, 0, 0, 0))
        shadow.putalpha(art.split()[3].point(lambda a: int(a * 0.25)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        ax = (W - art.width) // 2
        ay = top + 200
        img.paste((60, 40, 20), (ax + 18, ay + 22), shadow)
        img.paste(art, (ax, ay), art)
        art_bottom = ay + art.height
    else:
        art_bottom = cy + sr

    # ruban avec le prénom
    ry = art_bottom + 40
    rh = 300
    rx0, rx1 = 330, W - 330
    d.polygon([(rx0 - 120, ry + 60), (rx0 + 40, ry + 60), (rx0 + 40, ry + rh + 60), (rx0 - 120, ry + rh + 60), (rx0 - 40, ry + rh / 2 + 60)], fill=TERRA_DARK)
    d.polygon([(rx1 + 120, ry + 60), (rx1 - 40, ry + 60), (rx1 - 40, ry + rh + 60), (rx1 + 120, ry + rh + 60), (rx1 + 40, ry + rh / 2 + 60)], fill=TERRA_DARK)
    d.rectangle([rx0, ry, rx1, ry + rh], fill=TERRA)
    f_n = font_fit(d, nom, SCRIPT, rx1 - rx0 - 160, 230)
    d.text((W / 2, ry + rh / 2 - 10), nom, font=f_n, fill=CREAM, anchor="mm")

    # phrase
    lignes = [l.strip() for l in phrase.split("|")]
    y = ry + rh + 190
    for ligne in lignes[:2]:
        f_p = font_fit(d, ligne, BEBAS, px1 - px0 - 220, 220)
        d.text((W / 2, y), ligne, font=f_p, fill=NAVY, anchor="mm")
        y += 225

    # empreintes
    for i, x in enumerate([W / 2 - 170, W / 2, W / 2 + 170]):
        paw(d, x, bottom - 120 - (25 if i == 1 else 0), 34, TERRA)

    img.save(out, dpi=(300, 300))
    print(f"OK : {out}")


if __name__ == "__main__":
    if len(sys.argv) not in (5, 6):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
