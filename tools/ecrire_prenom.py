"""Écrit le prénom du client dans le cartouche vide du modèle et produit le fichier d'impression 20x30 cm (300 dpi).

Usage : python3 tools/ecrire_prenom.py designs/modele_golden_cartouche_vide.png "Max" designs/commande_max.png [police]
Polices : lobster (défaut), rye, slab
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONTS = Path(__file__).parent / "fonts"
POLICES = {"lobster": "Lobster-Regular.ttf", "rye": "Rye-Regular.ttf", "slab": "AlfaSlabOne-Regular.ttf"}
W, H = 2362, 3543
# zone du cartouche dans le modèle 1024x1536 (entre les deux empreintes)
ZONE = (275, 1130, 750, 1325)
ENCRE = (22, 52, 56)


def main(modele, prenom, out, police="lobster"):
    base = Image.open(modele).convert("RGB")
    sx, sy = W / base.width, H / base.height
    big = base.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    x0, y0, x1, y1 = [int(v * s) for v, s in zip(ZONE, (sx, sy, sx, sy))]
    zw, zh = x1 - x0, y1 - y0

    font_path = str(FONTS / POLICES[police])
    size = int(zh * 0.85)
    d0 = ImageDraw.Draw(big)
    while size > 40:
        f = ImageFont.truetype(font_path, size)
        l, t, r, b = d0.textbbox((0, 0), prenom, font=f, anchor="mm")
        if r - l <= zw and b - t <= zh * 0.8:
            break
        size -= 6

    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # calque texte + légère ombre claire (effet lettrage peint)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((cx + 6, cy + 8), prenom, font=f, fill=(255, 240, 200, 160), anchor="mm")
    ld.text((cx, cy), prenom, font=f, fill=ENCRE + (255,), anchor="mm")
    # usure : on laisse transparaître la texture du papier
    tex = big.convert("L").point(lambda v: 255 if v > 200 else int(150 + v * 0.5))
    alpha = ImageChops.multiply(layer.split()[3], tex)
    layer.putalpha(alpha)
    big = big.convert("RGBA")
    big.alpha_composite(layer)
    big.convert("RGB").save(out, dpi=(300, 300))
    print("OK :", out)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
