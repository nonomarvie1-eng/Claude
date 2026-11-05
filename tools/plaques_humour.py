"""Écrit le prénom dans les zones vides des plaques humoristiques (modèles 1024x1536 de ChatGPT)
et produit le fichier d'impression 20x30 cm à 300 dpi.

Usage : python3 tools/plaques_humour.py <modele> "<prénom>" <sortie.png>
Modèles connus : certificat (designs/modeles3/certificat_golden.png)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = Path(__file__).parent / "fonts"
W, H = 2362, 3543
CREME = (250, 236, 200)
ENCRE_FONCEE = (60, 20, 15)

# zone du prénom (coordonnées dans l'image 1024x1536) : x0, y0, x1, y1
ZONES = {
    "certificat": (245, 1108, 735, 1222),
}


def ecrire(big, zone, texte, police="AbrilFatface-Regular.ttf"):
    sx, sy = W / 1024, H / 1536
    x0, y0, x1, y1 = zone[0] * sx, zone[1] * sy, zone[2] * sx, zone[3] * sy
    zw, zh = x1 - x0, y1 - y0
    size = int(zh * 0.95)
    while True:
        f = ImageFont.truetype(str(FONTS / police), size)
        l, t, r, b = f.getbbox(texte)
        if (r - l) <= zw and (b - t) <= zh * 0.72:
            break
        size -= 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    calque = Image.new("RGBA", big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    d.text((cx + 6, cy + 8), texte, font=f, fill=(40, 10, 5, 170), anchor="mm")
    d.text((cx, cy), texte, font=f, fill=CREME + (255,), anchor="mm",
           stroke_width=4, stroke_fill=ENCRE_FONCEE + (255,))
    big.alpha_composite(calque)


def main(modele, prenom, out):
    nom = Path(modele).stem.split("_")[0]
    base = Image.open(modele).convert("RGB")
    big = base.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)).convert("RGBA")
    ecrire(big, ZONES[nom], prenom.upper())
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    big.convert("RGB").save(out, dpi=(300, 300))
    print("OK :", out)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
