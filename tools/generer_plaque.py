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
F_PHRASE = str(FONTS / "AbrilFatface-Regular.ttf")
F_PHRASE_CONDENSEE = str(FONTS / "Oswald.ttf")
W, H = 2362, 3543
ZONE_PRENOM = (275, 1130, 750, 1325)   # coordonnées dans le modèle 1024x1536
ZONE_PHRASE = (122, 294, 902, 352)
ENCRE = (22, 52, 56)


def _font(path, size):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f


def _fit(draw, text, path, max_w, max_h, start):
    size = start
    while size > 30:
        f = _font(path, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=f, anchor="mm")
        if r - l <= max_w and b - t <= max_h:
            return f
        size -= 4
    return _font(path, size)


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


def _ecrire_compresse(big, texte, ligne_base=790, fleche=100, demi_largeur=881,
                      hauteur_cap=118, x0=300, x1=2062):
    """Phrase posée lettre par lettre sur l'arc du bandeau (mesuré sur les modèles) :
    centre en haut, extrémités abaissées de `fleche` px, chaque lettre inclinée selon la courbe.
    Police à empattements grasse, compressée horizontalement si besoin. Coordonnées du fichier 2362x3543."""
    import math
    zw = x1 - x0
    size = 200
    while True:
        f = _font(F_PHRASE, size)
        cap = f.getbbox("H")
        if cap[3] - cap[1] <= hauteur_cap:
            break
        size -= 2
    def largeurs(fnt):
        adv = [fnt.getlength(texte[: i + 1]) - fnt.getlength(texte[:i]) for i in range(len(texte))]
        adv = [max(a, fnt.size * 0.42) if ch == " " else a for a, ch in zip(adv, texte)]
        lettres = sum(a for a, ch in zip(adv, texte) if ch != " ")
        espaces = sum(a for a, ch in zip(adv, texte) if ch == " ")
        return adv, lettres, espaces

    # les espaces gardent 90 % de leur largeur, seules les lettres sont compressées
    while True:
        adv, lettres, espaces = largeurs(f)
        c = min(1.0, (zw - espaces) / lettres)
        if c >= 0.62 or size <= 60:
            break
        size -= 4
        f = _font(F_PHRASE, size)
    tw = lettres * c + espaces
    asc, desc = f.getmetrics()
    cxp = W / 2

    def y_arc(x):
        return ligne_base + fleche * ((x - cxp) / demi_largeur) ** 2

    def pente(x):
        return 2 * fleche * (x - cxp) / demi_largeur ** 2

    layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
    x = cxp - tw / 2
    pad = 60
    for i, ch in enumerate(texte):
        avance = adv[i] * (c if ch != " " else 1.0)
        if ch != " ":
            gw = int(f.getlength(ch)) + 2 * pad
            gh = asc + desc + 2 * pad
            g = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            gd.text((pad + 5, pad + 6), ch, font=f, fill=(255, 240, 200, 150))
            gd.text((pad, pad), ch, font=f, fill=ENCRE + (255,), stroke_width=2, stroke_fill=ENCRE + (255,))
            g = g.resize((max(1, int((gw - 2 * pad) * c) + 2 * pad), gh), Image.LANCZOS)
            xc = x + avance / 2
            ang = math.degrees(math.atan(pente(xc)))
            pivot = (g.width / 2, pad + asc)
            g = g.rotate(-ang, resample=Image.BICUBIC, center=pivot)
            layer.paste(g, (int(xc - pivot[0]), int(y_arc(xc) - pivot[1])), g)
        x += avance
    tex = big.convert("L").point(lambda v: 255 if v > 200 else int(150 + v * 0.5))
    layer.putalpha(ImageChops.multiply(layer.split()[3], tex))
    big.alpha_composite(layer)


def main(modele, prenom, phrase, out):
    base = Image.open(modele).convert("RGB")
    big = base.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)).convert("RGBA")
    if phrase != "-":
        _ecrire_compresse(big, phrase.upper())
    _ecrire(big, ZONE_PRENOM, prenom, F_PRENOM, 0.8)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    big.convert("RGB").save(out, dpi=(300, 300))
    print("OK :", out)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
