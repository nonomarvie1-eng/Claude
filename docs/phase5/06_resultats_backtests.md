# Phase 5 — Résultats des backtests (lot 5-01)

*Généré par `python -m nexus.research.report_5` depuis `results/batch_5_01_indices/`.*

*Données : Kenneth R. French Data Library (dérivées de CRSP), usage de recherche, non redistribuées ; H5-EXP : Binance Vision (CC BY-NC-SA 4.0).*

Essais au registre après le lot : 176 (avant Monte Carlo et H5-EXP).

## 1. Reproduction des chiffres annoncés (RSI 2, US, 1993-2009, notionnel 100 %, sans stop)

| | Trades | Gagnants | Rendement moyen par trade | Profit factor | Temps investi | Multiple du capital |
|---|---|---|---|---|---|---|
| NEXUS, coûts NEXUS | 141 | 70.2 % | +0.42 % | 2.25 | 11.6 % | 1.77 (17 ans) |
| NEXUS, sans coûts | 141 | 72.3 % | +0.51 % | 2.70 | 11.6 % | 2.03 (17 ans) |
| Annoncé (SPY 1993 → ≈ 2026) | — | 76.6 % | +0.63 % | 2.98 | 10.6 % | 4,14 (sur ≈ 33 ans) |

Écarts attendus : indice CRSP (pas SPY), exécution à la clôture, fenêtre plus courte. L'ordre de grandeur est reproduit ; le taux de réussite et le gain moyen sont un peu inférieurs.

Stops catastrophe (3 × écart-type sur 5 séances, avant 2010) : US 6 %, Europe 8 %, Japan 11 %, AsiaPacExJapan 9 %.

## 2. Statistiques par trade (fenêtre principale ; US 2010-2023 S1, international 1991-2023 S1)

| Stratégie | Trades | Gagnants | Gain moyen | Perte moyenne | Rendement net moyen [IC95] | PF | Pire trade | Durée médiane (j) | Temps investi |
|---|---|---|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | 104 | 70.2 % | +1.02 % | -1.61 % | +0.236 % [-0.119 ; +0.545] | 1.49 | -10.64 % | 4 | 10.8 % |
| RSI 2 + stop (US) | 104 | 70.2 % | +1.02 % | -1.79 % | +0.181 % [-0.200 ; +0.512] | 1.34 | -8.33 % | 4 | 10.5 % |
| RSI 30/50 + stop (US) | 88 | 80.7 % | +1.40 % | -2.67 % | +0.616 % [+0.115 ; +1.049] | 2.19 | -8.33 % | 6 | 11.9 % |
| Double 5 + stop (US) | 211 | 75.4 % | +1.08 % | -2.25 % | +0.261 % [-0.014 ; +0.509] | 1.47 | -8.92 % | 6 | 30.1 % |
| RSI 2 + stop (Europe) | 223 | 66.4 % | +0.94 % | -1.48 % | +0.124 % [-0.093 ; +0.332] | 1.25 | -9.52 % | 5 | 9.9 % |
| RSI 2 + stop (Japon) | 184 | 72.3 % | +1.40 % | -1.96 % | +0.466 % [+0.178 ; +0.725] | 1.86 | -6.73 % | 4 | 7.9 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | 252 | 59.1 % | +0.93 % | -1.84 % | -0.201 % [-0.455 ; +0.042] | 0.73 | -11.16 % | 6 | 12.9 % |

## 3. Tests statistiques

| Stratégie | Entrées aléatoires (même régime, mêmes durées) : moyenne | 95e centile | p | p BH | Aléatoire + même sortie : gagnants | Alpha vs passif même exposition %/an [IC95] |
|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | +0.053 % | +0.304 % | 0.1195 | 0.2091 | 61.0 % | +0.043 [-0.275 ; +0.352] |
| RSI 2 + stop (US) | +0.049 % | +0.297 % | 0.1982 | 0.2332 | 61.0 % | -0.004 [-0.321 ; +0.304] |
| RSI 30/50 + stop (US) | +0.083 % | +0.395 % | 0.0015 | 0.0052 | 63.0 % | +0.290 [-0.063 ; +0.639] |
| Double 5 + stop (US) | +0.093 % | +0.297 % | 0.0858 | 0.2002 | 75.2 % | +0.000 [-0.451 ; +0.425] |
| RSI 2 + stop (Europe) | +0.030 % | +0.216 % | 0.1999 | 0.2332 | 59.9 % | -0.004 [-0.133 ; +0.123] |
| RSI 2 + stop (Japon) | -0.026 % | +0.224 % | 0.0011 | 0.0052 | 60.0 % | +0.148 [+0.038 ; +0.253] |
| RSI 2 + stop (Asie-Pacifique hors Japon) | +0.076 % | +0.275 % | 0.9858 | 0.9858 | 59.2 % | -0.218 [-0.362 ; -0.077] |

Le taux de réussite des entrées **aléatoires** avec la même sortie dépasse 59 % partout : comme l'annonçait le document 2, le taux de réussite élevé vient **surtout de la règle de sortie**.

## 4. Coûts, délai, stabilité, sensibilité

| Stratégie | Coûts × 2 | 0,20 %/côté | Exécution à t+1 | Sous-périodes | 1928-1992 (US) | Grille : part positive |
|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | +0.141 % | -0.105 % | +0.299 % | 2010-2015 +0.13 ; 2015-2020 +0.25 ; 2020-2023 +0.39 | -0.336 % (n = 539) | 100 % |
| RSI 2 + stop (US) | +0.087 % | -0.160 % | +0.317 % | 2010-2015 +0.19 ; 2015-2020 +0.19 ; 2020-2023 +0.15 | -0.321 % (n = 543) | 94 % |
| RSI 30/50 + stop (US) | +0.509 % | +0.275 % | +0.906 % | 2010-2015 +0.72 ; 2015-2020 +0.28 ; 2020-2023 +0.96 | -0.379 % (n = 371) | 100 % |
| Double 5 + stop (US) | +0.153 % | -0.079 % | +0.158 % | 2010-2015 +0.26 ; 2015-2020 +0.25 ; 2020-2023 +0.27 | -0.270 % (n = 845) | 100 % |
| RSI 2 + stop (Europe) | +0.028 % | -0.216 % | +0.313 % | 1991-2003 +0.14 ; 2003-2013 +0.26 ; 2013-2023 -0.04 | — | 100 % |
| RSI 2 + stop (Japon) | +0.371 % | +0.125 % | +0.507 % | 1991-2003 +0.22 ; 2003-2013 +0.33 ; 2013-2023 +0.73 | — | 94 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | -0.303 % | -0.541 % | -0.051 % | 1991-2003 -0.13 ; 2003-2013 -0.20 ; 2013-2023 -0.29 | — | 22 % |

## 5. Résultats en euros (1 000 €, effet de change ignoré)

| Stratégie | Taille | Capital final | Gain € | Rendement total | Annualisé | Max DD | Sharpe | Frais € | Financement € |
|---|---|---|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | NEXUS 0,5 % | 1021 € | +21 | +2.1 % | +0.15 % | 1.3 % | +0.27 | 5.3 | 3.7 |
| RSI 2 d'origine, sans stop (US) | prudent 0,25 % | 1010 € | +10 | +1.0 % | +0.08 % | 0.7 % | +0.27 | 5.3 | 3.7 |
| RSI 2 d'origine, sans stop (US) | notionnel 100 % (hors règle) | 1256 € | +256 | +25.6 % | +1.70 % | 16.0 % | +0.28 | 69.2 | 50.1 |
| ↳ références | achat-conservation : +407.8 % ; filtre SMA seul (100 %) : +94.7 %, DD 22.7 % | | | | | | | | |
| RSI 2 + stop (US) | NEXUS 0,5 % | 1016 € | +16 | +1.6 % | +0.12 % | 1.2 % | +0.23 | 5.3 | 3.6 |
| RSI 2 + stop (US) | prudent 0,25 % | 1008 € | +8 | +0.8 % | +0.06 % | 0.6 % | +0.23 | 5.3 | 3.6 |
| RSI 2 + stop (US) | notionnel 100 % (hors règle) | 1183 € | +183 | +18.3 % | +1.25 % | 14.3 % | +0.23 | 69.5 | 48.2 |
| ↳ références | achat-conservation : +407.8 % ; filtre SMA seul (100 %) : +94.7 %, DD 22.7 % | | | | | | | | |
| RSI 30/50 + stop (US) | NEXUS 0,5 % | 1046 € | +46 | +4.6 % | +0.33 % | 1.5 % | +0.60 | 4.5 | 4.4 |
| RSI 30/50 + stop (US) | prudent 0,25 % | 1023 € | +23 | +2.3 % | +0.17 % | 0.7 % | +0.60 | 4.5 | 4.4 |
| RSI 30/50 + stop (US) | notionnel 100 % (hors règle) | 1680 € | +680 | +68.0 % | +3.92 % | 16.9 % | +0.61 | 70.6 | 69.5 |
| ↳ références | achat-conservation : +407.8 % ; filtre SMA seul (100 %) : +94.7 %, DD 22.7 % | | | | | | | | |
| Double 5 + stop (US) | NEXUS 0,5 % | 1047 € | +47 | +4.7 % | +0.34 % | 1.8 % | +0.45 | 10.8 | 10.6 |
| Double 5 + stop (US) | prudent 0,25 % | 1023 € | +23 | +2.3 % | +0.17 % | 0.9 % | +0.45 | 10.8 | 10.6 |
| Double 5 + stop (US) | notionnel 100 % (hors règle) | 1662 € | +662 | +66.2 % | +3.84 % | 20.2 % | +0.45 | 162.8 | 165.6 |
| ↳ références | achat-conservation : +407.8 % ; filtre SMA seul (100 %) : +94.7 %, DD 22.7 % | | | | | | | | |
| RSI 2 + stop (Europe) | NEXUS 0,5 % | 1017 € | +17 | +1.7 % | +0.05 % | 1.3 % | +0.16 | 8.4 | 10.1 |
| RSI 2 + stop (Europe) | prudent 0,25 % | 1009 € | +9 | +0.9 % | +0.03 % | 0.6 % | +0.16 | 8.4 | 10.1 |
| RSI 2 + stop (Europe) | notionnel 100 % (hors règle) | 1283 € | +283 | +28.3 % | +0.78 % | 19.0 % | +0.17 | 153.0 | 177.5 |
| ↳ références | achat-conservation : +1029.7 % ; filtre SMA seul (100 %) : +265.5 %, DD 34.2 % | | | | | | | | |
| RSI 2 + stop (Japon) | NEXUS 0,5 % | 1040 € | +40 | +4.0 % | +0.12 % | 0.7 % | +0.42 | 5.1 | 5.5 |
| RSI 2 + stop (Japon) | prudent 0,25 % | 1020 € | +20 | +2.0 % | +0.06 % | 0.3 % | +0.42 | 5.1 | 5.5 |
| RSI 2 + stop (Japon) | notionnel 100 % (hors règle) | 2274 € | +1274 | +127.4 % | +2.60 % | 14.4 % | +0.42 | 157.0 | 157.7 |
| ↳ références | achat-conservation : +110.1 % ; filtre SMA seul (100 %) : -27.5 %, DD 65.1 % | | | | | | | | |
| RSI 2 + stop (Asie-Pacifique hors Japon) | NEXUS 0,5 % | 972 € | -28 | -2.8 % | -0.09 % | 3.4 % | -0.26 | 8.3 | 10.9 |
| RSI 2 + stop (Asie-Pacifique hors Japon) | prudent 0,25 % | 986 € | -14 | -1.4 % | -0.04 % | 1.7 % | -0.26 | 8.3 | 10.9 |
| RSI 2 + stop (Asie-Pacifique hors Japon) | notionnel 100 % (hors règle) | 571 € | -429 | -42.9 % | -1.74 % | 48.6 % | -0.26 | 124.6 | 169.7 |
| ↳ références | achat-conservation : +1211.5 % ; filtre SMA seul (100 %) : +555.0 %, DD 27.2 % | | | | | | | | |

## 6. Critères et verdicts

| Stratégie | C1 | C2 | C3 | C4 | C5 | C6 | Monte Carlo | Compatibilité Cubrik | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | non | non | oui | oui | non | oui | non | Native (si RSI 2 accepté) ; sans stop : contraire à la règle NEXUS | **rejeté** |
| RSI 2 + stop (US) | non | non | oui | oui | non | oui | non | Native (si RSI 2 accepté) | **rejeté** |
| RSI 30/50 + stop (US) | oui | oui | oui | oui | non | oui | oui | Native | **prometteur** |
| Double 5 + stop (US) | non | non | oui | oui | non | oui | oui | À vérifier (définition de `lowest`/`highest`) | **rejeté** |
| RSI 2 + stop (Europe) | non | non | oui | oui | oui | oui | non | Native ; CFD européen à vérifier | **rejeté** |
| RSI 2 + stop (Japon) | oui | oui | oui | oui | oui | oui | oui | Native ; CFD JP225 à vérifier (en JPY, nos données sont en USD) | **candidate** |
| RSI 2 + stop (Asie-Pacifique hors Japon) | non | non | non | non | non | oui | non | Native ; instrument à vérifier | **rejeté** |

## 7. H5-EXP — gestion de l'exposition sur P4-01 (cryptos, 2020-2023 S1)

| | Trades | Rendement | Max DD | Sharpe | PF | Expo. moy. | Alpha %/an [IC95] | p | Meilleur trade € | Part du meilleur trade | P&L sans meilleur trade | P&L sans 2021 | P&L sans MATIC | Rendu depuis le sommet |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4-01 original | 103 | +124.0 % | 45.4 % | +0.82 | 3.14 | 13.4 % | +13.54 [-10.81 ; +43.84] | 0.176 | 984 | 79 % | +255 | +471 | +324 | 43.7 % |
| P4-01 + lock 1/2 | 109 | +56.5 % | 29.2 % | +0.78 | 2.30 | 10.7 % | +1.79 [-13.95 ; +19.14] | 0.410 | 394 | 70 % | +170 | +588 | +531 | 27.0 % |

Sensibilité : lock 1/3 : alpha +8.81 %/an (p 0.203), DD 38.4 % ; lock 2/3 : alpha -1.70 %/an (p 0.605), DD 20.0 % ; lock 1/2 coûts x2 : alpha +1.57 %/an (p 0.420), DD 29.5 %.

Critères (phase 4) : C1 non, C2 non, C3 oui, C4 non, C5 non, C6 non → **rejeté**.

P&L par année d'entrée (avec gestion) : 2020 +692 €, 2021 -23 €, 2022 -115 €, 2023 +12 €.
