# Golden Rally — Match Point · Modes de jeu, bonus et symboles (v5, maths 3.0.0)

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

## 3. Deux bonus

| Scatters | Bonus | Tours | Multiplicateur de départ | E[gain du bonus] | Fréquence (mode Normal) |
|---|---|---|---|---|---|
| 3 | **TIE-BREAK** | 9 | ×1 | 45,5× | 1 / 184,7 |
| 4 | **SUPER TIE-BREAK** | 12 | ×2 | 97,0× | |
| 5 | SUPER TIE-BREAK | 15 | ×2 | 145,8× | 4+ scatters : 1 / 3 371 |
| 6 | SUPER TIE-BREAK | 20 | ×2 | 241,4× | |

Échelle commune ×1 → ×2 → ×3 → ×4 → ×5 → ×6 → ×8 → ×10 → ×12 → ×15 → ×20 ; le Super Tie-Break commence un cran plus haut. 3 scatters ou plus pendant un bonus : +5 tours (50 restants maximum). La proposition « 12 tours, ×2 » a été testée et retenue : elle est équilibrable (RTP total 96,52 %). Le Super Tie-Break offre de meilleures conditions **de départ**, pas un gain supérieur garanti.

5 et 6 scatters : possibles (un scatter maximum par rouleau, 6 rouleaux) ; ils donnent le Super Tie-Break avec 15 / 20 tours et un gain scatter plus élevé.

## 4. Modes de mise (Stake Engine `index.json`)

| Mode | Coût | RTP (exact, après plafond 5 000×) | Bonus | Écart-type | Garantie |
|---|---|---|---|---|---|
| `base` — Normal | 1× | **96,524 %** | 1 / 175 (TB 1/185, STB 1/3 371) | 12,5× | — |
| `bonus_chance` — Bonus Chance | **1,4×** | **96,513 %** | 1 / 74 (TB 1/80, STB 1/990) | 17,6× | aucun bonus garanti |
| `buy_tiebreak` — Achat Tie-Break | **49,4×** | **96,522 %** | 100 % Tie-Break | 125,6× | niveau Tie-Break (exactement 3 scatters) |
| `buy_super` — Achat Super Tie-Break | **105×** | **96,406 %** | 100 % Super Tie-Break | 211,3× | niveau Super (exactement 4 scatters) |

**Comment les prix ont été obtenus.** Prix d'achat = espérance exacte du tour acheté (tour déclencheur + bonus − effet du plafond) ÷ 96,5 %, arrondie au dixième pour rester dans la fenêtre 96,0–96,7 % du SDK. Tie-Break : 47,68× ÷ 0,965 = 49,41 → **49,4×**. Super : 101,23× ÷ 0,965 = 104,90 → **105×**. Le 100× historique n'était pas cohérent avec les nouvelles maths ; aucun prix n'a été supposé à l'avance.

**Bonus Chance.** Mêmes symboles, gains et bonus ; seul le nombre de scatters par rouleau passe de 1-2 à 2. Options étudiées (table dans MATH_REPORT §5) ; retenue : coût 1,4× pour ×2,35 sur la fréquence des bonus et ×3,4 sur le Super. RTP 96,51 % contre 96,52 % en Normal (écart −0,01 pt). Les probabilités ne dépendent jamais du solde, de l'historique ni des pertes. Le mode reste choisi tant que le joueur ne revient pas à Normal ; le prix réel du prochain tour est affiché dans le HUD.

**Achats.** Deux modes distincts, jamais de tirage entre les deux niveaux. Fenêtre de confirmation avec le montant exact avant tout achat ; double achat impossible (verrou côté client + refus côté RGS d'un tour actif). En démo, aucun argent réel. Les achats et Bonus Chance se masquent via `jurisdiction.disabledBuyBonus` / `disabledBonusChance` (noms de drapeaux à confirmer avec Stake).

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
- Vérificateur officiel `engineio/math-sdk` (commit 141b4e8) : format OK pour les 4 modes, **0 problème de soumission, 6/6 contrôles de risque** par mode.
- Limites lues dans le SDK : RTP 96,0–96,7 % par mode, un mode de base à 1×, coût ≤ 50 000×, gain max ≤ 1 000 000×, écart-type de base ≥ 0,6. Débit = mise × coût du mode.
- **Non vérifiable ici** : la page « approval guidelines » de stake-engine.com est inaccessible depuis cet environnement. La recevabilité éditoriale d'un mode de type « Bonus Chance » et des achats doit être confirmée avec Stake avant toute soumission.
