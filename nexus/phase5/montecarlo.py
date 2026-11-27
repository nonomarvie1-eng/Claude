"""Robustesse Monte Carlo sur une liste de trades (rendements nets par trade sur le notionnel).

Le capital est composé : capital ← capital × (1 + f × r) à chaque trade, f = fraction notionnelle.
Les drawdowns sont donc bornés à 100 % (portefeuille solvable, sans levier). Les simulations
mesurent la fragilité du résultat historique ; elles ne donnent pas une probabilité de succès futur.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def path_stats(r: np.ndarray, f: float) -> tuple[float, float]:
    eq = np.cumprod(1 + f * r)
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    return float(eq[-1] - 1) if len(eq) else 0.0, float((1 - eq / peak).max()) if len(eq) else 0.0


def summarize(tot: np.ndarray, dd: np.ndarray, dd_limit: float = 0.10) -> dict:
    return {"median_return_pct": float(np.median(tot) * 100), "p05_return_pct": float(np.percentile(tot, 5) * 100),
            "p95_drawdown_pct": float(np.percentile(dd, 95) * 100), "share_losing": float((tot < 0).mean()),
            "p_dd_over_limit": float((dd > dd_limit).mean())}


def shuffle(r, f, n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    out = np.array([path_stats(rng.permutation(r), f) for _ in range(n)])
    return summarize(out[:, 0], out[:, 1])


def block_bootstrap(r, months, f, n=10_000, seed=1):
    """Rééchantillonne des MOIS entiers (avec remise) pour préserver la dépendance intra-mois."""
    rng = np.random.default_rng(seed)
    uniq, inv = np.unique(months, return_inverse=True)
    groups = [r[inv == g] for g in range(len(uniq))]
    out = np.empty((n, 2))
    for k in range(n):
        pick = rng.integers(0, len(groups), len(groups))
        out[k] = path_stats(np.concatenate([groups[g] for g in pick]), f)
    return summarize(out[:, 0], out[:, 1])


def removal(r, f, share, n=10_000, seed=2):
    rng = np.random.default_rng(seed)
    keep = int(round(len(r) * (1 - share)))
    out = np.array([path_stats(r[np.sort(rng.choice(len(r), keep, replace=False))], f) for _ in range(n)])
    return summarize(out[:, 0], out[:, 1])


def concentration(trades: pd.DataFrame, f: float) -> dict:
    r = trades["ret_net"].to_numpy()
    tot, dd = path_stats(r, f)
    best = int(np.argmax(r))
    t_wo, _ = path_stats(np.delete(r, best), f)
    yr = pd.to_datetime(trades["entry_date"]).dt.year.to_numpy()
    by_year = {int(y): path_stats(r[yr == y], f)[0] for y in np.unique(yr)}
    best_year = max(by_year, key=by_year.get)
    t_wo_y, _ = path_stats(r[yr != best_year], f)
    pnl = trades["pnl"].to_numpy()
    pos = pnl[pnl > 0].sum()
    top5 = np.sort(pnl)[-5:].sum()
    return {"total_return_pct": tot * 100, "without_best_trade_pct": t_wo * 100, "best_trade_ret_pct": float(r[best] * 100),
            "best_year": best_year, "best_year_return_pct": by_year[best_year] * 100,
            "without_best_year_pct": t_wo_y * 100, "top5_share_of_gross_profit": float(top5 / pos) if pos > 0 else None}
