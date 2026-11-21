# V001 — Plans à filmer dans GTA 6 (midi contre minuit)

**But** : filmer **le même endroit, avec le même cadrage**, une fois vers midi et une fois vers
minuit. C'est la ressemblance des deux plans qui rend la comparaison satisfaisante.

## Réglages, une seule fois
- Xbox → Paramètres → Préférences → **Capture et partage** : **1080p**, **SDR**.
- Mode histoire, **caméra à la 3ᵉ personne derrière le personnage** (ou derrière la voiture).
- Masquez l'interface (HUD) si l'option existe dans les réglages d'affichage du jeu.
- Coupez le micro du chat de groupe pour ne garder que le son du jeu.

## Méthode
1. Choisissez 4 endroits et **mémorisez la position exacte** : un repère visible (panneau,
   palmier, lampadaire) et l'angle de caméra.
2. Filmez les 4 plans **de jour** (vers midi, beau temps si possible).
3. Revenez aux mêmes endroits **la nuit**. Utilisez le moyen du jeu pour faire passer le temps
   s'il en existe un ; sinon, jouez en attendant la nuit. Refilmez le même cadrage.
4. Pour chaque plan : **2 secondes immobile**, puis le mouvement, puis touche Xbox → **Capturer
   ce qui s'est passé → 30 dernières secondes**.

## Les 4 lieux (×2 = 8 captures)
| # | Fichiers (à renommer sur le PC) | Lieu | Mouvement |
|---|---|---|---|
| 1 | `MIDI_PLAGE` / `MINUIT_PLAGE` | Une plage | Marcher vers l'eau, caméra derrière |
| 2 | `MIDI_VILLE` / `MINUIT_VILLE` | Une rue animée avec des enseignes | Marcher ou rouler lentement |
| 3 | `MIDI_PORT` / `MINUIT_PORT` | Un port ou une marina avec des bateaux | Panoramique lent de la caméra |
| 4 | `MIDI_ROUTE` / `MINUIT_ROUTE` | Une grande route ou une autoroute | Rouler en voiture, caméra derrière |

Les lieux sont des suggestions : choisissez ceux qui vous paraissent les plus beaux. Gardez
juste **4 paires** au cadrage identique. Si vous changez un lieu, dites-le-moi pour que j'adapte
la légende.

## Après la session
1. Transférez les 8 captures dans `C:\GTA-MEDIA\inbox` et **renommez-les** comme ci-dessus.
2. `python gta.py ingest`, puis `python gta.py library`.
3. Envoyez-moi la liste affichée : je remplis le projet (fichiers et secondes exactes).
4. `python gta.py build projects\v001-midi-minuit\episode.yaml`
