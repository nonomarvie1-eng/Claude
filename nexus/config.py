"""Configuration globale : chemins, périodes figées, capital et profils de risque."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("NEXUS_DATA_DIR", ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
BARS_DIR = DATA_DIR / "bars"
RESULTS_DIR = Path(os.environ.get("NEXUS_RESULTS_DIR", ROOT / "results"))
REGISTRY_PATH = RESULTS_DIR / "registry.sqlite"

UTC = "UTC"

# ---------------------------------------------------------------------------
# Découpage chronologique validé (phase 1, confirmé par l'utilisateur)
# Bornes [début, fin) en UTC.
# ---------------------------------------------------------------------------
DEV = (pd.Timestamp("2020-01-01", tz=UTC), pd.Timestamp("2023-07-01", tz=UTC))
VALIDATION = (pd.Timestamp("2023-07-01", tz=UTC), pd.Timestamp("2025-01-01", tz=UTC))
FINAL_TEST = (pd.Timestamp("2025-01-01", tz=UTC), pd.Timestamp("2026-07-01", tz=UTC))
PERIODS = {"dev": DEV, "validation": VALIDATION, "final": FINAL_TEST}

# Capital simulé de référence
INITIAL_CAPITAL_EUR = 1_000.0


@dataclass(frozen=True)
class RiskProfile:
    name: str
    risk_per_trade: float          # fraction du capital COURANT, frais inclus
    daily_loss_limit: float = 0.02  # fraction du capital en début de journée
    max_drawdown_halt: float = 0.10  # arrêt automatique depuis le dernier sommet
    max_positions: int = 1


RISK_PROFILES = {
    "prudent": RiskProfile("prudent", 0.0025),
    "equilibre": RiskProfile("equilibre", 0.005),
    "dynamique": RiskProfile("dynamique", 0.01),
}
