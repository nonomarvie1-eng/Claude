"""Cartographie causale des niveaux de liquidité (PROXYS : aucune observation d'ordres réels).

Chaque niveau possède : type, prix, sens attendu de réaction (+1 support, −1 résistance),
date de création, date de DISPONIBILITÉ réelle (aucune utilisation avant), origine,
statut et éventuelle date d'invalidation, plus la fenêtre de contact étudiée.

Les sessions sont définies en America/New_York (fuseau IANA, DST automatique), comme
l'exigent les documents ICT. Les documents visent surtout NQ/ES et le Forex : leur
application à BTC (marché 24 h/24) est une transposition [PROP].
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..features.core import atr, fvg, resample, swings
from ..timeutils import local_to_utc

NY = "America/New_York"


@dataclass
class Level:
    kind: str
    price: float
    expect: int                  # +1 : support attendu (approche par le haut) ; −1 : résistance
    created: pd.Timestamp
    avail: pd.Timestamp
    origin: str
    touch_from: pd.Timestamp
    touch_to: pd.Timestamp
    status: str = "active"
    invalidated: pd.Timestamp | None = None
    extra: dict = field(default_factory=dict)


class Market:
    """Données préparées d'un actif : M1 (prix de transaction), M5, H1 avec ATR14."""

    def __init__(self, sig_m1: pd.DataFrame):
        self.m1 = sig_m1.reset_index(drop=True)
        self.ts = self.m1["ts"].dt.as_unit("ns").astype("int64").to_numpy()
        self.o, self.h, self.l, self.c = (self.m1[k].to_numpy(float) for k in "ohlc")
        self.m5 = resample(sig_m1, 5)
        self.m5["atr14"] = atr(self.m5["h"].to_numpy(), self.m5["l"].to_numpy(), self.m5["c"].to_numpy(), 14)
        self.m5_avail = self.m5["avail"].dt.as_unit("ns").astype("int64").to_numpy()
        self.m5_ts = self.m5["ts"].dt.as_unit("ns").astype("int64").to_numpy()
        self.h1 = resample(sig_m1, 60)
        self.h1["atr14"] = atr(self.h1["h"].to_numpy(), self.h1["l"].to_numpy(), self.h1["c"].to_numpy(), 14)
        self.h1_avail = self.h1["avail"].dt.as_unit("ns").astype("int64").to_numpy()
        local = sig_m1["ts"].dt.tz_convert(NY)
        self.ny_days = sorted({pd.Timestamp(d) for d in local.dt.date.unique()})

    def idx(self, t) -> int:
        return int(np.searchsorted(self.ts, pd.Timestamp(t).value, side="left"))

    def atr_h1_at(self, t) -> float:
        """ATR14 H1 de la dernière bougie H1 CLOSE à l'instant t."""
        k = int(np.searchsorted(self.h1_avail, pd.Timestamp(t).value, side="right")) - 1
        return float(self.h1["atr14"].iat[k]) if k >= 0 else np.nan

    def window_hl(self, a: pd.Timestamp, b: pd.Timestamp, min_cov: float = 0.9):
        i, j = self.idx(a), self.idx(b)
        exp = (b - a) / pd.Timedelta(minutes=1)
        if j - i < min_cov * exp or j <= i:
            return None
        return float(self.h[i:j].max()), float(self.l[i:j].min())


def ny(day, hm):
    return local_to_utc(day, hm, NY)


# ---------------------------------------------------------------------------
# Niveaux de jour, de semaine et de session
# ---------------------------------------------------------------------------
def pd_levels(mk: Market, horizon_h=24) -> list[Level]:
    out = []
    for d in mk.ny_days:
        a, b = ny(d, "00:00"), ny(d + pd.Timedelta(days=1), "00:00")
        hl = mk.window_hl(a, b)
        if hl is None:
            continue
        H = pd.Timedelta(hours=horizon_h)
        out.append(Level("PDH", hl[0], -1, a, b, "jour NY précédent", b, b + H))
        out.append(Level("PDL", hl[1], +1, a, b, "jour NY précédent", b, b + H))
    return out


def pw_levels(mk: Market, horizon_h=48) -> list[Level]:
    out = []
    mondays = [d for d in mk.ny_days if d.dayofweek == 0]
    for d in mondays:
        a, b = ny(d, "00:00"), ny(d + pd.Timedelta(days=7), "00:00")
        hl = mk.window_hl(a, b)
        if hl is None:
            continue
        H = pd.Timedelta(hours=horizon_h)
        out.append(Level("PWH", hl[0], -1, a, b, "semaine NY précédente", b, b + H))
        out.append(Level("PWL", hl[1], +1, a, b, "semaine NY précédente", b, b + H))
    return out


def session_levels(mk: Market, start: str, end: str, tag: str, touch_day_offset: int,
                   touch_start: str, touch_end: str) -> list[Level]:
    """Extrêmes de la fenêtre [start, end) NY du jour d ; contact étudié le jour d + offset
    entre touch_start et touch_end (NY), jamais avant la fin de la fenêtre."""
    out = []
    for d in mk.ny_days:
        a, b = ny(d, start), ny(d, end)
        hl = mk.window_hl(a, b)
        if hl is None:
            continue
        td = d + pd.Timedelta(days=touch_day_offset)
        t0, t1 = max(b, ny(td, touch_start)), ny(td, touch_end)
        if t1 <= t0:
            continue
        out.append(Level(f"{tag}_H", hl[0], -1, a, b, tag, t0, t1))
        out.append(Level(f"{tag}_L", hl[1], +1, a, b, tag, t0, t1))
    return out


# ---------------------------------------------------------------------------
# Swings H1 confirmés, equal highs/lows, failure swings (LRL) / HRL
# ---------------------------------------------------------------------------
def swing_levels(mk: Market, left=2, right=2, horizon_h=48, eq_tol_atr=0.1) -> dict:
    h1 = mk.h1
    H, L = h1["h"].to_numpy(), h1["l"].to_numpy()
    sh, sl = swings(H, L, left, right)
    av = h1["avail"]
    hz = pd.Timedelta(hours=horizon_h)
    res = {"swing": [], "eq": [], "lrl": [], "hrl": []}
    for idxs, arr, expect, nm in ((sh, H, -1, "SH"), (sl, L, +1, "SL")):
        prev_price, prev_i = None, None
        for i in idxs:
            t_av = av.iat[i + right]
            a = float(h1["atr14"].iat[i + right])
            if not np.isfinite(a):
                prev_price, prev_i = arr[i], i
                continue
            lvl = Level(nm, float(arr[i]), expect, h1["ts"].iat[i], t_av, "swing H1 2/2", t_av, t_av + hz)
            res["swing"].append(lvl)
            if prev_price is not None:
                swept_prev = (arr[i] > prev_price) if expect == -1 else (arr[i] < prev_price)
                lvl2 = Level(("HRL" if swept_prev else "LRL") + "_" + nm, float(arr[i]), expect, h1["ts"].iat[i], t_av,
                             "failure swing" if not swept_prev else "swing ayant balayé le précédent", t_av, t_av + hz)
                (res["hrl"] if swept_prev else res["lrl"]).append(lvl2)
                # relative equal : précédent swing du même côté non balayé entre-temps et à moins de tol
                seg_max = H[prev_i + 1:i].max() if expect == -1 and i > prev_i + 1 else None
                seg_min = L[prev_i + 1:i].min() if expect == +1 and i > prev_i + 1 else None
                unswept = (seg_max is None or seg_max < prev_price) if expect == -1 else (seg_min is None or seg_min > prev_price)
                if unswept and abs(arr[i] - prev_price) <= eq_tol_atr * a:
                    p = max(arr[i], prev_price) if expect == -1 else min(arr[i], prev_price)
                    res["eq"].append(Level("EQH" if expect == -1 else "EQL", float(p), expect, h1["ts"].iat[prev_i], t_av,
                                           "relative equal (2 swings H1)", t_av, t_av + hz))
            prev_price, prev_i = arr[i], i
    return res


# ---------------------------------------------------------------------------
# FVG M5, inversions, First Presented FVG with displacement, Unicorn
# ---------------------------------------------------------------------------
def fvg_records(mk: Market, min_size_atr=0.3) -> pd.DataFrame:
    m5 = mk.m5
    f = fvg(m5["h"].to_numpy(), m5["l"].to_numpy())
    a = m5["atr14"].to_numpy()
    rows = []
    c = m5["c"].to_numpy()
    for t in np.flatnonzero(f["fvg_bull"].to_numpy() | f["fvg_bear"].to_numpy()):
        lo, hi = f["fvg_lo"].iat[t], f["fvg_hi"].iat[t]
        if not np.isfinite(a[t]) or hi - lo < min_size_atr * a[t]:
            continue
        bull = bool(f["fvg_bull"].iat[t])
        # invalidation : première clôture M5 ultérieure au-delà du bord opposé
        later = c[t + 1:]
        hit = np.flatnonzero(later < lo) if bull else np.flatnonzero(later > hi)
        inv = int(t + 1 + hit[0]) if len(hit) else None
        rows.append({"t": int(t), "bull": bull, "lo": float(lo), "hi": float(hi), "ce": float((lo + hi) / 2),
                     "created": m5["ts"].iat[t - 2], "avail": m5["avail"].iat[t], "inv_bar": inv,
                     "invalidated": m5["avail"].iat[inv] if inv is not None else None})
    return pd.DataFrame(rows)


def fvg_levels(mk: Market, recs: pd.DataFrame, horizon_h=24) -> list[Level]:
    hz = pd.Timedelta(hours=horizon_h)
    out = []
    for r in recs.itertuples():
        out.append(Level("FVG_BULL" if r.bull else "FVG_BEAR", r.ce, +1 if r.bull else -1, r.created, r.avail,
                         "FVG M5 (CE)", r.avail, r.avail + hz, invalidated=r.invalidated,
                         extra={"lo": r.lo, "hi": r.hi, "hour_ny": r.avail.tz_convert(NY).hour,
                                "form_hour_ny": (r.avail - pd.Timedelta(minutes=5)).tz_convert(NY).hour,
                                "created_hour_ny": r.created.tz_convert(NY).hour, "t": r.t}))
    return out


def ifvg_levels(mk: Market, recs: pd.DataFrame, horizon_h=24) -> list[Level]:
    hz = pd.Timedelta(hours=horizon_h)
    out = []
    for r in recs.itertuples():
        if r.invalidated is None or pd.isna(r.invalidated):
            continue
        # FVG haussier invalidé → résistance ; baissier invalidé → support
        out.append(Level("IFVG_BEAR" if r.bull else "IFVG_BULL", r.ce, -1 if r.bull else +1, r.avail, r.invalidated,
                         "FVG M5 inversé", r.invalidated, r.invalidated + hz))
    return out


def fpfvg_split(mk: Market, recs: pd.DataFrame, lookback=12, horizon_h=24):
    """Premier FVG après 09:30 NY avec déplacement (bougie centrale au-delà de l'extrême des
    `lookback` bougies précédentes) ; contrôles = autres FVG du même jour NY, même sens, après 09:30."""
    m5 = mk.m5
    H, L = m5["h"].to_numpy(), m5["l"].to_numpy()
    hz = pd.Timedelta(hours=horizon_h)
    recs = recs.copy()
    recs["day"] = recs["avail"].dt.tz_convert(NY).dt.date
    first, ctrl = [], []
    for day, g in recs.groupby("day"):
        t930 = ny(pd.Timestamp(day), "09:30")
        g = g[g["created"] >= t930].sort_values("t")
        fp = None
        for r in g.itertuples():
            m = r.t - 1
            if m - lookback < 0:
                continue
            disp = H[m] > H[m - lookback:m].max() if r.bull else L[m] < L[m - lookback:m].min()
            if disp:
                fp = r
                break
        if fp is None:
            continue
        mk_lvl = lambda r: Level("FPFVG_D" if r is fp else "FVG_SAMEDAY", r.ce, +1 if r.bull else -1, r.created, r.avail,
                                 "first presented FVG with displacement" if r is fp else "autre FVG du jour",
                                 r.avail, r.avail + hz)
        first.append(mk_lvl(fp))
        for r in g.itertuples():
            if r.t != fp.t and r.bull == fp.bull:
                ctrl.append(mk_lvl(r))
    return first, ctrl


def unicorn_levels(mk: Market, recs: pd.DataFrame, left=2, right=2, horizon_h=24, max_bars=60) -> list[Level]:
    """Breaker haussier : swing bas L1, swing haut H1, plus bas L2 < L1 (balayage), puis clôture
    > H1 (déplacement). Bougie breaker = dernière bougie haussière avant la baisse vers L2.
    Unicorn = FVG haussier formé entre L2 et la clôture > H1 et chevauchant la bougie breaker.
    Disponible à la plus tardive des deux confirmations. Symétrique en baissier."""
    m5 = mk.m5
    O, H, L, C = (m5[k].to_numpy() for k in ("o", "h", "l", "c"))
    sh, sl = swings(H, L, left, right)
    hz = pd.Timedelta(hours=horizon_h)
    out = []
    by_t = {int(r.t): r for r in recs.itertuples()}
    for bull in (True, False):
        lows, highs = (sl, sh) if bull else (sh, sl)
        ext = L if bull else H
        opp = H if bull else L
        for a_i, b_i in zip(lows[:-1], lows[1:]):
            # L1 = a_i, L2 = b_i (plus bas plus bas en haussier)
            if not ((ext[b_i] < ext[a_i]) if bull else (ext[b_i] > ext[a_i])):
                continue
            mids = highs[(highs > a_i) & (highs < b_i)]
            if len(mids) == 0:
                continue
            h_i = mids[-1]
            lvl_h = opp[h_i]
            conf = b_i + right
            end = min(len(C), b_i + max_bars)
            brk = np.flatnonzero((C[conf:end] > lvl_h) if bull else (C[conf:end] < lvl_h))
            if len(brk) == 0:
                continue
            k_brk = conf + int(brk[0])
            seg = np.arange(h_i, b_i)
            cand = seg[(C[seg] > O[seg])] if bull else seg[(C[seg] < O[seg])]
            if len(cand) == 0:
                continue
            bc = int(cand[-1])
            z_lo, z_hi = L[bc], H[bc]
            for t in range(b_i + 2, k_brk + 1):
                r = by_t.get(t)
                if r is None or r.bull != bull:
                    continue
                o_lo, o_hi = max(z_lo, r.lo), min(z_hi, r.hi)
                if o_hi <= o_lo:
                    continue
                t_av = max(m5["avail"].iat[k_brk], r.avail)
                out.append(Level("UNICORN_BULL" if bull else "UNICORN_BEAR", float((o_lo + o_hi) / 2), +1 if bull else -1,
                                 m5["ts"].iat[a_i], t_av, "breaker + FVG chevauchant", t_av, t_av + hz))
                break
    return out
