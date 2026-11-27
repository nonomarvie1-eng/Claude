"""Retour à la moyenne journalier sur un indice de rendement total (données de clôture seulement).

Conventions (pré-enregistrement 5-01) :
- signal calculé à la clôture du jour t ; exécution à la clôture de t (delay=0) ou de t+1 (delay=1) ;
- une position à la fois, achat seulement ; stop catastrophe vérifié à la clôture ;
- coûts : `cost_side` par côté sur le notionnel ; financement de nuit (RF annuel + `fin_spread`) / 360
  par nuit calendaire ;
- taille : `fraction` du capital courant en notionnel (règle NEXUS : risque / stop ; documents : 1,0).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..phase4.sim import rsi, sma


@dataclass
class MRResult:
    equity: pd.Series
    exposure: pd.Series
    trades: pd.DataFrame


def flags(close: pd.Series, rule: dict) -> tuple[pd.Series, pd.Series]:
    """(entrée possible, sortie) évalués à chaque clôture, sans donnée future."""
    c = close
    trend = sma(c, rule.get("trend_sma", 200))
    up = c > trend
    k = rule["kind"]
    if k == "rsi2":
        r = rsi(c, rule["rsi_n"])
        entry = up & (r < rule["rsi_th"])
        exit_ = c > sma(c, rule.get("exit_sma", 5))
    elif k == "rsi3050":
        r = rsi(c, rule["rsi_n"])
        entry = up & (r < rule["entry_th"])
        exit_ = (r > rule["exit_th"]) & (r.shift(1) <= rule["exit_th"])
    elif k == "double":
        n = rule["n"]
        entry = up & (c <= c.rolling(n, min_periods=n).min())
        exit_ = c >= c.rolling(n, min_periods=n).max()
    elif k == "trend_only":
        entry = up
        exit_ = ~up
    else:
        raise ValueError(k)
    return entry.fillna(False).astype(bool), exit_.fillna(False).astype(bool)


def simulate(df: pd.DataFrame, rule: dict, start, end, *, stop: float | None, fraction: float, delay: int = 0,
             cost_side: float = 0.0003, fin_spread: float = 0.025, initial: float = 1000.0,
             signal_close: pd.Series | None = None) -> MRResult:
    """`df` : index date, colonnes close, rf. `signal_close` : série alternative pour les signaux
    (test de bruit) ; les prix d'exécution restent ceux de `close`."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    entry_f, exit_f = flags(signal_close if signal_close is not None else df["close"], rule)
    m = (df.index >= start) & (df.index < end)
    idx = np.flatnonzero(m)
    c = df["close"].to_numpy()
    rf_ann = df["rf"].to_numpy() * 252
    dates = df.index
    ent, ext = entry_f.to_numpy(), exit_f.to_numpy()
    cash, units, pos = initial, 0.0, None
    eq, ex, trades = [], [], []
    pending = None
    for i in idx:
        # financement de la nuit précédente
        if pos is not None and i > 0:
            nights = max((dates[i] - dates[i - 1]).days, 1)
            fin = units * c[i - 1] * (rf_ann[i - 1] + fin_spread) / 360 * nights
            cash -= fin
            pos["fin"] += fin
        # ordre différé (delay=1) exécuté à cette clôture
        if pending is not None:
            act, reason = pending
            pending = None
            if act == "exit" and pos is not None:
                cash, units, pos = _close(trades, pos, cash, units, c[i], dates[i], cost_side, reason)
            elif act == "entry" and pos is None:
                cash, units, pos = _open(cash, units, c[i], dates[i], fraction, cost_side, i)
        # décisions à la clôture i
        if pos is not None and pos["i"] < i:
            reason = None
            if stop is not None and c[i] <= pos["px"] * (1 - stop):
                reason = "stop"
            elif ext[i] or (rule.get("max_bars") and i - pos["i"] >= rule["max_bars"]):
                reason = "signal"
            if reason:
                if delay == 0 or reason == "stop":                  # le stop est un ordre en place : pas de délai
                    cash, units, pos = _close(trades, pos, cash, units, c[i], dates[i], cost_side, reason)
                else:
                    pending = ("exit", reason)
        elif pos is None and ent[i] and pending is None:
            if delay == 0:
                cash, units, pos = _open(cash, units, c[i], dates[i], fraction, cost_side, i)
            else:
                pending = ("entry", None)
        e = cash + units * c[i]
        eq.append(e)
        ex.append(units * c[i] / e if e > 0 else 0.0)
    if pos is not None:
        i = idx[-1]
        cash, units, pos = _close(trades, pos, cash, units, c[i], dates[i], cost_side, "end")
        eq[-1] = cash
    return MRResult(pd.Series(eq, index=dates[idx]), pd.Series(ex, index=dates[idx]), pd.DataFrame(trades))


def _open(cash, units, px, date, fraction, cost_side, i):
    notional = fraction * cash
    units = notional / px
    fee = notional * cost_side
    cash = cash - notional - fee
    return cash, units, {"px": px, "date": date, "i": i, "notional": notional, "fee": fee, "fin": 0.0}


def _close(trades, pos, cash, units, px, date, cost_side, reason):
    value = units * px
    fee = value * cost_side
    cash = cash + value - fee
    pnl = value - pos["notional"] - pos["fee"] - fee - pos["fin"]
    trades.append({"entry_date": pos["date"], "exit_date": date, "entry": pos["px"], "exit": px,
                   "notional": pos["notional"], "pnl": pnl, "ret_net": pnl / pos["notional"],
                   "ret_gross": px / pos["px"] - 1, "fees": pos["fee"] + fee, "financing": pos["fin"], "reason": reason})
    return cash, 0.0, None


# --------------------------------------------------------------------------- bases aléatoires
def random_entries(df: pd.DataFrame, rule: dict, start, end, durations: np.ndarray, n_reps: int, *, stop: float | None,
                   cost_side: float = 0.0003, fin_spread: float = 0.025, seed: int = 0) -> np.ndarray:
    """Moyenne du rendement net par trade pour des entrées tirées parmi les jours où la clôture est
    au-dessus de la SMA (même régime), avec les durées réelles permutées (mêmes nombre et durées)."""
    c = df["close"].to_numpy()
    rf = df["rf"].to_numpy() * 252
    up = (df["close"] > sma(df["close"], rule.get("trend_sma", 200))).to_numpy()
    m = np.flatnonzero((df.index >= pd.Timestamp(start)) & (df.index < pd.Timestamp(end)) & up)
    last = np.flatnonzero(df.index < pd.Timestamp(end))[-1]
    rng = np.random.default_rng(seed)
    durations = np.asarray(durations, int)
    kmax = int(durations.max())
    m = m[m + kmax <= last]
    nights = np.diff(df.index.values).astype("timedelta64[D]").astype(int)
    out = np.empty(n_reps)
    for r in range(n_reps):
        d0 = rng.choice(m, size=len(durations))
        k = rng.permutation(durations)
        rets = _path_returns(c, rf, nights, d0, k, stop, cost_side, fin_spread)
        out[r] = rets.mean()
    return out


def _path_returns(c, rf, nights, d0, k, stop, cost_side, fin_spread):
    kmax = int(k.max())
    steps = np.arange(1, kmax + 1)
    j = np.minimum(d0[:, None] + steps[None, :], len(c) - 1)
    rel = c[j] / c[d0][:, None]
    valid = steps[None, :] <= k[:, None]
    exit_step = k.copy()
    if stop is not None:
        hit = (rel <= 1 - stop) & valid
        any_hit = hit.any(axis=1)
        exit_step = np.where(any_hit, hit.argmax(axis=1) + 1, k)
    ex_i = np.minimum(d0 + exit_step, len(c) - 1)
    xe = c[ex_i] / c[d0]
    # financement approché : nuits réelles × (rf du jour d'entrée + écart) / 360, sur le notionnel initial
    cum_n = np.concatenate([[0], np.cumsum(nights)])
    nn = cum_n[ex_i] - cum_n[d0]
    fin = nn * (rf[d0] + fin_spread) / 360
    return xe * (1 - cost_side) - (1 + cost_side) - fin + 0.0


def random_same_exit(df: pd.DataFrame, rule: dict, start, end, n_trades: int, n_reps: int, *, stop: float | None,
                     cost_side: float = 0.0003, fin_spread: float = 0.025, seed: int = 1) -> dict:
    """Entrées au hasard (même régime) + la MÊME règle de sortie que la stratégie : isole l'effet de la sortie
    sur le taux de réussite (leçon du document 2)."""
    _, exit_f = flags(df["close"], rule)
    c = df["close"].to_numpy()
    rf = df["rf"].to_numpy() * 252
    ext = exit_f.to_numpy()
    up = (df["close"] > sma(df["close"], rule.get("trend_sma", 200))).to_numpy()
    last = np.flatnonzero(df.index < pd.Timestamp(end))[-1]
    m = np.flatnonzero((df.index >= pd.Timestamp(start)) & (df.index < pd.Timestamp(end)) & up)
    nxt = np.full(len(c), last)
    nxt_i = last
    for i in range(last, -1, -1):              # prochaine sortie strictement après i
        nxt[i] = nxt_i
        if ext[i]:
            nxt_i = i
    if rule.get("max_bars"):
        nxt = np.minimum(nxt, np.arange(len(c)) + rule["max_bars"])
    nxt = np.minimum(nxt, last)
    m = m[m < last]
    nights = np.diff(df.index.values).astype("timedelta64[D]").astype(int)
    rng = np.random.default_rng(seed)
    means, wins = np.empty(n_reps), np.empty(n_reps)
    for r in range(n_reps):
        d0 = rng.choice(m, size=n_trades)
        k = np.maximum(nxt[d0] - d0, 1)
        rets = _path_returns(c, rf, nights, d0, k, stop, cost_side, fin_spread)
        means[r], wins[r] = rets.mean(), (rets > 0).mean()
    return {"mean_ret": float(means.mean()), "win_rate": float(wins.mean()), "dist_mean": means}
