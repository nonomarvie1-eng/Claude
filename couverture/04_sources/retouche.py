#!/usr/bin/env python3
"""Retouche photographique classique, non destructive et reproductible.

Règles (cahier des charges §5) :
  - aucune génération d'image, aucun remplissage génératif, aucune retouche locale du visage ;
  - uniquement des opérations globales pixel par pixel (balance des blancs, exposition,
    contraste, saturation), un agrandissement Lanczos (interpolation mathématique, pas d'IA)
    et une accentuation douce ;
  - les originaux de 00_originaux/ sont en lecture seule et ne sont jamais réécrits ;
  - le détourage de l'assiette P6 est géométrique (ellipse ajustée sur le bord blanc de
    l'assiette) : aucun pixel de nourriture n'est modifié, seul un canal alpha est ajouté.

Usage : python3 04_sources/retouche.py   (depuis le dossier couverture/)
"""
import json, os
import numpy as np
import cv2
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "00_originaux")
DST = os.path.join(ROOT, "03_photos_retouchees")

# Paramètres par photo. wb = part de correction « gray world » (0 = aucune, 1 = neutre total).
# On ne neutralise que partiellement : la chaleur de la lumière fait partie de l'ambiance,
# mais la dominante orange relevée dans les essais précédents doit être réduite.
PARAMS = {
    "P1_portrait_cuisine_foutou.jpg": dict(wb=0.30, expo=1.03, contrast=1.04, sat=0.90, scales=[2.31, 1.60]),
    "P6_plat_poulet_yassa_thiere.png": dict(wb=0.22, expo=1.00, contrast=1.03, sat=0.90, scales=[1.92]),
    "P7_mortier_foutou.jpg":           dict(wb=0.28, expo=1.02, contrast=1.04, sat=0.92, scales=[1.65]),
}

def srgb_to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)

def lin_to_srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)

def retouch(img, wb, expo, contrast, sat):
    a = np.asarray(img.convert("RGB"), dtype=np.float64) / 255.0
    lin = srgb_to_lin(a)
    # Balance des blancs partielle (gray world, en lumière linéaire)
    means = lin.reshape(-1, 3).mean(0)
    gains = (means.mean() / means) ** wb
    gains /= gains[1]                      # on garde le vert comme référence (exposition stable)
    lin = lin * gains * expo
    out = lin_to_srgb(lin)
    # Contraste doux autour du gris moyen (courbe linéaire, pas de clipping agressif)
    out = np.clip((out - 0.5) * contrast + 0.5, 0, 1)
    # Saturation (mélange avec la luminance Rec.709)
    lum = (out * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)
    out = np.clip(lum + (out - lum) * sat, 0, 1)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8)), gains

def upscale(img, s):
    w, h = img.size
    big = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    # Accentuation raisonnable : compense le flou d'interpolation sans créer de halos
    return big.filter(ImageFilter.UnsharpMask(radius=1.4, percent=35, threshold=3))

def plate_alpha(path):
    """Masque de l'assiette P6 : ellipse ajustée sur le bord blanc, +3 px, bord adouci 1,5 px."""
    im = cv2.imread(path)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    white = ((hsv[..., 1] < 45) & (hsv[..., 2] > 190)).astype(np.uint8) * 255
    white = cv2.morphologyEx(white, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    (cx, cy), (a1, a2), ang = cv2.fitEllipse(max(cnts, key=cv2.contourArea))
    m = np.zeros(im.shape[:2], np.float32)
    cv2.ellipse(m, ((cx, cy), (a1 + 6, a2 + 6), ang), 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)
    return m, dict(cx=cx, cy=cy, axes=[a1, a2], angle=ang)

def main():
    os.makedirs(DST, exist_ok=True)
    log = {}
    for name, p in PARAMS.items():
        src = Image.open(os.path.join(SRC, name))
        corr, gains = retouch(src, p["wb"], p["expo"], p["contrast"], p["sat"])
        stem = os.path.splitext(name)[0]
        corr.save(os.path.join(DST, f"{stem}__retouche_1x.png"))
        log[name] = dict(params={k: v for k, v in p.items() if k != "scales"},
                         gains_rgb=[round(g, 4) for g in gains], outputs=[])
        for s in p["scales"]:
            out = upscale(corr, s)
            fn = f"{stem}__retouche_x{s:.2f}.png"
            out.save(os.path.join(DST, fn), optimize=False)
            log[name]["outputs"].append(dict(file=fn, size=out.size))
        if name.startswith("P6"):
            m, ell = plate_alpha(os.path.join(SRC, name))
            for s in p["scales"]:
                big = Image.open(os.path.join(DST, f"{stem}__retouche_x{s:.2f}.png")).convert("RGB")
                mm = cv2.resize(m, big.size, interpolation=cv2.INTER_CUBIC)
                rgba = big.copy(); rgba.putalpha(Image.fromarray((np.clip(mm, 0, 1) * 255).astype(np.uint8)))
                bb = rgba.getbbox()
                rgba.crop(bb).save(os.path.join(DST, f"{stem}__assiette_detouree_x{s:.2f}.png"))
                log[name]["outputs"].append(dict(file=f"{stem}__assiette_detouree_x{s:.2f}.png", ellipse_source_px=ell))
    with open(os.path.join(DST, "journal_retouche.json"), "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False, default=float)
    print(json.dumps(log, indent=1, default=float))

if __name__ == "__main__":
    main()
