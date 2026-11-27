## Lot 4-01 — stratégies compatibles Cubrik (période de développement 2020-01 → 2023-06)

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0 ; Binance n'est pas associé à ce projet.*

Univers (figé sur le volume d'oct.–déc. 2019) : BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, EOSUSDT, BCHUSDT, LTCUSDT, TRXUSDT, LINKUSDT, MATICUSDT. Perpétuels disponibles : BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, EOSUSDT, BCHUSDT, LTCUSDT, TRXUSDT, LINKUSDT, MATICUSDT. Essais au registre : 166.

### Stops % par actif (3 × médiane ATR14/clôture D1, S2 2019)

| Actif | ATR médian % | Stop % |
|---|---|---|
| BTCUSDT | 5.45 | 16 |
| ETHUSDT | 6.29 | 19 |
| BNBUSDT | 6.34 | 19 |
| XRPUSDT | 5.79 | 17 |
| EOSUSDT | 7.45 | 22 |
| BCHUSDT | 7.05 | 21 |
| LTCUSDT | 7.27 | 22 |
| TRXUSDT | 7.78 | 23 |
| LINKUSDT | 9.11 | 25 |
| MATICUSDT | 11.27 | 25 |

### Résultats principaux (USDT, risque 0,5 %/trade, sans arrêts globaux)

| Hypothèse | Trades | R moyen net [IC95] | Rendement total | CAGR | Max DD | Sharpe | PF | Réussite | Expo. moy. | Bêta | Δ vs référence %/an [IC95] | p | p BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4-01-DONCH | 103 | +2.548 [-0.098 ; +6.907] | +124.0 % | +26.0 % | 45.4 % | +0.82 | 3.14 | 27.2 % | 13.4 % | +0.227 | +13.54 [-10.81 ; +43.84] | 0.176 | 0.352 | **rejeté** |
| P4-02-SMA | 349 | +0.897 [-0.006 ; +2.353] | +140.6 % | +28.6 % | 52.4 % | +0.82 | 2.55 | 16.0 % | 21.2 % | +0.283 | +8.44 [-16.85 ; +39.78] | 0.279 | 0.372 | **rejeté** |
| P4-03-TSMOM-LS | 628 | +0.363 [-0.160 ; +1.298] | +70.0 % | +16.4 % | 58.4 % | +0.56 | 1.50 | 24.5 % | 30.1 % | +0.273 | +25.88 [-12.15 ; +70.01] | 0.113 | 0.352 | **rejeté** |
| P4-04-RSI2 | 253 | +0.004 [-0.106 ; +0.107] | +0.2 % | +0.1 % | 6.8 % | +0.04 | 1.01 | 62.8 % | 1.6 % | +0.023 | -1.77 [-5.06 ; +1.13] | 0.862 | 0.862 | **rejeté** |

Référence : panier équipondéré passif ramené à la même exposition moyenne (achat seulement) ; trésorerie pour P4-03.

### Critères

| Hypothèse | C1 alpha (p BH < 0,05) | C2 R > 0 (IC) | C3 coûts × 2 | C4 voisins | C5 sous-périodes | C6 DD < 10 % |
|---|---|---|---|---|---|---|
| P4-01-DONCH | non | non | oui | oui | non | non |
| P4-02-SMA | non | non | oui | oui | non | non |
| P4-03-TSMOM-LS | non | non | oui | oui | non | non |
| P4-04-RSI2 | non | non | non | non | non | oui |

### Stabilité temporelle (écart annualisé à la référence, %/an)

| Hypothèse | 2020 | 2021 | 2022 | 2023 S1 |
|---|---|---|---|---|
| P4-01-DONCH | -11.1 | +59.0 | +0.8 | -2.7 |
| P4-02-SMA | -23.5 | +52.6 | -0.6 | +2.1 |
| P4-03-TSMOM-LS | -13.0 | +111.1 | -9.6 | +4.1 |
| P4-04-RSI2 | +0.2 | -6.3 | -0.3 | +0.5 |

### Sensibilité (voisins pré-déclarés) et coûts × 2

| Hypothèse | Variante | Trades | R moyen | Δ vs référence %/an | p |
|---|---|---|---|---|---|
| P4-01-DONCH | {"entry_n": 40, "exit_n": 15} | 123 | +2.226 | +16.57 | 0.138 |
| P4-01-DONCH | {"entry_n": 70, "exit_n": 25} | 87 | +2.593 | +11.70 | 0.209 |
| P4-01-DONCH | {"stop_mult": 0.75} | 111 | +3.084 | +16.44 | 0.168 |
| P4-01-DONCH | {"stop_mult": 1.5} | 93 | +1.990 | +10.88 | 0.175 |
| P4-01-DONCH | coûts × 2 | 103 | +2.529 | +13.32 | 0.179 |
| P4-02-SMA | {"sma_n": 75} | 374 | +0.878 | +11.25 | 0.223 |
| P4-02-SMA | {"sma_n": 150} | 263 | +1.179 | +9.04 | 0.282 |
| P4-02-SMA | {"stop_mult": 0.75} | 349 | +1.206 | +9.78 | 0.278 |
| P4-02-SMA | {"stop_mult": 1.5} | 349 | +0.603 | +7.18 | 0.272 |
| P4-02-SMA | coûts × 2 | 349 | +0.881 | +7.70 | 0.296 |
| P4-03-TSMOM-LS | {"roc_n": 60} | 725 | +0.342 | +30.25 | 0.090 |
| P4-03-TSMOM-LS | {"roc_n": 120} | 502 | +0.554 | +36.38 | 0.064 |
| P4-03-TSMOM-LS | {"stop_mult": 0.75} | 627 | +0.506 | +32.22 | 0.098 |
| P4-03-TSMOM-LS | {"stop_mult": 1.5} | 628 | +0.230 | +18.62 | 0.134 |
| P4-03-TSMOM-LS | coûts × 2 | 628 | +0.353 | +25.04 | 0.122 |
| P4-04-RSI2 | {"rsi_th": 5} | 113 | +0.000 | -0.82 | 0.800 |
| P4-04-RSI2 | {"rsi_th": 15} | 395 | +0.028 | -1.33 | 0.772 |
| P4-04-RSI2 | {"stop_mult": 0.75} | 267 | -0.004 | -2.61 | 0.898 |
| P4-04-RSI2 | {"stop_mult": 1.5} | 242 | -0.004 | -1.48 | 0.857 |
| P4-04-RSI2 | coûts × 2 | 253 | -0.011 | -2.30 | 0.919 |

### Résultats en euros (1 000 €)

| Hypothèse | Équilibré 0,5 % : final € | Rendement | Max DD | Avec règles (2 %/jour, arrêt 10 %) : final € | Max DD | Événements 2 % | Arrêt | Prudent 0,25 % : final € | Max DD |
|---|---|---|---|---|---|---|---|---|---|
| P4-01-DONCH | 2285 | +129.0 % | 39.4 % | 1267 | 13.1 % | 10 | 2022-08-19 06:00:00+00:00 | 1672 | 27.8 % |
| P4-02-SMA | 2454 | +145.9 % | 46.6 % | 1244 | 19.2 % | 10 | 2022-05-11 11:00:00+00:00 | 1779 | 34.3 % |
| P4-03-TSMOM-LS | 1734 | +73.8 % | 56.5 % | 971 | 21.8 % | 3 | 2020-07-06 23:00:00+00:00 | 1481 | 43.7 % |
| P4-04-RSI2 | 1023 | +2.5 % | 14.5 % | 1052 | 13.7 % | 1 | non | 1022 | 15.0 % |

Panier passif équipondéré, 100 % investi : +893.8 % (USDT), +916.0 % en euros, drawdown maximal 80.7 %.

### Détail par sens et par actif (R moyen net)

- **P4-01-DONCH** — long : n = 103, R = +2.548. Sorties : signal 65, stop 36, end 2. Frais 10.6 USDT, financement +0.0 USDT. Par actif : BCH +0.18 (n = 10) ; BNB +6.53 (n = 10) ; BTC +1.15 (n = 11) ; EOS -0.84 (n = 11) ; ETH +2.65 (n = 9) ; LINK -0.10 (n = 13) ; LTC +0.46 (n = 9) ; MATIC +15.17 (n = 11) ; TRX +0.15 (n = 10) ; XRP -0.34 (n = 9).
- **P4-02-SMA** — long : n = 349, R = +0.897. Sorties : signal 328, stop 17, end 4. Frais 34.9 USDT, financement +0.0 USDT. Par actif : BCH +0.08 (n = 38) ; BNB +1.41 (n = 38) ; BTC +1.00 (n = 24) ; EOS -0.15 (n = 41) ; ETH +0.97 (n = 27) ; LINK +0.04 (n = 40) ; LTC +0.13 (n = 35) ; MATIC +6.22 (n = 33) ; TRX +0.20 (n = 28) ; XRP -0.11 (n = 45).
- **P4-03-TSMOM-LS** — long : n = 316, R = +0.891 ; short : n = 312, R = -0.172. Sorties : signal 545, stop 74, end 9. Frais 23.3 USDT, financement +297.0 USDT. Par actif : BCH -0.09 (n = 71) ; BNB +0.44 (n = 50) ; BTC +0.34 (n = 39) ; EOS -0.23 (n = 79) ; ETH +0.13 (n = 55) ; LINK -0.12 (n = 90) ; LTC -0.12 (n = 68) ; MATIC +4.21 (n = 59) ; TRX -0.06 (n = 59) ; XRP -0.28 (n = 58).
- **P4-04-RSI2** — long : n = 253, R = +0.004. Sorties : signal 217, stop 36. Frais 12.8 USDT, financement +0.0 USDT. Par actif : BCH +0.00 (n = 20) ; BNB +0.07 (n = 29) ; BTC +0.07 (n = 31) ; EOS -0.26 (n = 11) ; ETH +0.07 (n = 36) ; LINK +0.06 (n = 20) ; LTC -0.12 (n = 25) ; MATIC -0.04 (n = 30) ; TRX -0.03 (n = 25) ; XRP +0.04 (n = 26).

### Entrées aléatoires (même nombre, durée et sens ; 200 tirages ; R hors financement)

| Hypothèse | R moyen réel | R moyen aléatoire | 95e centile aléatoire | Centile du réel |
|---|---|---|---|---|
| P4-01-DONCH | +2.548 | +0.732 | +1.923 | 97 |
| P4-02-SMA | +0.897 | +0.293 | +0.744 | 96 |
| P4-03-TSMOM-LS | +0.466 | +0.118 | +0.416 | 98 |
| P4-04-RSI2 | +0.004 | +0.023 | +0.071 | 25 |
