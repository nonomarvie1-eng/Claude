Source : `results/batch_2b_01/summary_BTCUSDT.json` — version du code `e3cffad+dirty` — essais totaux dans le registre au moment du lot : 45.

### Statistique de l'avantage (R nets, profil statistique 0,5 %, sans disjoncteur)

| Actif | Session | Hypothèse | Variante | Trades | E[R] net | IC95 bloc-hebdo | E[R] brut | E[R] coûts ×1,5 | E[R] coûts ×2 | Aléatoire E[R] | p(>0) BH | p(>aléa) BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 198 | -0.156 | [-0.321 ; 0.019] | 0.013 | -0.269 | -0.381 | -0.190 | 0.967 | 0.348 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | paris | NXA-01 | `{"target_r": 2.0}` | 265 | -0.072 | [-0.202 ; 0.063] | 0.066 | -0.130 | -0.222 | -0.157 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | paris | NXA-01 | `{"target_r": "none"}` | 265 | -0.065 | [-0.219 ; 0.102] | 0.074 | -0.082 | -0.187 | -0.143 | 0.967 | 0.261 | Absence d'avantage démontré |
| BTCUSDT | paris | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 175 | -0.070 | [-0.236 ; 0.108] | 0.069 | -0.091 | -0.218 | -0.153 | 0.967 | 0.261 | Absence d'avantage démontré |
| BTCUSDT | paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 129 | 0.002 | [-0.219 ; 0.220] | 0.157 | -0.035 | -0.086 | -0.177 | 0.967 | 0.209 | Absence d'avantage démontré |
| BTCUSDT | paris | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 184 | -0.058 | [-0.222 ; 0.107] | 0.088 | -0.159 | -0.220 | -0.169 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | paris | NXB-01 | `{"target": "mid"}` | 16 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | paris | NXB-01 | `{"target": "2R"}` | 16 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | paris | NXB-02 | `{"require_choch": true, "target": "mid"}` | 14 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 199 | -0.144 | [-0.315 ; 0.028] | 0.025 | -0.285 | -0.365 | -0.197 | 0.967 | 0.306 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | london | NXA-01 | `{"target_r": 2.0}` | 267 | -0.071 | [-0.207 ; 0.067] | 0.071 | -0.115 | -0.234 | -0.161 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | london | NXA-01 | `{"target_r": "none"}` | 267 | -0.095 | [-0.252 ; 0.060] | 0.048 | -0.075 | -0.210 | -0.158 | 0.967 | 0.269 | Absence d'avantage démontré |
| BTCUSDT | london | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 172 | -0.060 | [-0.236 ; 0.125] | 0.082 | -0.044 | -0.214 | -0.154 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 131 | 0.002 | [-0.225 ; 0.228] | 0.165 | -0.006 | -0.048 | -0.183 | 0.967 | 0.209 | Absence d'avantage démontré |
| BTCUSDT | london | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 181 | -0.106 | [-0.270 ; 0.064] | 0.044 | -0.158 | -0.302 | -0.167 | 0.967 | 0.281 | Absence d'avantage démontré |
| BTCUSDT | london | NXB-01 | `{"target": "mid"}` | 15 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | london | NXB-01 | `{"target": "2R"}` | 15 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | london | NXB-02 | `{"require_choch": true, "target": "mid"}` | 14 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 197 | -0.146 | [-0.326 ; 0.043] | 0.023 | -0.274 | -0.353 | -0.196 | 0.967 | 0.306 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | utc | NXA-01 | `{"target_r": 2.0}` | 268 | -0.082 | [-0.216 ; 0.057] | 0.063 | -0.144 | -0.246 | -0.165 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | utc | NXA-01 | `{"target_r": "none"}` | 268 | -0.069 | [-0.232 ; 0.101] | 0.076 | -0.093 | -0.227 | -0.132 | 0.967 | 0.281 | Absence d'avantage démontré |
| BTCUSDT | utc | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 163 | -0.058 | [-0.235 ; 0.128] | 0.088 | -0.048 | -0.226 | -0.161 | 0.967 | 0.219 | Absence d'avantage démontré |
| BTCUSDT | utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 121 | 0.024 | [-0.205 ; 0.264] | 0.189 | 0.000 | -0.057 | -0.188 | 0.967 | 0.209 | Absence d'avantage démontré |
| BTCUSDT | utc | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 170 | -0.098 | [-0.279 ; 0.083] | 0.056 | -0.159 | -0.211 | -0.173 | 0.967 | 0.261 | Absence d'avantage démontré |
| BTCUSDT | utc | NXB-01 | `{"target": "mid"}` | 14 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | utc | NXB-01 | `{"target": "2R"}` | 14 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |
| BTCUSDT | utc | NXB-02 | `{"require_choch": true, "target": "mid"}` | 13 | — | — | — | — | — | — | — | — | Données insuffisantes (< 20 trades) |

### Refus du gestionnaire de risque (profil statistique)

| Actif | Session | Hypothèse | Variante | Signaux | Trades | Motifs de refus |
|---|---|---|---|---|---|---|
| BTCUSDT | paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 314 | 198 | coûts estimés > 33% du risque : 115; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | paris | NXA-01 | `{"target_r": 2.0}` | 314 | 265 | coûts estimés > 33% du risque : 48; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | paris | NXA-01 | `{"target_r": "none"}` | 314 | 265 | coûts estimés > 33% du risque : 48; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | paris | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 203 | 175 | coûts estimés > 33% du risque : 28 |
| BTCUSDT | paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 173 | 129 | coûts estimés > 33% du risque : 44 |
| BTCUSDT | paris | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 314 | 184 | coûts estimés > 33% du risque : 71; ordre non exécuté (expiré) : 58; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | paris | NXB-01 | `{"target": "mid"}` | 214 | 16 | coûts estimés > 33% du risque : 198 |
| BTCUSDT | paris | NXB-01 | `{"target": "2R"}` | 214 | 16 | coûts estimés > 33% du risque : 198 |
| BTCUSDT | paris | NXB-02 | `{"require_choch": true, "target": "mid"}` | 20 | 14 | coûts estimés > 33% du risque : 6 |
| BTCUSDT | london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 330 | 199 | coûts estimés > 33% du risque : 130; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | london | NXA-01 | `{"target_r": 2.0}` | 330 | 267 | coûts estimés > 33% du risque : 62; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | london | NXA-01 | `{"target_r": "none"}` | 330 | 267 | coûts estimés > 33% du risque : 62; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | london | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 207 | 172 | coûts estimés > 33% du risque : 35 |
| BTCUSDT | london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 185 | 131 | coûts estimés > 33% du risque : 54 |
| BTCUSDT | london | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 330 | 181 | coûts estimés > 33% du risque : 90; ordre non exécuté (expiré) : 58; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | london | NXB-01 | `{"target": "mid"}` | 234 | 15 | coûts estimés > 33% du risque : 219 |
| BTCUSDT | london | NXB-01 | `{"target": "2R"}` | 234 | 15 | coûts estimés > 33% du risque : 219 |
| BTCUSDT | london | NXB-02 | `{"require_choch": true, "target": "mid"}` | 18 | 14 | coûts estimés > 33% du risque : 4 |
| BTCUSDT | utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 353 | 197 | coûts estimés > 33% du risque : 155; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXA-01 | `{"target_r": 2.0}` | 353 | 268 | coûts estimés > 33% du risque : 84; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXA-01 | `{"target_r": "none"}` | 353 | 268 | coûts estimés > 33% du risque : 84; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | 210 | 163 | coûts estimés > 33% du risque : 47 |
| BTCUSDT | utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 192 | 121 | coûts estimés > 33% du risque : 71 |
| BTCUSDT | utc | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | 353 | 170 | coûts estimés > 33% du risque : 115; ordre non exécuté (expiré) : 67; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXB-01 | `{"target": "mid"}` | 240 | 14 | coûts estimés > 33% du risque : 225; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXB-01 | `{"target": "2R"}` | 240 | 14 | coûts estimés > 33% du risque : 225; taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXB-02 | `{"require_choch": true, "target": "mid"}` | 15 | 13 | coûts estimés > 33% du risque : 2 |

### Profils de risque (capital initial 1 000 €, limites actives)

| Actif | Session | Hypothèse | Variante | Profil | Trades | Capital final € | Profit net € | Rendement % | PF | Max DD % (observé) | Durée DD (j) | Win % | Gain moy. € | Perte moy. € | E[€] | Sharpe | Sortino | Calmar | Frais € | Série pertes max | Disjoncteur | P(DD≥10 %) MC | P(DD≥20 %) MC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | 198 | 936.14 | -63.86 | -6.39 | 0.76 | 8.57 | 816 | 37.4 | 2.78 | -2.18 | -0.323 | -0.94 | -1.37 | -0.22 | 68.39 | 11 | non | 0.41 | 0.00 |
| BTCUSDT | paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | 147 | 940.05 | -59.95 | -6.00 | 0.85 | 10.06 | 346 | 40.1 | 5.79 | -4.56 | -0.408 | -0.62 | -0.93 | -0.28 | 102.50 | 9 | oui : drawdown 10.06% >= seuil 10% | 0.91 | 0.35 |
| BTCUSDT | paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | 134 | 975.61 | -24.39 | -2.44 | 0.97 | 10.48 | 271 | 43.3 | 11.83 | -9.35 | -0.182 | -0.09 | -0.15 | -0.12 | 188.98 | 6 | oui : drawdown 10.48% >= seuil 10% | 1.00 | 0.90 |
| BTCUSDT | paris | NXA-01 | `{"target_r": 2.0}` | prudent | 265 | 958.40 | -41.60 | -4.16 | 0.86 | 7.79 | 594 | 41.5 | 2.37 | -1.95 | -0.157 | -0.56 | -0.85 | -0.16 | 78.03 | 11 | non | 0.21 | 0.00 |
| BTCUSDT | paris | NXA-01 | `{"target_r": 2.0}` | equilibre | 212 | 967.79 | -32.21 | -3.22 | 0.93 | 10.08 | 222 | 42.5 | 5.13 | -4.05 | -0.152 | -0.26 | -0.41 | -0.13 | 124.15 | 8 | oui : drawdown 10.08% >= seuil 10% | 0.78 | 0.17 |
| BTCUSDT | paris | NXA-01 | `{"target_r": 2.0}` | dynamique | 186 | 1036.30 | 36.30 | 3.63 | 1.04 | 10.16 | 155 | 44.6 | 10.79 | -8.34 | 0.195 | 0.23 | 0.36 | 0.17 | 226.70 | 8 | oui : drawdown 10.16% >= seuil 10% | 0.99 | 0.76 |
| BTCUSDT | paris | NXA-01 | `{"target_r": "none"}` | prudent | 265 | 962.87 | -37.13 | -3.71 | 0.88 | 9.32 | 594 | 39.2 | 2.73 | -1.99 | -0.140 | -0.41 | -0.73 | -0.12 | 78.81 | 11 | non | 0.25 | 0.00 |
| BTCUSDT | paris | NXA-01 | `{"target_r": "none"}` | equilibre | 207 | 1002.59 | 2.59 | 0.26 | 1.01 | 10.08 | 188 | 41.1 | 6.07 | -4.21 | 0.013 | 0.05 | 0.09 | 0.01 | 124.84 | 9 | oui : drawdown 10.08% >= seuil 10% | 0.83 | 0.21 |
| BTCUSDT | paris | NXA-01 | `{"target_r": "none"}` | dynamique | 183 | 1107.61 | 107.61 | 10.76 | 1.12 | 10.29 | 181 | 43.2 | 12.97 | -8.81 | 0.588 | 0.48 | 0.94 | 0.51 | 232.48 | 8 | oui : drawdown 10.29% >= seuil 10% | 1.00 | 0.81 |
| BTCUSDT | paris | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | prudent | 175 | 973.49 | -26.51 | -2.65 | 0.87 | 6.09 | 786 | 42.3 | 2.41 | -2.03 | -0.152 | -0.41 | -0.62 | -0.13 | 51.54 | 12 | non | 0.05 | 0.00 |
| BTCUSDT | paris | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | equilibre | 150 | 948.54 | -51.46 | -5.15 | 0.86 | 10.17 | 446 | 40.7 | 5.20 | -4.14 | -0.343 | -0.49 | -0.74 | -0.20 | 87.28 | 11 | oui : drawdown 10.17% >= seuil 10% | 0.58 | 0.04 |
| BTCUSDT | paris | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | dynamique | 110 | 1001.11 | 1.11 | 0.11 | 1.00 | 10.00 | 238 | 43.6 | 10.93 | -8.44 | 0.010 | 0.08 | 0.13 | 0.01 | 128.51 | 6 | oui : drawdown 10.00% >= seuil 10% | 0.96 | 0.54 |
| BTCUSDT | paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | 129 | 1001.02 | 1.02 | 0.10 | 1.01 | 3.62 | 519 | 44.2 | 2.65 | -2.09 | 0.008 | -0.05 | -0.07 | 0.01 | 42.34 | 8 | non | 0.01 | 0.00 |
| BTCUSDT | paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | 129 | 1001.19 | 1.19 | 0.12 | 1.00 | 7.13 | 519 | 44.2 | 5.35 | -4.22 | 0.009 | -0.05 | -0.07 | 0.01 | 85.50 | 8 | non | 0.25 | 0.01 |
| BTCUSDT | paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | 111 | 1011.72 | 11.72 | 1.17 | 1.02 | 10.40 | 342 | 44.1 | 11.33 | -8.76 | 0.106 | 0.02 | 0.03 | 0.05 | 147.67 | 8 | oui : drawdown 10.40% >= seuil 10% | 0.80 | 0.22 |
| BTCUSDT | paris | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | prudent | 184 | 975.43 | -24.57 | -2.46 | 0.88 | 6.84 | 726 | 44.0 | 2.26 | -2.01 | -0.134 | -0.40 | -0.61 | -0.11 | 56.67 | 10 | non | 0.04 | 0.00 |
| BTCUSDT | paris | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | equilibre | 152 | 969.77 | -30.23 | -3.02 | 0.91 | 10.21 | 366 | 44.7 | 4.73 | -4.19 | -0.199 | -0.30 | -0.46 | -0.12 | 94.18 | 6 | oui : drawdown 10.21% >= seuil 10% | 0.54 | 0.03 |
| BTCUSDT | paris | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | dynamique | 129 | 1042.67 | 42.67 | 4.27 | 1.07 | 10.41 | 183 | 48.8 | 10.12 | -9.01 | 0.331 | 0.30 | 0.49 | 0.21 | 167.26 | 5 | oui : drawdown 10.41% >= seuil 10% | 0.96 | 0.50 |
| BTCUSDT | london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | 199 | 940.11 | -59.89 | -5.99 | 0.78 | 8.08 | 833 | 38.2 | 2.78 | -2.20 | -0.301 | -0.87 | -1.27 | -0.22 | 69.01 | 13 | non | 0.37 | 0.00 |
| BTCUSDT | london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | 150 | 936.80 | -63.20 | -6.32 | 0.85 | 10.39 | 358 | 40.0 | 5.86 | -4.61 | -0.421 | -0.64 | -0.95 | -0.28 | 103.95 | 13 | oui : drawdown 10.39% >= seuil 10% | 0.90 | 0.32 |
| BTCUSDT | london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | 135 | 976.45 | -23.55 | -2.36 | 0.97 | 10.45 | 261 | 43.0 | 12.01 | -9.35 | -0.174 | -0.09 | -0.14 | -0.12 | 187.91 | 6 | oui : drawdown 10.45% >= seuil 10% | 1.00 | 0.88 |
| BTCUSDT | london | NXA-01 | `{"target_r": 2.0}` | prudent | 267 | 958.09 | -41.91 | -4.19 | 0.87 | 8.36 | 593 | 40.8 | 2.48 | -1.98 | -0.157 | -0.56 | -0.84 | -0.15 | 81.09 | 9 | non | 0.22 | 0.00 |
| BTCUSDT | london | NXA-01 | `{"target_r": 2.0}` | equilibre | 217 | 980.70 | -19.30 | -1.93 | 0.96 | 10.17 | 225 | 42.9 | 5.26 | -4.10 | -0.089 | -0.14 | -0.22 | -0.08 | 131.69 | 9 | oui : drawdown 10.17% >= seuil 10% | 0.81 | 0.18 |
| BTCUSDT | london | NXA-01 | `{"target_r": 2.0}` | dynamique | 191 | 1060.10 | 60.10 | 6.01 | 1.07 | 10.65 | 155 | 44.5 | 11.36 | -8.54 | 0.315 | 0.34 | 0.54 | 0.27 | 243.45 | 9 | oui : drawdown 10.65% >= seuil 10% | 0.99 | 0.78 |
| BTCUSDT | london | NXA-01 | `{"target_r": "none"}` | prudent | 248 | 954.89 | -45.11 | -4.51 | 0.86 | 10.15 | 365 | 37.5 | 2.90 | -2.03 | -0.182 | -0.57 | -0.99 | -0.16 | 75.79 | 9 | oui : drawdown 10.15% >= seuil 10% | 0.42 | 0.00 |
| BTCUSDT | london | NXA-01 | `{"target_r": "none"}` | equilibre | 202 | 1014.21 | 14.21 | 1.42 | 1.03 | 10.04 | 121 | 41.1 | 6.22 | -4.22 | 0.070 | 0.14 | 0.26 | 0.06 | 124.74 | 9 | oui : drawdown 10.04% >= seuil 10% | 0.91 | 0.38 |
| BTCUSDT | london | NXA-01 | `{"target_r": "none"}` | dynamique | 188 | 1126.06 | 126.06 | 12.61 | 1.13 | 10.79 | 106 | 42.6 | 13.54 | -8.86 | 0.671 | 0.54 | 1.06 | 0.56 | 246.59 | 9 | oui : drawdown 10.79% >= seuil 10% | 1.00 | 0.89 |
| BTCUSDT | london | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | prudent | 172 | 977.10 | -22.90 | -2.29 | 0.89 | 6.33 | 785 | 41.9 | 2.51 | -2.04 | -0.133 | -0.35 | -0.53 | -0.11 | 51.97 | 13 | non | 0.04 | 0.00 |
| BTCUSDT | london | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | equilibre | 148 | 963.06 | -36.94 | -3.69 | 0.90 | 10.18 | 446 | 41.2 | 5.36 | -4.18 | -0.250 | -0.34 | -0.51 | -0.15 | 89.34 | 12 | oui : drawdown 10.18% >= seuil 10% | 0.54 | 0.03 |
| BTCUSDT | london | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | dynamique | 110 | 1027.56 | 27.56 | 2.76 | 1.05 | 10.41 | 125 | 44.5 | 11.33 | -8.65 | 0.251 | 0.27 | 0.43 | 0.16 | 133.92 | 6 | oui : drawdown 10.41% >= seuil 10% | 0.95 | 0.50 |
| BTCUSDT | london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | 131 | 1000.84 | 0.84 | 0.08 | 1.01 | 4.88 | 519 | 42.7 | 2.93 | -2.18 | 0.006 | -0.05 | -0.07 | 0.01 | 45.07 | 8 | non | 0.00 | 0.00 |
| BTCUSDT | london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | 131 | 1000.78 | 0.78 | 0.08 | 1.00 | 9.55 | 519 | 42.7 | 5.97 | -4.44 | 0.006 | -0.05 | -0.07 | 0.00 | 91.80 | 8 | non | 0.27 | 0.00 |
| BTCUSDT | london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | 108 | 1057.31 | 57.31 | 5.73 | 1.10 | 10.48 | 188 | 45.4 | 12.45 | -9.37 | 0.531 | 0.29 | 0.46 | 0.25 | 152.59 | 8 | oui : drawdown 10.48% >= seuil 10% | 0.81 | 0.23 |
| BTCUSDT | london | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | prudent | 181 | 958.61 | -41.39 | -4.14 | 0.81 | 8.28 | 740 | 41.4 | 2.33 | -2.04 | -0.229 | -0.69 | -1.01 | -0.15 | 57.00 | 14 | non | 0.12 | 0.00 |
| BTCUSDT | london | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | equilibre | 144 | 981.03 | -18.97 | -1.90 | 0.94 | 10.14 | 271 | 45.1 | 4.93 | -4.29 | -0.132 | -0.20 | -0.30 | -0.09 | 92.30 | 7 | oui : drawdown 10.14% >= seuil 10% | 0.73 | 0.09 |
| BTCUSDT | london | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | dynamique | 127 | 1065.56 | 65.56 | 6.56 | 1.11 | 10.37 | 174 | 48.8 | 10.55 | -9.05 | 0.516 | 0.44 | 0.72 | 0.32 | 169.75 | 4 | oui : drawdown 10.37% >= seuil 10% | 0.98 | 0.71 |
| BTCUSDT | utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | 197 | 939.67 | -60.33 | -6.03 | 0.78 | 8.00 | 740 | 38.6 | 2.78 | -2.25 | -0.306 | -0.88 | -1.28 | -0.22 | 68.35 | 12 | non | 0.39 | 0.00 |
| BTCUSDT | utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | 162 | 933.84 | -66.16 | -6.62 | 0.85 | 10.41 | 372 | 41.4 | 5.65 | -4.68 | -0.408 | -0.60 | -0.90 | -0.26 | 111.93 | 12 | oui : drawdown 10.41% >= seuil 10% | 0.90 | 0.34 |
| BTCUSDT | utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | 140 | 966.33 | -33.67 | -3.37 | 0.96 | 10.78 | 181 | 44.3 | 11.60 | -9.65 | -0.241 | -0.14 | -0.22 | -0.16 | 196.57 | 6 | oui : drawdown 10.78% >= seuil 10% | 1.00 | 0.88 |
| BTCUSDT | utc | NXA-01 | `{"target_r": 2.0}` | prudent | 268 | 952.58 | -47.42 | -4.74 | 0.85 | 8.69 | 596 | 42.2 | 2.38 | -2.04 | -0.177 | -0.63 | -0.95 | -0.16 | 82.21 | 7 | non | 0.25 | 0.00 |
| BTCUSDT | utc | NXA-01 | `{"target_r": 2.0}` | equilibre | 221 | 978.28 | -21.72 | -2.17 | 0.96 | 10.02 | 230 | 44.8 | 5.00 | -4.23 | -0.098 | -0.16 | -0.25 | -0.09 | 135.03 | 7 | oui : drawdown 10.02% >= seuil 10% | 0.83 | 0.21 |
| BTCUSDT | utc | NXA-01 | `{"target_r": 2.0}` | dynamique | 195 | 1056.61 | 56.61 | 5.66 | 1.06 | 10.18 | 173 | 47.2 | 10.60 | -8.92 | 0.290 | 0.31 | 0.50 | 0.26 | 246.77 | 7 | oui : drawdown 10.18% >= seuil 10% | 0.99 | 0.81 |
| BTCUSDT | utc | NXA-01 | `{"target_r": "none"}` | prudent | 262 | 958.66 | -41.34 | -4.13 | 0.88 | 10.01 | 656 | 39.3 | 2.81 | -2.08 | -0.158 | -0.46 | -0.83 | -0.13 | 81.04 | 9 | oui : drawdown 10.01% >= seuil 10% | 0.31 | 0.00 |
| BTCUSDT | utc | NXA-01 | `{"target_r": "none"}` | equilibre | 216 | 1018.68 | 18.68 | 1.87 | 1.03 | 10.11 | 366 | 43.1 | 6.04 | -4.41 | 0.086 | 0.16 | 0.30 | 0.07 | 137.08 | 7 | oui : drawdown 10.11% >= seuil 10% | 0.86 | 0.28 |
| BTCUSDT | utc | NXA-01 | `{"target_r": "none"}` | dynamique | 195 | 1140.77 | 140.77 | 14.08 | 1.14 | 10.60 | 230 | 45.1 | 13.24 | -9.57 | 0.722 | 0.56 | 1.12 | 0.62 | 262.41 | 7 | oui : drawdown 10.60% >= seuil 10% | 1.00 | 0.84 |
| BTCUSDT | utc | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | prudent | 163 | 979.90 | -20.10 | -2.01 | 0.90 | 5.36 | 785 | 44.2 | 2.44 | -2.15 | -0.123 | -0.30 | -0.46 | -0.11 | 50.32 | 13 | non | 0.03 | 0.00 |
| BTCUSDT | utc | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | equilibre | 148 | 963.28 | -36.72 | -3.67 | 0.90 | 10.09 | 497 | 43.9 | 5.10 | -4.44 | -0.248 | -0.31 | -0.48 | -0.14 | 91.69 | 13 | oui : drawdown 10.09% >= seuil 10% | 0.50 | 0.02 |
| BTCUSDT | utc | NXA-02 | `{"target_r": 2.0, "trend_filter": true}` | dynamique | 134 | 1023.88 | 23.88 | 2.39 | 1.04 | 10.60 | 417 | 47.0 | 10.65 | -9.12 | 0.178 | 0.20 | 0.31 | 0.09 | 168.96 | 6 | oui : drawdown 10.60% >= seuil 10% | 0.93 | 0.46 |
| BTCUSDT | utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | 121 | 1006.70 | 6.70 | 0.67 | 1.05 | 5.00 | 532 | 47.1 | 2.61 | -2.22 | 0.055 | 0.19 | 0.30 | 0.04 | 42.14 | 20 | non | 0.00 | 0.00 |
| BTCUSDT | utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | 121 | 1012.59 | 12.59 | 1.26 | 1.04 | 9.76 | 532 | 47.1 | 5.30 | -4.53 | 0.104 | 0.19 | 0.30 | 0.04 | 85.95 | 20 | non | 0.19 | 0.00 |
| BTCUSDT | utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | 101 | 1096.86 | 96.86 | 9.69 | 1.21 | 10.60 | 122 | 51.5 | 10.92 | -9.61 | 0.959 | 0.72 | 1.20 | 0.45 | 144.55 | 12 | oui : drawdown 10.60% >= seuil 10% | 0.76 | 0.16 |
| BTCUSDT | utc | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | prudent | 170 | 963.66 | -36.34 | -3.63 | 0.83 | 7.15 | 740 | 41.2 | 2.46 | -2.09 | -0.214 | -0.60 | -0.89 | -0.15 | 54.50 | 12 | non | 0.10 | 0.00 |
| BTCUSDT | utc | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | equilibre | 143 | 967.42 | -32.58 | -3.26 | 0.91 | 10.13 | 376 | 43.4 | 5.13 | -4.33 | -0.228 | -0.33 | -0.50 | -0.13 | 92.16 | 7 | oui : drawdown 10.13% >= seuil 10% | 0.68 | 0.07 |
| BTCUSDT | utc | NXA-04 | `{"entry_mode": "retest", "target_r": 2.0}` | dynamique | 125 | 1033.21 | 33.21 | 3.32 | 1.05 | 10.63 | 221 | 46.4 | 11.14 | -9.15 | 0.266 | 0.24 | 0.38 | 0.15 | 167.90 | 5 | oui : drawdown 10.63% >= seuil 10% | 0.98 | 0.65 |

### Stabilité temporelle (E[R] net par semestre)

- BTCUSDT paris REF-SBA-01 `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` — 2020-01 : 0.20 (n=24), 2020-07 : -0.06 (n=26), 2021-01 : 0.06 (n=53), 2021-07 : -0.34 (n=36), 2022-01 : -0.82 (n=24), 2022-07 : -0.16 (n=25), 2023-01 : -0.11 (n=10)
- BTCUSDT paris NXA-01 `{"target_r": 2.0}` — 2020-01 : 0.09 (n=37), 2020-07 : -0.01 (n=37), 2021-01 : 0.15 (n=59), 2021-07 : -0.09 (n=48), 2022-01 : -0.49 (n=35), 2022-07 : -0.22 (n=30), 2023-01 : -0.13 (n=19)
- BTCUSDT paris NXA-01 `{"target_r": "none"}` — 2020-01 : 0.16 (n=37), 2020-07 : -0.01 (n=37), 2021-01 : 0.25 (n=59), 2021-07 : -0.08 (n=48), 2022-01 : -0.63 (n=35), 2022-07 : -0.24 (n=30), 2023-01 : -0.20 (n=19)
- BTCUSDT paris NXA-02 `{"target_r": 2.0, "trend_filter": true}` — 2020-01 : 0.06 (n=23), 2020-07 : -0.06 (n=31), 2021-01 : 0.12 (n=43), 2021-07 : -0.15 (n=34), 2022-01 : -0.56 (n=15), 2022-07 : -0.32 (n=14), 2023-01 : 0.04 (n=15)
- BTCUSDT paris NXA-03 `{"compression_filter": true, "target_r": 2.0}` — 2020-01 : 0.06 (n=17), 2020-07 : 0.07 (n=14), 2021-01 : 0.17 (n=38), 2021-07 : -0.07 (n=32), 2022-01 : -0.63 (n=13), 2022-07 : 0.13 (n=13), 2023-01 : 0.23 (n=2)
- BTCUSDT paris NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` — 2020-01 : 0.31 (n=26), 2020-07 : 0.08 (n=23), 2021-01 : 0.12 (n=46), 2021-07 : -0.27 (n=36), 2022-01 : -0.64 (n=25), 2022-07 : -0.15 (n=17), 2023-01 : 0.18 (n=11)
- BTCUSDT london REF-SBA-01 `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` — 2020-01 : 0.29 (n=22), 2020-07 : -0.07 (n=28), 2021-01 : 0.02 (n=55), 2021-07 : -0.40 (n=36), 2022-01 : -0.62 (n=22), 2022-07 : -0.17 (n=25), 2023-01 : -0.22 (n=11)
- BTCUSDT london NXA-01 `{"target_r": 2.0}` — 2020-01 : 0.16 (n=36), 2020-07 : 0.06 (n=40), 2021-01 : 0.14 (n=60), 2021-07 : -0.10 (n=49), 2022-01 : -0.53 (n=35), 2022-07 : -0.34 (n=31), 2023-01 : -0.11 (n=16)
- BTCUSDT london NXA-01 `{"target_r": "none"}` — 2020-01 : 0.16 (n=36), 2020-07 : 0.08 (n=40), 2021-01 : 0.24 (n=60), 2021-07 : -0.08 (n=49), 2022-01 : -0.81 (n=35), 2022-07 : -0.43 (n=31), 2023-01 : -0.19 (n=16)
- BTCUSDT london NXA-02 `{"target_r": 2.0, "trend_filter": true}` — 2020-01 : 0.21 (n=21), 2020-07 : -0.04 (n=31), 2021-01 : 0.13 (n=43), 2021-07 : -0.11 (n=33), 2022-01 : -0.60 (n=16), 2022-07 : -0.39 (n=15), 2023-01 : 0.01 (n=13)
- BTCUSDT london NXA-03 `{"compression_filter": true, "target_r": 2.0}` — 2020-01 : 0.17 (n=18), 2020-07 : 0.33 (n=14), 2021-01 : 0.18 (n=38), 2021-07 : -0.09 (n=32), 2022-01 : -0.78 (n=14), 2022-07 : -0.05 (n=14), 2023-01 : 0.48 (n=1)
- BTCUSDT london NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` — 2020-01 : 0.36 (n=23), 2020-07 : 0.19 (n=25), 2021-01 : 0.12 (n=47), 2021-07 : -0.31 (n=36), 2022-01 : -0.82 (n=25), 2022-07 : -0.38 (n=16), 2023-01 : 0.00 (n=9)
- BTCUSDT utc REF-SBA-01 `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` — 2020-01 : 0.16 (n=23), 2020-07 : 0.00 (n=26), 2021-01 : 0.08 (n=55), 2021-07 : -0.37 (n=39), 2022-01 : -0.51 (n=20), 2022-07 : -0.37 (n=24), 2023-01 : -0.36 (n=10)
- BTCUSDT utc NXA-01 `{"target_r": 2.0}` — 2020-01 : -0.00 (n=39), 2020-07 : 0.15 (n=40), 2021-01 : 0.13 (n=59), 2021-07 : -0.02 (n=53), 2022-01 : -0.60 (n=32), 2022-07 : -0.43 (n=31), 2023-01 : -0.15 (n=14)
- BTCUSDT utc NXA-01 `{"target_r": "none"}` — 2020-01 : 0.07 (n=39), 2020-07 : 0.14 (n=40), 2021-01 : 0.32 (n=59), 2021-07 : -0.10 (n=53), 2022-01 : -0.71 (n=32), 2022-07 : -0.48 (n=31), 2023-01 : -0.20 (n=14)
- BTCUSDT utc NXA-02 `{"target_r": 2.0, "trend_filter": true}` — 2020-01 : 0.04 (n=21), 2020-07 : 0.11 (n=30), 2021-01 : 0.11 (n=40), 2021-07 : 0.15 (n=31), 2022-01 : -0.84 (n=14), 2022-07 : -0.63 (n=16), 2023-01 : -0.05 (n=11)
- BTCUSDT utc NXA-03 `{"compression_filter": true, "target_r": 2.0}` — 2020-01 : 0.04 (n=15), 2020-07 : 0.12 (n=14), 2021-01 : 0.28 (n=38), 2021-07 : 0.15 (n=29), 2022-01 : -1.13 (n=13), 2022-07 : -0.14 (n=10), 2023-01 : 0.92 (n=2)
- BTCUSDT utc NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` — 2020-01 : 0.27 (n=23), 2020-07 : 0.32 (n=21), 2021-01 : 0.05 (n=42), 2021-07 : -0.19 (n=37), 2022-01 : -0.75 (n=21), 2022-07 : -0.46 (n=18), 2023-01 : -0.04 (n=8)

### Ablations (différence d'E[R] vs modèle de base, IC95 bootstrap hebdomadaire)

- BTCUSDT paris NXA-02 `{"target_r": 2.0, "trend_filter": true}` : Δ = 0.002 [-0.099 ; 0.101] → contribution non démontrée
- BTCUSDT paris NXA-03 `{"compression_filter": true, "target_r": 2.0}` : Δ = 0.074 [-0.067 ; 0.218] → contribution non démontrée
- BTCUSDT paris NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` : Δ = 0.014 [-0.107 ; 0.141] → contribution non démontrée
- BTCUSDT london NXA-02 `{"target_r": 2.0, "trend_filter": true}` : Δ = 0.011 [-0.096 ; 0.120] → contribution non démontrée
- BTCUSDT london NXA-03 `{"compression_filter": true, "target_r": 2.0}` : Δ = 0.073 [-0.071 ; 0.213] → contribution non démontrée
- BTCUSDT london NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` : Δ = -0.035 [-0.151 ; 0.082] → contribution non démontrée
- BTCUSDT utc NXA-02 `{"target_r": 2.0, "trend_filter": true}` : Δ = 0.024 [-0.095 ; 0.144] → contribution non démontrée
- BTCUSDT utc NXA-03 `{"compression_filter": true, "target_r": 2.0}` : Δ = 0.105 [-0.049 ; 0.265] → contribution non démontrée
- BTCUSDT utc NXA-04 `{"entry_mode": "retest", "target_r": 2.0}` : Δ = -0.016 [-0.151 ; 0.119] → contribution non démontrée
