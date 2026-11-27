"""NEXUS C (Trend Pullback), NEXUS F (Momentum), NEXUS D (Volatility Expansion),
et référence « moyenne mobile simple ». Achat uniquement (spot BTC : pas de vente).

Toutes les décisions sont prises à la CLÔTURE d'une bougie de l'unité de temps de
la stratégie (`avail`) et exécutées au plus tôt à la minute suivante.

Gestion de position commune :
- une position à la fois ; la stratégie ne cherche une nouvelle entrée qu'après
  son propre signal de sortie (règle : après un stop, on attend la réinitialisation
  du signal — pas de ré-entrée immédiate) ;
- stop initial obligatoire (volatilité ou structure) appliqué minute par minute ;
- sortie sur règle (invalidation, perte de momentum) : exécutée à la minute
  suivant la clôture de la bougie qui la déclenche ;
- stop suiveur éventuel : niveau recalculé à chaque clôture, en cliquet.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..features.core import atr, ema, last_confirmed_level, resample, structure_events, swings
from ..features.regime import trailing_percentile
from .base import Signal

TF_MIN = {"H1": 60, "H4": 240, "D1": 1440}


@dataclass
class TFContext:
    tf: str
    bars: pd.DataFrame
    period_end: pd.Timestamp

    @classmethod
    def build(cls, sig_m1: pd.DataFrame, tf: str) -> "TFContext":
        b = resample(sig_m1, TF_MIN[tf])
        # Une bougie incomplète (minutes manquantes) reste utilisable, mais la dernière
        # bougie de la période ne l'est que si elle est close dans la période.
        c, h, l = b["c"].to_numpy(), b["h"].to_numpy(), b["l"].to_numpy()
        b["ema20"] = ema(c, 20)
        b["ema100"] = ema(c, 100)
        b["sma50"] = pd.Series(c).rolling(50).mean().to_numpy()
        b["atr14"] = atr(h, l, c, 14)
        b["atr20"] = atr(h, l, c, 20)
        b["state"] = structure_events(b["o"].to_numpy(), h, l, c, 2, 2)["state"].to_numpy()
        sh, sl = swings(h, l, 2, 2)
        b["last_swing_low"] = last_confirmed_level(len(b), sl, l, 2)
        b["avail_ns"] = b["avail"].dt.as_unit("ns").astype("int64")
        end = sig_m1["ts"].iloc[-1] + pd.Timedelta(minutes=1)
        return cls(tf, b, end)


def _chandelier_path(b: pd.DataFrame, i_entry: int, j_exit: int, mult: float):
    """Niveaux de stop suiveur : plus haut des clôtures depuis l'entrée − mult × ATR,
    connus à la clôture de chaque bougie (i_entry+1 .. j_exit)."""
    if j_exit <= i_entry + 1:
        return None
    c = b["c"].to_numpy()[i_entry:j_exit + 1]
    a = b["atr14"].to_numpy()[i_entry:j_exit + 1]
    lv = np.maximum.accumulate(c) - mult * a
    return (b["avail_ns"].to_numpy()[i_entry:j_exit + 1], lv)


def _emit(ctx: TFContext, i: int, j: int | None, stop: float, *, target_r=None, trail_mult=None, tags=None):
    b = ctx.bars
    t_exit = b["avail"].iat[j] if j is not None else ctx.period_end
    path = _chandelier_path(b, i, j if j is not None else len(b) - 1, trail_mult) if trail_mult else None
    return Signal(avail=b["avail"].iat[i], side=1, stop=float(stop), time_exit=t_exit, target_r=target_r,
                  entry_est=float(b["c"].iat[i]), stop_path=path,
                  tags={"day": str(b["avail"].iat[i].date()), "tf": ctx.tf, **(tags or {})})


def _first(cond: np.ndarray, start: int) -> int | None:
    idx = np.flatnonzero(cond[start:])
    return int(start + idx[0]) if len(idx) else None


# ---------------------------------------------------------------------------
# NEXUS C — Trend Pullback
# ---------------------------------------------------------------------------
def nexus_c(ctx: TFContext, *, structure_filter=False, confirmation=False, stop_mode="atr",
            exit_mode="target_2r", regime=None, regime_filter=False) -> list[Signal]:
    """Version minimale : tendance (clôture > EMA100 et EMA100 en hausse sur 10 bougies)
    + retracement (plus bas <= EMA20 et clôture > EMA20). Stop 2 ATR. Sortie : 2R ou
    invalidation (clôture < EMA100).
    exit_mode : "target_2r" | "invalidation" | "trailing" (chandelier 3 ATR + invalidation)."""
    b = ctx.bars
    c, h, l = b["c"].to_numpy(), b["h"].to_numpy(), b["l"].to_numpy()
    e20, e100, a = b["ema20"].to_numpy(), b["ema100"].to_numpy(), b["atr14"].to_numpy()
    slope = e100 - np.concatenate([np.full(10, np.nan), e100[:-10]])
    trend = (c > e100) & (slope > 0)
    if structure_filter:
        trend &= b["state"].to_numpy() == 1
    pull = (l <= e20) & (c > e20)
    invalid = c < e100
    out = []
    i = 0
    n = len(b)
    while i < n:
        if not (trend[i] and pull[i] and np.isfinite(a[i])):
            i += 1; continue
        k = i
        if confirmation:
            k = None
            for m in range(i + 1, min(i + 4, n)):
                if invalid[m]:
                    break
                if c[m] > h[m - 1]:
                    k = m; break
            if k is None:
                i += 1; continue
        if regime_filter and regime is not None:
            from ..features.regime import regime_at
            if regime_at(regime, int(b["avail_ns"].iat[k]))["trend"] != "haussier":
                i = k + 1; continue
        if stop_mode == "atr":
            stop = c[k] - 2 * a[k]
        else:
            sl = b["last_swing_low"].iat[k]
            stop = sl - 0.1 * a[k] if np.isfinite(sl) else np.nan
            if not np.isfinite(stop) or not (0.5 * a[k] <= c[k] - stop <= 5 * a[k]):
                i = k + 1; continue
        j = _first(invalid, k + 1)
        out.append(_emit(ctx, k, j, stop, target_r=2.0 if exit_mode == "target_2r" else None,
                         trail_mult=3.0 if exit_mode == "trailing" else None))
        if j is None:
            break
        i = j + 1
    return out


# ---------------------------------------------------------------------------
# NEXUS F — Momentum (et référence moyenne mobile simple)
# ---------------------------------------------------------------------------
def _vol_ok(ctx: TFContext, max_pct: float = 0.8) -> np.ndarray:
    b = ctx.bars
    pct = trailing_percentile((b["atr20"] / b["c"]).to_numpy(), window=365 * 1440 // TF_MIN[ctx.tf],
                              min_periods=180 * 1440 // TF_MIN[ctx.tf])
    return np.where(np.isfinite(pct), pct <= max_pct, False)


def _state_machine(ctx: TFContext, enter: np.ndarray, leave: np.ndarray, stop_atr: float,
                   entry_ok: np.ndarray | None = None, trail_mult=None, use_leave=True) -> list[Signal]:
    b = ctx.bars
    c, a = b["c"].to_numpy(), b["atr20"].to_numpy()
    out, i, n = [], 0, len(b)
    while i < n:
        if not (enter[i] and np.isfinite(a[i]) and (entry_ok is None or entry_ok[i])):
            i += 1; continue
        j = _first(leave, i + 1) if use_leave else None
        out.append(_emit(ctx, i, j, c[i] - stop_atr * a[i], trail_mult=trail_mult))
        if j is None:
            break
        # attendre la réinitialisation : l'entrée exige un front montant
        i = j + 1
        while i < n and enter[i]:
            i += 1
    return out


def nexus_f_tsmom(ctx: TFContext, *, lookback: int, vol_filter=False) -> list[Signal]:
    """Momentum de série temporelle : long tant que clôture > clôture d'il y a `lookback` bougies.
    Entrée sur front montant, sortie quand la condition devient fausse. Stop initial 3 ATR20."""
    c = ctx.bars["c"].to_numpy()
    past = np.concatenate([np.full(lookback, np.nan), c[:-lookback]])
    up = c > past
    enter = up & ~np.concatenate([[True], up[:-1]])
    return _state_machine(ctx, enter, ~up & np.isfinite(past), 3.0, _vol_ok(ctx) if vol_filter else None)


def nexus_f_donchian(ctx: TFContext, *, n: int, vol_filter=False, trailing=False) -> list[Signal]:
    """Cassure de Donchian : clôture > plus haut des n bougies précédentes ; sortie
    clôture < plus bas des n/2 bougies précédentes (ou stop suiveur 3 ATR). Stop 2 ATR20."""
    b = ctx.bars
    hh = b["h"].rolling(n).max().shift(1).to_numpy()
    ll = b["l"].rolling(max(n // 2, 2)).min().shift(1).to_numpy()
    c = b["c"].to_numpy()
    enter = c > hh
    leave = c < ll
    if trailing:
        return _state_machine(ctx, enter, np.zeros(len(c), bool), 2.0, _vol_ok(ctx) if vol_filter else None,
                              trail_mult=3.0, use_leave=False)
    return _state_machine(ctx, enter, leave, 2.0, _vol_ok(ctx) if vol_filter else None)


def ref_sma(ctx: TFContext, *, n: int = 50) -> list[Signal]:
    """Référence : long quand clôture > SMA(n), sortie en dessous. Stop 3 ATR20."""
    b = ctx.bars
    c = b["c"].to_numpy()
    sma = b["c"].rolling(n).mean().to_numpy()
    up = c > sma
    enter = up & ~np.concatenate([[True], up[:-1]])
    return _state_machine(ctx, enter, ~up & np.isfinite(sma), 3.0)


# ---------------------------------------------------------------------------
# NEXUS D — Volatility Expansion (introduite après les conclusions C et F)
# ---------------------------------------------------------------------------
def nexus_d(ctx: TFContext, *, require_compression=True, pct_max: float = 0.2, window_days: int = 90) -> list[Signal]:
    """Compression : largeur des bandes de Bollinger(20, 2) / prix au plus bas
    `pct_max` de son historique des `window_days` jours précédents ; puis clôture
    au-dessus de la bande haute. Sortie : clôture sous la moyenne 20. Stop 2 ATR14.
    require_compression=False : même cassure sans condition de compression (contrôle)."""
    b = ctx.bars
    c = b["c"]
    mid = c.rolling(20).mean(); sd = c.rolling(20).std(ddof=0)
    upper = (mid + 2 * sd).to_numpy()
    width = ((4 * sd) / mid).to_numpy()
    per_day = 1440 // TF_MIN[ctx.tf]
    pct = trailing_percentile(width, window=window_days * per_day, min_periods=30 * per_day)
    comp_prev = np.concatenate([[False], (pct <= pct_max)[:-1]])   # compression sur la bougie précédente
    cc = c.to_numpy()
    enter = cc > upper
    if require_compression:
        enter &= comp_prev
    leave = cc < mid.to_numpy()
    a = b["atr14"].to_numpy()
    out, i, n = [], 0, len(b)
    while i < n:
        if not (enter[i] and np.isfinite(a[i])):
            i += 1; continue
        j = _first(leave, i + 1)
        out.append(_emit(ctx, i, j, cc[i] - 2 * a[i]))
        if j is None:
            break
        i = j + 1
    return out
