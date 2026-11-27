"""Simulateur d'exécution sur bougies M1 bid/ask.

Hypothèses conservatrices (documentées et testées) :
- Ordre au marché : exécuté à l'OUVERTURE de la première minute dont l'ouverture
  est >= l'instant de disponibilité du signal (jamais au prix de clôture du signal).
  Achat au ask (+ glissement), vente au bid (- glissement).
- Ordre limite : rempli seulement si le prix TRAVERSE le niveau d'au moins un tick
  (un simple contact ne suffit pas). Prix = niveau, ou ouverture si gap favorable.
  Non rempli avant expiration → ordre annulé et journalisé.
- Stop : déclenché quand le côté de sortie atteint le niveau ; prix = niveau ou
  ouverture si gap au-delà, puis glissement de stop. Une perte peut donc dépasser 1R.
- Stop et objectif touchés dans la même minute (ordre inconnu) → STOP d'abord.
- Minute de remplissage d'un ordre limite : seul le stop peut être déclenché
  dans cette minute (l'objectif est ignoré, ordre chronologique inconnu).
- Sortie temporelle : ouverture de la première minute >= heure de sortie.
- Trou de données pendant une position : la position est évaluée à la première
  minute disponible (le gap est subi, signalé par `gap_during_trade`).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..instruments import InstrumentSpec


@dataclass
class ExecFrame:
    """Tableaux numpy M1 pour l'exécution (côtés bid et ask)."""
    ts: np.ndarray       # int64 ns, ouverture de la minute
    bid_o: np.ndarray; bid_h: np.ndarray; bid_l: np.ndarray; bid_c: np.ndarray
    ask_o: np.ndarray; ask_h: np.ndarray; ask_l: np.ndarray; ask_c: np.ndarray

    @classmethod
    def from_m1(cls, m1: pd.DataFrame, spec: InstrumentSpec) -> "ExecFrame":
        ts = m1["ts"].dt.as_unit("ns").astype("int64").to_numpy()
        if not np.all(np.diff(ts) > 0):
            raise ValueError("ANOMALIE : horodatages non strictement croissants")
        mult = spec.cost_multiplier
        if spec.has_bid_ask:
            arrs = {}
            for k in "ohlc":
                b = m1[f"bid_{k}"].to_numpy(float); a = m1[f"ask_{k}"].to_numpy(float)
                mid = (a + b) / 2
                half = (a - b) / 2 * mult     # stress : spread observé multiplié
                arrs[f"bid_{k}"] = mid - half
                arrs[f"ask_{k}"] = mid + half
        else:
            arrs = {}
            hs = spec.modeled_half_spread_frac * mult
            for k in "ohlc":
                p = m1[k].to_numpy(float)
                arrs[f"bid_{k}"] = p * (1 - hs)
                arrs[f"ask_{k}"] = p * (1 + hs)
        for v in arrs.values():
            if np.isnan(v).any():
                raise ValueError("ANOMALIE : prix manquants (NaN) dans les données d'exécution")
        return cls(ts=ts, **arrs)

    def index_at_or_after(self, t_ns: int) -> int:
        return int(np.searchsorted(self.ts, t_ns, side="left"))


@dataclass
class Fill:
    filled: bool
    reason: str                 # "stop" | "target" | "time" | "end_of_data" | "unfilled"
    entry_idx: int = -1
    exit_idx: int = -1
    entry_price: float = np.nan
    exit_price: float = np.nan
    gap_during_trade: bool = False
    ambiguous_bar: bool = False  # stop et objectif dans la même minute


def _ns(t) -> int:
    return int(pd.Timestamp(t).value)


def simulate(ex: ExecFrame, spec: InstrumentSpec, *, side: int, signal_avail, stop: float,
             target: float | None, time_exit, entry_type: str = "market", target_r: float | None = None,
             limit_price: float | None = None, expiry=None, max_gap_min: float = 30.0,
             stop_path: tuple | None = None) -> Fill:
    """Simule un trade. side = +1 achat, -1 vente.

    stop_path : (t_ns, niveaux) — stop suiveur décidé par la stratégie à la clôture
    de ses bougies ; chaque niveau s'applique à partir des minutes dont l'ouverture
    est >= t_ns. Le stop ne peut que se resserrer (cliquet).
    """
    if side not in (1, -1):
        raise ValueError("side doit valoir +1 ou -1")
    if side == -1 and not spec.allow_short:
        raise ValueError(f"vente à découvert impossible sur {spec.symbol} ({spec.venue_kind})")
    tick = spec.price_tick
    slip_m = spec.slippage_market_frac * spec.cost_multiplier
    slip_s = spec.slippage_stop_frac * spec.cost_multiplier
    t_exit = _ns(time_exit)
    n = len(ex.ts)
    k = ex.index_at_or_after(_ns(signal_avail))
    if k >= n or ex.ts[k] >= t_exit:
        return Fill(False, "unfilled")

    # ---------------- Entrée ----------------
    limit_fill_bar = False
    if entry_type == "market":
        if side == 1:
            entry = ex.ask_o[k] * (1 + slip_m)
        else:
            entry = ex.bid_o[k] * (1 - slip_m)
    elif entry_type == "limit":
        t_exp = min(_ns(expiry), t_exit) if expiry is not None else t_exit
        e_end = int(np.searchsorted(ex.ts, t_exp, side="left"))
        if side == 1:
            hits = np.flatnonzero(ex.ask_l[k:e_end] <= limit_price - tick)
        else:
            hits = np.flatnonzero(ex.bid_h[k:e_end] >= limit_price + tick)
        if len(hits) == 0:
            return Fill(False, "unfilled")
        k = k + int(hits[0])
        entry = min(limit_price, ex.ask_o[k]) if side == 1 else max(limit_price, ex.bid_o[k])
        limit_fill_bar = True
    else:
        raise ValueError(entry_type)

    # Objectif exprimé en multiple du risque effectif (calculé sur le prix réellement obtenu)
    if target_r is not None:
        target = entry + side * target_r * abs(entry - stop)
    if (side == 1 and stop >= entry) or (side == -1 and stop <= entry):
        # Le prix d'exécution est déjà au-delà du stop (gap) : trade invalide, sortie immédiate.
        px = ex.bid_o[k] * (1 - slip_m) if side == 1 else ex.ask_o[k] * (1 + slip_m)
        return Fill(True, "stop", k, k, entry, px, False, False)
    entry_idx = k

    # ---------------- Sortie (recherche vectorisée du premier événement) ----------------
    end = int(np.searchsorted(ex.ts, t_exit, side="left"))   # première minute >= heure de sortie
    stops = np.full(max(end - k, 0), stop, dtype=float)
    if stop_path is not None and len(stop_path[0]) and end > k:
        pt, pl = np.asarray(stop_path[0], np.int64), np.asarray(stop_path[1], float)
        idx = np.searchsorted(pt, ex.ts[k:end], side="right") - 1
        lv = np.where(idx >= 0, pl[np.clip(idx, 0, None)], stop)
        stops = np.maximum.accumulate(np.maximum(lv, stop)) if side == 1 else np.minimum.accumulate(np.minimum(lv, stop))
    if side == 1:
        o_arr, h_arr, l_arr = ex.bid_o, ex.bid_h, ex.bid_l
        stop_hits = l_arr[k:end] <= stops
        tgt_hits = (h_arr[k:end] >= target + tick) if target is not None else np.zeros(end - k, bool)
    else:
        o_arr, h_arr, l_arr = ex.ask_o, ex.ask_h, ex.ask_l
        stop_hits = h_arr[k:end] >= stops
        tgt_hits = (l_arr[k:end] <= target - tick) if target is not None else np.zeros(end - k, bool)
    if limit_fill_bar and len(tgt_hits):
        tgt_hits[0] = False   # ordre chronologique inconnu dans la minute de remplissage
    i_stop = int(np.argmax(stop_hits)) if stop_hits.any() else None
    i_tgt = int(np.argmax(tgt_hits)) if tgt_hits.any() else None

    def gap_until(j_abs: int) -> bool:
        if j_abs <= entry_idx:
            return False
        return bool((np.diff(ex.ts[entry_idx:j_abs + 1]) > max_gap_min * 60e9).any())

    if i_stop is not None and (i_tgt is None or i_stop <= i_tgt):
        j = k + i_stop
        o = o_arr[j]
        stop = stops[i_stop]
        if side == 1:
            base = stop if (j == entry_idx and limit_fill_bar) else min(stop, o)
            px = base * (1 - slip_s)
        else:
            base = stop if (j == entry_idx and limit_fill_bar) else max(stop, o)
            px = base * (1 + slip_s)
        return Fill(True, "stop", entry_idx, j, entry, px, gap_until(j), i_tgt is not None and i_tgt == i_stop)
    if i_tgt is not None:
        j = k + i_tgt
        o = o_arr[j]
        px = max(target, o) if side == 1 else min(target, o)
        return Fill(True, "target", entry_idx, j, entry, px, gap_until(j))
    if end < n:
        px = ex.bid_o[end] * (1 - slip_m) if side == 1 else ex.ask_o[end] * (1 + slip_m)
        return Fill(True, "time", entry_idx, end, entry, px, gap_until(end))
    last = n - 1
    px = ex.bid_c[last] if side == 1 else ex.ask_c[last]
    return Fill(True, "end_of_data", entry_idx, last, entry, px, gap_until(last))
