## Audit technique 2D — effet des défauts corrigés sur les candidats 2C

*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*

Buy & Hold : +331.8 % → +332.1 %.

| Hypothèse | Variante | E[R] avant → après | Sharpe quotidien avant → après [IC95] | Alpha %/an avant → après [IC95] | CAGR équilibré % avant → après |
|---|---|---|---|---|---|
| NXF-01 | `{"lookback": 20, "tf": "D1"}` | +0.3627 → +0.3627 | +1.22 → +1.23 [+0.01 ; +2.37] | +1.52 → +1.43 [-0.45 ; +3.45] | +2.55 → +2.51 |
| NXF-01 | `{"lookback": 60, "tf": "D1"}` | +2.0946 → +2.0946 | +1.04 → +1.06 [+0.03 ; +2.10] | +3.17 → +2.97 [-1.17 ; +7.89] | +5.60 → +5.33 |
| NXF-02H4 | `{"n": 120, "tf": "H4"}` | +3.3517 → +3.3517 | +1.19 → +1.19 [-0.16 ; +2.32] | +5.86 → +5.45 [-2.24 ; +13.78] | +8.51 → +8.32 |
| NXF-03 | `{"lookback": 20, "tf": "D1", "vol_filter": true}` | +0.3428 → +0.3428 | +1.11 → +1.02 [-0.30 ; +2.21] | +1.35 → +1.04 [-0.89 ; +3.04] | +2.33 → +1.90 |
| REF-SMA-01 | `{"n": 50, "tf": "D1"}` | +2.0229 → +2.0229 | +1.23 → +1.26 [+0.29 ; +2.24] | +4.13 → +3.79 [-0.02 ; +8.26] | +6.53 → +6.26 |
| NXD-02 | `{"require_compression": false, "tf": "H4"}` | +0.4181 → +0.4181 | +1.22 → +1.27 [-0.06 ; +2.19] | +4.49 → +4.56 [-1.18 ; +10.35] | +7.07 → +7.01 |