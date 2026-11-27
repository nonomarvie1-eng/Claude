## Lot batch_2d_01

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Version du code : `28e13d6` ; essais au registre après le lot : 116.

### 1. Qualité intrinsèque des signaux (R par trade, profil statistique 0,5 %, sans arrêt)

| Hypothèse | Variante | Trades | E[R] net | IC95 net | E[R] sans frottement | IC95 sans frott. | E[R] avant commissions | Coûts ×1,5 | Coûts ×2 | Frais BNB (sensib.) | Aléatoire expo. comparable | p(>0) BH | p(>aléa) BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | 553 | -0.158 | [-0.237 ; -0.082] | -0.033 | [-0.117 ; +0.048] | -0.043 | -0.201 | -0.215 | -0.134 | -0.122 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | 126 | -0.211 | [-0.336 ; -0.087] | -0.144 | [-0.269 ; -0.022] | -0.153 | -0.244 | -0.259 | -0.196 | -0.018 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | 165 | -0.138 | [-0.301 ; +0.031] | +0.011 | [-0.139 ; +0.164] | -0.031 | -0.201 | -0.236 | -0.090 | -0.095 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | 37 | -0.164 | [-0.512 ; +0.164] | -0.105 | [-0.454 ; +0.228] | -0.113 | -0.194 | -0.224 | -0.151 | +0.011 | 1.000 | 1.000 | Absence d'avantage démontré |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | 203 | -0.091 | [-0.247 ; +0.070] | +0.013 | [-0.139 ; +0.160] | -0.001 | -0.124 | -0.155 | -0.068 | -0.069 | 1.000 | 1.000 | Absence d'avantage démontré |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | 44 | +0.196 | [-0.111 ; +0.503] | +0.243 | [-0.067 ; +0.551] | +0.236 | +0.173 | +0.149 | +0.206 | +0.021 | 0.840 | 1.000 | Absence d'avantage démontré |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | 479 | -0.136 | [-0.215 ; -0.060] | -0.017 | [-0.092 ; +0.057] | -0.021 | -0.186 | -0.213 | -0.116 | -0.121 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | 110 | -0.189 | [-0.332 ; -0.055] | -0.123 | [-0.266 ; +0.010] | -0.131 | -0.222 | -0.234 | -0.174 | -0.027 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |

### 2. Exposition, références et attribution au marché

| Hypothèse | Variante | Temps sur le marché % | Expo. moyenne % | Turnover/an | Durée moy. (h) | Rendement moyen/trade % | Aléatoire expo. comparable %/trade | Bêta | Alpha %/an [IC95] | Sharpe quotidien [IC95] | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | 13.1 | 3.20 | 79.2 | 7 | -0.04 | -0.21 | 0.027 | -12.59 [-18.36 ; -7.78] | -2.14 [-3.38 ; -1.14] | positif sur moins de la moitié des semestres |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | 12.9 | 1.67 | 9.7 | 31 | -0.35 | -0.03 | 0.012 | -4.34 [-6.70 ; -1.83] | -1.41 [-2.40 ; -0.39] | positif sur moins de la moitié des semestres |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | 7.5 | 1.72 | 22.0 | 14 | -0.13 | -0.18 | 0.015 | -3.94 [-7.00 ; -0.72] | -0.81 [-1.76 ; +0.09] | positif sur moins de la moitié des semestres |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | 6.2 | 0.75 | 2.6 | 51 | -0.13 | +0.05 | 0.007 | -1.29 [-2.92 ; +0.38] | -0.44 [-1.49 ; +0.51] | positif sur moins de la moitié des semestres |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | 10.4 | 2.06 | 23.2 | 16 | +0.13 | -0.15 | 0.021 | -3.67 [-7.00 ; -0.38] | -0.58 [-1.60 ; +0.31] | positif sur moins de la moitié des semestres |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | 10.5 | 0.98 | 2.4 | 73 | +1.50 | +0.13 | 0.009 | +0.62 [-1.21 ; +2.36] | +0.60 [-0.39 ; +1.57] | alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | 11.2 | 2.71 | 68.1 | 7 | +0.01 | -0.21 | 0.022 | -9.50 [-14.45 ; -5.15] | -1.75 [-2.89 ; -0.81] | positif sur moins de la moitié des semestres |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | 11.0 | 1.41 | 8.4 | 31 | -0.34 | -0.08 | 0.011 | -3.49 [-5.79 ; -1.25] | -1.16 [-2.16 ; -0.21] | positif sur moins de la moitié des semestres |

Références passives (même période) : **Buy & Hold** BTC +332.1 %, CAGR +52.0 %, drawdown max 73.6 %, temps sur le marché 100 % ; **liquidités** 0 %, drawdown 0 %. La colonne « passif même exposition » du tableau 3 donne la détention constante à l'exposition moyenne de chaque stratégie.


### 3. Capital simulé (1 000 €) : règles de risque, avec et sans arrêt à 10 %

Les lignes « sans arrêt » sont purement analytiques et ne modifient pas les règles du futur bot.

| Hypothèse | Variante | Profil | Trades | Capital final € | Rendement % | CAGR % | Max DD % (valorisé) | PF | Sharpe | Sortino | Calmar | Frais € | Série pertes | Arrêt (date) | Passif même expo. % / DD % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | prudent | 236 | 906 | -9.4 | -2.8 | 10.0 | 0.63 | -1.66 | -2.02 | -0.28 | 52.2 | 5 | 2021-07-14 | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | prudent_sans_arret | 553 | 827 | -17.3 | -5.3 | 18.3 | 0.68 | -2.14 | -2.63 | -0.29 | 125.7 | 8 | non | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | equilibre | 93 | 909 | -9.1 | -2.7 | 10.3 | 0.56 | -1.27 | -1.51 | -0.26 | 50.8 | 4 | 2020-09-05 | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | equilibre_sans_arret | 553 | 683 | -31.7 | -10.3 | 33.5 | 0.68 | -2.14 | -2.63 | -0.31 | 228.9 | 8 | non | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | dynamique | 67 | 923 | -7.7 | -2.3 | 10.0 | 0.72 | -0.60 | -0.75 | -0.23 | 66.6 | 4 | 2020-06-24 | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | dynamique_sans_arret | 553 | 462 | -53.8 | -19.8 | 56.1 | 0.68 | -2.13 | -2.63 | -0.35 | 382.1 | 8 | non | +10.6 / 16.9 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | prudent | 126 | 940 | -6.0 | -1.8 | 7.0 | 0.60 | -1.41 | -1.71 | -0.25 | 16.3 | 5 | non | +5.5 / 9.8 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | prudent_sans_arret | 126 | 940 | -6.0 | -1.8 | 7.0 | 0.60 | -1.41 | -1.71 | -0.25 | 16.3 | 5 | non | +5.5 / 9.8 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | equilibre | 99 | 904 | -9.6 | -2.9 | 10.0 | 0.58 | -1.30 | -1.58 | -0.28 | 22.4 | 5 | 2022-11-08 | +5.5 / 9.8 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | equilibre_sans_arret | 126 | 883 | -11.7 | -3.5 | 13.6 | 0.60 | -1.41 | -1.71 | -0.26 | 31.7 | 5 | non | +5.5 / 9.8 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | dynamique | 47 | 907 | -9.3 | -2.8 | 10.1 | 0.58 | -0.88 | -1.05 | -0.27 | 21.0 | 5 | 2021-06-18 | +5.5 / 9.8 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | dynamique_sans_arret | 126 | 778 | -22.2 | -6.9 | 25.5 | 0.60 | -1.41 | -1.72 | -0.27 | 59.6 | 5 | non | +5.5 / 9.8 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | prudent | 165 | 949 | -5.1 | -1.5 | 5.4 | 0.78 | -0.81 | -1.11 | -0.27 | 37.2 | 5 | non | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | prudent_sans_arret | 165 | 949 | -5.1 | -1.5 | 5.4 | 0.78 | -0.81 | -1.11 | -0.27 | 37.2 | 5 | non | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | equilibre | 134 | 901 | -9.9 | -2.9 | 10.1 | 0.74 | -0.89 | -1.21 | -0.29 | 53.4 | 5 | 2022-11-07 | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | equilibre_sans_arret | 165 | 900 | -10.0 | -3.0 | 10.6 | 0.78 | -0.81 | -1.11 | -0.28 | 71.9 | 5 | non | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | dynamique | 59 | 894 | -10.6 | -3.1 | 10.9 | 0.69 | -0.70 | -0.92 | -0.29 | 44.2 | 5 | 2021-06-21 | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | dynamique_sans_arret | 165 | 806 | -19.4 | -6.0 | 20.5 | 0.77 | -0.82 | -1.11 | -0.29 | 134.4 | 5 | non | +5.7 / 10.0 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | prudent | 37 | 986 | -1.4 | -0.4 | 2.2 | 0.75 | -0.44 | -0.61 | -0.19 | 4.4 | 5 | non | +2.5 / 4.7 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | prudent_sans_arret | 37 | 986 | -1.4 | -0.4 | 2.2 | 0.75 | -0.44 | -0.61 | -0.19 | 4.4 | 5 | non | +2.5 / 4.7 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | equilibre | 37 | 971 | -2.9 | -0.8 | 4.4 | 0.75 | -0.44 | -0.61 | -0.19 | 8.8 | 5 | non | +2.5 / 4.7 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | equilibre_sans_arret | 37 | 971 | -2.9 | -0.8 | 4.4 | 0.75 | -0.44 | -0.61 | -0.19 | 8.8 | 5 | non | +2.5 / 4.7 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | dynamique | 37 | 942 | -5.8 | -1.7 | 8.6 | 0.74 | -0.44 | -0.61 | -0.20 | 17.4 | 5 | non | +2.5 / 4.7 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | dynamique_sans_arret | 37 | 942 | -5.8 | -1.7 | 8.6 | 0.74 | -0.44 | -0.61 | -0.20 | 17.4 | 5 | non | +2.5 / 4.7 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | prudent | 203 | 960 | -4.0 | -1.1 | 5.1 | 0.85 | -0.57 | -0.80 | -0.22 | 39.9 | 7 | non | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | prudent_sans_arret | 203 | 960 | -4.0 | -1.1 | 5.1 | 0.85 | -0.57 | -0.80 | -0.22 | 39.9 | 7 | non | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | equilibre | 200 | 906 | -9.4 | -2.8 | 10.1 | 0.82 | -0.70 | -0.97 | -0.28 | 77.1 | 7 | 2023-06-10 | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | equilibre_sans_arret | 203 | 921 | -7.9 | -2.3 | 10.1 | 0.85 | -0.58 | -0.80 | -0.23 | 78.5 | 7 | non | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | dynamique | 103 | 905 | -9.5 | -2.8 | 10.8 | 0.82 | -0.48 | -0.65 | -0.26 | 72.3 | 7 | 2021-11-16 | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | dynamique_sans_arret | 203 | 844 | -15.6 | -4.8 | 19.6 | 0.85 | -0.58 | -0.80 | -0.24 | 151.3 | 7 | non | +6.9 / 11.8 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | prudent | 44 | 1021 | +2.1 | +0.6 | 1.0 | 1.46 | +0.60 | +0.87 | +0.59 | 4.2 | 4 | non | +3.3 / 6.0 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | prudent_sans_arret | 44 | 1021 | +2.1 | +0.6 | 1.0 | 1.46 | +0.60 | +0.87 | +0.59 | 4.2 | 4 | non | +3.3 / 6.0 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | equilibre | 44 | 1042 | +4.2 | +1.2 | 2.0 | 1.45 | +0.60 | +0.87 | +0.59 | 8.5 | 4 | non | +3.3 / 6.0 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | equilibre_sans_arret | 44 | 1042 | +4.2 | +1.2 | 2.0 | 1.45 | +0.60 | +0.87 | +0.59 | 8.5 | 4 | non | +3.3 / 6.0 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | dynamique | 44 | 1084 | +8.4 | +2.3 | 4.0 | 1.45 | +0.60 | +0.87 | +0.58 | 17.3 | 4 | non | +3.3 / 6.0 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | dynamique_sans_arret | 44 | 1084 | +8.4 | +2.3 | 4.0 | 1.45 | +0.60 | +0.87 | +0.58 | 17.3 | 4 | non | +3.3 / 6.0 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | prudent | 339 | 904 | -9.6 | -2.8 | 10.0 | 0.72 | -1.44 | -1.79 | -0.28 | 75.5 | 4 | 2022-05-05 | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | prudent_sans_arret | 479 | 868 | -13.2 | -4.0 | 14.2 | 0.71 | -1.75 | -2.16 | -0.28 | 110.5 | 10 | non | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | equilibre | 161 | 907 | -9.3 | -2.7 | 10.1 | 0.72 | -1.00 | -1.24 | -0.27 | 76.3 | 4 | 2021-04-16 | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | equilibre_sans_arret | 479 | 752 | -24.8 | -7.8 | 26.6 | 0.71 | -1.75 | -2.16 | -0.29 | 205.8 | 10 | non | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | dynamique | 73 | 916 | -8.4 | -2.5 | 10.0 | 0.71 | -0.66 | -0.82 | -0.25 | 79.6 | 4 | 2020-08-21 | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | dynamique_sans_arret | 479 | 562 | -43.8 | -15.2 | 46.4 | 0.71 | -1.75 | -2.16 | -0.33 | 358.0 | 10 | non | +9.0 / 14.8 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | prudent | 110 | 953 | -4.7 | -1.4 | 5.9 | 0.64 | -1.16 | -1.43 | -0.23 | 14.3 | 5 | non | +4.7 / 8.4 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | prudent_sans_arret | 110 | 953 | -4.7 | -1.4 | 5.9 | 0.64 | -1.16 | -1.43 | -0.23 | 14.3 | 5 | non | +4.7 / 8.4 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | equilibre | 93 | 904 | -9.6 | -2.8 | 10.3 | 0.58 | -1.29 | -1.57 | -0.27 | 22.5 | 5 | 2022-12-28 | +4.7 / 8.4 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | equilibre_sans_arret | 110 | 907 | -9.3 | -2.8 | 11.5 | 0.64 | -1.16 | -1.43 | -0.24 | 27.9 | 5 | non | +4.7 / 8.4 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | dynamique | 41 | 914 | -8.6 | -2.6 | 10.1 | 0.57 | -0.83 | -1.00 | -0.25 | 18.6 | 5 | 2021-06-18 | +4.7 / 8.4 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | dynamique_sans_arret | 110 | 821 | -17.9 | -5.5 | 21.8 | 0.64 | -1.16 | -1.43 | -0.25 | 53.2 | 5 | non | +4.7 / 8.4 |

### 4. Stabilité : E[R] net par année et par régime (régime causal à l'entrée)

| Hypothèse | Variante | Par année | Par tendance (n, E[R]) | Par volatilité (n, E[R]) | Part des 5 meilleurs trades % |
|---|---|---|---|---|---|
| NXE-01 | `{"mode": "zscore", "tf": "H1"}` | 2020 -0.15, 2021 -0.12, 2022 -0.18, 2023 -0.20 | baissier (199, -0.21), consolidation (41, -0.22), haussier (268, -0.13), indéfini (45, -0.07) | faible (214, -0.18), forte (134, -0.10), indéfini (74, -0.17), moyenne (131, -0.17) | 6 |
| NXE-01 | `{"mode": "zscore", "tf": "H4"}` | 2020 -0.24, 2021 -0.03, 2022 -0.49, 2023 -0.04 | baissier (46, -0.36), consolidation (6, -0.25), haussier (64, -0.10), indéfini (10, -0.25) | faible (60, -0.32), forte (22, -0.19), indéfini (18, -0.15), moyenne (26, -0.01) | 17 |
| NXE-02 | `{"mode": "atr", "tf": "H1"}` | 2020 -0.28, 2021 -0.16, 2022 -0.04, 2023 -0.13 | baissier (69, -0.09), consolidation (12, -0.19), haussier (71, -0.11), indéfini (13, -0.52) | faible (70, -0.16), forte (39, -0.12), indéfini (22, -0.39), moyenne (34, +0.06) | 14 |
| NXE-02 | `{"mode": "atr", "tf": "H4"}` | 2020 -0.51, 2021 +0.12, 2022 -0.14, 2023 -0.57 | baissier (18, +0.13), consolidation (4, -0.28), haussier (13, -0.40), indéfini (2, -1.06) | faible (19, -0.32), forte (6, +0.53), indéfini (3, -0.33), moyenne (9, -0.25) | 45 |
| NXE-03 | `{"mode": "shock", "tf": "H1"}` | 2020 -0.03, 2021 -0.14, 2022 -0.12, 2023 -0.04 | baissier (67, -0.03), consolidation (17, +0.15), haussier (107, -0.13), indéfini (12, -0.40) | faible (90, -0.25), forte (47, +0.01), indéfini (24, -0.05), moyenne (42, +0.10) | 11 |
| NXE-03 | `{"mode": "shock", "tf": "H4"}` | 2020 +0.50, 2021 -0.09, 2022 +0.03, 2023 +0.54 | baissier (14, +0.10), consolidation (3, +0.24), haussier (27, +0.24) | faible (18, -0.34), forte (11, +0.26), indéfini (2, +0.78), moyenne (13, +0.79) | 33 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H1"}` | 2020 -0.09, 2021 -0.15, 2022 -0.17, 2023 -0.11 | baissier (174, -0.19), consolidation (36, -0.14), haussier (232, -0.11), indéfini (37, -0.03) | faible (172, -0.18), forte (123, -0.10), indéfini (62, -0.10), moyenne (122, -0.14) | 6 |
| NXE-04 | `{"consolidation_filter": true, "mode": "zscore", "tf": "H4"}` | 2020 -0.20, 2021 -0.03, 2022 -0.49, 2023 +0.04 | baissier (39, -0.37), consolidation (4, -0.18), haussier (57, -0.08), indéfini (10, -0.06) | faible (48, -0.34), forte (17, -0.23), indéfini (18, -0.04), moyenne (27, +0.01) | 18 |

### 5. Walk-forward du processus de sélection (choix sur le passé, mesure sur le semestre suivant)

- Famille E : 300 trades hors échantillon, E[R] = -0.167 — 2020-07 → NXE-04 {"consolidation_filter": true, "mode": "zscore", "tf": "H1"}; 2021-01 → NXE-03 {"mode": "shock", "tf": "H4"}; 2021-07 → NXE-04 {"consolidation_filter": true, "mode": "zscore", "tf": "H1"}; 2022-01 → NXE-04 {"consolidation_filter": true, "mode": "zscore", "tf": "H1"}; 2022-07 → NXE-03 {"mode": "shock", "tf": "H1"}; 2023-01 → NXE-04 {"consolidation_filter": true, "mode": "zscore", "tf": "H1"}