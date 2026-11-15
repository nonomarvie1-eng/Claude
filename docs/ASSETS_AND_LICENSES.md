# Ressources et licences

## Inventaire

| Ressource | Origine | Droits |
|---|---|---|
| Personnages, symboles, décor, tableau de score, logo, cadran (`game/src/assets/img/*`) | Générés par `game/art/build-art.mjs` (code écrit pour ce projet, style cartoon) | Propriété du studio |
| Sons et musiques (`game/src/assets/audio/*`) | Synthétisés par `game/audio/synth.py` (code écrit pour ce projet, aucun échantillon externe) | Propriété du studio |
| Police Luckiest Guy | `@fontsource/luckiest-guy` 5.3.0 | **Apache 2.0** : usage commercial autorisé ; conserver la notice de licence |
| Polices Lilita One, Bangers | `@fontsource/*` 5.3.0 | **SIL Open Font License 1.1** : usage commercial et embarquement autorisés ; ne pas vendre la police seule ; conserver la licence |
| (v1, plus utilisées dans le jeu) Cinzel, Marcellus, Poiret One | `@fontsource/*` | OFL 1.1 |
| PixiJS 8.23.0 | npm | MIT |
| Svelte 5.57.3, Vite 6.4.6 | npm | MIT |
| numpy, scipy, matplotlib, zstandard | PyPI | BSD / PSF-compatible |
| engineio/math-sdk | Utilisé **uniquement comme outil de vérification**, non intégré au dépôt | MIT |
| engineio/web-sdk, engineio/ts-client | **Non utilisés** (aucune licence publiée) | Tous droits réservés |

Aucune image, aucun son, aucune marque ni aucun personnage tiers n'est utilisé.

## Points de vigilance

- **Marques** : vérifier « Golden Rally » auprès de l'EUIPO, de l'USPTO et de l'OMPI (classes 9, 28 et 41) avant toute diffusion publique.
- **Thème tennis** : n'ajouter aucun nom de joueur, de tournoi ou de fédération, et aucun visuel de lieu ou de trophée réel. Les personnages sont des caricatures génériques inventées ; il faut veiller à ce qu'aucun ne finisse par ressembler à un joueur ou une joueuse célèbre (coiffure, tenue, attributs distinctifs).
- **Inspiration concurrente** : les jeux montrés en référence (Hacksaw Gaming, Nolimit City) ont inspiré des principes (personnages, style assumé, grille intégrée au décor), pas des dessins. Ne jamais reproduire leurs personnages, logos, décors ou noms de mécaniques.

## Évolutions possibles (sans souscription automatique)

Pour des illustrations plus détaillées (personnages, scènes peintes) :

1. **Illustrateur freelance** avec contrat de cession de droits. C'est l'option la plus sûre juridiquement ; budget indicatif de 1 500 à 6 000 € pour un set complet. Hypothèse non vérifiée.
2. **IA générative d'images** : n'utiliser qu'un service dont les conditions d'utilisation accordent des droits commerciaux et dont le modèle est entraîné sur des données licenciées (vérifier la version en vigueur au moment de l'usage). Une retouche humaine est conseillée, car la protection par le droit d'auteur des images purement générées est incertaine dans plusieurs pays. **Aucun service payant n'a été souscrit.**
3. **Audio** : un compositeur ou sound designer avec cession de droits, ou des banques sous licence commerciale claire. Le moteur audio accepte n'importe quel fichier mp3 ou wav portant le même nom.
