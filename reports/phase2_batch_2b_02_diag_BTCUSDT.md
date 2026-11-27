Source : `results/batch_2b_02_diag/summary_BTCUSDT.json` — version du code `018f564` — essais totaux dans le registre au moment du lot : 51.

### Statistique de l'avantage (R nets, profil statistique 0,5 %, sans disjoncteur)

| Actif | Session | Hypothèse | Variante | Trades | E[R] net | IC95 bloc-hebdo | E[R] brut | E[R] coûts ×1,5 | E[R] coûts ×2 | Aléatoire E[R] | p(>0) BH | p(>aléa) BH | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | paris | NXB-01-DIAG | `{"target": "mid"}` | 214 | -1.324 | [-1.638 ; -1.001] | -0.209 | -1.841 | -2.282 | -1.171 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | paris | NXB-01-DIAG | `{"target": "2R"}` | 214 | -1.283 | [-1.544 ; -1.022] | -0.168 | -1.800 | -2.235 | -1.160 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | london | NXB-01-DIAG | `{"target": "mid"}` | 234 | -1.364 | [-1.677 ; -1.056] | -0.193 | -1.901 | -2.359 | -1.225 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | london | NXB-01-DIAG | `{"target": "2R"}` | 234 | -1.295 | [-1.553 ; -1.052] | -0.124 | -1.853 | -2.302 | -1.213 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | utc | NXB-01-DIAG | `{"target": "mid"}` | 239 | -1.594 | [-1.868 ; -1.328] | -0.416 | -2.133 | -2.595 | -1.220 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |
| BTCUSDT | utc | NXB-01-DIAG | `{"target": "2R"}` | 239 | -1.392 | [-1.642 ; -1.158] | -0.213 | -1.973 | -2.422 | -1.231 | 1.000 | 1.000 | Résultats incompatibles avec une exploitation rentable |

### Refus du gestionnaire de risque (profil statistique)

| Actif | Session | Hypothèse | Variante | Signaux | Trades | Motifs de refus |
|---|---|---|---|---|---|---|
| BTCUSDT | paris | NXB-01-DIAG | `{"target": "mid"}` | 214 | 214 | — |
| BTCUSDT | paris | NXB-01-DIAG | `{"target": "2R"}` | 214 | 214 | — |
| BTCUSDT | london | NXB-01-DIAG | `{"target": "mid"}` | 234 | 234 | — |
| BTCUSDT | london | NXB-01-DIAG | `{"target": "2R"}` | 234 | 234 | — |
| BTCUSDT | utc | NXB-01-DIAG | `{"target": "mid"}` | 240 | 239 | taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |
| BTCUSDT | utc | NXB-01-DIAG | `{"target": "2R"}` | 240 | 239 | taux de change indisponible (ANOMALIE : aucun taux de change disponible avant cet instant) : 1 |

### Profils de risque (capital initial 1 000 €, limites actives)

| Actif | Session | Hypothèse | Variante | Profil | Trades | Capital final € | Profit net € | Rendement % | PF | Max DD % (observé) | Durée DD (j) | Win % | Gain moy. € | Perte moy. € | E[€] | Sharpe | Sortino | Calmar | Frais € | Série pertes max | Disjoncteur | P(DD≥10 %) MC | P(DD≥20 %) MC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Stabilité temporelle (E[R] net par semestre)

- BTCUSDT paris NXB-01-DIAG `{"target": "mid"}` — 2020-01 : -1.18 (n=27), 2020-07 : -1.46 (n=44), 2021-01 : -0.66 (n=29), 2021-07 : -1.39 (n=31), 2022-01 : -1.56 (n=30), 2022-07 : -1.49 (n=29), 2023-01 : -1.45 (n=24)
- BTCUSDT paris NXB-01-DIAG `{"target": "2R"}` — 2020-01 : -0.78 (n=27), 2020-07 : -1.47 (n=44), 2021-01 : -0.66 (n=29), 2021-07 : -1.65 (n=31), 2022-01 : -1.46 (n=30), 2022-07 : -1.00 (n=29), 2023-01 : -1.91 (n=24)
- BTCUSDT london NXB-01-DIAG `{"target": "mid"}` — 2020-01 : -1.16 (n=26), 2020-07 : -1.42 (n=46), 2021-01 : -0.73 (n=33), 2021-07 : -1.42 (n=30), 2022-01 : -1.59 (n=34), 2022-07 : -1.38 (n=35), 2023-01 : -1.82 (n=30)
- BTCUSDT london NXB-01-DIAG `{"target": "2R"}` — 2020-01 : -0.74 (n=26), 2020-07 : -1.49 (n=46), 2021-01 : -0.67 (n=33), 2021-07 : -1.66 (n=30), 2022-01 : -1.22 (n=34), 2022-07 : -1.04 (n=35), 2023-01 : -2.18 (n=30)
- BTCUSDT utc NXB-01-DIAG `{"target": "mid"}` — 2020-01 : -1.34 (n=30), 2020-07 : -1.31 (n=45), 2021-01 : -1.01 (n=31), 2021-07 : -1.70 (n=32), 2022-01 : -1.74 (n=33), 2022-07 : -1.70 (n=34), 2023-01 : -2.39 (n=34)
- BTCUSDT utc NXB-01-DIAG `{"target": "2R"}` — 2020-01 : -1.11 (n=30), 2020-07 : -1.39 (n=45), 2021-01 : -0.64 (n=31), 2021-07 : -1.78 (n=32), 2022-01 : -1.28 (n=33), 2022-07 : -1.38 (n=34), 2023-01 : -2.09 (n=34)

### Ablations (différence d'E[R] vs modèle de base, IC95 bootstrap hebdomadaire)

