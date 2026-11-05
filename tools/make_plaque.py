"""Cree le fichier d'impression d'une plaque 20x30 cm (300 dpi) a partir d'une illustration.

Usage :
  python3 tools/make_plaque.py illustration.png "MAX" "Chien gentil mais très bavard" sortie.png
Si l'illustration est absente ("-"), un cadre vide est dessine (pour tester la mise en page).
"""
import sys
from PIL import Image, ImageDraw, ImageFont

DPI = 300
W, H = 2362, 3543  # 20 x 30 cm a 300 dpi (portrait)
BLEED = 35         # ~3 mm de marge de securite
CREME = (247, 240, 228)
ENCRE = (40, 52, 58)
ACCENT = (196, 92, 62)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def remove_white_bg(art, seuil=235):
    """Rend transparent le fond blanc relie aux bords (le blanc a l'interieur du dessin est conserve)."""
    rgb = art.convert("RGB")
    mask = Image.new("L", art.size, 0)
    w, h = art.size
    for start in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        tmp = rgb.copy()
        ImageDraw.floodfill(tmp, start, (255, 0, 255), thresh=255 - seuil)
        px = tmp.load()
        m = mask.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] == (255, 0, 255):
                    m[x, y] = 255
    alpha = Image.eval(mask, lambda v: 255 - v)
    art.putalpha(alpha)
    return art


def fit_font(draw, text, path, max_w, start):
    size = start
    while size > 20:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def main(illu, nom, phrase, out):
    img = Image.new("RGB", (W, H), CREME)
    d = ImageDraw.Draw(img)
    m = BLEED + 90
    # double cadre
    d.rounded_rectangle([m, m, W - m, H - m], radius=90, outline=ENCRE, width=22)
    d.rounded_rectangle([m + 45, m + 45, W - m - 45, H - m - 45], radius=60, outline=ACCENT, width=8)

    # bandeau du haut
    titre = "ATTENTION"
    f_t = fit_font(d, titre, FONT_BOLD, W - 2 * m - 300, 300)
    d.text((W / 2, m + 260), titre, font=f_t, fill=ACCENT, anchor="mm")

    # illustration
    box = (m + 160, m + 470, W - m - 160, m + 470 + 1750)
    bw, bh = box[2] - box[0], box[3] - box[1]
    if illu != "-":
        art = remove_white_bg(Image.open(illu).convert("RGBA"))
        art = art.crop(art.getbbox())
        scale = min(bw / art.width, bh / art.height)
        art = art.resize((int(art.width * scale), int(art.height * scale)), Image.LANCZOS)
        x = box[0] + (bw - art.width) // 2
        y = box[1] + (bh - art.height) // 2
        img.paste(art, (x, y), art)
    else:
        d.rectangle(box, outline=(170, 170, 170), width=6)
        d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), "illustration",
               font=ImageFont.truetype(FONT_REG, 90), fill=(150, 150, 150), anchor="mm")

    # phrase
    f_p = ImageFont.truetype(FONT_REG, 125)
    lines = wrap(d, phrase, f_p, W - 2 * m - 320)
    y = box[3] + 150
    for line in lines[:3]:
        d.text((W / 2, y), line, font=f_p, fill=ENCRE, anchor="mm")
        y += 165

    # prenom
    f_n = fit_font(d, nom.upper(), FONT_BOLD, W - 2 * m - 400, 330)
    d.text((W / 2, H - m - 330), nom.upper(), font=f_n, fill=ACCENT, anchor="mm")

    img.save(out, dpi=(DPI, DPI))
    print(f"OK : {out} ({W}x{H} px, 300 dpi, 20x30 cm)")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
