"""Régimes de marché déterministes et causals (journaliers, UTC).

Le régime du jour D est calculé à la CLÔTURE de D et n'est utilisable qu'à partir
de D+1 00:00 UTC (colonne `avail`). Aucun seuil n'est estimé sur l'échantillon
complet : le percentile de volatilité est calculé sur les 365 jours PRÉCÉDENTS.

Tendance (règle fixée a priori, non optimisée) :
    haussier  : clôture > EMA100 et EMA100 en hausse sur 20 jours
    baissier  : clôture < EMA100 et EMA100 en baisse sur 20 jours
    consolidation : sinon
Volatilité : rang percentile de ATR14/clôture parmi les 365 jours précédents
    faible < 1/3 <= moyenne <= 2/3 < forte
Indicateurs complémentaires publiés pour analyse : ADX14, efficacité directionnelle ER20.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .core import atr, ema, resample


def adx(h, l, c, n: int = 14) -> np.ndarray:
    h, l, c = (np.asarray(v, float) for v in (h, l, c))
    up = np.diff(h, prepend=np.nan); dn = -np.diff(l, prepend=np.nan)
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr_atr = atr(h, l, c, n)

    def wilder(x):
        out = np.full(len(x), np.nan)
        if len(x) <= n:
            return out
        out[n] = np.nansum(x[1:n + 1]) / n
        for i in range(n + 1, len(x)):
            out[i] = out[i - 1] + (x[i] - out[i - 1]) / n
        return out

    pdi = 100 * wilder(pdm) / tr_atr
    ndi = 100 * wilder(ndm) / tr_atr
    dx = 100 * np.abs(pdi - ndi) / (pdi + ndi)
    out = np.full(len(c), np.nan)
    valid = np.flatnonzero(np.isfinite(dx))
    if len(valid) > n:
        s = valid[0]
        out[s + n - 1] = np.mean(dx[s:s + n])
        for i in range(s + n, len(c)):
            out[i] = out[i - 1] + (dx[i] - out[i - 1]) / n
    return out


def efficiency_ratio(c, n: int = 20) -> np.ndarray:
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    d = np.abs(np.diff(c, prepend=np.nan))
    for i in range(n, len(c)):
        den = np.nansum(d[i - n + 1:i + 1])
        out[i] = abs(c[i] - c[i - n]) / den if den > 0 else np.nan
    return out


def trailing_percentile(x: np.ndarray, window: int = 365, min_periods: int = 180) -> np.ndarray:
    """Rang percentile de x[t] parmi x[t-window .. t-1] (strictement passé)."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    for t in range(len(x)):
        past = x[max(0, t - window):t]
        past = past[np.isfinite(past)]
        if len(past) >= min_periods and np.isfinite(x[t]):
            out[t] = (past < x[t]).mean()
    return out


def daily_regimes(sig_m1: pd.DataFrame) -> pd.DataFrame:
    d = resample(sig_m1, 1440)
    c, h, l = d["c"].to_numpy(), d["h"].to_numpy(), d["l"].to_numpy()
    e = ema(c, 100)
    slope = e - np.concatenate([np.full(20, np.nan), e[:-20]])
    trend = np.where((c > e) & (slope > 0), "haussier", np.where((c < e) & (slope < 0), "baissier", "consolidation"))
    trend = np.where(np.isfinite(e) & np.isfinite(slope), trend, "indéfini")
    atrp = atr(h, l, c, 14) / c
    pct = trailing_percentile(atrp)
    vol = np.where(pct < 1 / 3, "faible", np.where(pct > 2 / 3, "forte", "moyenne"))
    vol = np.where(np.isfinite(pct), vol, "indéfini")
    out = pd.DataFrame({"day": d["ts"], "avail": d["avail"], "trend": trend, "vol": vol,
                        "atr_pct": atrp, "vol_pctile": pct, "adx14": adx(h, l, c, 14), "er20": efficiency_ratio(c, 20),
                        "close": c})
    out["avail_ns"] = out["avail"].dt.as_unit("ns").astype("int64")
    return out


def regime_at(reg: pd.DataFrame, t_ns: int) -> dict:
    """Dernier régime connu à l'instant t (jamais celui du jour en cours)."""
    i = int(np.searchsorted(reg["avail_ns"].to_numpy(), t_ns, side="right")) - 1
    if i < 0:
        return {"trend": "indéfini", "vol": "indéfini"}
    r = reg.iloc[i]
    return {"trend": r["trend"], "vol": r["vol"]}
