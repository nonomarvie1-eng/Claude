"""Primitives causales.

Règle : chaque grandeur calculée pour la bougie i n'utilise que les bougies <= i,
SAUF les pivots, qui ne sont connus qu'à la clôture de la bougie i+R : la fonction
`swings` renvoie explicitement l'indice de disponibilité.

Les bougies sont horodatées à l'OUVERTURE (`ts`) ; une information issue de la
bougie i est disponible à `ts[i] + durée` (colonne `avail`).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Rééchantillonnage
# ---------------------------------------------------------------------------
def signal_frame(m1: pd.DataFrame) -> pd.DataFrame:
    """Prix de signal M1 : mid si bid/ask disponibles, sinon prix de transaction."""
    if "bid_o" in m1.columns:
        out = pd.DataFrame({"ts": m1["ts"]})
        for k in "ohlc":
            out[k] = (m1[f"bid_{k}"] + m1[f"ask_{k}"]) / 2.0
        out["volume"] = m1["bid_tickvol"] + m1["ask_tickvol"]  # volume de cotations (tick volume)
        return out
    cols = ["ts", "o", "h", "l", "c"] + (["volume"] if "volume" in m1.columns else [])
    return m1[cols].copy()


def resample(sig_m1: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """Agrège en bougies de `minutes`, étiquetées à l'ouverture, avec `avail` = ouverture + durée.

    Une bougie n'est créée que si au moins une minute existe. `n_m1` permet de
    juger la complétude.
    """
    s = sig_m1.set_index("ts")
    rule = f"{minutes}min"
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    if "volume" in s.columns:
        agg["volume"] = "sum"
    out = s.resample(rule, label="left", closed="left").agg(agg)
    out["n_m1"] = s["c"].resample(rule, label="left", closed="left").count()
    out = out[out["n_m1"] > 0].reset_index()
    out["avail"] = out["ts"] + pd.Timedelta(minutes=minutes)
    return out


# ---------------------------------------------------------------------------
# Indicateurs
# ---------------------------------------------------------------------------
def ema(x: np.ndarray, n: int) -> np.ndarray:
    """EMA amorcée par la SMA des n premières valeurs ; NaN avant."""
    x = np.asarray(x, dtype=float)
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def atr(h: np.ndarray, l: np.ndarray, c: np.ndarray, n: int = 14) -> np.ndarray:
    """ATR de Wilder ; NaN pendant l'amorçage."""
    h, l, c = (np.asarray(v, dtype=float) for v in (h, l, c))
    prev_c = np.concatenate([[np.nan], c[:-1]])
    tr = np.nanmax(np.vstack([h - l, np.abs(h - prev_c), np.abs(l - prev_c)]), axis=0)
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = out[i - 1] + (tr[i] - out[i - 1]) / n
    return out


# ---------------------------------------------------------------------------
# Pivots
# ---------------------------------------------------------------------------
def swings(h: np.ndarray, l: np.ndarray, left: int = 1, right: int = 1):
    """Pivots fractals. Renvoie (sh_idx, sl_idx) : tableaux d'indices des bougies
    centrales. Un pivot en i n'est DISPONIBLE qu'à la clôture de i+right.

    Swing High : H_i > max(H[i-left:i]) et H_i >= max(H[i+1:i+right+1]).
    Swing Low  : L_i < min(L[i-left:i]) et L_i <= min(L[i+1:i+right+1]).
    """
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    n = len(h)
    sh, sl = [], []
    for i in range(left, n - right):
        if h[i] > h[i - left:i].max() and h[i] >= h[i + 1:i + right + 1].max():
            sh.append(i)
        if l[i] < l[i - left:i].min() and l[i] <= l[i + 1:i + right + 1].min():
            sl.append(i)
    return np.array(sh, dtype=int), np.array(sl, dtype=int)


def last_confirmed_level(n: int, idx: np.ndarray, values: np.ndarray, right: int) -> np.ndarray:
    """Pour chaque bougie t, niveau du dernier pivot confirmé au plus tard à t
    (pivot en i confirmé à i+right). NaN si aucun."""
    out = np.full(n, np.nan)
    for i in idx:
        j = i + right
        if j < n:
            out[j] = values[i]
    # propagation vers l'avant (dernier connu)
    s = pd.Series(out).ffill().to_numpy()
    return s


# ---------------------------------------------------------------------------
# Structure : BOS / CHoCH (mode clôture)
# ---------------------------------------------------------------------------
def structure_events(o, h, l, c, left: int = 2, right: int = 2) -> pd.DataFrame:
    """Machine à états causale. Pour chaque bougie t (connue à sa clôture) :
    state (+1 haussier, -1 baissier, 0 indéfini), bos (+1/-1/0), choch (+1/-1/0).

    - BOS haussier : état haussier et clôture > dernier swing high confirmé non consommé.
    - CHoCH baissier : état haussier et clôture < swing low protégé (dernier swing low
      confirmé avant le BOS courant). Symétrique.
    - Initialisation : premier franchissement en clôture d'un swing confirmé.
    """
    h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    n = len(c)
    sh_idx, sl_idx = swings(h, l, left, right)
    conf_sh = {i + right: h[i] for i in sh_idx}
    conf_sl = {i + right: l[i] for i in sl_idx}
    state = np.zeros(n, int); bos = np.zeros(n, int); choch = np.zeros(n, int)
    cur = 0
    last_sh = np.nan; last_sl = np.nan
    sh_used = True; sl_used = True
    protected_low = np.nan; protected_high = np.nan
    for t in range(n):
        # les pivots confirmés à t sont utilisables à partir de la clôture de t
        if t in conf_sh:
            last_sh = conf_sh[t]; sh_used = False
        if t in conf_sl:
            last_sl = conf_sl[t]; sl_used = False
        if cur >= 0 and not sh_used and c[t] > last_sh:
            if cur == 0:
                cur = 1; choch[t] = 1
            else:
                bos[t] = 1
            sh_used = True
            protected_low = last_sl
        elif cur <= 0 and not sl_used and c[t] < last_sl:
            if cur == 0:
                cur = -1; choch[t] = -1
            else:
                bos[t] = -1
            sl_used = True
            protected_high = last_sh
        elif cur == 1 and not np.isnan(protected_low) and c[t] < protected_low:
            cur = -1; choch[t] = -1
            protected_high = last_sh; sl_used = True
        elif cur == -1 and not np.isnan(protected_high) and c[t] > protected_high:
            cur = 1; choch[t] = 1
            protected_low = last_sl; sh_used = True
        state[t] = cur
    return pd.DataFrame({"state": state, "bos": bos, "choch": choch})


# ---------------------------------------------------------------------------
# Fair Value Gaps
# ---------------------------------------------------------------------------
def fvg(h, l) -> pd.DataFrame:
    """FVG sur (t-2, t-1, t), connu à la clôture de t.
    Haussier : L_t > H_{t-2} → zone [H_{t-2}, L_t]. Baissier : H_t < L_{t-2} → [H_t, L_{t-2}]."""
    h = np.asarray(h, float); l = np.asarray(l, float)
    n = len(h)
    bull = np.zeros(n, bool); bear = np.zeros(n, bool)
    lo = np.full(n, np.nan); hi = np.full(n, np.nan)
    bull[2:] = l[2:] > h[:-2]
    bear[2:] = h[2:] < l[:-2]
    lo[2:] = np.where(bull[2:], h[:-2], np.where(bear[2:], h[2:], np.nan))
    hi[2:] = np.where(bull[2:], l[2:], np.where(bear[2:], l[:-2], np.nan))
    return pd.DataFrame({"fvg_bull": bull, "fvg_bear": bear, "fvg_lo": lo, "fvg_hi": hi})


# ---------------------------------------------------------------------------
# Range de session
# ---------------------------------------------------------------------------
def session_range(bars: pd.DataFrame, start_utc: pd.Timestamp, end_utc: pd.Timestamp,
                  bar_minutes: int, min_coverage: float = 0.9):
    """Plus haut / plus bas des bougies entièrement contenues dans [start, end).
    Disponible à `end_utc`. Renvoie None si couverture insuffisante."""
    m = (bars["ts"] >= start_utc) & (bars["avail"] <= end_utc)
    sub = bars.loc[m]
    expected = (end_utc - start_utc) / pd.Timedelta(minutes=bar_minutes)
    if expected <= 0 or len(sub) < min_coverage * expected:
        return None
    return float(sub["h"].max()), float(sub["l"].min())
