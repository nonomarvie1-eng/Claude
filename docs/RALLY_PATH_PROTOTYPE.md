# RALLY PATH — prototype expérimental (Championship Night)

> Statut : **PROTOTYPE**. Il tourne uniquement dans le « Labo Rally Path » de la démo (Réglages). Il n'y a **ni mise débitée ni gain crédité**. Il ne fait pas partie des modes Stake. Le jeu normal v6 (THE FINAL SET), ses rouleaux, sa table de gains et son RTP **ne changent pas** : un test le vérifie.

## 1. Audit de départ (état du projet avant le prototype)

| Domaine | État |
|---|---|
| Moteur 6×5, 15 625 façons, Python (référence) + port TS (parité testée) | **Fonctionnel, vérifié** (pytest, vitest, fixtures de parité) |
| RNG : démo = CSPRNG navigateur avec rejet du biais ; Stake = tirage côté RGS | **Fonctionnel**. Aucun changement de RNG dans ce prototype |
| 11 symboles, table de gains, RTP 96,46–96,56 % par mode, vérificateur math-sdk | **Fonctionnel, vérifié** (v6) |
| Bonus v6 THE FINAL SET (Court Control, Power Shots, Hawk-Eye…) | **Fonctionnel**, mais jugé trop chargé par la nouvelle mission → candidat au remplacement |
| Court Takeover (Championship Night, 3 zones) | **Abandonné**, conservé sur la branche locale `wip/court-takeover-draft` |
| Cinématiques 3D, vrais assets finaux | **Non réalisé** (assets temporaires) |
| Interface mobile (9 formats testés en e2e) | **Fonctionnel, vérifié** dans Chromium uniquement |
| Rally Path (ce document) | **Expérimental** : règles, maths exactes, tests, labo jouable |

Version stable préservée : commit `26785c5` (v6) et branches `backup/before-final-set`, `backup/before-championship-night`.

## 2. Règles exactes (version prototype)

- **Balle d'or (G)** : nouveau symbole, présent **uniquement sur le rouleau 1**. Ce n'est ni un Wild ni un Scatter. Elle ne paie rien en façons et ne remplace aucun symbole.
- **Service** : une Balle d'or sur le rouleau 1 sert. La balle avance rouleau par rouleau. Depuis la rangée r du rouleau i, elle est renvoyée sur le rouleau i+1 par une **raquette** (symbole H4) placée sur la rangée r, r−1 ou r+1. Sans raquette à l'une de ces trois places, l'échange s'arrête.
- **Longueur** = nombre de coups, service compris (1 à 6). On ne paie qu'**un seul Rally Path par tour** : le plus long.
- **Choix du chemin affiché (déterministe)** : s'il y a plusieurs balles, on prend celle qui donne l'échange le plus long ; à égalité, la plus haute. À chaque coup, on prend la suite qui mène à l'échange le plus long ; à égalité, la même rangée, puis la rangée du dessus, puis celle du dessous. La longueur, et donc le gain, ne dépendent pas de ce choix.
- **Récompense** (× mise) : 1 coup → 0 ; 2 → 2 ; 3 → 8 ; 4 → 30 ; 5 → 100.
- **6 coups = CHAMPIONSHIP SHOT** : le gain est tiré par le moteur dans cette table (1 tirage supplémentaire sur 1 000, fait à chaque tour, que l'échange soit complet ou non) :

| Gain | 150× | 300× | 750× | 1 500× | 4 000× |
|---|---|---|---|---|---|
| Poids / 1 000 | 450 | 300 | 170 | 60 | 20 |

  Moyenne 455,5×. L'animation ne décide de rien : elle affiche la valeur déjà présente dans l'événement `rallyPath`.
- Le gain Rally Path est **ajouté** au gain des façons, mais affiché à part (plaque « RALLY PATH · n COUPS · montant » en haut du cadre, la plaque des façons reste en bas). Aucune double comptabilisation : un test vérifie que façons + Rally Path + scatters = gain final.
- **RALLY CHALLENGE** (exactement 3 scatters) : 8 tours, Rally Path actif, gains normaux conservés, Championship Shot possible, sans multiplicateur ni zone ni compteur. Panneau : tours, événement en cours, gain total.
- **THE GRAND FINAL** (4 scatters ou plus) : 12 tours + **SECOND SERVE** une seule fois. Dans la version testée, le premier tour dont l'échange s'arrête avant le 3ᵉ coup (longueur 1 ou 2) ajoute 1 tour gratuit indépendant, affiché dans le compteur. Voir §5 : cette règle se déclenche trop souvent.

### Différence avec les façons et les mécaniques « à chemin »

- Les **façons** comptent, rouleau par rouleau, des symboles identiques sans contrainte de position : tout est multiplié. Le Rally Path impose une **continuité géométrique**, au plus une rangée d'écart entre deux coups. Il part d'un **point d'origine unique** (la Balle d'or) et suit **un seul chemin**. Deux grilles avec les mêmes comptes de raquettes par rouleau peuvent donner 1 coup ou 6 coups.
- Les **lignes de paiement** classiques sont fixes, définies à l'avance. Ici, le chemin est trouvé sur la grille à chaque tour. Il ressemble davantage aux mécaniques de « chemin adjacent » (cluster et connexions), mais en restant **linéaire et orienté de gauche à droite**, avec une seule source. C'est ce qui le rend lisible comme un échange de tennis.
- Pas de copie : aucun nom, visuel ou code repris d'un jeu existant. Les références citées dans la mission servent uniquement de niveau de qualité.

## 3. Variante retenue et pourquoi

Avec les rouleaux actuels sans modification, le prototype ne passait pas l'évaluation : 85 % des Balles d'or s'arrêtent dès le service et le Rally Challenge valait environ 6×. Changements appliqués **au prototype seulement** :

1. Les rouleaux de bonus du prototype ont 35 raquettes par rouleau, aucun scatter, et 6 Balles d'or sur le rouleau 1. En jeu de base, il y a 2 Balles d'or sur le rouleau 1 et les rouleaux normaux.
2. La raquette paie très peu en façons dans le prototype (3, 4 ou 5 rouleaux → 0,1× ; 6 → 0,2×). Sans cela, les rouleaux denses en raquettes faisaient exploser les gains en façons (17,8× par tour). Le changement passe par un gestionnaire de contexte qui restaure la table : un test vérifie que la table du jeu normal reste intacte.

## 4. Mathématiques (exactes, puis contrôlées par simulation)

Méthode exacte : les rouleaux sont indépendants. La longueur ne dépend que des rangées où se trouvent les raquettes. On propage donc l'ensemble des rangées atteignables, soit 32 états, rouleau par rouleau. Les gains en façons sont calculés exactement par polynômes générateurs (`exact.joint_stats`). Fichiers : `math/reports/rally_path_exact.json` (exact) et `math/reports/rally_path_sim.json` (simulation, graine 2026).

| | Jeu de base (prototype) | Tours de bonus |
|---|---|---|
| P(Balle d'or) par tour | 9,43 % | 22,73 % |
| P(au moins un renvoi \| balle) | 15,0 % | 44,7 % |
| Longueur \| balle : 1 / 2 / 3 / 4 / 5 / 6 | 84,95 / 12,04 / 2,26 / 0,61 / 0,11 / 0,03 % | 55,28 / 25,45 / 10,40 / 4,62 / 1,85 / 2,40 % |
| Championship Shot | 1 tour sur 36 906 | 1 tour sur 183 |
| Valeur moyenne des façons / tour | 0,602× | 2,189× |
| Valeur moyenne du Rally Path / tour | 0,0798× | — |

Bonus (exact, contrôlé par 400 000 bonus simulés par niveau) :

| | Rally Challenge | The Grand Final |
|---|---|---|
| Espérance exacte | 45,71× | 73,78× |
| Simulation (IC 95 %) | 45,77× [45,25 ; 46,29] | 73,58× [72,92 ; 74,24] |
| Écart-type | 167× | 212× |
| Médiane / P(< 10×) | 12,2× / 43,3 % | 25,7× / 19,5 % |
| P(≥ 100×) / P(≥ 1 000×) | 9,98 % / 0,38 % | 16,5 % / 0,64 % |
| P(au moins 1 Championship Shot) | 4,3 % | 6,8 % |
| P(Second Serve) | — | 91,2 % (exact et simulé) |

RTP d'une partie prototype complète (exact) : façons du jeu de base 60,22 % + Rally Path 7,98 % + scatters 1,23 % + Rally Challenge 24,58 % + Grand Final 2,17 % = **96,18 %**. La simulation donne 96,09 % sur 10 M tours, IC 95 % [95,16 ; 97,02]. L'écart-type par tour est de 15,0× et la fréquence de gain de 29,7 %. Le gain maximal est le plafond 5 000× (atteint en simulation dans le Grand Final). Il n'existe **aucun prix d'achat** pour ces bonus prototypes, et aucun n'est affiché.

## 5. Évaluation sur les 5 critères

| Critère | Verdict | Commentaire |
|---|---|---|
| Originalité | ✅ | Un seul point d'origine, chemin continu, longueur = récit d'un échange. Distinct des façons (§2). |
| Lisibilité | ✅ (à confirmer sur joueurs) | Balle d'or bien distincte (médaillon marine, feutre doré). Chaque coup est numéroté. La plaque Rally Path est séparée du gain des façons. Plus simple que THE FINAL SET : 1 règle au lieu de 6 coups spéciaux, zones, marques et Hawk-Eye. |
| Potentiel | 🟡 | Volatilité forte, comme demandé : écart-type du RC 167× contre 40,5× pour l'ancien Rally Challenge, maximum 5 000×. Mais 43 % des Rally Challenge rapportent moins de 10×, et **le Grand Final (73,8×) vaut moins que l'ancien (97,8×)** et seulement 1,6 fois le RC. |
| Animation | ✅ | Révélation 0,3 s, trajet 0,15 à 0,24 s par coup (au plus 1,1 s), arrêt net, Championship Shot ≈ 2,5 s, Second Serve 1,1 s. Tout est accélérable par toucher, et le résultat est identique (test e2e). |
| Intégration | ✅ | Même grille 6×5, mêmes symboles, port TS en parité exacte. Le jeu normal n'est pas touché. |

**Problèmes trouvés et propositions (non appliquées, à valider) :**
1. **Second Serve quasi automatique** (91,2 % des Grand Final). Variantes calculées :
   - « dernière balle » : seul le dernier tour déclenche, si son échange s'arrête avant le 3ᵉ coup → **18,3 %** ;
   - « faute de service » : longueur 1 sur n'importe quel tour → 80,0 % ;
   - longueur exactement 2 → 51,1 %.

   Recommandation : la variante « dernière balle ». Elle est rare, a un sens tennistique (une seconde balle en fin de match) et coûte peu : le Grand Final passerait de 73,8× à environ 69,6×, soit −0,1 point de RTP global.
2. **Écart RC / GF trop faible** : passer de 6 à 8 Balles d'or sur le rouleau 1 des tours du Grand Final, ou utiliser une table de Championship Shot plus haute en Grand Final. À recalibrer par le calcul exact avant tout changement de prix.
3. **Jeu de base** : le Rally Path y est rare et court (85 % sans renvoi). C'est voulu pour la volatilité, mais la Balle d'or doit rester une promesse et non une déception. À tester sur joueurs.

## 6. Labo jouable (démo)

Réglages → « LABO RALLY PATH ». Le labo propose :
- 3 lancements aléatoires : Rally Path, Rally Challenge, The Grand Final ;
- une option « le bouton Lancer joue un tour prototype » ;
- **8 scénarios reproductibles** (tirages enregistrés, rejoués exactement) : balle sans retour, échange court, 3 coups, 5 coups, 6 coups / Championship Shot, Rally Challenge sans événement exceptionnel, Grand Final avec Second Serve, Grand Final avec Championship Shot.

Les scénarios ne modifient aucune probabilité : ils rejouent des tirages enregistrés. Les montants s'affichent avec le bandeau « test non crédité » et le solde ne bouge pas (test e2e).

## 7. Fichiers

- `math/rally_math/rally_path.py` : règles, moteur à événements, maths exactes, simulateurs.
- `math/rally_math/export_rally_proto.py` → `shared/rally-path-proto.json` : rouleaux, règles, stats, scénarios, fixtures de parité.
- `math/tests/test_rally_path.py` : 17 tests (règles, départage, DP = force brute, exact = simulation, Second Serve une fois, pas de double comptabilisation, rejeu, jeu normal intact).
- `game/src/engine/rallyPath.ts` + `rallyPath.test.ts` : port TS et parité.
- `game/src/render/scene.ts` (méthodes `rallyPath`, `championshipShot`, `protoBonusStart`, `secondServe`, `protoBonusEnd`), `game/src/game/player.ts`, `controller.ts` (`labRound`), `ui/Settings.svelte`.
- `game/src/assets/img/sym_G.webp` : **asset temporaire**, dérivé recoloré du symbole balle du pack. À remplacer par une illustration finale.
- `game/e2e/lab-e2e.mjs` : tests et captures 320×568, 375×812, 390×844, 430×932, 768×1024, 1440×900.

## 8. Limites connues

- Chromium uniquement, rendu logiciel. Les durées mesurées en e2e (de 5 à 30 s par tour) incluent la présentation complète des gains en façons et le ralentissement du rendu logiciel. Elles ne représentent pas un vrai téléphone.
- Pas de test de compréhension auprès de joueurs : la comparaison avec l'ancien bonus est analytique (§5).
- Les bonus prototypes ne sont ni achetables ni exportés vers Stake. Un passage en production demande de choisir la règle du Second Serve, de recalibrer, de calculer les prix, d'exporter les books et de passer le vérificateur.
