# Phase 2 — Architecture du moteur de recherche

```
nexus/
  config.py              périodes figées, capital 1 000 €, profils de risque
  instruments.py         spécifications instrument × cadre d'exécution (spot / CFD), coûts, lots
  timeutils.py           hypothèses de session en fuseaux IANA
  data/
    http.py              téléchargement poli (bibliothèque standard, Windows compatible)
    binance.py           Binance Data Vision (SHA-256, ms/µs)
    dukascopy.py         flux Dukascopy bid/ask M1 (.bi5)
    store.py             Parquet par actif/année, VERROU du test final
    quality.py           contrôles qualité (couverture seule pour la période verrouillée)
  features/core.py       EMA, ATR, pivots (disponibilité i+R), BOS/CHoCH, FVG, ranges
  strategies/
    base.py              Signal = intention (jamais un ordre)
    session.py           NEXUS A, NEXUS B, référence SBA
    random_baseline.py   entrées aléatoires comparables
  engine/
    execution.py         simulateur M1 bid/ask conservateur (vectorisé, validé)
    risk.py              gestionnaire de risque indépendant
    backtest.py          boucle signaux → risque → exécution → journal ; conversion EUR
  stats/
    metrics.py           métriques € et R
    inference.py         tailles d'échantillon, bootstrap par blocs, BH, DSR, verdict
  research/
    registry.py          registre SQLite permanent (hypothèses, essais, accès au test final)
    runner.py            exécution d'un lot pré-enregistré
    report.py            rapport Markdown généré depuis les résultats
experiments/preregistration/*.toml   hypothèses écrites avant exécution
results/registry.sqlite              registre versionné dans git
```

## Garanties et leur test

| Garantie | Mécanisme | Test |
|---|---|---|
| Pas d'exécution rétroactive | Ordre au marché à l'ouverture de la minute ≥ disponibilité du signal | `test_market_entry_uses_next_bar_open_not_signal_close` |
| Pivots disponibles après confirmation | `last_confirmed_level` décale de R bougies | `test_swing_only_available_after_right_bars`, troncature |
| Aucune fuite dans les indicateurs | Calcul récursif causal | Tests de troncature EMA, ATR, pivots, structure, FVG |
| Multi-unités de temps | `avail` = clôture ; jointure sur la disponibilité | `test_resample_avail_is_bar_close`, filtre H1 par `avail_ns` |
| SL et TP dans la même minute → SL | Règle explicite | `test_same_bar_stop_and_target_is_resolved_as_stop` |
| Limite : traversée d'un tick exigée | Règle explicite | `test_limit_not_filled_on_touch_and_expires` |
| Ordres non exécutés journalisés | `Fill(filled=False)` → refus « ordre non exécuté » | idem |
| Gap à travers le stop | Exécution à l'ouverture (perte > 1R possible) | `test_gap_through_stop_fills_at_open` |
| Équivalence vectorisé / naïf | 3 000 trades aléatoires comparés | `test_vectorized_matches_reference` |
| Marche aléatoire ⇒ espérance ≈ −coûts | Contrôle global | `test_random_walk_expectancy_is_minus_costs` |
| Taille = f(capital courant), frais inclus | `RiskManager.size` | `test_sizing_*`, `test_fees_are_included_in_risk_budget` |
| Lots minimaux, arrondi vers le bas | `round_down`, refus sous le minimum | `test_min_size_rejection` |
| Pas de levier ni de vente en spot | `max_leverage=1`, `allow_short=False` | `test_spot_has_no_leverage`, `test_short_refused_on_spot` |
| Limite journalière 2 %, arrêt à 10 % | `RiskManager` | `test_daily_loss_limit_*`, `test_drawdown_halt_is_permanent` |
| Anti-martingale | Pas de dépendance aux pertes passées | `test_risk_never_increases_after_loss` |
| Arrêt sur anomalie | Horodatages, NaN, taux de change absent/périmé | `test_non_monotonic_timestamps_raise_anomaly`, FX |
| Conversion EUR sans taux futur | Taux disponible à la clôture de sa bougie | `test_fx_converter_never_uses_future_rate` |
| DST | `zoneinfo` | `test_paris_midnight_*`, `test_us_eu_dst_mismatch_week` |
| Test final verrouillé | `LockedPeriodError` + journal d'accès | `test_final_test_is_locked` |
| Pré-enregistrement obligatoire et immuable | Registre | `test_registry_requires_preregistration` |

Les données synthétiques ne servent qu'à ces tests du moteur, jamais à évaluer une stratégie.

## Reproductibilité

Chaque essai enregistre la version git du code (suffixe `+dirty` si des fichiers de `nexus/` étaient modifiés), le hachage de sa configuration, la graine aléatoire (= identifiant de l'essai) et la spécification pré-enregistrée hachée. Les données brutes sont re-téléchargeables à l'identique (sommes de contrôle Binance).

Limite connue : les essais du lot 2B-01 portent la version `e3cffad+dirty`, car le code n'était pas encore commité au moment de l'exécution. Le code correspondant est celui du commit `018f564`. Les lots suivants seront exécutés sur du code commité.

## Vers le bot autonome (phase 4)

L'architecture sépare déjà les intentions (stratégies), le gestionnaire de risque (dernier mot) et l'exécution (simulée). Le bot de paper trading réutilisera `strategies/`, `engine/risk.py` et `stats/` tels quels. Il ajoutera : un collecteur temps réel en lecture seule, un simulateur d'exécution temps réel, la persistance de l'état pour reprendre après redémarrage sans dupliquer les positions (clé idempotente par signal), des rapports quotidiens et hebdomadaires, et un tableau de bord local avec arrêt d'urgence. Il ne dépendra d'aucune API d'intelligence artificielle. Les paramètres ne pourront être modifiés que par une nouvelle version validée et approuvée manuellement.
