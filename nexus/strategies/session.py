"""Stratégies fondées sur un range de session : NEXUS A (cassure), NEXUS B (fausse
cassure), référence SBA, et générateur d'entrées aléatoires appariées.

Toutes les décisions sont prises à la CLÔTURE d'une bougie M5 (instant `avail`) ;
l'exécution a lieu au plus tôt à l'ouverture de la minute suivante.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..features.core import atr, ema, resample, structure_events
from ..timeutils import SessionHypothesis, local_to_utc
from .base import Signal

SIG_TF = 5  # minutes


@dataclass
class SessionContext:
    """Bougies de signal et caractéristiques causales précalculées pour un actif."""
    m5: pd.DataFrame
    h1: pd.DataFrame
    d1_atr_prev: pd.Series     # ATR(14) journalier UTC des jours COMPLETS précédents, indexé par jour
    hyp: SessionHypothesis
    days: list

    @classmethod
    def build(cls, sig_m1: pd.DataFrame, hyp: SessionHypothesis) -> "SessionContext":
        m5 = resample(sig_m1, SIG_TF)
        m5["ema50"] = ema(m5["c"].to_numpy(), 50)
        m5["atr14"] = atr(m5["h"].to_numpy(), m5["l"].to_numpy(), m5["c"].to_numpy(), 14)
        st = structure_events(m5["o"].to_numpy(), m5["h"].to_numpy(), m5["l"].to_numpy(), m5["c"].to_numpy(), 2, 2)
        m5["choch"] = st["choch"].to_numpy()
        h1 = resample(sig_m1, 60)
        h1["ema100"] = ema(h1["c"].to_numpy(), 100)
        for f in (m5, h1):
            f["ts_ns"] = f["ts"].dt.as_unit("ns").astype("int64")
            f["avail_ns"] = f["avail"].dt.as_unit("ns").astype("int64")
        d1 = resample(sig_m1, 1440)
        d1_atr = pd.Series(atr(d1["h"].to_numpy(), d1["l"].to_numpy(), d1["c"].to_numpy(), 14),
                           index=d1["ts"].dt.date)
        d1_atr_prev = d1_atr.shift(1)  # ATR connu au début du jour = celui de la veille
        local = sig_m1["ts"].dt.tz_convert(hyp.tz)
        days = sorted({pd.Timestamp(d) for d in local.dt.date.unique()})
        return cls(m5, h1, d1_atr_prev, hyp, days)


def _window(ctx: SessionContext, day):
    h = ctx.hyp
    rs, re_ = local_to_utc(day, h.range_start, h.tz), local_to_utc(day, h.range_end, h.tz)
    ee, xt = local_to_utc(day, h.entry_end, h.tz), local_to_utc(day, h.exit_time, h.tz)
    ts = ctx.m5["ts_ns"].to_numpy(); av = ctx.m5["avail_ns"].to_numpy()
    i0 = int(np.searchsorted(ts, rs.value))
    i1 = int(np.searchsorted(av, re_.value, side="right"))
    j1 = int(np.searchsorted(av, ee.value, side="right"))
    return rs, re_, ee, xt, i0, i1, j1


def _range(ctx, i0, i1, rs, re_, min_cov=0.9):
    expected = (re_ - rs) / pd.Timedelta(minutes=SIG_TF)
    if i1 - i0 < min_cov * expected:
        return None
    sub = ctx.m5.iloc[i0:i1]
    return float(sub["h"].max()), float(sub["l"].min())


def _trend_ok(ctx: SessionContext, t_avail: pd.Timestamp, side: int) -> bool:
    """Filtre directionnel : clôture H1 complète la plus récente vs EMA100 H1."""
    av = ctx.h1["avail_ns"].to_numpy()
    k = int(np.searchsorted(av, t_avail.value, side="right")) - 1
    if k < 0:
        return False
    e = ctx.h1["ema100"].iat[k]
    if np.isnan(e):
        return False
    return (ctx.h1["c"].iat[k] > e) if side == 1 else (ctx.h1["c"].iat[k] < e)


def _compression_series(ctx: SessionContext) -> dict:
    """Largeur du range / ATR journalier de la veille, et sa médiane glissante
    sur les 60 jours PRÉCÉDENTS (causale)."""
    vals = {}
    for day in ctx.days:
        rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
        rg = _range(ctx, i0, i1, rs, re_)
        a = ctx.d1_atr_prev.get(re_.date(), np.nan)
        if rg is None or not np.isfinite(a) or a <= 0:
            continue
        vals[day] = (rg[0] - rg[1]) / a
    s = pd.Series(vals).sort_index()
    med = s.shift(1).rolling(60, min_periods=30).median()
    return {d: (s[d], med[d]) for d in s.index}


# ---------------------------------------------------------------------------
# NEXUS A — Session Breakout
# ---------------------------------------------------------------------------
def nexus_a(ctx: SessionContext, *, allow_short: bool, target_r: float | None = 2.0,
            confirm_buffer_atr: float = 0.0, trend_filter: bool = False,
            compression_filter: bool = False, entry_mode: str = "market",
            retest_expiry_min: int = 60) -> list[Signal]:
    comp = _compression_series(ctx) if compression_filter else None
    m5 = ctx.m5
    out = []
    for day in ctx.days:
        rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
        rg = _range(ctx, i0, i1, rs, re_)
        if rg is None:
            continue
        hi, lo = rg
        if comp is not None:
            v = comp.get(day)
            if v is None or not np.isfinite(v[1]) or v[0] > v[1]:
                continue
        mid = (hi + lo) / 2
        for i in range(i1, j1):
            c = m5["c"].iat[i]
            a = m5["atr14"].iat[i]
            buf = confirm_buffer_atr * (a if np.isfinite(a) else np.inf)
            side = 1 if c > hi + buf else (-1 if c < lo - buf else 0)
            if side == 0:
                continue
            # première cassure du jour seulement (dans un sens ou dans l'autre)
            if side == -1 and not allow_short:
                break
            t_av = m5["avail"].iat[i]
            if trend_filter and not _trend_ok(ctx, t_av, side):
                break
            tags = {"day": str(day.date()), "range_hi": hi, "range_lo": lo}
            if entry_mode == "market":
                out.append(Signal(avail=t_av, side=side, stop=mid, time_exit=xt, target_r=target_r,
                                  entry_est=c, tags=tags))
            else:  # retest : limite sur le niveau cassé
                lvl = hi if side == 1 else lo
                out.append(Signal(avail=t_av, side=side, stop=mid, time_exit=xt, target_r=target_r,
                                  entry_type="limit", limit_price=lvl, entry_est=lvl,
                                  expiry=t_av + pd.Timedelta(minutes=retest_expiry_min), tags=tags))
            break
    return out


# ---------------------------------------------------------------------------
# NEXUS B — Liquidity Reversal (fausse cassure du range)
# ---------------------------------------------------------------------------
def nexus_b(ctx: SessionContext, *, allow_short: bool, target: str = "mid",
            require_choch: bool = False, choch_window: int = 6) -> list[Signal]:
    """Sweep : bougie M5 dont la mèche dépasse un extrême du range et qui clôture
    à l'intérieur. Entrée à contre-sens. Stop au-delà de l'extrême balayé.
    target = "mid" (milieu du range) ou "2R"."""
    m5 = ctx.m5
    out = []
    for day in ctx.days:
        rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
        rg = _range(ctx, i0, i1, rs, re_)
        if rg is None:
            continue
        hi, lo = rg
        mid = (hi + lo) / 2
        ext_hi, ext_lo = hi, lo
        for i in range(i1, j1):
            h, l, c = m5["h"].iat[i], m5["l"].iat[i], m5["c"].iat[i]
            ext_hi = max(ext_hi, h); ext_lo = min(ext_lo, l)
            side = 0
            if h > hi and lo < c < hi:
                side, stop = -1, ext_hi
            elif l < lo and lo < c < hi:
                side, stop = 1, ext_lo
            if side == 0:
                # une clôture franche hors du range invalide le jour pour B
                if c > hi or c < lo:
                    break
                continue
            if side == -1 and not allow_short:
                break
            k = i
            if require_choch:
                ok = False
                for k in range(i, min(i + choch_window + 1, j1)):
                    if m5["choch"].iat[k] == side:
                        ok = True; break
                if not ok:
                    break
                c = m5["c"].iat[k]
                if (side == 1 and c <= stop) or (side == -1 and c >= stop):
                    break
            t_av = m5["avail"].iat[k]
            tags = {"day": str(day.date()), "range_hi": hi, "range_lo": lo}
            if target == "mid":
                if (side == 1 and c >= mid) or (side == -1 and c <= mid):
                    break  # plus de potentiel jusqu'au milieu
                out.append(Signal(avail=t_av, side=side, stop=stop, time_exit=xt, target=mid,
                                  entry_est=c, tags=tags))
            else:
                out.append(Signal(avail=t_av, side=side, stop=stop, time_exit=xt, target_r=2.0,
                                  entry_est=c, tags=tags))
            break
    return out


# ---------------------------------------------------------------------------
# Référence SBA (document) — stop EMA 50, TP 2R, sortie horaire
# ---------------------------------------------------------------------------
def sba_reference(ctx: SessionContext, *, allow_short: bool, target_r: float = 2.0,
                  ema_buffer_atr: float = 0.1, min_stop_atr: float = 0.5) -> list[Signal]:
    m5 = ctx.m5
    out = []
    for day in ctx.days:
        rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
        rg = _range(ctx, i0, i1, rs, re_)
        if rg is None:
            continue
        hi, lo = rg
        for i in range(i1, j1):
            c = m5["c"].iat[i]
            side = 1 if c > hi else (-1 if c < lo else 0)
            if side == 0:
                continue
            if side == -1 and not allow_short:
                break
            e, a = m5["ema50"].iat[i], m5["atr14"].iat[i]
            if not (np.isfinite(e) and np.isfinite(a)):
                break
            stop = e - side * ema_buffer_atr * a
            if side * (c - stop) < min_stop_atr * a:   # EMA du mauvais côté ou trop proche : trade ignoré
                break
            out.append(Signal(avail=m5["avail"].iat[i], side=side, stop=stop, time_exit=xt,
                              target_r=target_r, entry_est=c, tags={"day": str(day.date())}))
            break
    return out
