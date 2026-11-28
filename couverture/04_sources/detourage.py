#!/usr/bin/env python3
"""Détourage non génératif — série 2.

1. Segmentation : BiRefNet-portrait (licence MIT, modèle de SEGMENTATION, il ne produit qu'un masque ;
   aucune image n'est générée). Poids : huggingface.co/onnx-community/BiRefNet-portrait-ONNX
2. Affinage des cheveux : matting « closed-form » (Levin et al., pymatting) dans la seule bande d'incertitude.
3. Pixels : là où alpha >= 0,999, ce sont les pixels de la photo (retouchée globalement), inchangés.
   Seuls les pixels de bord semi-transparents reçoivent une estimation de la couleur de premier plan
   (décontamination standard), pour supprimer le liseré de l'ancien fond.

Usage : python3 04_sources/detourage.py P1 P7 ...   (le modèle est attendu dans $BIREFNET ou ./birefnet/onnx/model.onnx)
"""
import sys, os, numpy as np, cv2
from PIL import Image
import onnxruntime as ort
from pymatting import estimate_alpha_cf, estimate_foreground_ml

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("BIREFNET", "birefnet/onnx/model.onnx")
CFG = {  # source (retouche globale déjà appliquée) ; coupe basse en px source (None = garder tout)
    "P1": dict(src="03_photos_retouchees/P1_portrait_cuisine_foutou__retouche_1x.png", ybas=1340),
    "P7": dict(src="03_photos_retouchees/P7_mortier_foutou__retouche_1x.png", ybas=None),
    "P8": dict(src="03_photos_retouchees/serie2/P8_portrait_sourire__retouche_1x.png", ybas=None),
}

def segment(img):
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name
    x = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    y = sess.run(None, {name: x.transpose(2, 0, 1)[None].astype(np.float32)})[-1][0, 0]
    y = 1 / (1 + np.exp(-y))
    return cv2.resize(y, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC).clip(0, 1)

def run(key):
    c = CFG[key]
    im = np.asarray(Image.open(os.path.join(R, c["src"])).convert("RGB"))
    if c["ybas"]: im = im[:c["ybas"]]
    a0 = segment(im)
    # trimap : sûr si a0 > .97 / < .03, inconnu dans la zone de transition élargie
    fg = (a0 > .97).astype(np.uint8); bg = (a0 < .03).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg = cv2.erode(fg, k); bg = cv2.erode(bg, k)
    tri = np.full(a0.shape, .5); tri[fg > 0] = 1; tri[bg > 0] = 0
    img = im.astype(np.float64) / 255
    alpha = estimate_alpha_cf(img, tri)
    # garde-fou : le matting ne peut pas ajouter de zones que le réseau juge clairement fond
    alpha = np.where(a0 < .01, 0, alpha).clip(0, 1)
    fgc = estimate_foreground_ml(img, alpha)
    out = np.where(alpha[..., None] >= .999, img, fgc)
    rgba = (np.dstack([out.clip(0, 1), alpha]) * 255 + .5).astype(np.uint8)
    os.makedirs(os.path.join(R, "03_photos_retouchees/serie2"), exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(os.path.join(R, f"03_photos_retouchees/serie2/{key}_detoure_1x.png"))
    Image.fromarray((a0 * 255).astype(np.uint8)).save(os.path.join(R, f"01_audit/serie2_{key}_masque_reseau.png"))
    print(key, "ok", rgba.shape, "pixels identiques à la source :", f"{(alpha >= .999).mean():.1%}")

if __name__ == "__main__":
    for k in sys.argv[1:]: run(k)
