# Phase 5 — Robustesse Monte Carlo

*Généré par `python -m nexus.research.report_5`.*

*Données : Kenneth R. French Data Library (dérivées de CRSP), usage de recherche, non redistribuées ; H5-EXP : Binance Vision (CC BY-NC-SA 4.0).*

**Ces simulations ne donnent pas une probabilité de réussite future.** Elles mesurent la fragilité du résultat historique. Les drawdowns sont calculés sur un capital composé et solvable (≤ 100 %).

## 1. Dimensionnement NEXUS (0,5 % de risque au stop), 10 000 simulations

| Stratégie | Méthode | Rendement médian | 5e percentile | 95e percentile du DD | Simulations perdantes | P(DD > 10 %) |
|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | mélange de l'ordre | +2.05 % | +2.05 % | 1.72 % | 0.0 % | 0.00 % |
| RSI 2 d'origine, sans stop (US) | bootstrap par blocs mensuels | +2.13 % | -0.59 % | 2.35 % | 9.4 % | 0.00 % |
| RSI 2 d'origine, sans stop (US) | suppression 5 % | +1.90 % | +1.52 % | 1.13 % | 0.0 % | 0.00 % |
| RSI 2 d'origine, sans stop (US) | suppression 10 % | +1.79 % | +1.21 % | 1.14 % | 0.0 % | 0.00 % |
| RSI 2 d'origine, sans stop (US) | suppression 20 % | +1.59 % | +0.68 % | 1.16 % | 0.1 % | 0.00 % |
| RSI 2 + stop (US) | mélange de l'ordre | +1.56 % | +1.56 % | 2.00 % | 0.0 % | 0.00 % |
| RSI 2 + stop (US) | bootstrap par blocs mensuels | +1.63 % | -1.18 % | 2.71 % | 16.7 % | 0.00 % |
| RSI 2 + stop (US) | suppression 5 % | +1.42 % | +1.03 % | 1.37 % | 0.0 % | 0.00 % |
| RSI 2 + stop (US) | suppression 10 % | +1.34 % | +0.73 % | 1.41 % | 0.0 % | 0.00 % |
| RSI 2 + stop (US) | suppression 20 % | +1.21 % | +0.22 % | 1.49 % | 1.7 % | 0.00 % |
| RSI 30/50 + stop (US) | mélange de l'ordre | +4.60 % | +4.60 % | 1.70 % | 0.0 % | 0.00 % |
| RSI 30/50 + stop (US) | bootstrap par blocs mensuels | +4.70 % | +1.55 % | 2.09 % | 0.8 % | 0.00 % |
| RSI 30/50 + stop (US) | suppression 5 % | +4.29 % | +3.95 % | 1.61 % | 0.0 % | 0.00 % |
| RSI 30/50 + stop (US) | suppression 10 % | +4.04 % | +3.40 % | 1.72 % | 0.0 % | 0.00 % |
| RSI 30/50 + stop (US) | suppression 20 % | +3.60 % | +2.58 % | 1.72 % | 0.0 % | 0.00 % |
| Double 5 + stop (US) | mélange de l'ordre | +4.67 % | +4.67 % | 2.61 % | 0.0 % | 0.00 % |
| Double 5 + stop (US) | bootstrap par blocs mensuels | +4.70 % | +0.68 % | 3.03 % | 2.8 % | 0.00 % |
| Double 5 + stop (US) | suppression 5 % | +4.35 % | +3.64 % | 1.56 % | 0.0 % | 0.00 % |
| Double 5 + stop (US) | suppression 10 % | +4.14 % | +3.08 % | 1.63 % | 0.0 % | 0.00 % |
| Double 5 + stop (US) | suppression 20 % | +3.68 % | +2.18 % | 1.76 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Europe) | mélange de l'ordre | +1.74 % | +1.74 % | 1.75 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Europe) | bootstrap par blocs mensuels | +1.72 % | -0.81 % | 2.33 % | 13.0 % | 0.00 % |
| RSI 2 + stop (Europe) | suppression 5 % | +1.62 % | +1.18 % | 1.20 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Europe) | suppression 10 % | +1.54 % | +0.89 % | 1.23 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Europe) | suppression 20 % | +1.37 % | +0.43 % | 1.26 % | 0.8 % | 0.00 % |
| RSI 2 + stop (Japon) | mélange de l'ordre | +3.97 % | +3.97 % | 0.97 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Japon) | bootstrap par blocs mensuels | +3.98 % | +1.94 % | 1.07 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Japon) | suppression 5 % | +3.75 % | +3.37 % | 0.65 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Japon) | suppression 10 % | +3.56 % | +3.00 % | 0.70 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Japon) | suppression 20 % | +3.14 % | +2.37 % | 0.73 % | 0.0 % | 0.00 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | mélange de l'ordre | -2.80 % | -2.80 % | 4.17 % | 100.0 % | 0.00 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | bootstrap par blocs mensuels | -2.76 % | -5.67 % | 6.07 % | 95.1 % | 0.00 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | suppression 5 % | -2.70 % | -3.20 % | 3.61 % | 100.0 % | 0.00 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | suppression 10 % | -2.55 % | -3.31 % | 3.72 % | 100.0 % | 0.00 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | suppression 20 % | -2.28 % | -3.34 % | 3.72 % | 99.9 % | 0.00 % |

## 2. Notionnel 100 % sans levier (comme les documents ; hors règle de risque), bootstrap par blocs

| Stratégie | Rendement médian | 5e percentile | 95e percentile du DD | Simulations perdantes | P(DD > 10 %) |
|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | +26.8 % | -9.0 % | 26.1 % | 11.4 % | 73.8 % |
| RSI 2 + stop (US) | +19.3 % | -15.5 % | 29.5 % | 19.4 % | 80.5 % |
| RSI 30/50 + stop (US) | +69.9 % | +16.7 % | 23.4 % | 1.1 % | 67.5 % |
| Double 5 + stop (US) | +66.8 % | +3.1 % | 32.5 % | 4.1 % | 95.6 % |
| RSI 2 + stop (Europe) | +27.9 % | -14.9 % | 32.9 % | 15.7 % | 93.6 % |
| RSI 2 + stop (Japon) | +128.0 % | +47.2 % | 21.9 % | 0.1 % | 78.5 % |
| RSI 2 + stop (Asie-Pacifique hors Japon) | -42.6 % | -67.3 % | 69.5 % | 96.4 % | 100.0 % |

## 3. Concentration, bruit, régimes (notionnel 100 %, pour la lisibilité)

| Stratégie | Total | Sans le meilleur trade | Meilleure année | Sans la meilleure année | Part des 5 meilleurs dans les gains bruts | Bruit ±0,1 % : part positive (5e pct) | Volatilité basse / moyenne / haute (rendement moyen) |
|---|---|---|---|---|---|---|---|
| RSI 2 d'origine, sans stop (US) | +25.6 % | +20.5 % | 2015 (+7.3 %) | +17.1 % | 20 % | 100 % (+0.198 %) | +0.14 % (n = 35) / +0.60 % (n = 34) / -0.02 % (n = 35) |
| RSI 2 + stop (US) | +18.3 % | +13.5 % | 2015 (+7.3 %) | +10.3 % | 19 % | 100 % (+0.140 %) | +0.14 % (n = 35) / +0.52 % (n = 34) / -0.11 % (n = 35) |
| RSI 30/50 + stop (US) | +68.0 % | +61.2 % | 2021 (+17.3 %) | +43.2 % | 17 % | 100 % (+0.572 %) | +0.58 % (n = 30) / +0.80 % (n = 29) / +0.47 % (n = 29) |
| Double 5 + stop (US) | +66.2 % | +59.0 % | 2013 (+20.4 %) | +38.1 % | 10 % | 100 % (+0.220 %) | +0.17 % (n = 71) / +0.51 % (n = 70) / +0.11 % (n = 70) |
| RSI 2 + stop (Europe) | +28.3 % | +23.2 % | 2011 (+10.2 %) | +16.4 % | 11 % | 100 % (+0.080 %) | +0.06 % (n = 75) / +0.02 % (n = 74) / +0.29 % (n = 74) |
| RSI 2 + stop (Japon) | +127.4 % | +116.9 % | 2013 (+23.1 %) | +84.7 % | 11 % | 100 % (+0.329 %) | +0.05 % (n = 62) / +0.49 % (n = 61) / +0.86 % (n = 61) |
| RSI 2 + stop (Asie-Pacifique hors Japon) | -42.9 % | -44.8 % | 1996 (+7.8 %) | -47.1 % | 11 % | 0 % (-0.307 %) | -0.13 % (n = 84) / -0.41 % (n = 84) / -0.06 % (n = 84) |

Lecture : un rendement qui ne dépend ni du meilleur trade, ni de la meilleure année, et qui reste positif au 5e percentile, est moins fragile. Volatilité : le rendement moyen est le plus élevé en volatilité haute pour le Japon et l'Europe (cohérent avec Nagel 2012 et le document 7), mais pas pour les stratégies américaines, plus rentables en volatilité moyenne : l'effet n'est pas uniforme.
