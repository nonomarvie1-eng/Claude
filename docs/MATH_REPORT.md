# Rapport mathématique — Golden Rally

Version math : **1.0.0** · généré automatiquement par `math/rally_math/report.py` à partir des sorties de calcul (aucun chiffre saisi à la main).

## 1. Modèle

- Grille 5 × 3, **20 lignes fixes**, gains de gauche à droite, mise totale = 1 (toutes les valeurs sont des multiples de la mise totale).
- Bandes de rouleaux : `math/reels/BASE.csv` (jeu de base) et `math/reels/FREE.csv` (tours gratuits). Chaque position d'arrêt est équiprobable.
- Cycle complet du jeu de base : **168 490 125** grilles ; cycle des tours gratuits : **25 690 112** grilles.
- Wild (Raquette d'Or) sur les rouleaux 2-4, remplace tout sauf le Scatter. Scatter (Trophée) paie partout ; 3/4/5 → 10/12/15 tours gratuits.
- Multiplicateur « Rally » pendant les tours gratuits : ×1 → ×2 → ×3 → ×4 → ×5 → ×6 → ×8 → ×10, indexé sur le nombre de Wilds tombés depuis le début du bonus ; appliqué aux gains de ligne du tour où le Wild tombe. Relance : 3+ Scatters = +5 tours (50 restants max).
- Plafond de gain : **5 000× la mise** par tour.

### Table des gains (× mise totale, par ligne)

| Symbole | 3 | 4 | 5 |
|---|---|---|---|
| Raquette d'Or (W) | 2 | 10 | 50 |
| Balle d'Or (H1) | 2 | 10 | 50 |
| Chaise d'arbitre (H2) | 1.5 | 6 | 25 |
| Tube de balles (H3) | 1.2 | 4 | 15 |
| Casquette du club (H4) | 1 | 3 | 10 |
| Avantage (L1) | 0.5 | 1.5 | 5 |
| Quarante (L2) | 0.4 | 1.2 | 4 |
| Trente (L3) | 0.3 | 1 | 3 |
| Quinze (L4) | 0.2 | 0.8 | 2.2 |
| Trophée (S, n'importe où) | 2 | 10 | 50 |

## 2. Résultats exacts (énumération complète + chaîne de Markov)

| Indicateur | Valeur |
|---|---|
| **RTP théorique total** | **96.4857 %** |
| dont jeu de base (lignes) | 62.793 % |
| dont Scatters du jeu de base | 1.662 % |
| dont tours gratuits | 32.030 % |
| Fréquence de gain (tour gagnant) | 37.98 % (1 sur 2.63) |
| Fréquence du bonus | 1 sur 144.5 (0.6919 %) |
| Gain moyen d'un bonus | 46.29× |
| Écart-type par tour (volatilité) | 6.526× (jeu de base seul : 1.649×) |
| Résidu numérique de la chaîne de Markov | 2.4e-12 |

| Déclenchement | Tours | Gain moyen | Écart-type | Tours joués (moy.) | P(atteindre ×10) | Multiplicateur final moyen |
|---|---|---|---|---|---|---|
| 3 Trophées (p = 6.600e-03) | 10 | 45.56× | 57.94× | 10.43 | 27.0 % | ×7.30 |
| 4 Trophées (p = 3.134e-04) | 12 | 60.94× | 69.45× | 12.52 | 46.8 % | ×8.31 |
| 5 Trophées (p = 5.769e-06) | 15 | 85.97× | 84.97× | 15.65 | 72.7 % | ×9.28 |

Limite connue : la forme fermée n'inclut pas le plafond de 5 000× (il faudrait la loi complète du total du bonus). Son effet est mesuré ci-dessous par simulation : aucun tour plafonné observé, effet inférieur à la précision de toute mesure réalisable.

## 3. Contrôle Monte-Carlo (moteur de référence, tours indépendants)

Générateur : numpy PCG64, SeedSequence.spawn per worker, graine 20261115.

| Indicateur | Simulé | Exact |
|---|---|---|
| Tours simulés | 10 000 000 | — |
| RTP | 96.203 % ± 0.402 % (IC 95 %) | 96.486 % |
| Écart normalisé z | -1.38 | (|z| < 2 attendu) |
| Fréquence de gain | 37.97 % | 37.98 % |
| Bonus 1 sur | 145.3 | 144.5 |
| Écart-type | 6.484 | 6.526 |
| RTP base / bonus | 64.491 % / 31.713 % | 64.455 % / 32.030 % |
| Tours gratuits joués par bonus | 10.53 | — |
| Bonus terminés à ×10 | 37.2 % | — |
| Tours plafonnés à 5 000× | 0 | — |
| Plus gros gain observé | 1389.2× | plafond 5 000× |

![Distribution des gains](img/win_distribution.png)

![RTP par session](img/session_rtp.png)

Sur une session de 10 000 tours, le RTP observé a un écart-type d'environ **nan points** : un joueur ou un opérateur peut s'écarter largement de 96,49 % à court terme. C'est la conséquence normale de la volatilité, pas une anomalie.

## 4. Fichiers Stake Engine (table de correspondance publiée)

- 110 500 tours enregistrés (« books »)  pondérés par strates aux probabilités exactes (pas de bonus / bonus à 3  4  5 Trophées)  puis calibrés par basculement exponentiel minimal à l'intérieur de chaque strate.
- **RTP de la table publiée : 96.48565 %** (écart au modèle exact : 8.7e-12).
- Écart-type : 6.608× · fréquence de gain : 37.92 % · gain maximal présent dans la table : **1137.1×**.

| Strate | Probabilité | Books | Moyenne visée | Moyenne échantillon | Divergence KL | Poids max / uniforme |
|---|---|---|---|---|---|---|
| no_bonus | 9.9308e-01 | 100000 | 0.6309× | 0.6304× | 4.9e-08 | 1.0128 |
| bonus_3_scatters | 6.5998e-03 | 8000 | 47.7751× | 47.5948× | 4.7e-06 | 1.0546 |
| bonus_4_scatters | 3.1344e-04 | 2000 | 71.0421× | 71.0436× | 1.8e-10 | 1.0000 |
| bonus_5_scatters | 5.7689e-06 | 500 | 135.9739× | 136.7830× | 4.2e-05 | 1.0091 |

Empreintes SHA-256 : books `8234273d3996f954…`, table `aefc1ce28450deac…`.

**Important** — sur Stake Engine, le serveur ne peut tirer que des tours présents dans les books. Le gain maximal *réellement atteignable* en production est donc celui de la table (1137.1×), pas le plafond théorique de 5 000×. Avant soumission, il faudra soit afficher ce maximum, soit ajouter une strate de queue (échantillonnage d'importance) contenant des tours proches du plafond. Voir `docs/DISTRIBUTION_READINESS.md`.

## 5. Vérification par l'outil officiel (engineio/math-sdk)

- Commit du SDK : `141b4e89065ac4400769709a919259a923430c4d`
- Format de la table et des books : conforme ; paiements books = table : conforme.
- Problèmes bloquant la soumission : **0** · contrôles de risque en échec : **0**.
- RTP mesuré par l'outil : 96.49 % (limites de soumission du SDK : 96,0 %–96,7 %) · écart-type : 6.61.

Cette vérification automatique n'est **pas** une approbation : l'approbation relève de Stake Engine et, selon les marchés, d'un laboratoire de certification.

## 6. Indépendance des tours

Le résultat d'un tour est une fonction pure des positions d'arrêt tirées pour ce tour. Aucun paramètre ne dépend du solde, de l'historique, des gains précédents ou du comportement du joueur. Les tests `test_determinism_and_replay` et `test_independence_of_rounds_order` le vérifient ; sur Stake Engine, chaque tour est un tirage indépendant dans la table publiée.
