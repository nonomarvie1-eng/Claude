## Lot batch_2c_02

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Version du code : `5bea129` ; essais au registre après le lot : 92.

### 1. Qualité intrinsèque des signaux (R par trade, profil statistique 0,5 %, sans arrêt)

| Hypothèse | Variante | Trades | E[R] net | IC95 net | E[R] sans frottement | IC95 sans frott. | E[R] avant commissions | Coûts ×1,5 | Coûts ×2 | Frais BNB (sensib.) | Aléatoire expo. comparable | p(>0) BH | p(>aléa) BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | 251 | +0.097 | [-0.123 ; +0.352] | +0.296 | [+0.083 ; +0.537] | +0.239 | -0.027 | -0.225 | +0.159 | -0.132 | 0.290 | 0.020 | Absence d'avantage démontré |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | 78 | +0.481 | [-0.114 ; +1.244] | +0.579 | [-0.026 ; +1.355] | +0.560 | +0.197 | -0.052 | +0.501 | +0.022 | 0.176 | 0.030 | Absence d'avantage démontré |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | 557 | +0.032 | [-0.096 ; +0.175] | +0.194 | [+0.063 ; +0.329] | +0.154 | -0.054 | -0.182 | +0.074 | -0.102 | 0.307 | 0.027 | Absence d'avantage démontré |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | 137 | +0.418 | [+0.026 ; +0.891] | +0.500 | [+0.099 ; +0.984] | +0.485 | +0.245 | +0.095 | +0.435 | +0.006 | 0.151 | 0.020 | Résultats prometteurs mais preuves insuffisantes |

### 2. Exposition, références et attribution au marché

| Hypothèse | Variante | Temps sur le marché % | Expo. moyenne % | Turnover/an | Durée moy. (h) | Rendement moyen/trade % | Aléatoire expo. comparable %/trade | Bêta | Alpha %/an [IC95] | Sharpe quotidien [IC95] | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | 11.6 | 3.53 | 43.3 | 14 | +0.25 | -0.18 | 0.036 | +0.35 [-5.95 ; +7.24] | +0.32 [-0.69 ; +1.22] | ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | 15.5 | 2.75 | 7.9 | 61 | +1.02 | +0.09 | 0.019 | +3.27 [-1.96 ; +9.00] | +0.96 [-0.46 ; +1.90] | > 50 % du profit brut sur 5 trades; positif sur moins de la moitié des semestres; ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | 27.0 | 7.05 | 84.0 | 15 | +0.18 | -0.16 | 0.072 | -3.10 [-10.95 ; +4.51] | +0.17 [-0.88 ; +1.04] | positif sur moins de la moitié des semestres; ne résiste pas au doublement des coûts; alpha non distinguable de zéro : performance expliquée par l'exposition au marché |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | 29.1 | 4.39 | 11.8 | 65 | +1.11 | +0.04 | 0.035 | +4.49 [-1.48 ; +10.01] | +1.22 [-0.05 ; +2.15] | alpha non distinguable de zéro : performance expliquée par l'exposition au marché |

Références passives (même période) : **Buy & Hold** BTC +331.8 %, CAGR +52.0 %, drawdown max 73.6 %, temps sur le marché 100 % ; **liquidités** 0 %, drawdown 0 %. La colonne « passif même exposition » du tableau 3 donne la détention constante à l'exposition moyenne de chaque stratégie.


### 3. Capital simulé (1 000 €) : règles de risque, avec et sans arrêt à 10 %

Les lignes « sans arrêt » sont purement analytiques et ne modifient pas les règles du futur bot.

| Hypothèse | Variante | Profil | Trades | Capital final € | Rendement % | CAGR % | Max DD % (valorisé) | PF | Sharpe | Sortino | Calmar | Frais € | Série pertes | Arrêt (date) | Passif même expo. % / DD % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | prudent | 251 | 1045 | +4.5 | +1.3 | 6.6 | 1.14 | +0.32 | +0.68 | +0.20 | 78.2 | 11 | non | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | prudent_sans_arret | 251 | 1045 | +4.5 | +1.3 | 6.6 | 1.14 | +0.32 | +0.68 | +0.20 | 78.2 | 11 | non | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | equilibre | 161 | 1034 | +3.4 | +1.7 | 10.5 | 1.08 | +0.17 | +0.37 | +0.16 | 95.7 | 10 | 2022-02-07 | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | equilibre_sans_arret | 251 | 1086 | +8.6 | +2.5 | 12.8 | 1.13 | +0.32 | +0.69 | +0.19 | 161.4 | 11 | non | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | dynamique | 85 | 1176 | +17.6 | +12.6 | 11.1 | 1.40 | +0.69 | +1.64 | +1.13 | 119.6 | 10 | 2021-06-17 | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | dynamique_sans_arret | 251 | 1159 | +15.9 | +4.5 | 24.3 | 1.11 | +0.32 | +0.69 | +0.18 | 340.9 | 11 | non | +11.7 / 18.3 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | prudent | 78 | 1078 | +7.8 | +2.3 | 2.2 | 1.82 | +0.96 | +2.21 | +1.00 | 14.2 | 6 | non | +9.1 / 14.9 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | prudent_sans_arret | 78 | 1078 | +7.8 | +2.3 | 2.2 | 1.82 | +0.96 | +2.21 | +1.00 | 14.2 | 6 | non | +9.1 / 14.9 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | equilibre | 78 | 1159 | +15.9 | +4.5 | 4.5 | 1.81 | +0.96 | +2.19 | +1.00 | 29.2 | 6 | non | +9.1 / 14.9 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | equilibre_sans_arret | 78 | 1159 | +15.9 | +4.5 | 4.5 | 1.81 | +0.96 | +2.19 | +1.00 | 29.2 | 6 | non | +9.1 / 14.9 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | dynamique | 78 | 1325 | +32.5 | +8.7 | 8.8 | 1.79 | +0.95 | +2.16 | +0.99 | 61.3 | 6 | non | +9.1 / 14.9 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | dynamique_sans_arret | 78 | 1325 | +32.5 | +8.7 | 8.8 | 1.79 | +0.95 | +2.16 | +0.99 | 61.3 | 6 | non | +9.1 / 14.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | prudent | 557 | 1026 | +2.6 | +0.7 | 9.2 | 1.04 | +0.17 | +0.34 | +0.08 | 150.9 | 12 | non | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | prudent_sans_arret | 557 | 1026 | +2.6 | +0.7 | 9.2 | 1.04 | +0.17 | +0.34 | +0.08 | 150.9 | 12 | non | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | equilibre | 340 | 1060 | +6.0 | +2.9 | 10.3 | 1.07 | +0.33 | +0.64 | +0.28 | 179.9 | 12 | 2022-01-20 | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | equilibre_sans_arret | 557 | 1044 | +4.4 | +1.2 | 17.7 | 1.03 | +0.17 | +0.35 | +0.07 | 309.2 | 12 | non | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | dynamique | 117 | 1032 | +3.2 | +4.5 | 12.5 | 1.06 | +0.30 | +0.60 | +0.36 | 147.9 | 12 | 2020-09-18 | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | dynamique_sans_arret | 557 | 1057 | +5.7 | +1.6 | 33.0 | 1.02 | +0.18 | +0.35 | +0.05 | 642.5 | 12 | non | +23.4 / 29.9 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | prudent | 137 | 1128 | +12.8 | +3.5 | 2.3 | 1.88 | +1.22 | +2.53 | +1.54 | 21.8 | 7 | non | +14.6 / 21.5 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | prudent_sans_arret | 137 | 1128 | +12.8 | +3.5 | 2.3 | 1.88 | +1.22 | +2.53 | +1.54 | 21.8 | 7 | non | +14.6 / 21.5 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | equilibre | 137 | 1267 | +26.7 | +7.1 | 4.6 | 1.87 | +1.22 | +2.52 | +1.54 | 45.8 | 7 | non | +14.6 / 21.5 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | equilibre_sans_arret | 137 | 1267 | +26.7 | +7.1 | 4.6 | 1.87 | +1.22 | +2.52 | +1.54 | 45.8 | 7 | non | +14.6 / 21.5 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | dynamique | 137 | 1581 | +58.1 | +14.1 | 9.1 | 1.85 | +1.22 | +2.51 | +1.55 | 100.7 | 7 | non | +14.6 / 21.5 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | dynamique_sans_arret | 137 | 1581 | +58.1 | +14.1 | 9.1 | 1.85 | +1.22 | +2.51 | +1.55 | 100.7 | 7 | non | +14.6 / 21.5 |

### 4. Stabilité : E[R] net par année et par régime (régime causal à l'entrée)

| Hypothèse | Variante | Par année | Par tendance (n, E[R]) | Par volatilité (n, E[R]) | Part des 5 meilleurs trades % |
|---|---|---|---|---|---|
| NXD-01 | `{"require_compression": true, "tf": "H1"}` | 2020 +0.43, 2021 -0.04, 2022 -0.04, 2023 +0.30 | baissier (96, -0.11), consolidation (23, +0.61), haussier (118, +0.08), indéfini (14, +0.85) | faible (108, -0.01), forte (38, -0.16), indéfini (35, +0.28), moyenne (70, +0.31) | 29 |
| NXD-01 | `{"require_compression": true, "tf": "H4"}` | 2020 +0.54, 2021 +0.22, 2022 -0.28, 2023 +2.74 | baissier (28, +0.55), consolidation (5, +1.18), haussier (39, +0.38), indéfini (6, +0.27) | faible (46, +0.66), forte (7, +1.07), indéfini (12, -0.17), moyenne (13, +0.14) | 63 |
| NXD-02 | `{"require_compression": false, "tf": "H1"}` | 2020 +0.17, 2021 -0.02, 2022 -0.14, 2023 +0.17 | baissier (186, -0.14), consolidation (49, +0.43), haussier (269, +0.03), indéfini (53, +0.28) | faible (193, -0.05), forte (121, -0.03), indéfini (87, +0.11), moyenne (156, +0.14) | 16 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | 2020 +0.49, 2021 +0.05, 2022 -0.14, 2023 +2.16 | baissier (41, +0.34), consolidation (10, +0.64), haussier (72, +0.40), indéfini (14, +0.55) | faible (60, +0.52), forte (25, +0.41), indéfini (22, +0.20), moyenne (30, +0.39) | 44 |

### 5. Walk-forward du processus de sélection (choix sur le passé, mesure sur le semestre suivant)

- Famille D : 475 trades hors échantillon, E[R] = +0.019 — 2020-07 → NXD-02 {"require_compression": false, "tf": "H1"}; 2021-01 → NXD-02 {"require_compression": false, "tf": "H1"}; 2021-07 → NXD-02 {"require_compression": false, "tf": "H1"}; 2022-01 → NXD-02 {"require_compression": false, "tf": "H1"}; 2022-07 → NXD-02 {"require_compression": false, "tf": "H1"}; 2023-01 → NXD-02 {"require_compression": false, "tf": "H1"}