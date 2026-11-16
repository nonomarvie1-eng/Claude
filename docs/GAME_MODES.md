# Golden Rally — The Final Set · Modes de jeu, bonus et symboles (v6, maths 4.0.0)

Toutes les valeurs ci-dessous viennent de `math/reports/exact.json` et `math/reports/montecarlo.json` ; le détail est dans [MATH_REPORT.md](MATH_REPORT.md). Le jeu (navigateur) n'invente aucun résultat : il présente les « books » renvoyés par le RGS (en démo : moteur TypeScript dont la parité avec le moteur Python de référence est testée).

## 1. Symboles (11) et correspondance avec les anciens identifiants

| Id moteur | Rôle | Nouveau symbole (fichier du pack) | Ancien visuel (v4) |
|---|---|---|---|
| W | Wild | WILD magenta couronné (`wild_magenta.png`) | Balle couronnée |
| S | Scatter | SCATTER stade bleu électrique (`scatter_blue.png`) | Le Central |
| H1 | Premium 1 | Ace, la mascotte (`ace_mascot.png`) | Le Champion |
| H2 | Premium 2 | Trophée doré (`gold_trophy.png`) | La Championne |
| H3 | Premium 3 | Sac de tennis (`tennis_bag.png`) | L'Arbitre |
| H4 | Premium 4 | Raquette (`tennis_racket.png`) | Trophée de la victoire |
| — | (supprimé) | — | H5 « Ace » (portrait) |
| L1 | Classique 1 | Balle de tennis (`tennis_ball.png`) | AD |
| L2 | Classique 2 | Chaussure (`tennis_shoe.png`) | 40 |
| L3 | Classique 3 | Casquette (`tennis_cap.png`) | 30 |
| L4 | Classique 4 | Gourde (`water_bottle.png`) | 15 |
| L5 | Classique 5 | Poignet éponge (`red_wristband.png`) | LOVE |

Le passage de 12 à 11 symboles (un premium en moins) **a changé les mathématiques** : avec un symbole de moins, chaque symbole restant est plus fréquent et le RTP brut montait à 160 %. Table de gains, composition des rouleaux et bonus ont été recalculés entièrement (méthode exacte + simulations, voir MATH_REPORT). Les images ont été traitées séparément (`game/art/import-pack.mjs`), les originaux sont conservés dans `game/art/pack-v5/` et les anciens sprites dans `game/art/legacy-symbols-v4/`.

Lisibilité : les symboles sont désormais **empilés** par blocs de 1 à 3 sur les rouleaux. La fréquence de gain passe de ~67 % (beaucoup de petits gains illisibles) à **27,9 %**, avec des gains plus nets.

## 2. Règles de paiement

- 6 rouleaux × 5 rangées, **15 625 façons** (5⁶, vérifié). Un symbole paie s'il est présent (ou le Wild) sur des rouleaux adjacents depuis le rouleau 1, sur 3 à 6 rouleaux ; gain = valeur × nombre de façons (produit du nombre de symboles par rouleau).
- WILD : remplace tout sauf le Scatter, absent du rouleau 1 ; en bonus, chaque Wild fait monter le multiplicateur d'un cran.
- SCATTER : au plus un par rouleau ; paie n'importe où (3 = 2×, 4 = 5×, 5 = 20×, 6 = 100× la mise), jamais multiplié.

## 3. Deux bonus : THE FINAL SET

Les tours gratuits et le multiplicateur ×1→×20 ont été **supprimés**. Les deux bonus sont des matchs joués sur la grille (Court Control, Power Shots, marques, Hawk-Eye) : voir [FINAL_SET_DESIGN.md](FINAL_SET_DESIGN.md).

| Scatters | Bonus | Échanges | Particularités | E[gain du bonus] | Fréquence (mode Normal) |
|---|---|---|---|---|---|
| 3 | **RALLY CHALLENGE** | 8 | table « Rally Challenge » | 44,79× | 1 / 184,7 |
| 4 | **THE GRAND FINAL** | 12 | plus de coups spéciaux, Hawk-Eye, Championship Point | 97,78× | 4+ : 1 / 3 371 |
| 5 / 6 | THE GRAND FINAL | 14 / 16 | idem | 114,5× / 131,2× | |

## 4. Modes de mise (Stake Engine `index.json`)

| Mode | Coût | RTP calculé | Bonus | Écart-type | Garantie |
|---|---|---|---|---|---|
| `base` — Normal | 1× | **96,54 %** ± 0,01 | 1 / 175 (RC 1/185, GF 1/3 371) | 8,2× | — |
| `bonus_chance` — Bonus Chance | **1,4×** | **96,55 %** ± 0,01 | 1 / 74 (RC 1/80, GF 1/990) | 9,8× | aucun bonus garanti |
| `buy_rally` — Achat Rally Challenge | **48,8×** | **96,56 %** ± 0,03 | 100 % Rally Challenge | 40,6× | niveau RC (exactement 3 scatters) |
| `buy_final` — Achat The Grand Final | **106,8×** | **96,46 %** ± 0,02 | 100 % Grand Final | 63,5× | niveau GF (exactement 4 scatters) |

Prix = espérance du tour acheté ÷ 96,5 %, arrondie au dixième dans la fenêtre 96,0–96,7 % : Rally Challenge 47,12× → **48,8×** ; Grand Final 103,02× → **106,8×**. Bonus Chance : 2 scatters par rouleau, coût 1,4×, bonus ×2,35 plus fréquent. Les probabilités ne dépendent jamais du solde ni de l'historique.

## 5. Affichage des connexions gagnantes

À la fin de chaque tour, pour chaque combinaison **présente dans le book** :
1. les autres symboles sont assombris ;
2. ses symboles sont encadrés dans la couleur du symbole ;
3. un tracé part du rouleau 1 (flèche) et rejoint le dernier rouleau de la combinaison (point), avec des branches vers chaque symbole ;
4. le nombre de symboles par rouleau est affiché au-dessus des rouleaux (leur produit = nombre de façons) ;
5. la plaque indique « symbole · N rouleaux · 2×1×3 = 6 façons · gain » (et le multiplicateur en bonus).

Plusieurs combinaisons : toutes ensemble, puis une par une, puis ensemble avec le total. Tout est statique et lisible sans animation. Le bouton « Revoir les gains » (barre du haut) rejoue fidèlement le dernier tour, sans effet sur le solde. Un test navigateur vérifie que les combinaisons dessinées sont exactement celles du book.

## 6. Compatibilité Stake Engine

- Fichiers : `stake/publish_files/index.json` (4 modes), `books_<mode>.jsonl.zst`, `lookUpTable_<mode>_0.csv`.
- Vérificateur officiel `engineio/math-sdk` (commit 141b4e8) : format OK pour les 4 modes (`base`, `bonus_chance`, `buy_rally`, `buy_final`), **0 problème de soumission, 6/6 contrôles de risque** par mode.
- Limites lues dans le SDK : RTP 96,0–96,7 % par mode, un mode de base à 1×, coût ≤ 50 000×, gain max ≤ 1 000 000×, écart-type de base ≥ 0,6. Débit = mise × coût du mode.
- **Non vérifiable ici** : la page « approval guidelines » de stake-engine.com est inaccessible depuis cet environnement. La recevabilité éditoriale d'un mode de type « Bonus Chance », des achats et d'un bonus non « free spins » doit être confirmée avec Stake avant toute soumission.
