# Ressources et licences

## Inventaire

| Ressource | Origine | Droits |
|---|---|---|
| **Symboles des rouleaux v5 (11)** (`game/src/assets/img/sym_*.webp`) | **Pack de 11 symboles fourni par le client** (`Golden_Rally_Couleurs_Pack_Claude.zip`, originaux dans `game/art/pack-v5/`), importé par `game/art/import-pack.mjs` (rognage, mise à l'échelle uniforme, WebP ; dessin non modifié) | **À confirmer par le client** : le pack indique « sprites créés à partir d'une feuille d'illustrations IA, vérifier leurs droits d'utilisation avant toute distribution commerciale ». |
| Balle d'or, emblème Tie-Break (v4) et anciens symboles v4 (`game/art/legacy-symbols-v4/`) (`game/src/assets/img/sym_*.webp`, `ui_*.webp`, PNG de secours dans `img-png/`) | **Pack de 15 illustrations fourni par le client** (ZIP « Golden Rally: Match Point », original dans `game/art/pack/`), importé par `game/art/import-pack.mjs` (recadrage + WebP uniquement, aucune retouche du dessin) | **À confirmer par le client** : le README du pack demande de « vérifier les licences et droits d'utilisation commerciale ». Aucune preuve de cession de droits n'est jointe ; à obtenir avant toute exploitation commerciale. |
| `champion_racket` (pack) | Conservé en réserve, non utilisé (aucun ID moteur correspondant) | idem |
| Décor stade de nuit, cadre, logo, particules (`bg_*`, `crowd_*`, `fore_*`, `flags_*`, `frame`, `logo`, `sparkle`, `glow`) | Générés par `game/art/build-art.mjs` (code écrit pour ce projet) | Propriété du studio |
| Anciens symboles générés v3 | Sauvegardés dans `game/art/legacy-symbols-v3/` (retour arrière possible) | Propriété du studio |
| Sons et musiques (`game/src/assets/audio/*`, dont service, rebond, raquette, ambiance stade, transition Tie-Break) | Synthétisés par `game/audio/synth.py` (code écrit pour ce projet, aucun échantillon externe) | Propriété du studio |
| Polices Cinzel (titres) et Inter (interface) | `@fontsource/cinzel` 5.3.0, `@fontsource/inter` 5.2.5 | **SIL Open Font License 1.1** : usage commercial et embarquement autorisés ; conserver la licence |
| Luckiest Guy (Apache 2.0), Lilita One, Bangers, Marcellus, Poiret One (OFL) : plus affichées dans le jeu, encore référencées par le pipeline `game/art/` | `@fontsource/*` | Licences conservées |
| PixiJS 8.23.0 | npm | MIT |
| Svelte 5.57.3, Vite 6.4.6 | npm | MIT |
| numpy, scipy, matplotlib, zstandard | PyPI | BSD / PSF-compatible |
| engineio/math-sdk | Utilisé **uniquement comme outil de vérification**, non intégré au dépôt | MIT |
| engineio/web-sdk, engineio/ts-client | **Non utilisés** (aucune licence publiée) | Tous droits réservés |

En dehors du pack de symboles fourni par le client (droits à confirmer), aucune image, aucun son, aucune marque ni aucun personnage tiers n'est utilisé.

## Points de vigilance

- **Marques** : vérifier « Golden Rally » auprès de l'EUIPO, de l'USPTO et de l'OMPI (classes 9, 28 et 41) avant toute diffusion publique.
- **Thème tennis** : n'ajouter aucun nom de joueur, de tournoi ou de fédération, et aucun visuel de lieu ou de trophée réel. Les personnages sont des caricatures génériques inventées ; il faut veiller à ce qu'aucun ne finisse par ressembler à un joueur ou une joueuse célèbre (coiffure, tenue, attributs distinctifs).
- **Inspiration concurrente** : les jeux montrés en référence (Hacksaw Gaming, Nolimit City) ont inspiré des principes (personnages, style assumé, grille intégrée au décor), pas des dessins. Ne jamais reproduire leurs personnages, logos, décors ou noms de mécaniques.

## Évolutions possibles (sans souscription automatique)

Pour des illustrations plus détaillées (personnages, scènes peintes) :

1. **Illustrateur freelance** avec contrat de cession de droits. C'est l'option la plus sûre juridiquement ; budget indicatif de 1 500 à 6 000 € pour un set complet. Hypothèse non vérifiée.
2. **IA générative d'images** : n'utiliser qu'un service dont les conditions d'utilisation accordent des droits commerciaux et dont le modèle est entraîné sur des données licenciées (vérifier la version en vigueur au moment de l'usage). Une retouche humaine est conseillée, car la protection par le droit d'auteur des images purement générées est incertaine dans plusieurs pays. **Aucun service payant n'a été souscrit.**
3. **Audio** : un compositeur ou sound designer avec cession de droits, ou des banques sous licence commerciale claire. Le moteur audio accepte n'importe quel fichier mp3 ou wav portant le même nom.
