"""Métriques de performance (en euros et en R)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def longest_streak(mask: np.ndarray) -> int:
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best


def drawdown_stats(eq: pd.Series) -> dict:
    if len(eq) == 0:
        return {"max_dd_pct": 0.0, "max_dd_eur": 0.0, "max_dd_duration_days": 0}
    peak = eq.cummax()
    dd = eq / peak - 1
    # durée : plus longue période sous un sommet antérieur
    under = (dd < 0).to_numpy()
    dur = longest_streak(under)
    return {"max_dd_pct": float(-dd.min()), "max_dd_eur": float((peak - eq).max()), "max_dd_duration_days": int(dur)}


def summarize(trades: pd.DataFrame, equity_daily: pd.Series, initial: float, *, periods_per_year: int) -> dict:
    out: dict = {"initial_capital_eur": initial}
    n = len(trades)
    out["n_trades"] = n
    if n == 0:
        out.update({"final_capital_eur": initial, "net_profit_eur": 0.0})
        return out
    pnl = trades["pnl_eur"].to_numpy()
    r = trades["r_net"].to_numpy()
    final = float(trades["equity_after"].iloc[-1])
    out["final_capital_eur"] = final
    out["net_profit_eur"] = final - initial
    out["net_return_pct"] = (final / initial - 1) * 100
    days = (equity_daily.index[-1] - equity_daily.index[0]).days + 1 if len(equity_daily) else 1
    years = days / 365.25
    out["years"] = years
    out["cagr_pct"] = ((final / initial) ** (1 / years) - 1) * 100 if years >= 0.5 and final > 0 else np.nan
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    out["profit_factor"] = float(wins.sum() / -losses.sum()) if losses.sum() < 0 else np.inf
    out["win_rate_pct"] = float((pnl > 0).mean() * 100)
    out["avg_win_eur"] = float(wins.mean()) if len(wins) else 0.0
    out["avg_loss_eur"] = float(losses.mean()) if len(losses) else 0.0
    out["expectancy_eur"] = float(pnl.mean())
    out["expectancy_r_net"] = float(np.nanmean(r))
    out["expectancy_r_gross"] = float(np.nanmean(trades["r_gross"]))
    out["r_std"] = float(np.nanstd(r, ddof=1)) if n > 1 else np.nan
    out["total_fees_eur"] = float(trades["fees_eur"].sum())
    out["longest_losing_streak"] = longest_streak(pnl <= 0)
    out["share_ambiguous_bars_pct"] = float(trades["ambiguous_bar"].mean() * 100)
    out["exit_reasons"] = trades["exit_reason"].value_counts().to_dict()
    out.update(drawdown_stats(equity_daily))
    ret = equity_daily.pct_change().dropna()
    if len(ret) > 2 and ret.std() > 0:
        out["sharpe"] = float(ret.mean() / ret.std() * np.sqrt(periods_per_year))
        downside = ret[ret < 0]
        dd_std = np.sqrt((downside ** 2).sum() / len(ret))
        out["sortino"] = float(ret.mean() / dd_std * np.sqrt(periods_per_year)) if dd_std > 0 else np.nan
        out["ann_vol_pct"] = float(ret.std() * np.sqrt(periods_per_year) * 100)
    out["calmar"] = (out["cagr_pct"] / 100 / out["max_dd_pct"]) if out.get("max_dd_pct") and np.isfinite(out.get("cagr_pct", np.nan)) else np.nan
    # Concentration : part du profit brut apportée par les 5 meilleurs trades
    if wins.sum() > 0:
        out["top5_share_of_gross_profit_pct"] = float(np.sort(wins)[-5:].sum() / wins.sum() * 100)
    tr = trades.set_index("exit_time")
    out["monthly_pnl_eur"] = {str(k.date()): round(float(v), 2) for k, v in tr["pnl_eur"].resample("MS").sum().items()}
    out["annual_pnl_eur"] = {str(k.year): round(float(v), 2) for k, v in tr["pnl_eur"].resample("YS").sum().items()}
    out["annual_mean_r"] = {str(k.year): round(float(v), 4) for k, v in tr["r_net"].resample("YS").mean().items()}
    return out
