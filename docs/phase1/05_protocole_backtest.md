# 05 — Protocole expérimental et moteur de backtest

## 1. Découpage chronologique (figé avant tout test)

Période cible : 2020-01-01 → 2026-06-30 (≈ 6,5 ans, sous réserve de disponibilité).

| Bloc | Période | Usage |
|---|---|---|
| Développement | 2020-01 → 2023-06 | Mise au point du code, walk-forward, choix des paramètres |
| Validation | 2023-07 → 2024-12 | Sélection entre stratégies survivantes, une seule passe par version |
| **Test final verrouillé** | 2025-01 → 2026-06 | **Une seule exécution**, sur les stratégies pré-sélectionnées, paramètres gelés |
| Paper trading | à partir de la validation finale | Simulation en temps réel ≥ 3 mois, aucun ordre réel |

Verrouillage : les fichiers du test final sont stockés à part, avec un hash ; le chargeur refuse de les lire sans un drapeau explicite `--unlock-final-test` qui écrit l'accès dans le journal SQLite (date, version de stratégie, hash de la config). Chaque accès est donc traçable.

Une purge (« embargo ») d'une journée est appliquée à chaque frontière pour éviter qu'un trade ouvert dans un bloc ne se termine dans le suivant.

## 2. Walk-forward

Dans le bloc Développement + Validation : fenêtres glissantes **18 mois d'entraînement / 6 mois de test, pas de 6 mois** (≈ 6 plis). Pour chaque pli : sélection des paramètres sur l'entraînement par un critère robuste (médiane de l'espérance sur un voisinage de paramètres, pas le maximum), application sans modification au test. La performance retenue est la **concaténation des segments de test**.

## 3. Pré-enregistrement et contrôle des comparaisons multiples

- Chaque hypothèse est décrite dans un fichier YAML versionné dans git **avant** son exécution (règles, grille, actifs, critère de succès).
- Chaque exécution est journalisée (SQLite) : on connaît donc le **nombre total d'essais** `N`, y compris les échecs.
- Corrections :
  - **Deflated Sharpe Ratio** (Bailey & López de Prado) en fonction de `N`, de l'asymétrie et de l'aplatissement des rendements.
  - **Probability of Backtest Overfitting** (PBO) par validation croisée combinatoire symétrique (CSCV) sur la grille de paramètres.
  - **White's Reality Check / Hansen SPA** (bootstrap stationnaire) : la meilleure stratégie bat-elle le benchmark au-delà de ce que le hasard produirait sur `N` essais ?
  - **Benjamini–Hochberg** (FDR 10 %) sur les familles stratégie × actif.

### Taille d'échantillon nécessaire (calcul effectué)

Pour un trade à résultat binaire −1R / +RR avec probabilité de gain au point mort, l'écart-type par trade vaut `σ = √(p·RR² + (1−p))` avec `p = 1/(1+RR)` (soit `σ = √RR`). Nombre de trades pour détecter une espérance de **+0,10R** :

| RR | σ (R) | n à z = 1,96 | n à z = 3 (comparaisons multiples) |
|---|---|---|---|
| 1 | 1,00 | 385 | 900 |
| 2 | 1,41 | 769 | 1 801 |
| 4 | 2,00 | 1 537 | 3 600 |

Conséquence directe : une stratégie à ~1 trade/jour/actif produit ≈ 250 trades/an/actif. Valider un RR 4 à +0,1R demande ≈ **14 années-actifs**. Les stratégies rares (S2 ICT, S3 H4) ne pourront probablement **pas** être validées statistiquement actif par actif ; elles devront l'être en pool multi-actifs, avec la prudence que cela implique (corrélations).

## 4. Monte-Carlo et sensibilité

1. **Bootstrap des trades** (10 000 tirages, par blocs de semaines pour conserver l'autocorrélation) → intervalles de confiance de l'espérance, du PF, du MaxDD, de la plus longue série de pertes.
2. **Entrées aléatoires appariées** (voir `03`) → distribution nulle ; p-valeur = part des tirages aléatoires ≥ stratégie.
3. **Perturbation d'exécution** : délai d'une bougie, slippage ×2, spread ×1,5, suppression aléatoire de 10 % des trades.
4. **Sensibilité paramétrique** : chaque paramètre à ±20 % / un cran de grille ; on exige un **plateau**, pas un pic.
5. **Sensibilité au fuseau** (S1) et au choix des swings (L, R).

## 5. Critères d'acceptation (définis maintenant, pas après)

Une stratégie n'est déclarée « candidate au paper trading » que si **toutes** les conditions sont remplies :

1. Espérance nette > 0 en walk-forward **avec coûts × 1,5**.
2. Profit Factor net ≥ 1,15 sur les segments OOS concaténés.
3. Au moins 300 trades OOS (pool) et ≥ 100 par actif retenu.
4. Deflated Sharpe significatif à 95 % ; PBO < 0,3.
5. Bat les entrées aléatoires appariées à p < 0,05 après correction BH.
6. Positive sur au moins 4 des 6 plis walk-forward ; aucune année n'apporte plus de 50 % du profit.
7. Drawdown observé dans l'intervalle Monte-Carlo à 95 %.
8. Plateau de paramètres confirmé.
9. Résultat sur le test final verrouillé : espérance > 0 et dans l'intervalle de confiance attendu. Un échec ici = **rejet définitif de cette version** (pas de réglage et nouvel essai sur le même test).

## 6. Moteur de backtest : modèle d'exécution

| Aspect | Modélisation |
|---|---|
| Prix | Signaux sur mid (ou bid), exécution achat au **ask**, vente au **bid**. Si seul le bid existe : spread modélisé par heure de la journée, calibré sur Dukascopy/MT5. |
| Ordres au marché | Exécutés à l'ouverture de la bougie suivant le signal + slippage `s` (fixe en ticks + composante proportionnelle à l'ATR ; ×3 dans les 5 min suivant une news ou une ouverture de session). |
| Ordres limites | Remplis seulement si le prix **traverse** le niveau d'au moins un tick (pas sur simple contact) — conservateur. |
| Stops | Exécutés au niveau ou au pire prix d'ouverture en cas de gap ; slippage appliqué. |
| SL et TP sur la même bougie | **Hypothèse conservatrice par défaut : SL d'abord.** Variante : résolution par les ticks Dukascopy de cette minute. Variante : chemin OHLC (bougie haussière O→L→H→C, baissière O→H→L→C). Les trois résultats sont publiés ; un écart important signale une stratégie dépendante de l'intrabar, donc fragile. |
| Entrée et sortie sur la bougie d'entrée | Même traitement : si une limite est remplie et que le SL est atteint dans la même bougie, la perte est comptée. |
| Latence | Paramètre en secondes ; avec données M1, équivaut à décaler l'exécution d'une bougie dans le test de robustesse. |
| Taille de position | `lots = floor((risque € / (distance stop × valeur du point €)) / pas) × pas`. Si < lot minimal : trade ignoré (ou lot minimal si le risque reste ≤ 1 %). Journalisé dans les deux cas. |
| Commissions | Par lot et par côté (FX/CFD ECN) ou en % du notionnel (crypto, taker par défaut). Valeurs par défaut à calibrer sur un courtier réel, à vérifier. |
| Swaps / funding | Swap FX/CFD appliqué à chaque passage de 23:00 Paris (triple le mercredi) ; funding perpétuels Binance aux horodatages réels de l'historique de funding. |
| Données manquantes | Pas de nouvelle entrée si la fenêtre de calcul a une couverture < 95 % ; position ouverte : évaluée au premier prix disponible après le trou (gap). |
| Devise du compte | EUR ; conversion du P&L au taux EUR/quote contemporain. |
| Marge | Levier maximal réglementaire UE retail (30:1 FX majeures, 20:1 or et indices majeurs, 2:1 crypto CFD) ; un trade est refusé si la marge requise dépasse la marge disponible. |

Validation du moteur : tests unitaires sur scénarios synthétiques à résultat connu (un trade, un gap, une bougie ambiguë, un week-end), et vérification que des **entrées aléatoires sur une marche aléatoire produisent une espérance ≈ −coûts**.

## 7. Métriques calculées

Par stratégie, actif, année, régime et session :

- Rendement net (€ et %), CAGR ; Profit Factor ; espérance (R et €) avec IC 95 % bootstrap.
- Win rate, comparé au point mort `1/(1+RR)` ; gain moyen, perte moyenne, ratio.
- Maximum Drawdown (€, %), durée du drawdown, Ulcer Index.
- Sharpe et Sortino (sur rendements **journaliers** du compte, annualisés √252 FX/indices, √365 crypto), Deflated Sharpe.
- Nombre de trades, exposition (temps en position), plus longue série de pertes observée vs attendue.
- Coût moyen en R ; espérance brute vs nette ; **coût de point mort** (multiplicateur de coûts qui annule l'espérance).
- MFE / MAE (excursions favorables/défavorables) pour diagnostiquer les sorties.
- Écart vs benchmarks (§ `03`).

Règle : on ne classe jamais par rendement maximal. Le classement principal est la **borne inférieure de l'IC 95 % de l'espérance nette en R**, en OOS.
