# Phase 2C — Protocole, budget d'expériences et règles de verdict

Rédigé **avant** l'exécution des familles C, F, D et du filtre de régime. Toute modification ultérieure est versionnée dans git et, pour les budgets, journalisée dans la table `budget_changes` du registre.

## 1. Cadre inchangé

- Capital simulé 1 000 € ; profils 0,25 / 0,5 / 1 % ; perte journalière 2 % ; arrêt à 10 % de drawdown ; une position ; spot BTC sans levier ni vente à découvert.
- Données : BTC/USDT M1 (Binance Data Vision) et EUR/USDT H1, **période de développement uniquement** (2020-01-01 → 2023-07-01). Validation et test final verrouillés.
- Usage des données : backtesting historique pour une recherche personnelle hors production, usage explicitement autorisé par les Binance Vision Dataset Terms §4.1 (voir `02_conditions_utilisation.md`).

## 2. Moteur pour H1, H4, D1 — vérifications ajoutées

| Point | Traitement | Test |
|---|---|---|
| Décisions à la clôture H1/H4/D1 | `avail` = ouverture + durée ; exécution à la minute suivante | `test_trend_strategies_signals_do_not_depend_on_future` (décision alignée sur une clôture H4) |
| Indépendance vis-à-vis du futur | Signaux identiques avec et sans données postérieures | même test, 6 stratégies |
| Positions de plusieurs jours | Courbe de capital valorisée chaque jour (mark-to-market) | `test_daily_mark_to_market_for_multi_day_position` |
| Stop suiveur | Niveau décidé à chaque clôture, appliqué aux minutes suivantes, en cliquet | `test_trailing_stop_*` |
| Régimes | Régime du jour D utilisable à partir de D+1 00:00 ; percentiles sur les 365 jours précédents | `test_regimes_are_causal_truncation`, `test_trailing_percentile_uses_only_past` |
| Ré-entrée après stop | Interdite avant le signal de sortie de la stratégie (front montant exigé) | règle documentée dans `strategies/trend.py` |

Limite connue : le disjoncteur et la limite journalière portent sur le capital **réalisé**. Le drawdown publié, lui, est calculé sur la courbe valorisée quotidiennement, qui inclut les pertes latentes.

## 3. Budget d'expériences

### Justification statistique

Avec m essais dans une famille, le seuil unilatéral de Bonferroni à 5 % vaut z = Φ⁻¹(1 − 0,05/m) : 2,64 pour m = 12, 2,86 pour m = 24, 2,99 pour m = 36. À puissance 80 %, la taille d'échantillon requise est multipliée par ((z_m + 0,84)/(1,645 + 0,84))² ≈ 1,96 pour m = 12 et 2,22 pour m = 24. Au-delà d'une douzaine d'essais par famille, chaque essai supplémentaire coûte de la puissance sans gain d'information proportionné. Les horizons longs produisent peu de trades : environ 10 à 40 en D1, 40 à 150 en H4 et 150 à 400 en H1 sur 3,5 ans. Les familles D1 auront donc très probablement un IC trop large pour conclure. C'est assumé à l'avance.

### Justification informatique

Mesuré dans le cloud : 10 à 40 s par essai, dominé par les 200 réplications aléatoires. Le PC Windows à 2 cœurs serait environ 3 à 4 fois plus lent. Un budget de 40 essais représente moins d'une heure de calcul cloud.

| Famille | Budget | Prévu | Contenu |
|---|---|---|---|
| AUDIT | 12 | 12 | Ré-analyse diagnostique du lot 2B-01 (aucune sélection) |
| C (Trend Pullback) | 12 | 12 | H1, H4 × (minimal + 5 ablations unitaires) |
| F (Momentum) | 12 | 11 | TSMOM D1 (2), Donchian D1 (2) + H4 (1), filtre de volatilité (4), stop suiveur (1) |
| REF | 2 | 1 | Moyenne mobile simple D1 |
| REG | 4 | 2 | Filtre de régime journalier sur C minimal (H1, H4) |
| D (Volatility Expansion) | 8 | 4 | H1, H4 × (avec compression, sans compression = contrôle) — **seulement après les conclusions C et F** |

Le budget n'est pas augmenté si les résultats sont négatifs. Toute extension est journalisée (`budget_changes`) et entre dans la correction des comparaisons multiples. Le registre refuse techniquement tout essai au-delà du budget (`test_budget_enforced_and_extensions_logged`). Les 51 essais antérieurs restent comptés dans le total.

Composants listés par vous mais **non testés** dans ce lot, pour tenir le budget : retracement de Fibonacci et zone ATR pour C ; ADX et efficacité directionnelle comme filtres. Ces deux derniers sont calculés et publiés à titre descriptif dans les analyses de régime. Ils pourront faire l'objet d'un lot ultérieur pré-enregistré.

## 4. Règles de verdict (verdict_v2)

Inférence principale : espérance nette en R par trade, IC95 par bootstrap par **blocs mensuels** (H4, D1) ou hebdomadaires (H1), afin de respecter la dépendance temporelle. p-valeurs corrigées par Benjamini–Hochberg **au sein de chaque famille**.

1. Moins de 20 trades : **données insuffisantes** (aucune conclusion).
2. Borne haute de l'IC95 < 0 : **incompatible avec une exploitation rentable**.
3. **Prometteur mais preuves insuffisantes** si, simultanément : espérance nette > 0, p(>0) BH < 0,25, espérance > 0 avec coûts × 2, **et** meilleure que les entrées aléatoires à exposition comparable (moyenne supérieure et p BH < 0,25). Cette dernière condition est nouvelle : elle empêche de confondre la hausse générale de BTC avec un avantage.
4. Espérance ≤ 0, borne haute < 0,05R et espérance négative avec coûts × 2 : **incompatible**.
5. Sinon : **absence d'avantage démontré**.
6. **Démontré** : impossible sur le développement. Cela exige la validation puis le test final.

Indicateurs complémentaires publiés, sans effet automatique sur le verdict : alpha et bêta quotidiens par rapport à BTC (IC95, blocs de 20 jours), Sharpe quotidien (IC95), alertes de surajustement (`research/lab.py: overfit_flags`), walk-forward du processus de sélection.

## 5. Références obligatoires

Pour chaque stratégie :

- Buy & Hold ;
- liquidités (0 %) ;
- détention passive à la même exposition moyenne ;
- entrées aléatoires à exposition comparable : même nombre de trades, mêmes durées, mêmes distances de stop ;
- moyenne mobile simple (REF-SMA-01) ;
- momentum minimal (NXF-01) ;
- version sans filtre (modèle minimal de la famille).

## 6. Frais

Scénario principal : compte Binance standard, frais spot **0,10 % maker et 0,10 % taker** (barème public pour les comptes réguliers, à vérifier sur la page officielle des frais). Tous les ordres simulés sont **au marché (taker)** : on ne suppose jamais l'exécution d'un ordre limite. Demi-spread modélisé à 0,5 pb, glissement de 1 pb (2 pb supplémentaires sur stop). Pour un ordre de quelques dizaines d'euros, la liquidité de BTC/USDT n'est pas un facteur limitant. Taille minimale ≈ 5 USDT et pas de quantité 0,00001 BTC (filtres d'échange, hypothèse à revérifier).

Sensibilité seulement : remise BNB de 25 % (0,075 %). Elle n'est jamais utilisée pour un verdict.

La conversion EUR ↔ USDT utilise EUR/USDT horaire (dernier taux connu). Le coût réel de conversion d'un dépôt en euros n'est pas modélisé, car il serait ponctuel.

## 7. Ordre d'exécution

1. Audit du lot 2B-01 (famille AUDIT).
2. Lot 2C-01 : C, F, REF, REG.
3. Conclusions intermédiaires C et F, enregistrées.
4. Seulement ensuite, si c'est scientifiquement justifié : lot 2C-02 (famille D).
