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


def exposure_stats(trades: pd.DataFrame, start, end) -> dict:
    """Temps passé sur le marché, exposition moyenne, turnover, durée moyenne."""
    if len(trades) == 0:
        return {"time_in_market_pct": 0.0, "avg_exposure_pct": 0.0, "turnover_per_year": 0.0, "avg_duration_h": 0.0}
    span_h = (pd.Timestamp(end) - pd.Timestamp(start)).total_seconds() / 3600
    dur = trades["duration_h"].to_numpy()
    expo = trades["exposure_frac"].to_numpy()
    years = span_h / (24 * 365.25)
    return {
        "time_in_market_pct": float(dur.sum() / span_h * 100),
        # exposition moyenne pondérée par le temps, sur toute la période (0 en liquidités)
        "avg_exposure_pct": float((dur * expo).sum() / span_h * 100),
        "avg_exposure_when_invested_pct": float((dur * expo).sum() / dur.sum() * 100) if dur.sum() > 0 else 0.0,
        "turnover_per_year": float(2 * expo.sum() / years),
        "avg_duration_h": float(dur.mean()),
        "median_duration_h": float(np.median(dur)),
    }


def market_attribution(eq_daily: pd.Series, asset_close_daily: pd.Series, n_boot: int = 2000,
                       block: int = 20, seed: int = 0) -> dict:
    """Régression des rendements quotidiens de la stratégie sur ceux de l'actif :
    r_s = alpha + beta * r_m. Alpha annualisé (365 j) avec IC95 par bootstrap par
    blocs de `block` jours (dépendance temporelle). Analyse descriptive."""
    rs = eq_daily.pct_change()
    rm = asset_close_daily.reindex(eq_daily.index).ffill().pct_change()
    df = pd.concat([rs, rm], axis=1, keys=["s", "m"]).dropna()
    if len(df) < 60 or df["m"].var() == 0:
        return {}
    x, y = df["m"].to_numpy(), df["s"].to_numpy()

    def fit(xx, yy):
        b = np.cov(xx, yy, ddof=1)[0, 1] / np.var(xx, ddof=1)
        return yy.mean() - b * xx.mean(), b

    a, b = fit(x, y)
    rng = np.random.default_rng(seed)
    n = len(x); nb = int(np.ceil(n / block))
    alphas = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        alphas.append(fit(x[idx], y[idx])[0])
    lo, hi = np.percentile(alphas, [2.5, 97.5])
    resid = y - (a + b * x)
    return {"beta": float(b), "alpha_ann_pct": float(a * 365 * 100), "alpha_ci95_ann_pct": [float(lo * 365 * 100), float(hi * 365 * 100)],
            "r2": float(1 - resid.var() / y.var()) if y.var() > 0 else np.nan, "n_days": int(n)}


def daily_sharpe_ci(eq_daily: pd.Series, periods: int = 365, block: int = 20, n_boot: int = 2000, seed: int = 0) -> dict:
    r = eq_daily.pct_change().dropna().to_numpy()
    if len(r) < 60 or r.std() == 0:
        return {}
    rng = np.random.default_rng(seed)
    n = len(r); nb = int(np.ceil(n / block))
    srs = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block + 1, nb)
        s = r[np.concatenate([np.arange(k, k + block) for k in starts])[:n]]
        srs.append(s.mean() / s.std() * np.sqrt(periods) if s.std() > 0 else 0.0)
    return {"sharpe": float(r.mean() / r.std() * np.sqrt(periods)), "sharpe_ci95": [float(np.percentile(srs, 2.5)), float(np.percentile(srs, 97.5))]}


def passive_benchmarks(asset_close_daily: pd.Series, fx_quote_per_eur_daily: pd.Series, initial: float,
                       fee_rate: float, exposure: float, start_price: float | None = None) -> dict:
    """Buy & Hold (100 % investi), liquidités (0 %), et détention passive constante
    à l'exposition moyenne de la stratégie (rééquilibrage ignoré, borne indicative).
    start_price : prix d'OUVERTURE du premier jour (audit 2D : sans lui, la référence
    partait de la clôture du premier jour et omettait ce jour)."""
    p = asset_close_daily.dropna()
    if start_price is not None:
        p = pd.concat([pd.Series([start_price], index=[p.index[0] - pd.Timedelta(seconds=1)]), p])
    fx = fx_quote_per_eur_daily.reindex(p.index, method="ffill").ffill().bfill()
    val_eur = initial * (1 - fee_rate) * (p / p.iloc[0]) * (fx.iloc[0] / fx) * (1 - fee_rate)
    dd = float(-(val_eur / val_eur.cummax() - 1).min())
    years = (p.index[-1] - p.index[0]).days / 365.25
    bh_ret = float(val_eur.iloc[-1] / initial - 1)
    expo_val = initial * (1 + exposure * (val_eur / initial - 1))
    return {
        "buy_hold": {"final_eur": float(val_eur.iloc[-1]), "net_return_pct": bh_ret * 100,
                     "cagr_pct": ((1 + bh_ret) ** (1 / years) - 1) * 100, "max_dd_pct": dd * 100,
                     "time_in_market_pct": 100.0},
        "cash": {"final_eur": initial, "net_return_pct": 0.0, "max_dd_pct": 0.0, "time_in_market_pct": 0.0},
        "passive_same_exposure": {"exposure_pct": exposure * 100, "final_eur": float(expo_val.iloc[-1]),
                                  "net_return_pct": float(expo_val.iloc[-1] / initial - 1) * 100,
                                  "max_dd_pct": float(-(expo_val / expo_val.cummax() - 1).min()) * 100},
    }
