"""Écrit la PHRASE (bandeau du haut) et le PRÉNOM (cartouche du bas) sur un modèle vide,
puis produit le fichier d'impression 20x30 cm à 300 dpi.

Usage :
  python3 tools/generer_plaque.py <modele.png> "<prénom>" "<phrase>" <sortie.png>
Exemple :
  python3 tools/generer_plaque.py designs/modeles2/golden_jardin.png "Max" "UN CHIEN GÂTÉ VIT ICI" designs/commandes/max.png
Mettre "-" comme phrase pour un modèle dont la phrase est déjà dessinée.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONTS = Path(__file__).parent / "fonts"
F_PRENOM = str(FONTS / "Lobster-Regular.ttf")
F_PHRASE = str(FONTS / "DMSerifDisplay-Regular.ttf")
W, H = 2362, 3543
ZONE_PRENOM = (275, 1130, 750, 1325)   # coordonnées dans le modèle 1024x1536
ZONE_PHRASE = (150, 262, 880, 352)
ENCRE = (22, 52, 56)


def _fit(draw, text, path, max_w, max_h, start):
    size = start
    while size > 30:
        f = ImageFont.truetype(path, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=f, anchor="mm")
        if r - l <= max_w and b - t <= max_h:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def _ecrire(big, zone, texte, police, ratio_h, epaisseur=0):
    sx, sy = W / 1024, H / 1536
    x0, y0, x1, y1 = int(zone[0] * sx), int(zone[1] * sy), int(zone[2] * sx), int(zone[3] * sy)
    d = ImageDraw.Draw(big)
    f = _fit(d, texte, police, x1 - x0, (y1 - y0) * ratio_h, int((y1 - y0) * 0.95))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((cx + 5, cy + 6), texte, font=f, fill=(255, 240, 200, 150), anchor="mm")
    ld.text((cx, cy), texte, font=f, fill=ENCRE + (255,), anchor="mm",
            stroke_width=epaisseur, stroke_fill=ENCRE + (255,))
    tex = big.convert("L").point(lambda v: 255 if v > 200 else int(150 + v * 0.5))
    layer.putalpha(ImageChops.multiply(layer.split()[3], tex))
    big.alpha_composite(layer)


def main(modele, prenom, phrase, out):
    base = Image.open(modele).convert("RGB")
    big = base.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)).convert("RGBA")
    if phrase != "-":
        _ecrire(big, ZONE_PHRASE, phrase.upper(), F_PHRASE, 0.78, epaisseur=2)
    _ecrire(big, ZONE_PRENOM, prenom, F_PRENOM, 0.8)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    big.convert("RGB").save(out, dpi=(300, 300))
    print("OK :", out)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
