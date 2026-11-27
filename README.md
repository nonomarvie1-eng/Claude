# NEXUS QUANT

Projet de recherche en trading algorithmique **en simulation uniquement** (aucun ordre réel, aucune connexion permettant de passer des ordres).

Objectif : déterminer scientifiquement si un avantage statistique robuste, après coûts, existe dans un ensemble de stratégies intraday, et le dire explicitement si ce n'est pas le cas.

## Phase 2D — Diversification, allocation dynamique, audit technique

Commencer par [`docs/phase2d/RAPPORT_PHASE_2D.md`](docs/phase2d/RAPPORT_PHASE_2D.md).

```bash
python -m pytest                                                        # 77 tests
python -m nexus.research.g_runner experiments/preregistration/batch_2d_01.toml     # NEXUS G
python -m nexus.research.lab_runner experiments/preregistration/batch_2d_01.toml   # NEXUS E
python -m nexus.research.report_2d
```

Données Dukascopy : téléchargement automatique **bloqué** (conditions d'utilisation, voir `docs/phase2d/01_conditions_utilisation.md`).

## Phase 2C — Recherche avancée BTC (H1/H4/D1)

Commencer par [`docs/phase2c/RAPPORT_PHASE_2C.md`](docs/phase2c/RAPPORT_PHASE_2C.md).

```bash
python -m pytest
python -m nexus.research.audit_2b                                        # audit des résultats 2B
python -m nexus.research.lab_runner experiments/preregistration/batch_2c_01.toml
python -m nexus.research.report_2c                                       # rapports générés
python scripts/transfer.py verify|pack|import ...                        # données EUR/USD
```

*Les résultats publiés dans `reports/` et `results/` sont dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0 ; Binance n'est pas associé à ce projet. Les données elles-mêmes ne sont jamais versionnées ni redistribuées.*

## Phase 2 — Moteur et premières expériences

Commencer par [`docs/phase2/RAPPORT_PHASE_2.md`](docs/phase2/RAPPORT_PHASE_2.md).

```bash
pip install -e .[dev]            # numpy, pandas, pyarrow, scipy, pytest
python -m pytest
python scripts/download_data.py binance BTCUSDT 2020-01 2026-07
python scripts/build_bars.py BTCUSDT
python -m nexus.research.runner experiments/preregistration/batch_2b_01.toml --symbols BTCUSDT
```

Windows (données EUR/USD) : `scripts/windows/telecharger_eurusd.ps1` — voir [`docs/phase2/02_acces_donnees.md`](docs/phase2/02_acces_donnees.md).

## Phase 1 — Audit et protocole (validée)

Commencer par [`docs/phase1/00_SYNTHESE.md`](docs/phase1/00_SYNTHESE.md).

| Document | Contenu |
|---|---|
| [01 Audit](docs/phase1/01_audit_strategies.md) | Audit comparatif des cinq stratégies |
| [02 Formalisation](docs/phase1/02_formalisation.md) | Définitions algorithmiques causales |
| [03 Candidates](docs/phase1/03_strategies_candidates.md) | Références, hybrides, hypothèses, benchmarks, ablations |
| [04 Données](docs/phase1/04_donnees.md) | Sources, fuseaux, qualité, volumes |
| [05 Protocole](docs/phase1/05_protocole_backtest.md) | Découpage, walk-forward, Monte-Carlo, moteur d'exécution, métriques |
| [06 Ressources](docs/phase1/06_ressources_couts.md) | Environnement, capital, coûts, stockage, calcul |
| [07 Risques](docs/phase1/07_risques_limites.md) | Risques et limites |
| [08 Plan](docs/phase1/08_plan_developpement.md) | Architecture et plan de développement |

Inspection de votre machine : `python scripts/check_env.py` (lecture seule).
