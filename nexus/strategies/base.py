"""Interface commune des stratégies : elles émettent des INTENTIONS, jamais des ordres."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Signal:
    avail: pd.Timestamp        # instant où toute l'information utilisée est connue
    side: int                  # +1 achat, -1 vente
    stop: float
    time_exit: pd.Timestamp
    entry_type: str = "market"
    limit_price: float | None = None
    expiry: pd.Timestamp | None = None
    target: float | None = None
    target_r: float | None = None
    entry_est: float | None = None   # estimation du prix d'entrée pour le dimensionnement
    day: object = None
    tags: dict = field(default_factory=dict)
