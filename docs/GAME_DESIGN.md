# Golden Rally — Conception du jeu (v2)

## Identité

- **Nom de travail** : Golden Rally. Une recherche de marque est à faire avant toute diffusion publique.
- **Style : cartoon à gros traits.** Contours d'encre épais, aplats de couleur avec ombrage cel, ombres décalées façon BD, trames de points. Typographies Luckiest Guy et Lilita One.
- **Univers** : le club de tennis du quartier, un jour de tournoi interne. Fanions, tribune pleine, court en terre battue, et le **vieux tableau de score en bois du club** qui sert de grille de jeu.
- **Ton** : humour et caractère. Chaque symbole fort est un personnage avec une attitude.
- **Inspiration, pas de copie** : on reprend des jeux du marché les principes qui créent la personnalité (personnages, style assumé, grille intégrée au décor, palette signature). Aucun dessin, nom ou mécanique propriétaire n'est repris. Aucun personnage ne représente une personne réelle, un tournoi ou une marque.

## Personnages et symboles

| Code | Symbole | Rôle | Gain par façon 3/4/5/6 (× mise) |
|---|---|---|---|
| W | **Smash** : raquette qui frappe la balle | Wild (rouleaux 2 à 6) | — |
| S | **Trophée** | Scatter, déclenche le Tie-Break | 2 / 5 / 20 / 100 (total, n'importe où) |
| H1 | **Le Président** : moustache, monocle, nœud papillon, air satisfait | Haut | 0,5 / 1 / 2 / 5 |
| H2 | **La Championne** : bandeau, regard déterminé, raquette sur l'épaule | Haut | 0,4 / 0,8 / 1,5 / 3 |
| H3 | **L'Arbitre** : lunettes, crie « OUT ! » | Haut | 0,3 / 0,5 / 1,2 / 2,5 |
| H4 | **Le Ramasseur** : casquette à l'envers, taches de rousseur, dent manquante | Haut | 0,2 / 0,4 / 1 / 2 |
| H5 | **Le Bulldog du club** : bandeau éponge, balle dans la gueule | Haut | 0,2 / 0,3 / 0,8 / 1,5 |
| L1–L5 | **Plaques de score** AD, 40, 30, 15, 0 accrochées au tableau | Bas | 0,1 → 0,7 |

Les symboles bas reprennent toute la progression du score au tennis (0, 15, 30, 40, AD). C'est notre clin d'œil, à la place des cartes A, K, Q, J habituelles.

## Gameplay

- **Grille 6 × 5, 15 625 façons de gagner** : un symbole paie s'il est présent, ou remplacé par un Smash, sur des rouleaux adjacents à partir de la gauche, sur 3 à 6 rouleaux. Le gain vaut la valeur par façon multipliée par le nombre de façons.
- **Tie-Break (tours gratuits)** : 3, 4, 5 ou 6 Trophées donnent 9, 12, 15 ou 20 tours.
- **Mécanique signature « Rally »** : pendant le Tie-Break, chaque Smash qui tombe *relance l'échange*. Le multiplicateur de tous les gains en façons monte, avant le calcul du tour : ×1 → ×2 → ×3 → ×4 → ×5 → ×6 → ×8 → ×10 → ×12 → ×15 → ×20. Il ne redescend jamais pendant le bonus et s'affiche sur le cadran RALLY.
- Relance du bonus : 3 Trophées ou plus ajoutent 5 tours, avec au plus 50 tours restants.
- **Achat du Tie-Break** (badge « ACHAT BONUS ») : **75× la mise** pour lancer directement le bonus avec 10 tours gratuits. Le tour acheté montre 3 Trophées, puis le Tie-Break se déroule normalement. Le RTP exact de ce mode est de 96,482 %. Une confirmation affiche le prix et le RTP. Le badge peut être désactivé par juridiction.
- **Tours automatiques** : 10, 25, 50 ou 100 tours. La **limite de perte est obligatoire**. Arrêts optionnels sur un gros gain unitaire et au déclenchement du bonus (activé par défaut). Le bouton Stop arrête la série après le tour en cours, et la barre d'espace arrête aussi. Désactivable par juridiction.
- Gain maximal : 5 000× la mise. Ce gain est **réellement présent** dans les fichiers Stake.
- RTP : **96,487 %** (calcul exact). Volatilité élevée : écart-type de 7,8× la mise. Bonus en moyenne une fois tous les 174 tours.

## Finitions visuelles (v2.1)

- Les personnages **débordent de leur carte** (la tête dépasse le cadre). Ils ont une deuxième couche d'ombre, un liseré de lumière et un motif de fond propre à chacun : losanges VIP pour le Président, lignes de court pour la Championne, damier de tableau pour l'Arbitre, filet pour le Ramasseur, empreintes de pattes pour le Bulldog.
- Les plaques de score sont agrandies et remplissent mieux la case sur mobile.
- Le **décor est animé** : la tribune ondule doucement et **saute de joie** sur les gros gains et au Tie-Break, et les fanions oscillent. Les rouleaux s'écrasent légèrement à l'atterrissage et les symboles gagnants se dandinent.

## Présentation (le résultat est toujours fixé avant l'animation)

- Les rouleaux défilent sur leurs vraies bandes et s'arrêtent sur les positions tirées par le serveur.
- Les gains sont mis en valeur symbole par symbole (cadres jaunes, nombre de façons, montant). Les gains inférieurs ou égaux à la mise ne sont pas célébrés.
- Tie-Break : écran « TIE-BREAK ! ». À chaque Smash, la balle vole vers le cadran RALLY et l'aiguille avance, puis vient l'écran récapitulatif.
- Gros gains (≥ 10× la mise **débitée**, soit 10 × 75 × la mise pour un bonus acheté) : célébration avec pluie de balles et tribune en délire, qu'un toucher écourte sans changer le montant.

## Production 100 % par code

- `game/art/build-art.mjs` dessine tout en SVG (personnages, décor, tableau, logo, cadran), puis `game/art/rasterize.mjs` les rend en PNG avec Chromium.
- `game/audio/synth.py` synthétise tous les sons (balles, rebonds, swoosh, carillons, applaudissements) et les musiques en boucle.
- **Limite assumée** : un style graphique fort et des personnages cartoon sont produits ici à un niveau professionnel. Des illustrations *peintes* ou très détaillées, comme celles de certains jeux concurrents, demanderaient un illustrateur ou un outil d'IA d'image (voir `ASSETS_AND_LICENSES.md`).

## Accessibilité et confort

- Mode « réduire les animations », qui suit aussi le réglage système.
- Mode rapide, désactivable par juridiction.
- Volumes séparés (général, musique, effets) ; son coupé quand l'onglet est masqué.
- Navigation au clavier ; la barre d'espace lance un tour.
- Langues : français et anglais.
