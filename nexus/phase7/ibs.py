"""IBS et équivalents (Williams %R(1), stochastique brut %K(1)) ; chargeur OHLC journalier et
simulateur journalier à exécution causale (ouverture suivante) avec stop intrajournalier.

Le chargeur accepte un export MetaTrader 5 (colonnes <DATE> <OPEN> <HIGH> <LOW> <CLOSE>…, séparateur
tabulation) ou un CSV générique (date, open, high, low, close). Toute observation >= fin de la période
de développement est écartée à la lecture (verrous de la validation et du test final).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import DEV
from ..phase4.sim import rsi


# --------------------------------------------------------------------------- indicateurs
def ibs(d: pd.DataFrame) -> pd.Series:
    """(C − L)/(H − L) ; non défini (NaN) quand H = L."""
    rng = d["h"] - d["l"]
    return ((d["c"] - d["l"]) / rng).where(rng > 0)


def williams_r(d: pd.DataFrame, n: int) -> pd.Series:
    hh = d["h"].rolling(n, min_periods=n).max()
    ll = d["l"].rolling(n, min_periods=n).min()
    return (-100 * (hh - d["c"]) / (hh - ll)).where(hh > ll)


def stoch_k(d: pd.DataFrame, n: int, smooth: int = 1) -> pd.Series:
    hh = d["h"].rolling(n, min_periods=n).max()
    ll = d["l"].rolling(n, min_periods=n).min()
    k = (100 * (d["c"] - ll) / (hh - ll)).where(hh > ll)
    return k.rolling(smooth, min_periods=smooth).mean() if smooth > 1 else k


# --------------------------------------------------------------------------- données
def load_ohlc_csv(path: str | Path, cutoff=DEV[1]) -> pd.DataFrame:
    """Index date (UTC, jour), colonnes o, h, l, c. Rien n'est conservé après `cutoff`."""
    raw = pd.read_csv(path, sep=None, engine="python")
    cols = {c.strip("<>").lower(): c for c in raw.columns}
    date = pd.to_datetime(raw[cols["date"]].astype(str), utc=True, format="mixed")
    df = pd.DataFrame({"o": raw[cols["open"]].astype(float), "h": raw[cols["high"]].astype(float),
                       "l": raw[cols["low"]].astype(float), "c": raw[cols["close"]].astype(float)}, index=date.dt.normalize())
    df = df[~df.index.duplicated()].sort_index()
    return df[df.index < cutoff]


# --------------------------------------------------------------------------- simulation
def flags(d: pd.DataFrame, rule: dict) -> tuple[pd.Series, pd.Series]:
    x = ibs(d)
    if rule["kind"] == "ibs":
        entry = x < rule["ibs_entry"]
        exit_ = x > rule["ibs_exit"]
    elif rule["kind"] == "rsi3ibs":
        entry = (rsi(d["c"], rule["rsi_n"]) < rule["rsi_th"]) & (x < rule["ibs_entry"])
        exit_ = (x > rule["ibs_exit"]) | ((d["c"] > d["h"].shift(1)) if rule.get("exit_prev_high") else False)
    else:
        raise ValueError(rule["kind"])
    return entry.fillna(False).astype(bool), exit_.fillna(False).astype(bool)


@dataclass
class DayResult:
    equity: pd.Series
    exposure: pd.Series
    trades: pd.DataFrame


def simulate(d: pd.DataFrame, rule: dict, start, end, *, stop: float | None, fraction: float, cost_side: float = 0.0003,
             fin_annual: float = 0.0, exec_mode: str = "next_open", extra_delay: int = 0, initial: float = 1000.0) -> DayResult:
    """Signal à la clôture du jour t. Exécution à l'ouverture de t+1+extra_delay (« next_open ») ou à la
    clôture de t (« close », non réalisable, comparaison seulement). Stop vérifié sur le plus bas de
    chaque jour suivant l'entrée : exécution au stop, ou à l'ouverture si elle est déjà sous le stop."""
    ent, ext = (x.to_numpy() for x in flags(d, rule))
    idx = np.flatnonzero((d.index >= pd.Timestamp(start)) & (d.index < pd.Timestamp(end)))
    o, h, l, c = (d[x].to_numpy() for x in "ohlc")
    dates = d.index
    cash, units, pos, pend = initial, 0.0, None, None
    eq, ex, trades = [], [], []

    def close_pos(px, i, reason):
        nonlocal cash, units, pos
        val = units * px
        fee = val * cost_side
        cash += val - fee
        pnl = val - pos["notional"] - pos["fee"] - fee - pos["fin"]
        trades.append({"entry_date": dates[pos["i"]], "exit_date": dates[i], "entry": pos["px"], "exit": px, "notional": pos["notional"],
                       "pnl": pnl, "ret_net": pnl / pos["notional"], "fees": pos["fee"] + fee, "financing": pos["fin"], "reason": reason})
        units, pos = 0.0, None

    def open_pos(px, i):
        nonlocal cash, units, pos
        notional = fraction * cash
        units = notional / px
        fee = notional * cost_side
        cash -= notional + fee
        pos = {"px": px, "i": i, "notional": notional, "fee": fee, "fin": 0.0}

    for j, i in enumerate(idx):
        if pos is not None and i > idx[0]:
            nights = max((dates[i] - dates[i - 1]).days, 1)
            f = units * c[i - 1] * fin_annual / 360 * nights
            cash -= f
            pos["fin"] += f
        # ordres en attente : exécution à l'ouverture
        if pend is not None and pend[1] <= i:
            act = pend[0]
            pend = None
            if act == "exit" and pos is not None:
                close_pos(o[i], i, "signal")
            elif act == "entry" and pos is None:
                open_pos(o[i], i)
        # stop intrajournalier (jour d'entrée inclus si entrée à l'ouverture)
        if pos is not None and stop is not None:
            sp = pos["px"] * (1 - stop)
            if (exec_mode == "next_open" or pos["i"] < i) and l[i] <= sp:
                close_pos(min(o[i], sp) if pos["i"] < i else sp, i, "stop")
        # signaux à la clôture
        if exec_mode == "close":
            if pos is not None and pos["i"] < i and ext[i]:
                close_pos(c[i], i, "signal")
            elif pos is None and ent[i]:
                open_pos(c[i], i)
        else:
            if pos is not None and ext[i] and pend is None:
                pend = ("exit", i + 1 + extra_delay)
            elif pos is None and ent[i] and pend is None:
                pend = ("entry", i + 1 + extra_delay)
        e = cash + units * c[i]
        eq.append(e)
        ex.append(units * c[i] / e if e > 0 else 0.0)
    if pos is not None:
        close_pos(c[idx[-1]], idx[-1], "end")
        eq[-1] = cash
    return DayResult(pd.Series(eq, index=dates[idx]), pd.Series(ex, index=dates[idx]), pd.DataFrame(trades))
