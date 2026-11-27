# Phase 8 — Résultats (lot 8-01, H1, 10 perpétuels crypto, 2020-01 → 2023-06)

Sources : `results/batch_8_01_intraday/results.json`, `trades_*.csv`, `equity_daily_*.csv`.

- Simulation **chronologique du portefeuille complet** : 0,5 % de risque par trade, 2 positions au maximum, 1 % de risque cumulé, blocage des entrées après −2 % dans la journée, levier 1.
- Capital initial : 1 000 € (effet de change ignoré).
- *Données : Binance Vision (CC BY-NC-SA 4.0), recherche personnelle.*

Stops calibrés (2 × ATR H1 médian du S2 2019) : BTC 1,71 % · ETH 1,94 % · BNB 2,03 % · XRP 1,81 % · EOS 2,22 % · BCH 2,23 % · LTC 2,24 % · TRX 2,34 % · LINK 3,16 % · MATIC 3,97 %.

## 1. Portefeuille complet (configuration pré-enregistrée)

| | H8-3 Bollinger + ADX | H8-4 RSI + EMA 50/200 | H8-1 Cassure 24 h | H8-2 VWAP + EMA |
|---|---|---|---|---|
| Capital final | **53 €** | **201 €** | **920 €** | **52 €** |
| Gain net | −947 € | −799 € | −80 € | −948 € |
| Rendement journalier moyen / médian | −0,22 % / −0,08 % | −0,12 % / 0,00 % | +0,02 % / −0,33 % | −0,21 % / −0,51 % |
| Rendement mensuel moyen | −6,5 % | −3,7 % | +0,3 % | −6,6 % |
| Trades par jour (journées sans trade incluses) | 2,9 | 1,3 | 1,7 | **7,2** |
| Espérance nette par trade [IC95] | **−0,155 R** [−0,19 ; −0,12] | **−0,187 R** [−0,25 ; −0,12] | +0,015 R [−0,11 ; +0,15] | **−0,060 R** [−0,09 ; −0,03] |
| Taux de réussite | 47,4 % | 38,7 % | 26,0 % | 21,9 % |
| Gain moyen / perte moyenne (R) | +0,79 / −1,00 | +1,20 / −1,06 | +2,68 / −0,93 | +1,21 / −0,42 |
| Profit factor | 0,70 | 0,70 | 0,99 | 0,86 |
| Sharpe (annualisé) | −4,08 | −2,65 | +0,14 | −2,12 |
| Drawdown maximal | 94,8 % | 80,0 % | 73,5 % | 95,6 % |
| Drawdown au 95e percentile (bootstrap de semaines) | 97,2 % | 87,9 % | 75,6 % | 98,3 % |
| P(drawdown > 50 %), « ruine » | 100 % | 100 % | 53 % | 100 % |
| Pire journée / pire semaine | −3,2 % / −9,9 % | −3,1 % / −7,8 % | −8,7 % / −7,4 % | −9,7 % / −11,7 % |
| Plus longue série de pertes | 16 | 17 | 21 | 66 |
| Journées à +5 % | 0,2 % | 0,0 % | 2,0 % | 1,8 % |
| Journées gagnantes | 36,1 % | 32,2 % | 41,7 % | 36,8 % |
| Frais / financement (€) | 271 / −21 | 191 / +1 | 933 / 314 | 973 / 84 |
| Coût total des transactions | 250 € | 192 € | **1 247 €** | **1 058 €** |
| Risque de liquidation (levier 1) | nul | nul | nul | nul |

## 2. Critères (C1 à C8) et verdict

| | p Holm | C1 | C2 | C3 (coûts × 2 / retard) | C4 (voisins) | C5 (2020-21 / 2022-23) | C6 (mono-actif) | C7 (DD < 10 %) | C8 (Sharpe déflaté) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H8-3 | 1,00 | non | non | −0,25 / −0,15 R | 0/4 (−0,15 à −0,17) | −0,17 / −0,13 | 0/10 positifs | non | 0,00 | **rejeté** |
| H8-4 | 1,00 | non | non | −0,28 / −0,18 R | 0/4 (−0,13 à −0,23) | −0,20 / −0,18 | 1/10 (XRP +0,01) | non | 0,00 | **rejeté** |
| H8-1 | 1,00 | non | non | −0,08 / −0,12 R | 0/4 (−0,08 à −0,01) | **+0,17** / **−0,18** | 1/10 (ETH +0,005) | non | 0,00 | **rejeté** |
| H8-2 | 1,00 | non | non | −0,16 / −0,08 R | 0/4 (−0,09 à −0,04) | −0,04 / −0,09 | 0/10 | non | 0,00 | **rejeté** |

- Le Sharpe déflaté est calculé avec **217 essais** au registre.
- **Aucune hypothèse n'est candidate ni prometteuse.**
- Conformément au pré-enregistrement, le Monte Carlo à 10 000 tirages et l'**analyse du levier n'ont pas été exécutés**.

## 3. Pourquoi elles échouent

| | R réel (hors financement) | R d'entrées aléatoires appariées (moyenne ; 95e centile) | Centile du réel | Lecture |
|---|---|---|---|---|
| H8-3 Bollinger + ADX | −0,158 | −0,098 ; −0,072 | **0** | **Pire que le hasard** : en H1, les cryptos prolongent leurs excès au lieu d'y revenir. Le retour à la moyenne est pénalisé |
| H8-4 RSI + EMA | −0,188 | −0,097 ; −0,054 | **0** | Idem : acheter les replis en H1, c'est acheter un mouvement qui continue |
| H8-1 Cassure 24 h | +0,030 | −0,084 ; −0,035 | **100** | Le timing contient de l'information (environ **+0,11 R** de mieux que le hasard), mais elle est **absorbée par les coûts** (≈ 0,10 R par trade) et **dépend du régime** : achats +0,21 R, ventes −0,22 R ; 2020-21 +0,17 R, 2022-23 −0,18 R |
| H8-2 VWAP + EMA | −0,057 | −0,100 ; −0,085 | **100** | Meilleur que le hasard d'environ 0,04 R, mais **7 trades par jour** avec des stops courts : les coûts (1 058 €) dépassent le capital |

**Les entrées aléatoires perdent en moyenne 0,08 à 0,10 R par trade** : c'est le **coût d'un trade H1** dans ces conditions (frais + glissement + financement). Toute stratégie doit d'abord gagner au moins cela.

**H8-1 en détail** :

- le capital passe de 1 000 € à **3 016 € à mi-2021** (marché haussier), puis rend tout, jusqu'à 920 € à mi-2023 ;
- le meilleur trade vaut +59,7 R ; la médiane des trades est à −1,05 R ;
- c'est une **exposition au régime haussier**, pas un avantage stable.

## 4. Mono-actif (alternative Cubrik la plus reproductible)

Espérance nette par trade, une seule position, même règle et mêmes coûts :

| | BTC | ETH | BNB | XRP | EOS | BCH | LTC | TRX | LINK | MATIC |
|---|---|---|---|---|---|---|---|---|---|---|
| H8-3 | −0,21 | −0,20 | −0,26 | −0,25 | −0,10 | −0,08 | −0,15 | −0,09 | −0,15 | −0,12 |
| H8-4 | −0,34 | −0,28 | −0,25 | +0,01 | −0,24 | −0,16 | −0,10 | −0,07 | −0,18 | −0,12 |
| H8-1 | −0,09 | +0,005 | −0,05 | −0,21 | −0,18 | −0,03 | −0,12 | −0,11 | −0,07 | −0,00 |
| H8-2 | −0,09 | −0,04 | −0,03 | −0,10 | −0,07 | −0,07 | −0,10 | −0,06 | −0,03 | −0,02 |

**Aucun actif** n'offre une espérance positive au-delà du bruit. La version mono-actif réduirait la fréquence d'environ 10 fois, sans changer le signe du résultat.

## 5. Profils de risque (information)

Capital final et drawdown maximal :

| | 0,25 % | 0,5 % (décision) | 1 % | 2 % |
|---|---|---|---|---|
| H8-3 | 219 € (78 %) | 53 € (95 %) | 13 € (99 %) | 23 € (98 %) |
| H8-4 | 408 € (60 %) | 201 € (80 %) | 115 € (89 %) | 120 € (89 %) |
| H8-1 | 984 € (44 %) | 920 € (74 %) | 76 € (96 %) | 110 € (96 %) |
| H8-2 | 209 € (81 %) | 52 € (96 %) | 10 € (99 %) | 3 € (100 %) |

À 2 %, le plafond de notionnel (levier 1) bloque une partie des entrées. Avec des stops de 1,7 à 4 %, 2 % de risque correspondraient à 50 à 117 % du capital par position. Une espérance négative ne devient pas positive en augmentant la taille : elle accélère la ruine.

## 6. Levier

**Non simulé**, conformément au pré-enregistrement : aucun avantage n'a été démontré sans levier.

À titre d'illustration arithmétique (sans backtest), la distance de liquidation d'une position isolée vaut environ 1/levier − 0,5 % (marge de maintenance) :

| Levier | ×1 | ×2 | ×3 | ×5 | ×10 | ×20 |
|---|---|---|---|---|---|---|
| Liquidation à environ | — | −49,5 % | −32,8 % | −19,5 % | −9,5 % | **−4,5 %** |

- À **risque égal** (0,5 % au stop), le levier ne change que la marge immobilisée : le rendement reste identique.
- Utilisé pour **augmenter** la taille, il multiplie une espérance négative.
- À ×20, un mouvement de 4,5 % liquide la position. Les mouvements H1 de plus de 4,5 % sont fréquents sur les altcoins ; le pire jour du portefeuille H8-1 est de −8,7 %.

## 7. Stress et signaux manqués

- **Coûts × 2** : les quatre hypothèses deviennent nettement plus négatives (H8-2 : 1 000 € → 0,80 €).
- **Une bougie de retard** (contrôle Cubrik toutes les 60 min) : toutes restent négatives ; H8-1 passe de +0,015 à −0,12 R.
- **Signaux manqués** (5, 10 ou 20 % des trades retirés au hasard) : le R médian ne change pas. Le problème n'est pas l'exécution, mais l'**absence d'espérance**.
