# Phase 7 — Pré-enregistrement (lot 7-01)

Fichier machine : `experiments/preregistration/batch_7_01.toml`, commité **avant** tout code d'exécution.

## 1. Les trois hypothèses retenues

| Clé | Hypothèse | Classe Cubrik | Données | Statut |
|---|---|---|---|---|
| **H7-A** | IBS < 0,1 → achat ; IBS > 0,9 → sortie (Nasdaq 100) ; ouverture suivante ; stop catastrophe | D (`stochastic(1)` brut à vérifier) | **Absentes** : OHLC journalier de NAS100 ou QQQ | Pré-enregistrée, **en attente** |
| **H7-B** | RSI(3) < 30 et IBS < 0,2 → achat ; sortie IBS > 0,9 ou clôture > plus haut de la veille (S&P 500) | D | **Absentes** : OHLC de US500 ou SPY | Pré-enregistrée, **en attente** |
| **H7-C** | Adaptation H4 de la stratégie Freqtrade : clôture < Bollinger basse (20, 2) ET RSI(14) > 55 ET ADX(14) > 25 ; sortie clôture > Bollinger haute ; stop fixe de 4,5 ATR médian (S2 2019) ; 10 cryptos au comptant, achat seulement | B (adaptation substantielle, donc nouvelle hypothèse) | Binance H1 → H4, 2020-01 → 2023-06 | **Exécutée** |

**Non retenues** :

- IBS XLP, Williams %R GBP/USD, Turnaround Tuesday, lundi Nikkei, or Fibonacci : classe C, ou données absentes ;
- l'IBS sur crypto : sans justification économique propre.

## 2. Règles communes

- **Exécution à l'ouverture de la bougie suivante** : c'est la décision. La clôture du signal sert seulement à comparer avec les chiffres annoncés.
- **Stop obligatoire** : vérifié sur le **plus bas** de chaque bougie (H4 pour H7-C, journalier pour H7-A/B). Exécution au stop, ou à l'ouverture en cas de gap.
- **Coûts** :
  - crypto au comptant : 0,10 % + 0,05 % par côté ;
  - CFD indice : 0,03 % par côté, plus le financement de nuit.
- **Taille** : 0,5 % de risque au stop (décision) ; 0,25 % et notionnel 100 % pour information.

## 3. Critères et risque de sélection

- **C1 à C6**, Monte Carlo et verdicts : voir le TOML.
- **Risque de sélection** :
  - le registre compte 194 essais, dont beaucoup sur des familles proches ;
  - je calcule donc, en plus des p corrigés, le **Sharpe déflaté** (Bailey & López de Prado, 2014) avec le nombre **total** d'essais du registre ;
  - une hypothèse n'est candidate que si ce Sharpe déflaté dépasse 0,95.

## 4. Dimensionnement par ATR (diagnostic)

- **Règle** : notionnel = budget B ÷ ATR21 % (plafonné à 100 %, sans levier), pour B ∈ {0,25 % ; 0,5 % ; 1 %}.
- **Appliqué** aux deux stratégies figées de la phase 5.
- **ATR approché** par la moyenne sur 21 jours de |Δ clôture|, faute de plus haut et de plus bas dans les données French.
- Le résultat est **comparé** aux profils de la phase 6. **Aucune règle officielle n'est modifiée.**
