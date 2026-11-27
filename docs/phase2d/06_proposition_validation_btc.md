# Phase 2D — Proposition de validation BTC (non lancée)

Brouillon figé : `experiments/drafts/validation_btc_trend_01.toml`. Il n'est **ni enregistré ni exécuté**. La validation est désormais verrouillée techniquement et ne sera ouverte qu'avec votre autorisation.

## Hypothèse unique

Une allocation BTC/liquidités conditionnée par la tendance, avec des règles figées, obtient un rendement quotidien moyen supérieur à celui du portefeuille passif de même exposition moyenne, avec un drawdown inférieur ou égal.

## Choix des 3 variantes (justifié avant tout accès)

| Variante | Raison |
|---|---|
| NXG-01 (moyenne mobile 100 j), plafond 10 % | Meilleur verdict pré-enregistré du développement (« prometteur ») et la règle la plus simple |
| NXG-04 (progressive), plafond 10 % | Seul autre « prometteur » ; mécanisme différent (exposition graduée) |
| NXG-02 (momentum 90 j), plafond 10 % | Référence « momentum simple », non sélectionnée sur son résultat (« absence d'avantage ») : elle contrôle si un succès de NXG-01 et NXG-04 est propre à leur règle ou générique |

Plafond de 10 % plutôt que 25 % : en développement, le plafond de 25 % dépasse la cible de drawdown de 10 % (11 à 18 %), ce qui le rend incompatible avec les règles du projet.

Variantes à risque fixe par trade (REF-SMA-01, NXF-02 H4, NXD-02 H4) non retenues : elles exposent seulement 2 à 4 % du capital, et leurs alphas ne sont pas significatifs.

## Critère principal, significativité et décision

- **Critère principal** : différence de rendement quotidien moyen par rapport au passif à même exposition (mêmes coûts).
  - Test unilatéral, bootstrap par blocs de 20 jours.
  - **α = 0,05/3 ≈ 0,0167** (Bonferroni sur les 3 variantes).
- **Critères secondaires** :
  - drawdown inférieur ou égal à celui du poids fixe 10 % ;
  - Sharpe supérieur ou égal à celui du passif ;
  - différence positive avec coûts × 2.
- **Décision** :
  - une variante est validée si le critère principal et les critères secondaires 1 et 3 sont remplis ;
  - sinon, elle est rejetée définitivement, sans réglage suivi d'un nouvel essai sur la validation ;
  - une variante validée devient candidate au test final, qui reste verrouillé et exige une nouvelle autorisation.

## Limite de puissance (à connaître avant de décider)

La période de validation (2023-07 → 2024-12) est **majoritairement haussière**. Un filtre de tendance y sera presque toujours investi : la différence avec le passif sera faible, et le test peu puissant. Un échec n'invaliderait pas l'effet de protection en marché baissier, observé en 2022 ; un succès ne le démontrerait pas. **C'est une décision scientifique qui vous revient** : ouvrir la validation maintenant, ou attendre de disposer d'une reproduction sur un autre marché (hypothèse S1).

Conditions juridiques : la validation reste un backtest historique personnel, couvert par le §4.1 de Binance Vision. Une phase en argent réel resterait soumise au §4.2.
