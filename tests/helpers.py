"""Construction de petits jeux de données synthétiques vérifiables à la main.

Les données synthétiques servent UNIQUEMENT à vérifier le moteur, jamais à
évaluer une stratégie.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from nexus.instruments import EURUSD_CFD

T0 = pd.Timestamp("2021-03-01 08:00", tz="UTC")

# Instrument de test sans aucun coût : les résultats se calculent de tête.
ZERO_COST = replace(EURUSD_CFD, commission_per_unit_side=0.0, slippage_market_frac=0.0, slippage_stop_frac=0.0,
                    price_tick=0.0001)


def m1_from_bid(rows, spread=0.0, start=T0, step_min=1):
    """rows = liste de (o, h, l, c) côté bid ; ask = bid + spread."""
    ts = [start + pd.Timedelta(minutes=i * step_min) for i in range(len(rows))]
    a = np.array(rows, float)
    df = pd.DataFrame({"ts": ts})
    for j, k in enumerate("ohlc"):
        df[f"bid_{k}"] = a[:, j]
        df[f"ask_{k}"] = a[:, j] + spread
    df["bid_tickvol"] = 1.0
    df["ask_tickvol"] = 1.0
    return df
