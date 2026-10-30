# Sapin & Lin – designs de Noël

Fichiers d'impression pour Gelato (sans prénom : le client l'ajoute via le Personalization Studio).

- `impression/classique` : style blanc / sapin (+ variantes vert sapin)
- `impression/rouge` : style rouge traditionnel
- `impression/nuit` : style nuit étoilée
- `apercus` : images de présentation

Formats : mug 11 oz = 2409 × 1169 px (20,4 × 9,9 cm, 300 dpi) ; boule ronde = 2000 × 2000 px.

Texte du prénom dans Gelato : police Great Vibes ; couleur #1F3D2C (classique) ou #FBF6EA (rouge, nuit, vert sapin).

## Régénérer les fichiers

Le dossier `generateur` contient les modèles (HTML/SVG) et les scripts de rendu (Node + Playwright, Python + Pillow).
Exemple : `node generateur/render-all.js generateur` (créer d'abord un dossier `final/` dans `generateur`).
Paramètres d'URL : `style`, `fmt` (boule|mug), `title`, `icon` (diamond|star|heart|house|paw), `year`, `name`.
