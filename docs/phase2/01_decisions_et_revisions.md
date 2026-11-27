# Phase 2 — Décisions validées et révisions de la phase 1

## 1. Décisions validées (utilisateur)

| Sujet | Décision | Où c'est appliqué dans le code |
|---|---|---|
| Capital simulé | 1 000 € | `nexus/config.py: INITIAL_CAPITAL_EUR` |
| Découpage | Dév. 2020-01 → 2023-07 ; validation 2023-07 → 2025-01 ; test final verrouillé 2025-01 → 2026-07 | `nexus/config.py: DEV, VALIDATION, FINAL_TEST` ; verrou dans `nexus/data/store.py` |
| Premiers actifs | EUR/USD, BTC/USDT | `nexus/instruments.py` |
| Ordres réels | Aucun ; aucun module d'ordres dans le dépôt | — |
| Crypto | Spot, sans levier, sans vente à découvert | `BTCUSDT_SPOT.allow_short=False, max_leverage=1` |
| Martingale / récupération | Interdites | `RiskManager` : taille = f(capital courant, distance du stop) uniquement ; test `test_risk_never_increases_after_loss` |

## 2. Gestion du risque

Trois profils comparés, sur le **capital courant**, **frais estimés inclus dans le budget de risque** :

| Profil | Risque/trade | Budget initial |
|---|---|---|
| prudent | 0,25 % | 2,50 € |
| équilibré | 0,50 % | 5,00 € |
| dynamique | 1,00 % | 10,00 € |

Limites communes : perte journalière max 2 % du capital de début de journée (un trade est refusé si sa perte potentielle ferait dépasser la limite) ; arrêt automatique et définitif à 10 % de drawdown depuis le dernier sommet ; une seule position ; stop obligatoire ; arrêt sur anomalie (horodatages non croissants, prix manquants, taux de change absent ou périmé).

**Distinction importante** : le seuil d'arrêt (10 %) n'est pas une garantie. Le drawdown **observé** peut le dépasser : glissement sur stop, gap à travers le stop (le simulateur exécute alors à l'ouverture, test `test_gap_through_stop_fills_at_open`) et dernière perte qui déclenche l'arrêt. Le rapport affiche séparément le drawdown observé, l'activation du disjoncteur et la probabilité Monte-Carlo de dépasser 10 % et 20 %.

Le profil n'est **pas** choisi sur le rendement maximal : les trois sont présentés côte à côte (rendement, drawdown, volatilité, probabilité de perte importante). Le profil d'un éventuel paper trading sera choisi avant ouverture du test final, sur un critère de risque.

## 3. Justification mathématique des tailles d'échantillon (correction)

On teste H0 : espérance μ ≤ 0 contre H1 : μ = μ₁ > 0, sur n trades de résultat en R, d'écart-type σ.

Statistique : `T = x̄ / (σ/√n)`. Pour un test unilatéral de niveau α et de puissance 1−β :

```
n = ((z_{1−α} + z_{1−β}) · σ / μ₁)² · (1 + 2·Σρ_k)
```

**Hypothèses de variance.** Pour un trade binaire −1R / +RR au point mort (p = 1/(1+RR)), `σ² = p·RR² + (1−p) − μ² = RR` (car μ = 0), donc σ = √RR : 1 (RR 1), 1,41 (RR 2), 2 (RR 4). Les sorties horaires et le glissement modifient σ ; le moteur mesure σ empirique (`r_std`) et l'autocorrélation (`rho_sum`) pour chaque essai.

**Correction de la phase 1.** Les chiffres 1 537 (≈ 1 500) et 3 600 utilisaient `n = (z·σ/μ)²` avec z = 1,96 puis z = 3. Cette formule correspond à une **puissance de 50 %** seulement (z_{1−β} = 0) : on a une chance sur deux de rater un vrai avantage de +0,10R. z = 3 équivaut à un α unilatéral de 0,00135, soit une correction de Bonferroni pour ≈ 18 tests à 2,5 %.

**Table corrigée** (μ₁ = +0,10R, unilatéral α = 5 %, calcul `nexus.stats.inference.required_trades`) :

| RR | σ | Puissance 50 %, α 2,5 % (phase 1) | Puissance 80 % | 80 %, Bonferroni 50 tests | 80 %, 200 tests | 80 %, 50 tests, Σρ = 0,2 |
|---|---|---|---|---|---|---|
| 1 | 1,00 | 385 | 619 | 1 546 | 1 869 | 2 165 |
| 2 | 1,41 | 769 | 1 237 | 3 092 | 3 737 | 4 329 |
| 4 | 2,00 | 1 537 | 2 474 | 6 184 | 7 474 | 8 658 |

**Dépendance.** Les trades d'une même semaine ou d'un même régime ne sont pas indépendants. L'inférence utilise donc un **bootstrap par blocs hebdomadaires** (`block_bootstrap_mean`), et la formule ci-dessus inclut le facteur `1 + 2Σρ` (taille effective).

**Comparaisons multiples.** Bonferroni est conservateur. Le lanceur applique Benjamini–Hochberg (FDR) sur toutes les p-valeurs d'un lot, et le registre compte **tous** les essais (y compris les essais de rodage) pour le Deflated Sharpe Ratio.

**Pas de rejet automatique sur le nombre de trades.** Un faible nombre de trades élargit l'intervalle de confiance : c'est ce dernier qui détermine la catégorie de verdict, pas un seuil de n. Seuls les essais à moins de 20 trades sont marqués « données insuffisantes » (statistique non calculable de façon fiable).

## 4. Quatre catégories de verdict (règles fixées avant les résultats)

Implémentées dans `nexus/stats/inference.py: verdict` :

1. **Avantage statistique démontré** : IC95 bootstrap > 0, p (BH) < 0,05, bat les entrées aléatoires (p BH < 0,05), espérance > 0 avec coûts × 2, **et** confirmé en validation puis au test final. *Inatteignable sur la seule période de développement.*
2. **Résultats prometteurs mais preuves insuffisantes** : espérance nette > 0, p (BH) < 0,25 et espérance > 0 avec coûts × 2 (ou critères forts remplis, mais uniquement sur le développement).
3. **Absence d'avantage démontré** : ni prometteur, ni incompatible.
4. **Résultats incompatibles avec une exploitation rentable** : borne haute de l'IC95 < 0, ou espérance ≤ 0 avec une borne haute < +0,05R et une espérance négative avec coûts × 2.

Aucun objectif de rendement n'est fixé ; aucune estimation de revenu n'est présentée.

## 5. Hypothèses de session (fuseau SBA non présumé)

Le document SBA ne précise pas le fuseau. Hypothèses testées, en fuseaux IANA (changements d'heure automatiques), **comptées comme essais distincts** (`nexus/timeutils.py`) :

| Clé | Fuseau | Range | Entrée | Sortie forcée | Justification |
|---|---|---|---|---|---|
| paris | Europe/Paris | 00:00–09:00 | 09:00–13:00 | 20:00 | Lecture littérale, vidéaste francophone |
| london | Europe/London | 00:00–08:00 | 08:00–12:00 | 19:00 | Ouverture de Londres, principal centre Forex |
| utc | UTC | 00:00–07:00 | 07:00–11:00 | 18:00 | Définition fixe sans DST (contrôle) |
| newyork | America/New_York | 00:00–09:30 | 09:30–11:30 | 15:55 | Ouverture US (réservée à un lot ultérieur) |

## 6. Organisation de la recherche en six familles

A (Session Breakout) et B (Liquidity Reversal) sont lancées en premier, chacune par son **modèle minimal**, puis **un filtre à la fois** (ablation). C (Trend Pullback), D (Volatility Expansion), E (Mean Reversion) et F (Momentum) seront introduites progressivement, chacune avec son propre pré-enregistrement, pour contrôler le nombre de comparaisons. Pour le Forex, le volume disponible est un **volume de cotations** (tick volume) ; il est nommé ainsi dans les données (`bid_tickvol`, `ask_tickvol`) et ne sera jamais présenté comme un volume échangé. Pour BTC, le volume Binance est un volume échangé réel.
