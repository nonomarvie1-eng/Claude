# V001 — Plans à filmer (environ 15 à 20 minutes)

**But** : filmer la **même action** dans GTA 5 puis dans GTA 6, avec un **cadrage aussi
proche que possible**. C'est la ressemblance des deux plans qui rend la comparaison
satisfaisante à regarder.

## Réglages, une seule fois
- Xbox → Paramètres → Préférences → **Capture et partage** : résolution **1080p**, **SDR** (HDR désactivé pour les captures).
- Dans les deux jeux : **mode histoire** (pas en ligne), **caméra à la 3ᵉ personne, derrière le personnage**.
- Masquez l'interface (HUD) si l'option existe dans les réglages d'affichage. Sinon, ce n'est pas grave.
- Pour les plans de jour : **vers midi, beau temps**, dans les deux jeux.
- Le jeu en cours sur la console doit être celui que vous filmez. Pour garder le son du jeu,
  coupez le micro du chat de groupe.

## Méthode pour chaque plan
1. Mettez-vous en place, puis **attendez 2 secondes sans bouger**.
2. Faites l'action, puis laissez la caméra tourner **3 secondes après**.
3. Touche Xbox → **Capturer ce qui s'est passé → 30 dernières secondes**.
4. Faites le même plan dans l'autre jeu.

## Les 4 plans (×2 jeux = 8 captures)
| # | Nom du fichier (à renommer sur le PC) | Action | Conseils |
|---|---|---|---|
| 1 | `GTA5_PLONGEON` / `GTA6_PLONGEON` | Courir et **sauter dans l'eau** depuis un ponton ou une jetée | Caméra derrière, l'eau bien visible devant |
| 2 | `GTA5_CRASH` / `GTA6_CRASH` | Voiture de sport, **foncer dans un mur ou un poteau** à environ 100 km/h, ligne droite | Caméra derrière la voiture, sans ralenti |
| 3 | `GTA5_PLAGE` / `GTA6_PLAGE` | **Courir sur le sable**, au bord de l'eau, une dizaine de mètres | Caméra derrière, avec les pieds et le sable dans l'image |
| 4 | `GTA5_NUIT` / `GTA6_NUIT` | **Rouler de nuit** dans une rue éclairée (néons, enseignes) | Vitesse modérée, caméra derrière la voiture |

Si un plan est impossible dans un jeu (pas de lieu adapté), dites-le-moi : je le remplace.

## Après la session
1. Transférez les 8 captures dans `C:\GTA-MEDIA\inbox` (application Xbox ou OneDrive).
2. **Renommez-les** avec les noms ci-dessus, par exemple `GTA5_PLONGEON.mp4`.
3. `python gta.py ingest`, puis `python gta.py library` pour voir les noms dans la bibliothèque.
4. Envoyez-moi la liste affichée par `library` : je remplis le projet (fichiers et secondes exactes).
5. `python gta.py build projects\v001-gta5-vs-gta6\episode.yaml`

**Important** : la vidéo ne dit rien d'autre que ce qu'on voit. Il n'y a donc aucune
affirmation à vérifier, ce qui en fait le format idéal pour démarrer.
