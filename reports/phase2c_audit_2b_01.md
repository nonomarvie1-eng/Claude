## Audit du lot 2B-01 (NEXUS A et référence SBA, BTC/USDT spot, M5)

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Prix BTC : 7201 → 30472 USDT sur la période de développement.

| Session | Hypothèse | Variante | Trades | Reproduction (enregistré → recalculé) | E[R] sans frottement [IC95] | E[R] avant commissions [IC95] | E[R] net [IC95] | Coût moyen (R) | Frais BNB (sensib.) | Aléatoire expo. comparable (p) | Rendement/trade % : stratégie / aléatoire / détention même fenêtre | Alpha %/an [IC95] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 198 | -0.1562 → -0.1562 | +0.056 [-0.088 ; +0.201] | +0.013 [-0.153 ; +0.189] | -0.156 [-0.321 ; +0.019] | 0.169 | -0.116 | -0.191 (0.358) | +0.005 / -0.228 / -0.155 | -4.41 [-8.34 ; -0.36] |
| paris | NXA-01 | `{"target_r": 2.0}` | 265 | -0.0723 → -0.0723 | +0.102 [-0.028 ; +0.234] | +0.066 [-0.064 ; +0.201] | -0.072 [-0.202 ; +0.063] | 0.138 | -0.058 | -0.153 (0.100) | +0.061 / -0.225 / -0.155 | -3.42 [-7.15 ; +0.73] |
| paris | NXA-01 | `{"target_r": "none"}` | 265 | -0.0647 → -0.0647 | +0.144 [-0.018 ; +0.312] | +0.074 [-0.081 ; +0.241] | -0.065 [-0.219 ; +0.102] | 0.138 | -0.024 | -0.149 (0.090) | +0.062 / -0.217 / -0.155 | -3.54 [-7.70 ; +1.05] |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 129 | +0.0015 → +0.0015 | +0.156 [-0.040 ; +0.350] | +0.157 [-0.064 ; +0.374] | +0.002 [-0.219 ; +0.220] | 0.155 | -0.034 | -0.172 (0.040) | +0.257 / -0.224 / -0.155 | -0.80 [-4.09 ; +2.71] |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 199 | -0.1444 → -0.1444 | +0.071 [-0.071 ; +0.211] | +0.025 [-0.145 ; +0.199] | -0.144 [-0.315 ; +0.028] | 0.170 | -0.094 | -0.193 (0.244) | -0.004 / -0.230 / -0.155 | -4.08 [-7.58 ; -0.17] |
| london | NXA-01 | `{"target_r": 2.0}` | 267 | -0.0711 → -0.0711 | +0.095 [-0.033 ; +0.225] | +0.071 [-0.066 ; +0.210] | -0.071 [-0.207 ; +0.067] | 0.142 | -0.077 | -0.154 (0.080) | +0.024 / -0.218 / -0.155 | -3.26 [-7.12 ; +1.01] |
| london | NXA-01 | `{"target_r": "none"}` | 267 | -0.0948 → -0.0948 | +0.128 [-0.039 ; +0.301] | +0.048 [-0.110 ; +0.204] | -0.095 [-0.252 ; +0.060] | 0.142 | -0.075 | -0.152 (0.204) | +0.001 / -0.216 / -0.155 | -4.31 [-8.63 ; +0.48] |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 131 | +0.0020 → +0.0020 | +0.133 [-0.053 ; +0.316] | +0.165 [-0.061 ; +0.391] | +0.002 [-0.225 ; +0.228] | 0.162 | -0.057 | -0.187 (0.020) | +0.240 / -0.230 / -0.155 | -0.75 [-4.26 ; +2.90] |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 197 | -0.1459 → -0.1459 | +0.020 [-0.116 ; +0.154] | +0.023 [-0.158 ; +0.213] | -0.146 [-0.326 ; +0.043] | 0.169 | -0.072 | -0.200 (0.229) | -0.046 / -0.235 / -0.145 | -4.14 [-7.85 ; +0.11] |
| utc | NXA-01 | `{"target_r": 2.0}` | 268 | -0.0817 → -0.0817 | +0.042 [-0.081 ; +0.170] | +0.063 [-0.072 ; +0.204] | -0.082 [-0.216 ; +0.057] | 0.145 | -0.091 | -0.158 (0.129) | +0.019 / -0.218 / -0.145 | -3.61 [-7.24 ; +0.53] |
| utc | NXA-01 | `{"target_r": "none"}` | 268 | -0.0694 → -0.0694 | +0.106 [-0.062 ; +0.277] | +0.076 [-0.088 ; +0.246] | -0.069 [-0.232 ; +0.101] | 0.145 | -0.074 | -0.158 (0.080) | +0.052 / -0.224 / -0.145 | -3.56 [-7.69 ; +1.33] |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 121 | +0.0237 → +0.0237 | +0.090 [-0.108 ; +0.286] | +0.189 [-0.038 ; +0.427] | +0.024 [-0.205 ; +0.264] | 0.165 | -0.032 | -0.186 (0.025) | +0.291 / -0.228 / -0.145 | +0.10 [-3.46 ; +3.08] |

### Sensibilité aux coûts (E[R] net ; multiplicateur de tous les coûts — le nombre de trades varie car le filtre de faisabilité s'applique)

| Session | Hypothèse | Variante | ×0 | ×0,25 | ×0,5 | ×0,75 | ×1 | ×1,5 | ×2 |
|---|---|---|---|---|---|---|---|---|---|
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | +0.056 (n=313) | -0.015 (n=313) | -0.082 (n=296) | -0.113 (n=246) | -0.156 (n=198) | -0.269 (n=111) | -0.381 (n=58) |
| paris | NXA-01 | `{"target_r": 2.0}` | +0.102 (n=313) | +0.049 (n=313) | -0.008 (n=310) | -0.057 (n=288) | -0.072 (n=265) | -0.130 (n=191) | -0.222 (n=139) |
| paris | NXA-01 | `{"target_r": "none"}` | +0.144 (n=313) | +0.092 (n=313) | +0.034 (n=310) | -0.020 (n=288) | -0.065 (n=265) | -0.082 (n=191) | -0.187 (n=139) |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | +0.156 (n=173) | +0.089 (n=173) | +0.020 (n=170) | -0.035 (n=150) | +0.002 (n=129) | -0.035 (n=79) | -0.086 (n=47) |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | +0.071 (n=329) | -0.002 (n=329) | -0.075 (n=306) | -0.097 (n=255) | -0.144 (n=199) | -0.285 (n=111) | -0.365 (n=57) |
| london | NXA-01 | `{"target_r": 2.0}` | +0.095 (n=329) | +0.033 (n=328) | -0.023 (n=325) | -0.073 (n=296) | -0.071 (n=267) | -0.115 (n=184) | -0.234 (n=134) |
| london | NXA-01 | `{"target_r": "none"}` | +0.128 (n=329) | +0.059 (n=328) | -0.003 (n=325) | -0.073 (n=296) | -0.095 (n=267) | -0.075 (n=184) | -0.210 (n=134) |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | +0.133 (n=185) | +0.052 (n=184) | -0.019 (n=181) | -0.053 (n=155) | +0.002 (n=131) | -0.006 (n=73) | -0.048 (n=44) |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | +0.020 (n=352) | -0.054 (n=348) | -0.113 (n=317) | -0.078 (n=256) | -0.146 (n=197) | -0.274 (n=111) | -0.353 (n=52) |
| utc | NXA-01 | `{"target_r": 2.0}` | +0.042 (n=352) | -0.016 (n=349) | -0.078 (n=343) | -0.090 (n=305) | -0.082 (n=268) | -0.144 (n=184) | -0.246 (n=128) |
| utc | NXA-01 | `{"target_r": "none"}` | +0.106 (n=352) | +0.039 (n=349) | -0.035 (n=343) | -0.074 (n=305) | -0.069 (n=268) | -0.093 (n=184) | -0.227 (n=128) |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | +0.090 (n=192) | +0.016 (n=189) | -0.055 (n=183) | -0.025 (n=148) | +0.024 (n=121) | +0.000 (n=69) | -0.057 (n=41) |

### Par année et par régime de tendance (E[R] net)

| Session | Hypothèse | Variante | Années | Tendance (n, E[R]) |
|---|---|---|---|---|
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 2020 +0.07, 2021 -0.10, 2022 -0.49, 2023 -0.11 | baissier (72, -0.35), consolidation (13, -0.59), haussier (95, -0.00), indéfini (18, +0.10) |
| paris | NXA-01 | `{"target_r": 2.0}` | 2020 +0.04, 2021 +0.04, 2022 -0.37, 2023 -0.13 | baissier (92, -0.26), consolidation (16, -0.20), haussier (130, +0.04), indéfini (27, +0.09) |
| paris | NXA-01 | `{"target_r": "none"}` | 2020 +0.07, 2021 +0.10, 2022 -0.45, 2023 -0.20 | baissier (92, -0.31), consolidation (16, -0.16), haussier (130, +0.07), indéfini (27, +0.19) |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 2020 +0.06, 2021 +0.06, 2022 -0.25, 2023 +0.23 | baissier (46, -0.15), consolidation (5, -0.17), haussier (67, +0.12), indéfini (11, +0.01) |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 2020 +0.09, 2021 -0.14, 2022 -0.38, 2023 -0.22 | baissier (70, -0.29), consolidation (15, -0.54), haussier (97, -0.04), indéfini (17, +0.20) |
| london | NXA-01 | `{"target_r": 2.0}` | 2020 +0.11, 2021 +0.03, 2022 -0.44, 2023 -0.11 | baissier (93, -0.31), consolidation (18, -0.21), haussier (130, +0.07), indéfini (26, +0.18) |
| london | NXA-01 | `{"target_r": "none"}` | 2020 +0.12, 2021 +0.10, 2022 -0.63, 2023 -0.19 | baissier (93, -0.44), consolidation (18, -0.16), haussier (130, +0.11), indéfini (26, +0.16) |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 2020 +0.24, 2021 +0.05, 2022 -0.41, 2023 +0.48 | baissier (46, -0.31), consolidation (7, +0.07), haussier (66, +0.18), indéfini (12, +0.15) |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | 2020 +0.07, 2021 -0.11, 2022 -0.43, 2023 -0.36 | baissier (68, -0.29), consolidation (17, -0.69), haussier (96, -0.00), indéfini (16, +0.19) |
| utc | NXA-01 | `{"target_r": 2.0}` | 2020 +0.07, 2021 +0.06, 2022 -0.51, 2023 -0.15 | baissier (91, -0.32), consolidation (20, -0.27), haussier (131, +0.09), indéfini (26, +0.06) |
| utc | NXA-01 | `{"target_r": "none"}` | 2020 +0.10, 2021 +0.12, 2022 -0.60, 2023 -0.20 | baissier (91, -0.40), consolidation (20, -0.23), haussier (131, +0.14), indéfini (26, +0.15) |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | 2020 +0.08, 2021 +0.22, 2022 -0.70, 2023 +0.92 | baissier (42, -0.40), consolidation (6, +0.02), haussier (63, +0.29), indéfini (10, +0.12) |

### Biais de l'arrêt à 10 % : capital avec et sans arrêt (analytique)

| Session | Hypothèse | Variante | Profil | Avec arrêt : rendement % / DD % / date d'arrêt | Sans arrêt : rendement % / DD % |
|---|---|---|---|---|---|
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | -6.4 / 8.6 / non | -6.4 / 8.6 |
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | -6.0 / 10.1 / 2022-02-27 | -12.5 / 16.5 |
| paris | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | -2.4 / 10.5 / 2021-12-14 | -23.9 / 30.5 |
| paris | NXA-01 | `{"target_r": 2.0}` | prudent | -4.2 / 7.8 / non | -4.2 / 7.8 |
| paris | NXA-01 | `{"target_r": 2.0}` | equilibre | -3.2 / 10.1 / 2022-06-20 | -8.3 / 15.0 |
| paris | NXA-01 | `{"target_r": 2.0}` | dynamique | +3.6 / 10.2 / 2022-01-26 | -16.4 / 27.9 |
| paris | NXA-01 | `{"target_r": "none"}` | prudent | -3.7 / 9.3 / non | -3.7 / 9.3 |
| paris | NXA-01 | `{"target_r": "none"}` | equilibre | +0.3 / 10.1 / 2022-05-17 | -7.5 / 17.8 |
| paris | NXA-01 | `{"target_r": "none"}` | dynamique | +10.8 / 10.3 / 2022-01-05 | -15.2 / 32.6 |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | +0.1 / 3.6 / non | +0.1 / 3.6 |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | +0.1 / 7.1 / non | +0.1 / 7.1 |
| paris | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | +1.2 / 10.4 / 2022-05-21 | -0.1 / 13.8 |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | -6.0 / 8.1 / non | -6.0 / 8.1 |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | -6.3 / 10.4 / 2022-03-08 | -11.7 / 15.6 |
| london | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | -2.4 / 10.4 / 2021-12-01 | -22.6 / 29.0 |
| london | NXA-01 | `{"target_r": 2.0}` | prudent | -4.2 / 8.4 / non | -4.2 / 8.4 |
| london | NXA-01 | `{"target_r": 2.0}` | equilibre | -1.9 / 10.2 / 2022-06-23 | -8.4 / 16.1 |
| london | NXA-01 | `{"target_r": 2.0}` | dynamique | +6.0 / 10.6 / 2022-02-01 | -16.6 / 29.7 |
| london | NXA-01 | `{"target_r": "none"}` | prudent | -4.5 / 10.2 / 2022-11-10 | -5.3 / 11.1 |
| london | NXA-01 | `{"target_r": "none"}` | equilibre | +1.4 / 10.0 / 2022-03-11 | -10.6 / 21.0 |
| london | NXA-01 | `{"target_r": "none"}` | dynamique | +12.6 / 10.8 / 2022-01-11 | -20.8 / 37.7 |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | +0.1 / 4.9 / non | +0.1 / 4.9 |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | +0.1 / 9.6 / non | +0.1 / 9.6 |
| london | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | +5.7 / 10.5 / 2022-04-15 | -0.2 / 18.3 |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | prudent | -6.0 / 8.0 / non | -6.0 / 8.0 |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | equilibre | -6.6 / 10.4 / 2022-06-23 | -11.8 / 15.4 |
| utc | REF-SBA-01 | `{"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}` | dynamique | -3.4 / 10.8 / 2021-12-14 | -22.7 / 28.6 |
| utc | NXA-01 | `{"target_r": 2.0}` | prudent | -4.7 / 8.7 / non | -4.7 / 8.7 |
| utc | NXA-01 | `{"target_r": 2.0}` | equilibre | -2.2 / 10.0 / 2022-06-25 | -9.4 / 16.7 |
| utc | NXA-01 | `{"target_r": 2.0}` | dynamique | +5.7 / 10.2 / 2022-02-01 | -18.5 / 30.7 |
| utc | NXA-01 | `{"target_r": "none"}` | prudent | -4.1 / 10.0 / 2023-04-03 | -4.0 / 10.0 |
| utc | NXA-01 | `{"target_r": "none"}` | equilibre | +1.9 / 10.1 / 2022-06-17 | -8.0 / 19.1 |
| utc | NXA-01 | `{"target_r": "none"}` | dynamique | +14.1 / 10.6 / 2022-02-01 | -16.2 / 34.7 |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | prudent | +0.7 / 5.0 / non | +0.7 / 5.0 |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | equilibre | +1.3 / 9.8 / non | +1.3 / 9.8 |
| utc | NXA-03 | `{"compression_filter": true, "target_r": 2.0}` | dynamique | +9.7 / 10.6 / 2022-03-05 | +2.2 / 18.6 |