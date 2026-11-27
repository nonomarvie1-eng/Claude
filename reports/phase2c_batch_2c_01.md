## Lot batch_2c_01

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Version du code : `3922fa5` ; essais au registre après le lot : 88.

### 1. Qualité intrinsèque des signaux (R par trade, profil statistique 0,5 %, sans arrêt)

| Hypothèse | Variante | Trades | E[R] net | IC95 net | E[R] sans frottement | IC95 sans frott. | E[R] avant commissions | Coûts ×1,5 | Coûts ×2 | Frais BNB (sensib.) | Aléatoire expo. comparable | p(>0) BH | p(>aléa) BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXC-01 | `{"tf": "H1"}` | 301 | -0.135 | [-0.253 ; -0.004] | +0.018 | [-0.102 ; +0.144] | -0.016 | -0.192 | -0.270 | -0.085 | -0.106 | 0.995 | 0.716 | Résultats incompatibles avec une exploitation rentable |
| NXC-01 | `{"tf": "H4"}` | 74 | +0.019 | [-0.203 ; +0.284] | +0.090 | [-0.132 ; +0.352] | +0.085 | -0.017 | -0.071 | +0.035 | +0.011 | 0.912 | 0.694 | Absence d'avantage démontré |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | 238 | -0.191 | [-0.330 ; -0.040] | -0.037 | [-0.168 ; +0.093] | -0.072 | -0.255 | -0.291 | -0.148 | -0.101 | 0.995 | 0.861 | Résultats incompatibles avec une exploitation rentable |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | 55 | +0.097 | [-0.166 ; +0.379] | +0.164 | [-0.099 ; +0.450] | +0.160 | +0.064 | -0.015 | +0.113 | +0.014 | 0.912 | 0.694 | Absence d'avantage démontré |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | 199 | -0.092 | [-0.270 ; +0.110] | +0.043 | [-0.124 ; +0.214] | +0.028 | -0.204 | -0.193 | -0.069 | -0.105 | 0.995 | 0.694 | Absence d'avantage démontré |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | 52 | +0.047 | [-0.285 ; +0.443] | +0.118 | [-0.211 ; +0.510] | +0.113 | +0.011 | -0.093 | +0.063 | -0.007 | 0.912 | 0.694 | Absence d'avantage démontré |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | 231 | -0.141 | [-0.277 ; +0.001] | +0.019 | [-0.105 ; +0.144] | -0.017 | -0.205 | -0.170 | -0.097 | -0.120 | 0.995 | 0.716 | Résultats incompatibles avec une exploitation rentable |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | 69 | -0.104 | [-0.369 ; +0.190] | +0.053 | [-0.219 ; +0.355] | -0.023 | -0.101 | -0.024 | -0.058 | -0.041 | 0.995 | 0.716 | Absence d'avantage démontré |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | 301 | -0.089 | [-0.233 ; +0.067] | +0.172 | [-0.008 ; +0.385] | +0.030 | -0.154 | -0.233 | +0.063 | -0.100 | 0.995 | 0.694 | Absence d'avantage démontré |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | 74 | +0.608 | [-0.051 ; +1.701] | +0.693 | [+0.022 ; +1.809] | +0.675 | +0.566 | +0.121 | +0.625 | +0.027 | 0.650 | 0.119 | Absence d'avantage démontré |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | 301 | +0.046 | [-0.205 ; +0.345] | +0.494 | [+0.114 ; +0.948] | +0.165 | -0.009 | -0.140 | +0.278 | -0.078 | 0.912 | 0.418 | Absence d'avantage démontré |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | 74 | +0.736 | [-0.160 ; +1.971] | +0.820 | [-0.087 ; +2.083] | +0.802 | +0.694 | +0.329 | +0.752 | +0.100 | 0.650 | 0.149 | Absence d'avantage démontré |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | 51 | +0.363 | [+0.029 ; +0.815] | +0.380 | [+0.044 ; +0.833] | +0.378 | +0.354 | +0.345 | +0.366 | +0.128 | 0.176 | 0.090 | Résultats prometteurs mais preuves insuffisantes |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | 20 | +2.095 | [-0.262 ; +6.276] | +2.120 | [-0.243 ; +6.314] | +2.113 | +2.082 | +2.069 | +2.099 | +0.395 | 0.196 | 0.081 | Résultats prometteurs mais preuves insuffisantes |
| NXF-02 | `{"n": 20, "tf": "D1"}` | 17 | +3.850 | [-0.271 ; +11.336] | +3.893 | [-0.243 ; +11.404] | +3.879 | +3.829 | +3.807 | +3.857 | +0.569 | 0.176 | 0.081 | Données insuffisantes (< 20 trades) |
| NXF-02 | `{"n": 55, "tf": "D1"}` | 8 | +4.896 | [-0.673 ; +17.232] | +4.946 | [-0.649 ; +17.326] | +4.928 | +4.871 | +4.847 | +4.904 | +1.186 | 0.196 | 0.096 | Données insuffisantes (< 20 trades) |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | 20 | +3.352 | [+0.315 ; +6.574] | +3.475 | [+0.396 ; +6.743] | +3.430 | +2.054 | +1.411 | +3.371 | +0.339 | 0.176 | 0.081 | Résultats prometteurs mais preuves insuffisantes |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | 41 | +0.343 | [-0.045 ; +0.869] | +0.361 | [-0.030 ; +0.890] | +0.358 | +0.334 | +0.325 | +0.347 | +0.137 | 0.176 | 0.164 | Résultats prometteurs mais preuves insuffisantes |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | 15 | +2.828 | [-0.306 ; +9.505] | +2.857 | [-0.289 ; +9.556] | +2.848 | +2.814 | +2.800 | +2.833 | +0.453 | 0.196 | 0.081 | Données insuffisantes (< 20 trades) |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | 15 | +4.610 | [-0.093 ; +13.260] | +4.658 | [-0.066 ; +13.343] | +4.641 | +4.586 | +4.561 | +4.618 | +0.702 | 0.176 | 0.081 | Données insuffisantes (< 20 trades) |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | 8 | +4.894 | [-0.677 ; +17.232] | +4.946 | [-0.649 ; +17.326] | +4.928 | +4.868 | +4.842 | +4.903 | +1.543 | 0.196 | 0.146 | Données insuffisantes (< 20 trades) |
| NXF-05 | `{"n": 20, "tf": "D1", "trailing": true}` | 1 | — | — | — | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | 24 | +2.023 | [-0.159 ; +6.280] | +2.046 | [-0.143 ; +6.315] | +2.040 | +2.011 | +1.999 | +2.027 | +0.444 | 0.140 | 0.065 | Résultats prometteurs mais preuves insuffisantes |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | 155 | -0.171 | [-0.322 ; -0.005] | -0.027 | [-0.191 ; +0.140] | -0.051 | -0.190 | -0.340 | -0.127 | -0.108 | 0.986 | 0.736 | Résultats incompatibles avec une exploitation rentable |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | 45 | +0.096 | [-0.222 ; +0.505] | +0.165 | [-0.147 ; +0.568] | +0.159 | +0.062 | +0.028 | +0.112 | +0.032 | 0.618 | 0.687 | Absence d'avantage démontré |

### 2. Exposition, références et attribution au marché

| Hypothèse | Variante | Temps sur le marché % | Expo. moyenne % | Turnover/an | Durée moy. (h) | Rendement moyen/trade % | Aléatoire expo. comparable %/trade | Bêta | Alpha %/an [IC95] | Sharpe quotidien [IC95] | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NXC-01 | `{"tf": "H1"}` | 14.0 | 3.41 | 44.3 | 14 | -0.07 | -0.17 | 0.020 | -6.39 [-11.28 ; -2.31] | -1.05 [-2.19 ; -0.10] | positif sur moins de la moitié des semestres |
| NXC-01 | `{"tf": "H4"}` | 15.7 | 1.96 | 6.4 | 65 | +0.24 | +0.12 | 0.010 | -0.43 [-3.18 ; +1.62] | +0.08 [-1.09 ; +0.93] | ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | 11.5 | 2.82 | 35.0 | 15 | -0.16 | -0.17 | 0.019 | -6.84 [-10.96 ; -2.67] | -1.27 [-2.31 ; -0.22] | positif sur moins de la moitié des semestres |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | 13.4 | 1.69 | 4.5 | 75 | +0.46 | +0.10 | 0.010 | +0.13 [-2.42 ; +1.75] | +0.29 [-0.85 ; +1.09] | ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | 12.4 | 2.96 | 29.5 | 19 | -0.06 | -0.16 | 0.018 | -3.85 [-7.61 ; +0.21] | -0.60 [-1.57 ; +0.39] | positif sur moins de la moitié des semestres |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | 11.8 | 1.53 | 4.5 | 70 | +0.44 | +0.07 | 0.009 | -0.28 [-3.06 ; +1.56] | +0.12 [-1.16 ; +0.93] | ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | 10.0 | 2.25 | 34.9 | 13 | -0.04 | -0.17 | 0.014 | -5.05 [-9.02 ; -1.23] | -0.99 [-2.02 ; +0.02] | positif sur moins de la moitié des semestres |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | 10.8 | 1.24 | 7.1 | 48 | -0.03 | +0.01 | 0.010 | -1.46 [-4.42 ; +0.88] | -0.33 [-1.47 ; +0.53] | positif sur moins de la moitié des semestres |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | 17.1 | 4.35 | 44.3 | 17 | +0.03 | -0.16 | 0.030 | -5.21 [-9.50 ; -0.68] | -0.54 [-1.61 ; +0.30] | positif sur moins de la moitié des semestres |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | 19.0 | 2.98 | 6.4 | 79 | +1.27 | +0.15 | 0.019 | +4.13 [-1.52 ; +10.47] | +1.19 [-0.35 ; +2.19] | > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | 30.8 | 7.67 | 44.3 | 31 | +0.30 | -0.12 | 0.061 | -2.26 [-9.81 ; +4.97] | +0.20 [-1.00 ; +1.21] | ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | 33.8 | 5.18 | 6.4 | 140 | +1.66 | +0.37 | 0.040 | +4.13 [-3.75 ; +11.09] | +1.05 [-0.47 ; +2.05] | > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | 45.0 | 1.78 | 1.0 | 270 | +4.05 | +1.64 | 0.016 | +1.52 [-0.65 ; +3.43] | +1.22 [-0.10 ; +2.31] | > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | 36.2 | 1.74 | 0.5 | 555 | +16.75 | +4.12 | 0.038 | +3.17 [-1.67 ; +7.64] | +1.04 [-0.03 ; +2.19] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-02 | `{"n": 20, "tf": "D1"}` | 38.3 | 2.44 | 0.6 | 690 | +23.06 | +4.40 | 0.047 | +5.56 [-0.56 ; +11.50] | +1.26 [+0.20 ; +2.26] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-02 | `{"n": 55, "tf": "D1"}` | 32.3 | 2.46 | 0.3 | 1237 | +27.21 | +7.49 | 0.065 | +1.90 [-4.60 ; +8.47] | +0.73 [-0.37 ; +1.90] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; positif sur moins de la moitié des semestres; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | 22.2 | 4.12 | 1.9 | 340 | +7.13 | +1.02 | 0.043 | +5.86 [-2.38 ; +14.42] | +1.19 [-0.26 ; +2.38] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | 34.7 | 1.40 | 0.9 | 259 | +3.58 | +1.65 | 0.017 | +1.35 [-0.95 ; +3.80] | +1.11 [-0.25 ; +2.52] | > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | 30.5 | 1.55 | 0.4 | 623 | +22.83 | +4.14 | 0.046 | +3.47 [-1.55 ; +8.47] | +1.12 [-0.07 ; +2.15] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | 34.2 | 2.40 | 0.6 | 699 | +26.84 | +4.78 | 0.060 | +6.61 [-0.16 ; +13.45] | +1.43 [+0.20 ; +2.57] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | 35.1 | 2.71 | 0.3 | 1345 | +27.73 | +9.67 | 0.070 | +2.06 [-4.97 ; +9.37] | +0.75 [-0.49 ; +1.96] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; positif sur moins de la moitié des semestres; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | 43.2 | 2.01 | 0.5 | 552 | +17.93 | +4.53 | 0.038 | +4.13 [-0.08 ; +8.78] | +1.23 [+0.25 ; +2.23] | échantillon < 30 trades : IC très large; > 50 % du profit brut sur 5 trades; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | 7.8 | 2.02 | 22.9 | 15 | -0.11 | -0.17 | 0.012 | -4.70 [-8.47 ; -1.26] | -1.12 [-2.20 ; -0.13] | positif sur moins de la moitié des semestres |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | 12.6 | 1.47 | 3.7 | 86 | +0.88 | +0.21 | 0.010 | -0.15 [-1.76 ; +2.60] | +0.20 [-0.61 ; +1.50] | alpha non distinguable de zéro : performance expliquée par l'exposition au marché |

Références passives (même période) : **Buy & Hold** BTC +331.8 %, CAGR +52.0 %, drawdown max 73.6 %, temps sur le marché 100 % ; **liquidités** 0 %, drawdown 0 %. La colonne « passif même exposition » du tableau 3 donne la détention constante à l'exposition moyenne de chaque stratégie.


### 3. Capital simulé (1 000 €) : règles de risque, avec et sans arrêt à 10 %

Les lignes « sans arrêt » sont purement analytiques et ne modifient pas les règles du futur bot.

| Hypothèse | Variante | Profil | Trades | Capital final € | Rendement % | CAGR % | Max DD % (valorisé) | PF | Sharpe | Sortino | Calmar | Frais € | Série pertes | Arrêt (date) | Passif même expo. % / DD % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXC-01 | `{"tf": "H1"}` | prudent | 298 | 907 | -9.3 | -2.8 | 10.1 | 0.73 | -1.14 | -1.60 | -0.28 | 73.7 | 19 | 2023-06-13 | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H1"}` | prudent_sans_arret | 301 | 913 | -8.7 | -2.6 | 10.1 | 0.75 | -1.04 | -1.47 | -0.25 | 74.7 | 19 | non | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H1"}` | equilibre | 173 | 914 | -8.6 | -4.5 | 10.2 | 0.79 | -0.86 | -1.22 | -0.44 | 79.5 | 12 | 2021-12-19 | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H1"}` | equilibre_sans_arret | 301 | 832 | -16.8 | -5.1 | 19.4 | 0.75 | -1.04 | -1.47 | -0.27 | 144.2 | 19 | non | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H1"}` | dynamique | 125 | 928 | -7.2 | -4.9 | 10.3 | 0.88 | -0.39 | -0.57 | -0.48 | 116.3 | 11 | 2021-06-25 | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H1"}` | dynamique_sans_arret | 297 | 699 | -30.1 | -9.8 | 34.3 | 0.76 | -1.00 | -1.42 | -0.28 | 267.5 | 19 | non | +11.3 / 17.8 |
| NXC-01 | `{"tf": "H4"}` | prudent | 74 | 1003 | +0.3 | +0.1 | 2.3 | 1.03 | +0.08 | +0.11 | +0.03 | 11.1 | 8 | non | +6.5 / 11.3 |
| NXC-01 | `{"tf": "H4"}` | prudent_sans_arret | 74 | 1003 | +0.3 | +0.1 | 2.3 | 1.03 | +0.08 | +0.11 | +0.03 | 11.1 | 8 | non | +6.5 / 11.3 |
| NXC-01 | `{"tf": "H4"}` | equilibre | 74 | 1005 | +0.5 | +0.1 | 4.5 | 1.03 | +0.08 | +0.12 | +0.03 | 22.0 | 8 | non | +6.5 / 11.3 |
| NXC-01 | `{"tf": "H4"}` | equilibre_sans_arret | 74 | 1005 | +0.5 | +0.1 | 4.5 | 1.03 | +0.08 | +0.12 | +0.03 | 22.0 | 8 | non | +6.5 / 11.3 |
| NXC-01 | `{"tf": "H4"}` | dynamique | 74 | 1007 | +0.7 | +0.2 | 8.8 | 1.02 | +0.08 | +0.12 | +0.02 | 43.5 | 8 | non | +6.5 / 11.3 |
| NXC-01 | `{"tf": "H4"}` | dynamique_sans_arret | 74 | 1007 | +0.7 | +0.2 | 8.8 | 1.02 | +0.08 | +0.12 | +0.02 | 43.5 | 8 | non | +6.5 / 11.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | prudent | 231 | 910 | -9.0 | -2.8 | 10.1 | 0.70 | -1.22 | -1.69 | -0.27 | 56.4 | 19 | 2023-05-18 | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | prudent_sans_arret | 238 | 904 | -9.6 | -2.9 | 10.9 | 0.69 | -1.27 | -1.75 | -0.26 | 58.8 | 21 | non | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | equilibre | 132 | 919 | -8.1 | -4.3 | 10.2 | 0.77 | -0.88 | -1.24 | -0.42 | 61.4 | 10 | 2021-12-13 | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | equilibre_sans_arret | 238 | 816 | -18.4 | -5.7 | 20.7 | 0.69 | -1.27 | -1.75 | -0.27 | 113.3 | 21 | non | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | dynamique | 95 | 942 | -5.8 | -4.0 | 10.2 | 0.88 | -0.32 | -0.47 | -0.39 | 89.8 | 9 | 2021-06-27 | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | dynamique_sans_arret | 235 | 672 | -32.8 | -10.8 | 36.6 | 0.70 | -1.22 | -1.70 | -0.29 | 209.1 | 21 | non | +9.3 / 15.3 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | prudent | 55 | 1012 | +1.2 | +0.3 | 1.5 | 1.19 | +0.29 | +0.42 | +0.23 | 7.9 | 8 | non | +5.6 / 9.9 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | prudent_sans_arret | 55 | 1012 | +1.2 | +0.3 | 1.5 | 1.19 | +0.29 | +0.42 | +0.23 | 7.9 | 8 | non | +5.6 / 9.9 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | equilibre | 55 | 1023 | +2.3 | +0.7 | 3.0 | 1.19 | +0.29 | +0.42 | +0.22 | 15.8 | 8 | non | +5.6 / 9.9 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | equilibre_sans_arret | 55 | 1023 | +2.3 | +0.7 | 3.0 | 1.19 | +0.29 | +0.42 | +0.22 | 15.8 | 8 | non | +5.6 / 9.9 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | dynamique | 55 | 1044 | +4.4 | +1.3 | 5.9 | 1.18 | +0.29 | +0.43 | +0.22 | 31.6 | 8 | non | +5.6 / 9.9 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | dynamique_sans_arret | 55 | 1044 | +4.4 | +1.3 | 5.9 | 1.18 | +0.29 | +0.43 | +0.22 | 31.6 | 8 | non | +5.6 / 9.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | prudent | 199 | 958 | -4.2 | -1.2 | 6.8 | 0.85 | -0.60 | -0.89 | -0.18 | 50.5 | 9 | non | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | prudent_sans_arret | 199 | 958 | -4.2 | -1.2 | 6.8 | 0.85 | -0.60 | -0.89 | -0.18 | 50.5 | 9 | non | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | equilibre | 126 | 922 | -7.8 | -4.0 | 10.3 | 0.78 | -0.95 | -1.38 | -0.39 | 61.5 | 9 | 2021-12-23 | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | equilibre_sans_arret | 199 | 916 | -8.4 | -2.5 | 13.2 | 0.84 | -0.60 | -0.89 | -0.19 | 99.0 | 9 | non | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | dynamique | 92 | 945 | -5.5 | -4.0 | 10.6 | 0.89 | -0.50 | -0.74 | -0.37 | 93.2 | 9 | 2021-06-01 | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | dynamique_sans_arret | 199 | 833 | -16.7 | -5.1 | 25.0 | 0.84 | -0.60 | -0.89 | -0.20 | 190.0 | 9 | non | +9.8 / 15.9 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | prudent | 52 | 1005 | +0.5 | +0.2 | 1.7 | 1.08 | +0.12 | +0.19 | +0.09 | 8.0 | 8 | non | +5.1 / 9.1 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | prudent_sans_arret | 52 | 1005 | +0.5 | +0.2 | 1.7 | 1.08 | +0.12 | +0.19 | +0.09 | 8.0 | 8 | non | +5.1 / 9.1 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | equilibre | 52 | 1010 | +1.0 | +0.3 | 3.4 | 1.07 | +0.12 | +0.19 | +0.09 | 16.0 | 8 | non | +5.1 / 9.1 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | equilibre_sans_arret | 52 | 1010 | +1.0 | +0.3 | 3.4 | 1.07 | +0.12 | +0.19 | +0.09 | 16.0 | 8 | non | +5.1 / 9.1 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | dynamique | 52 | 1019 | +1.9 | +0.5 | 6.7 | 1.06 | +0.12 | +0.19 | +0.08 | 32.3 | 8 | non | +5.1 / 9.1 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | dynamique_sans_arret | 52 | 1019 | +1.9 | +0.5 | 6.7 | 1.06 | +0.12 | +0.19 | +0.08 | 32.3 | 8 | non | +5.1 / 9.1 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | prudent | 231 | 931 | -6.9 | -2.0 | 7.4 | 0.74 | -0.99 | -1.36 | -0.28 | 59.0 | 15 | non | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | prudent_sans_arret | 231 | 931 | -6.9 | -2.0 | 7.4 | 0.74 | -0.99 | -1.36 | -0.28 | 59.0 | 15 | non | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | equilibre | 159 | 901 | -9.9 | -4.3 | 10.1 | 0.75 | -1.01 | -1.38 | -0.42 | 76.7 | 11 | 2022-05-20 | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | equilibre_sans_arret | 231 | 865 | -13.5 | -4.1 | 14.3 | 0.74 | -0.99 | -1.36 | -0.28 | 114.2 | 15 | non | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | dynamique | 107 | 901 | -9.9 | -6.7 | 10.5 | 0.81 | -0.73 | -1.02 | -0.63 | 99.0 | 11 | 2021-07-10 | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | dynamique_sans_arret | 227 | 743 | -25.7 | -8.2 | 27.2 | 0.74 | -1.01 | -1.39 | -0.30 | 209.8 | 14 | non | +7.5 / 12.7 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | prudent | 69 | 985 | -1.5 | -0.5 | 3.2 | 0.82 | -0.33 | -0.47 | -0.14 | 12.3 | 10 | non | +4.1 / 7.5 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | prudent_sans_arret | 69 | 985 | -1.5 | -0.5 | 3.2 | 0.82 | -0.33 | -0.47 | -0.14 | 12.3 | 10 | non | +4.1 / 7.5 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | equilibre | 69 | 969 | -3.1 | -0.9 | 6.3 | 0.81 | -0.33 | -0.47 | -0.15 | 24.1 | 10 | non | +4.1 / 7.5 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | equilibre_sans_arret | 69 | 969 | -3.1 | -0.9 | 6.3 | 0.81 | -0.33 | -0.47 | -0.15 | 24.1 | 10 | non | +4.1 / 7.5 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | dynamique | 23 | 906 | -9.4 | -13.2 | 10.0 | 0.28 | -1.91 | -2.31 | -1.31 | 18.3 | 8 | 2020-10-01 | +4.1 / 7.5 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | dynamique_sans_arret | 69 | 937 | -6.3 | -1.9 | 12.1 | 0.81 | -0.32 | -0.46 | -0.16 | 46.7 | 10 | non | +4.1 / 7.5 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | prudent | 301 | 941 | -5.9 | -1.7 | 8.5 | 0.82 | -0.54 | -0.98 | -0.20 | 76.7 | 19 | non | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | prudent_sans_arret | 301 | 941 | -5.9 | -1.7 | 8.5 | 0.82 | -0.54 | -0.98 | -0.20 | 76.7 | 19 | non | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | equilibre | 208 | 945 | -5.5 | -2.3 | 10.6 | 0.88 | -0.32 | -0.58 | -0.22 | 98.9 | 16 | 2022-05-25 | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | equilibre_sans_arret | 301 | 883 | -11.7 | -3.5 | 16.4 | 0.82 | -0.54 | -0.97 | -0.21 | 151.8 | 19 | non | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | dynamique | 142 | 988 | -1.2 | -0.7 | 10.9 | 0.98 | +0.05 | +0.08 | -0.07 | 135.2 | 13 | 2021-08-29 | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | dynamique_sans_arret | 297 | 778 | -22.2 | -7.0 | 29.8 | 0.82 | -0.52 | -0.95 | -0.23 | 292.9 | 18 | non | +14.4 / 21.4 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | prudent | 74 | 1096 | +9.6 | +2.7 | 2.3 | 2.35 | +1.19 | +2.42 | +1.18 | 11.4 | 8 | non | +9.9 / 15.9 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | prudent_sans_arret | 74 | 1096 | +9.6 | +2.7 | 2.3 | 2.35 | +1.19 | +2.42 | +1.18 | 11.4 | 8 | non | +9.9 / 15.9 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | equilibre | 74 | 1195 | +19.5 | +5.3 | 4.5 | 2.36 | +1.19 | +2.42 | +1.18 | 23.0 | 8 | non | +9.9 / 15.9 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | equilibre_sans_arret | 74 | 1195 | +19.5 | +5.3 | 4.5 | 2.36 | +1.19 | +2.42 | +1.18 | 23.0 | 8 | non | +9.9 / 15.9 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | dynamique | 74 | 1404 | +40.4 | +10.4 | 8.8 | 2.36 | +1.19 | +2.42 | +1.18 | 47.2 | 8 | non | +9.9 / 15.9 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | dynamique_sans_arret | 74 | 1404 | +40.4 | +10.4 | 8.8 | 2.36 | +1.19 | +2.42 | +1.18 | 47.2 | 8 | non | +9.9 / 15.9 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | prudent | 301 | 1026 | +2.6 | +0.7 | 9.6 | 1.07 | +0.20 | +0.35 | +0.08 | 81.4 | 28 | non | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | prudent_sans_arret | 301 | 1026 | +2.6 | +0.7 | 9.6 | 1.07 | +0.20 | +0.35 | +0.08 | 81.4 | 28 | non | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | equilibre | 253 | 1091 | +9.1 | +3.1 | 10.9 | 1.13 | +0.39 | +0.68 | +0.28 | 135.7 | 19 | 2022-11-18 | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | equilibre_sans_arret | 301 | 1045 | +4.5 | +1.3 | 18.4 | 1.05 | +0.20 | +0.35 | +0.07 | 170.3 | 28 | non | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | dynamique | 123 | 1304 | +30.4 | +20.3 | 13.2 | 1.42 | +1.02 | +1.87 | +1.54 | 134.5 | 14 | 2021-06-10 | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | dynamique_sans_arret | 297 | 1082 | +8.2 | +2.3 | 32.8 | 1.04 | +0.23 | +0.41 | +0.07 | 367.8 | 28 | non | +25.4 / 31.5 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | prudent | 74 | 1121 | +12.1 | +3.4 | 3.5 | 2.32 | +1.04 | +1.72 | +0.97 | 11.6 | 9 | non | +17.2 / 24.3 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | prudent_sans_arret | 74 | 1121 | +12.1 | +3.4 | 3.5 | 2.32 | +1.04 | +1.72 | +0.97 | 11.6 | 9 | non | +17.2 / 24.3 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | equilibre | 74 | 1247 | +24.7 | +6.6 | 6.8 | 2.30 | +1.05 | +1.74 | +0.97 | 23.9 | 9 | non | +17.2 / 24.3 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | equilibre_sans_arret | 74 | 1247 | +24.7 | +6.6 | 6.8 | 2.30 | +1.05 | +1.74 | +0.97 | 23.9 | 9 | non | +17.2 / 24.3 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | dynamique | 23 | 940 | -6.0 | -8.5 | 12.2 | 0.50 | -0.92 | -1.25 | -0.70 | 15.3 | 8 | 2020-09-30 | +17.2 / 24.3 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | dynamique_sans_arret | 74 | 1516 | +51.6 | +12.9 | 13.2 | 2.28 | +1.06 | +1.76 | +0.98 | 50.6 | 9 | non | +17.2 / 24.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | prudent | 51 | 1045 | +4.5 | +1.3 | 1.3 | 2.84 | +1.21 | +1.93 | +0.95 | 1.9 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | prudent_sans_arret | 51 | 1045 | +4.5 | +1.3 | 1.3 | 2.84 | +1.21 | +1.93 | +0.95 | 1.9 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | equilibre | 51 | 1091 | +9.1 | +2.6 | 2.7 | 2.79 | +1.22 | +1.93 | +0.95 | 3.9 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | equilibre_sans_arret | 51 | 1091 | +9.1 | +2.6 | 2.7 | 2.79 | +1.22 | +1.93 | +0.95 | 3.9 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | dynamique | 51 | 1186 | +18.6 | +5.1 | 5.3 | 2.72 | +1.23 | +1.96 | +0.95 | 8.3 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | dynamique_sans_arret | 51 | 1186 | +18.6 | +5.1 | 5.3 | 2.72 | +1.23 | +1.96 | +0.95 | 8.3 | 7 | non | +5.9 / 10.3 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | prudent | 20 | 1100 | +10.0 | +2.9 | 3.1 | 8.44 | +1.00 | +1.62 | +0.93 | 1.0 | 6 | non | +5.8 / 10.2 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | prudent_sans_arret | 20 | 1100 | +10.0 | +2.9 | 3.1 | 8.44 | +1.00 | +1.62 | +0.93 | 1.0 | 6 | non | +5.8 / 10.2 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | equilibre | 20 | 1199 | +19.9 | +5.6 | 5.7 | 7.81 | +1.04 | +1.68 | +0.98 | 2.1 | 6 | non | +5.8 / 10.2 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | equilibre_sans_arret | 20 | 1199 | +19.9 | +5.6 | 5.7 | 7.81 | +1.04 | +1.68 | +0.98 | 2.1 | 6 | non | +5.8 / 10.2 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | dynamique | 20 | 1396 | +39.6 | +10.5 | 9.9 | 6.84 | +1.09 | +1.78 | +1.06 | 4.6 | 6 | non | +5.8 / 10.2 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | dynamique_sans_arret | 20 | 1396 | +39.6 | +10.5 | 9.9 | 6.84 | +1.09 | +1.78 | +1.06 | 4.6 | 6 | non | +5.8 / 10.2 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | prudent | 17 | 1159 | +15.9 | +4.4 | 3.7 | 8.01 | +1.21 | +2.04 | +1.18 | 1.3 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | prudent_sans_arret | 17 | 1159 | +15.9 | +4.4 | 3.7 | 8.01 | +1.21 | +2.04 | +1.18 | 1.3 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | equilibre | 17 | 1321 | +32.1 | +8.5 | 6.6 | 7.34 | +1.26 | +2.13 | +1.29 | 2.9 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | equilibre_sans_arret | 17 | 1321 | +32.1 | +8.5 | 6.6 | 7.34 | +1.26 | +2.13 | +1.29 | 2.9 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | dynamique | 17 | 1655 | +65.5 | +15.9 | 10.5 | 6.35 | +1.34 | +2.28 | +1.51 | 6.7 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | dynamique_sans_arret | 17 | 1655 | +65.5 | +15.9 | 10.5 | 6.35 | +1.34 | +2.28 | +1.51 | 6.7 | 6 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | prudent | 8 | 1091 | +9.1 | +2.8 | 6.1 | 10.20 | +0.68 | +1.04 | +0.46 | 0.7 | 1 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | prudent_sans_arret | 8 | 1091 | +9.1 | +2.8 | 6.1 | 10.20 | +0.68 | +1.04 | +0.46 | 0.7 | 1 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | equilibre | 8 | 1182 | +18.2 | +5.5 | 10.8 | 9.63 | +0.73 | +1.12 | +0.50 | 1.4 | 1 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | equilibre_sans_arret | 8 | 1182 | +18.2 | +5.5 | 10.8 | 9.63 | +0.73 | +1.12 | +0.50 | 1.4 | 1 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | dynamique | 8 | 1361 | +36.1 | +10.3 | 17.6 | 8.65 | +0.80 | +1.26 | +0.58 | 3.0 | 1 | non | +8.1 / 13.6 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | dynamique_sans_arret | 8 | 1361 | +36.1 | +10.3 | 17.6 | 8.65 | +0.80 | +1.26 | +0.58 | 3.0 | 1 | non | +8.1 / 13.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | prudent | 20 | 1154 | +15.4 | +4.3 | 3.2 | 5.76 | +1.16 | +1.92 | +1.31 | 3.8 | 3 | non | +13.7 / 20.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | prudent_sans_arret | 20 | 1154 | +15.4 | +4.3 | 3.2 | 5.76 | +1.16 | +1.92 | +1.31 | 3.8 | 3 | non | +13.7 / 20.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | equilibre | 20 | 1322 | +32.2 | +8.5 | 6.1 | 5.64 | +1.19 | +1.98 | +1.39 | 8.0 | 3 | non | +13.7 / 20.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | equilibre_sans_arret | 20 | 1322 | +32.2 | +8.5 | 6.1 | 5.64 | +1.19 | +1.98 | +1.39 | 8.0 | 3 | non | +13.7 / 20.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | dynamique | 20 | 1706 | +70.6 | +16.9 | 10.9 | 5.40 | +1.23 | +2.09 | +1.55 | 18.3 | 3 | non | +13.7 / 20.6 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | dynamique_sans_arret | 20 | 1706 | +70.6 | +16.9 | 10.9 | 5.40 | +1.23 | +2.09 | +1.55 | 18.3 | 3 | non | +13.7 / 20.6 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | prudent | 41 | 1034 | +3.4 | +1.2 | 1.5 | 2.46 | +1.10 | +1.74 | +0.78 | 1.6 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | prudent_sans_arret | 41 | 1034 | +3.4 | +1.2 | 1.5 | 2.46 | +1.10 | +1.74 | +0.78 | 1.6 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | equilibre | 41 | 1068 | +6.8 | +2.3 | 3.0 | 2.43 | +1.11 | +1.75 | +0.79 | 3.2 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | equilibre_sans_arret | 41 | 1068 | +6.8 | +2.3 | 3.0 | 2.43 | +1.11 | +1.75 | +0.79 | 3.2 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | dynamique | 41 | 1138 | +13.8 | +4.6 | 5.8 | 2.38 | +1.12 | +1.77 | +0.80 | 6.7 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | dynamique_sans_arret | 41 | 1138 | +13.8 | +4.6 | 5.8 | 2.38 | +1.12 | +1.77 | +0.80 | 6.7 | 7 | non | +4.6 / 8.4 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | prudent | 15 | 1101 | +10.1 | +3.3 | 3.1 | 9.47 | +1.09 | +1.76 | +1.07 | 0.8 | 6 | non | +5.1 / 9.1 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | prudent_sans_arret | 15 | 1101 | +10.1 | +3.3 | 3.1 | 9.47 | +1.09 | +1.76 | +1.07 | 0.8 | 6 | non | +5.1 / 9.1 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | equilibre | 15 | 1202 | +20.2 | +6.4 | 5.7 | 8.70 | +1.12 | +1.83 | +1.13 | 1.7 | 6 | non | +5.1 / 9.1 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | equilibre_sans_arret | 15 | 1202 | +20.2 | +6.4 | 5.7 | 8.70 | +1.12 | +1.83 | +1.13 | 1.7 | 6 | non | +5.1 / 9.1 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | dynamique | 15 | 1403 | +40.3 | +12.2 | 9.8 | 7.51 | +1.18 | +1.94 | +1.24 | 3.9 | 6 | non | +5.1 / 9.1 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | dynamique_sans_arret | 15 | 1403 | +40.3 | +12.2 | 9.8 | 7.51 | +1.18 | +1.94 | +1.24 | 3.9 | 6 | non | +5.1 / 9.1 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | prudent | 15 | 1169 | +16.9 | +5.5 | 3.7 | 9.41 | +1.37 | +2.31 | +1.46 | 1.3 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | prudent_sans_arret | 15 | 1169 | +16.9 | +5.5 | 3.7 | 9.41 | +1.37 | +2.31 | +1.46 | 1.3 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | equilibre | 15 | 1344 | +34.4 | +10.6 | 6.6 | 8.50 | +1.43 | +2.42 | +1.61 | 2.8 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | equilibre_sans_arret | 15 | 1344 | +34.4 | +10.6 | 6.6 | 8.50 | +1.43 | +2.42 | +1.61 | 2.8 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | dynamique | 15 | 1712 | +71.2 | +20.1 | 10.5 | 7.19 | +1.52 | +2.61 | +1.91 | 6.7 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | dynamique_sans_arret | 15 | 1712 | +71.2 | +20.1 | 10.5 | 7.19 | +1.52 | +2.61 | +1.91 | 6.7 | 6 | non | +8.0 / 13.4 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | prudent | 8 | 1091 | +9.1 | +3.0 | 6.1 | 10.20 | +0.70 | +1.07 | +0.49 | 0.7 | 1 | non | +9.0 / 14.8 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | prudent_sans_arret | 8 | 1091 | +9.1 | +3.0 | 6.1 | 10.20 | +0.70 | +1.07 | +0.49 | 0.7 | 1 | non | +9.0 / 14.8 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | equilibre | 8 | 1182 | +18.2 | +5.9 | 10.8 | 9.62 | +0.75 | +1.16 | +0.54 | 1.4 | 1 | non | +9.0 / 14.8 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | equilibre_sans_arret | 8 | 1182 | +18.2 | +5.9 | 10.8 | 9.62 | +0.75 | +1.16 | +0.54 | 1.4 | 1 | non | +9.0 / 14.8 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | dynamique | 8 | 1361 | +36.1 | +11.1 | 17.6 | 8.65 | +0.83 | +1.29 | +0.63 | 3.2 | 1 | non | +9.0 / 14.8 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | dynamique_sans_arret | 8 | 1361 | +36.1 | +11.1 | 17.6 | 8.65 | +0.83 | +1.29 | +0.63 | 3.2 | 1 | non | +9.0 / 14.8 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | prudent | 24 | 1117 | +11.7 | +3.4 | 2.7 | 7.60 | +1.19 | +1.96 | +1.26 | 1.1 | 10 | non | +6.7 / 11.5 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | prudent_sans_arret | 24 | 1117 | +11.7 | +3.4 | 2.7 | 7.60 | +1.19 | +1.96 | +1.26 | 1.1 | 10 | non | +6.7 / 11.5 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | equilibre | 24 | 1237 | +23.7 | +6.5 | 4.8 | 7.15 | +1.23 | +2.03 | +1.35 | 2.3 | 10 | non | +6.7 / 11.5 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | equilibre_sans_arret | 24 | 1237 | +23.7 | +6.5 | 4.8 | 7.15 | +1.23 | +2.03 | +1.35 | 2.3 | 10 | non | +6.7 / 11.5 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | dynamique | 24 | 1481 | +48.1 | +12.4 | 8.2 | 6.46 | +1.29 | +2.14 | +1.51 | 5.2 | 10 | non | +6.7 / 11.5 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | dynamique_sans_arret | 24 | 1481 | +48.1 | +12.4 | 8.2 | 6.46 | +1.29 | +2.14 | +1.51 | 5.2 | 10 | non | +6.7 / 11.5 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | prudent | 155 | 943 | -5.7 | -1.9 | 7.4 | 0.70 | -1.12 | -1.57 | -0.25 | 39.5 | 19 | non | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | prudent_sans_arret | 155 | 943 | -5.7 | -1.9 | 7.4 | 0.70 | -1.12 | -1.57 | -0.25 | 39.5 | 19 | non | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | equilibre | 137 | 921 | -7.9 | -2.8 | 10.4 | 0.76 | -0.88 | -1.26 | -0.27 | 67.3 | 16 | 2023-03-24 | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | equilibre_sans_arret | 155 | 888 | -11.2 | -3.7 | 14.3 | 0.71 | -1.12 | -1.57 | -0.26 | 78.1 | 19 | non | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | dynamique | 98 | 950 | -5.0 | -3.8 | 10.0 | 0.89 | -0.53 | -0.77 | -0.38 | 96.5 | 13 | 2021-09-03 | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | dynamique_sans_arret | 154 | 789 | -21.1 | -7.3 | 26.7 | 0.72 | -1.10 | -1.56 | -0.27 | 151.5 | 19 | non | +6.7 / 11.6 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | prudent | 45 | 1011 | +1.1 | +0.3 | 2.3 | 1.23 | +0.19 | +0.28 | +0.14 | 6.5 | 8 | non | +4.9 / 8.7 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | prudent_sans_arret | 45 | 1011 | +1.1 | +0.3 | 2.3 | 1.23 | +0.19 | +0.28 | +0.14 | 6.5 | 8 | non | +4.9 / 8.7 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | equilibre | 45 | 1021 | +2.1 | +0.7 | 4.6 | 1.23 | +0.20 | +0.29 | +0.14 | 12.9 | 8 | non | +4.9 / 8.7 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | equilibre_sans_arret | 45 | 1021 | +2.1 | +0.7 | 4.6 | 1.23 | +0.20 | +0.29 | +0.14 | 12.9 | 8 | non | +4.9 / 8.7 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | dynamique | 45 | 1041 | +4.1 | +1.3 | 9.0 | 1.23 | +0.20 | +0.29 | +0.14 | 25.6 | 8 | non | +4.9 / 8.7 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | dynamique_sans_arret | 45 | 1041 | +4.1 | +1.3 | 9.0 | 1.23 | +0.20 | +0.29 | +0.14 | 25.6 | 8 | non | +4.9 / 8.7 |

### 4. Stabilité : E[R] net par année et par régime (régime causal à l'entrée)

| Hypothèse | Variante | Par année | Par tendance (n, E[R]) | Par volatilité (n, E[R]) | Part des 5 meilleurs trades % |
|---|---|---|---|---|---|
| NXC-01 | `{"tf": "H1"}` | 2020 -0.05, 2021 -0.15, 2022 -0.14, 2023 -0.28 | baissier (113, -0.12), consolidation (19, +0.45), haussier (149, -0.22), indéfini (20, -0.20) | faible (115, -0.23), forte (79, -0.12), indéfini (35, -0.09), moyenne (72, -0.03) | 9 |
| NXC-01 | `{"tf": "H4"}` | 2020 -0.21, 2021 +0.21, 2022 -0.03, 2023 +0.41 | baissier (23, -0.00), consolidation (2, +0.46), haussier (40, +0.09), indéfini (9, -0.35) | faible (30, -0.08), forte (17, +0.25), indéfini (14, -0.21), moyenne (13, +0.18) | 29 |
| NXC-02 | `{"structure_filter": true, "tf": "H1"}` | 2020 -0.03, 2021 -0.27, 2022 -0.11, 2023 -0.58 | baissier (91, -0.13), consolidation (15, -0.09), haussier (115, -0.27), indéfini (17, -0.09) | faible (94, -0.31), forte (61, -0.17), indéfini (27, -0.15), moyenne (56, -0.03) | 11 |
| NXC-02 | `{"structure_filter": true, "tf": "H4"}` | 2020 -0.06, 2021 -0.01, 2022 +0.43, 2023 +0.41 | baissier (16, +0.27), consolidation (2, +0.46), haussier (31, +0.05), indéfini (6, -0.21) | faible (22, -0.02), forte (14, +0.21), indéfini (10, -0.18), moyenne (9, +0.52) | 33 |
| NXC-03 | `{"confirmation": true, "tf": "H1"}` | 2020 -0.02, 2021 -0.29, 2022 +0.08, 2023 -0.18 | baissier (66, -0.01), consolidation (12, +0.62), haussier (104, -0.25), indéfini (17, +0.02) | faible (67, -0.05), forte (49, -0.26), indéfini (29, -0.03), moyenne (54, -0.02) | 10 |
| NXC-03 | `{"confirmation": true, "tf": "H4"}` | 2020 -0.07, 2021 +0.18, 2022 +0.12, 2023 -0.06 | baissier (12, +0.17), consolidation (3, +0.94), haussier (33, -0.06), indéfini (4, -0.12) | faible (26, -0.30), forte (10, +0.39), indéfini (8, +0.34), moyenne (8, +0.44) | 31 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H1"}` | 2020 -0.09, 2021 -0.13, 2022 -0.22, 2023 -0.08 | baissier (91, -0.21), consolidation (9, +0.20), haussier (116, -0.06), indéfini (15, -0.56) | faible (82, -0.17), forte (74, -0.18), indéfini (25, -0.17), moyenne (50, -0.01) | 11 |
| NXC-04 | `{"stop_mode": "structure", "tf": "H4"}` | 2020 -0.43, 2021 +0.19, 2022 +0.09, 2023 -0.20 | baissier (19, -0.01), consolidation (2, -1.08), haussier (39, -0.02), indéfini (9, -0.46) | faible (26, -0.20), forte (17, +0.44), indéfini (13, -0.53), moyenne (13, -0.20) | 32 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H1"}` | 2020 +0.03, 2021 -0.06, 2022 -0.11, 2023 -0.41 | baissier (113, -0.14), consolidation (19, +0.39), haussier (149, -0.12), indéfini (20, +0.02) | faible (115, -0.21), forte (79, -0.08), indéfini (35, -0.06), moyenne (72, +0.09) | 26 |
| NXC-05 | `{"exit_mode": "trailing", "tf": "H4"}` | 2020 -0.03, 2021 +0.41, 2022 +0.01, 2023 +5.11 | baissier (23, +1.54), consolidation (2, +0.50), haussier (40, +0.25), indéfini (9, -0.18) | faible (30, +1.22), forte (17, +0.38), indéfini (14, -0.14), moyenne (13, +0.29) | 70 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H1"}` | 2020 +0.21, 2021 +0.20, 2022 -0.19, 2023 -0.13 | baissier (113, -0.16), consolidation (19, +1.55), haussier (149, -0.07), indéfini (20, +0.65) | faible (115, -0.34), forte (79, +0.15), indéfini (35, +0.31), moyenne (72, +0.41) | 34 |
| NXC-06 | `{"exit_mode": "invalidation", "tf": "H4"}` | 2020 +0.55, 2021 +0.38, 2022 -0.30, 2023 +5.04 | baissier (23, +1.25), consolidation (2, -1.04), haussier (40, +0.67), indéfini (9, +0.10) | faible (30, +1.47), forte (17, +0.53), indéfini (14, -0.14), moyenne (13, +0.25) | 77 |
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | 2020 +0.99, 2021 +0.48, 2022 -0.21, 2023 +0.93 | baissier (25, +0.12), consolidation (4, -0.05), haussier (20, +0.76), indéfini (2, +0.25) | faible (23, +0.42), forte (6, +1.07), indéfini (6, -0.01), moyenne (16, +0.16) | 74 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | 2020 +0.35, 2021 +10.88, 2022 -0.49, 2023 +0.18 | baissier (9, -0.43), consolidation (4, +0.43), haussier (6, +7.42), indéfini (1, -0.43) | faible (12, +3.49), forte (1, -0.11), indéfini (4, -0.11), moyenne (3, +0.19) | 100 |
| NXF-02 | `{"n": 20, "tf": "D1"}` | 2020 +0.02, 2021 +12.30, 2022 -0.80, 2023 +1.97 | baissier (6, +0.78), consolidation (2, +0.45), haussier (7, +8.40), indéfini (2, +0.54) | faible (10, +6.43), indéfini (3, +0.02), moyenne (4, +0.27) | 96 |
| NXF-02 | `{"n": 55, "tf": "D1"}` | 2020 -1.02, 2021 +13.32, 2022 -1.02, 2023 +0.42 | consolidation (3, -0.08), haussier (5, +7.88) | faible (4, +10.44), indéfini (1, -1.02), moyenne (3, -0.52) | 100 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | 2020 +2.11, 2021 +5.37, 2022 -0.86, 2023 +7.14 | baissier (6, +6.87), consolidation (2, +1.82), haussier (10, +2.25), indéfini (2, -0.17) | faible (10, +3.72), forte (3, -0.09), indéfini (3, -0.47), moyenne (4, +7.87) | 97 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | 2020 +1.65, 2021 +0.49, 2022 -0.21, 2023 +0.93 | baissier (22, +0.12), consolidation (4, -0.05), haussier (15, +0.77) | faible (23, +0.27), forte (2, +2.66), moyenne (16, +0.16) | 84 |
| NXF-03 | `{"lookback": 60, "tf": "D1", "vol_filter": true}` | 2020 +2.17, 2021 +14.54, 2022 -0.49, 2023 +0.18 | baissier (9, -0.43), consolidation (3, +0.56), haussier (3, +14.88) | faible (12, +3.49), moyenne (3, +0.19) | 100 |
| NXF-04 | `{"n": 20, "tf": "D1", "vol_filter": true}` | 2020 +3.75, 2021 +12.30, 2022 -0.80, 2023 +1.97 | baissier (6, +0.78), consolidation (2, +0.45), haussier (7, +9.08) | faible (11, +6.19), moyenne (4, +0.27) | 96 |
| NXF-04 | `{"n": 55, "tf": "D1", "vol_filter": true}` | 2020 -1.04, 2021 +13.32, 2022 -1.02, 2023 +0.42 | consolidation (3, -0.08), haussier (5, +7.88) | faible (5, +8.14), moyenne (3, -0.52) | 100 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | 2020 -0.09, 2021 +7.76, 2022 -0.44, 2023 +2.27 | baissier (12, +0.16), consolidation (1, +0.76), haussier (9, +5.20), indéfini (2, -0.43) | faible (9, +5.42), forte (2, -0.12), indéfini (4, -0.37), moyenne (9, +0.16) | 97 |
| REG-01 | `{"regime_filter": true, "tf": "H1"}` | 2020 -0.01, 2021 -0.20, 2022 -0.96, 2023 -0.35 | haussier (155, -0.17) | faible (66, -0.28), forte (39, +0.04), indéfini (15, +0.07), moyenne (35, -0.30) | 17 |
| REG-01 | `{"regime_filter": true, "tf": "H4"}` | 2020 -0.30, 2021 +0.55, 2022 -1.07, 2023 +0.13 | haussier (45, +0.10) | faible (20, -0.13), forte (12, +0.36), indéfini (5, -0.56), moyenne (8, +0.68) | 42 |

### 5. Walk-forward du processus de sélection (choix sur le passé, mesure sur le semestre suivant)

- Famille C : 258 trades hors échantillon, E[R] = -0.077 — 2020-07 → NXC-03 {"confirmation": true, "tf": "H1"}; 2021-01 → NXC-05 {"exit_mode": "trailing", "tf": "H1"}; 2021-07 → NXC-06 {"exit_mode": "invalidation", "tf": "H1"}; 2022-01 → NXC-06 {"exit_mode": "invalidation", "tf": "H1"}; 2022-07 → NXC-06 {"exit_mode": "invalidation", "tf": "H1"}; 2023-01 → NXC-06 {"exit_mode": "invalidation", "tf": "H1"}
- Famille F : 40 trades hors échantillon, E[R] = +0.093 — 2020-07 → aucun choix; 2021-01 → NXF-01 {"lookback": 20, "tf": "D1"}; 2021-07 → NXF-01 {"lookback": 20, "tf": "D1"}; 2022-01 → NXF-01 {"lookback": 20, "tf": "D1"}; 2022-07 → NXF-01 {"lookback": 20, "tf": "D1"}; 2023-01 → NXF-01 {"lookback": 20, "tf": "D1"}
- Famille REF : 13 trades hors échantillon, E[R] = +0.184 — 2020-07 → aucun choix; 2021-01 → aucun choix; 2021-07 → aucun choix; 2022-01 → REF-SMA-01 {"n": 50, "tf": "D1"}; 2022-07 → REF-SMA-01 {"n": 50, "tf": "D1"}; 2023-01 → REF-SMA-01 {"n": 50, "tf": "D1"}
- Famille REG : 115 trades hors échantillon, E[R] = -0.123 — 2020-07 → REG-01 {"regime_filter": true, "tf": "H1"}; 2021-01 → REG-01 {"regime_filter": true, "tf": "H1"}; 2021-07 → REG-01 {"regime_filter": true, "tf": "H1"}; 2022-01 → REG-01 {"regime_filter": true, "tf": "H4"}; 2022-07 → REG-01 {"regime_filter": true, "tf": "H4"}; 2023-01 → REG-01 {"regime_filter": true, "tf": "H4"}

### 6. Ablations (différence d'E[R], IC95 bootstrap hebdomadaire)

- NXC-02 {"structure_filter": true, "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = -0.055 [-0.155 ; +0.039] (n = 238/301) → contribution non démontrée
- NXC-03 {"confirmation": true, "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = +0.044 [-0.084 ; +0.183] (n = 199/301) → contribution non démontrée
- NXC-04 {"stop_mode": "structure", "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = -0.006 [-0.134 ; +0.112] (n = 231/301) → contribution non démontrée
- NXC-05 {"exit_mode": "trailing", "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = +0.047 [-0.069 ; +0.170] (n = 301/301) → contribution non démontrée
- NXC-06 {"exit_mode": "invalidation", "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = +0.181 [-0.039 ; +0.434] (n = 301/301) → contribution non démontrée
- REG-01 {"regime_filter": true, "tf": "H1"} vs NXC-01 {"tf": "H1"} : Δ = -0.035 [-0.157 ; +0.090] (n = 155/301) → contribution non démontrée
- NXC-02 {"structure_filter": true, "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = +0.078 [-0.106 ; +0.285] (n = 55/74) → contribution non démontrée
- NXC-03 {"confirmation": true, "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = +0.028 [-0.207 ; +0.284] (n = 52/74) → contribution non démontrée
- NXC-04 {"stop_mode": "structure", "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = -0.123 [-0.360 ; +0.119] (n = 69/74) → contribution non démontrée
- NXC-05 {"exit_mode": "trailing", "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = +0.589 [-0.108 ; +1.712] (n = 74/74) → contribution non démontrée
- NXC-06 {"exit_mode": "invalidation", "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = +0.717 [-0.216 ; +1.947] (n = 74/74) → contribution non démontrée
- REG-01 {"regime_filter": true, "tf": "H4"} vs NXC-01 {"tf": "H4"} : Δ = +0.077 [-0.198 ; +0.374] (n = 45/74) → contribution non démontrée
- NXF-03 {"lookback": 20, "tf": "D1", "vol_filter": true} vs NXF-01 {"lookback": 20, "tf": "D1"} : Δ = -0.020 [-0.186 ; +0.137] (n = 41/51) → contribution non démontrée
- NXF-03 {"lookback": 60, "tf": "D1", "vol_filter": true} vs NXF-01 {"lookback": 60, "tf": "D1"} : Δ = +0.734 [-0.071 ; +2.875] (n = 15/20) → contribution non démontrée
- NXF-04 {"n": 20, "tf": "D1", "vol_filter": true} vs NXF-02 {"n": 20, "tf": "D1"} : Δ = +0.760 [-0.133 ; +2.836] (n = 15/17) → contribution non démontrée
- NXF-04 {"n": 55, "tf": "D1", "vol_filter": true} vs NXF-02 {"n": 55, "tf": "D1"} : Δ = -0.002 [-2.800 ; +2.828] (n = 8/8) → contribution non démontrée
- NXF-01 {"lookback": 20, "tf": "D1"} vs REF-SMA-01 {"n": 50, "tf": "D1"} : Δ = -1.660 [-6.064 ; +0.620] (n = 51/24) → contribution non démontrée
- NXF-02 {"n": 20, "tf": "D1"} vs REF-SMA-01 {"n": 50, "tf": "D1"} : Δ = +1.827 [-4.889 ; +10.507] (n = 17/24) → contribution non démontrée