# NEXUS QUANT

Projet de recherche en trading algorithmique **en simulation uniquement** (aucun ordre réel, aucune connexion permettant de passer des ordres).

Objectif : déterminer scientifiquement si un avantage statistique robuste, après coûts, existe dans un ensemble de stratégies intraday, et le dire explicitement si ce n'est pas le cas.

## Phase 1 — Audit et protocole (terminée, en attente de validation)

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
