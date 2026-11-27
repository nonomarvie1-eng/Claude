"""Données de la phase 4 (Binance Vision, recherche personnelle uniquement).

- Klines au comptant 1d et 1h (archives mensuelles, sommes SHA-256 vérifiées).
- Taux de financement des perpétuels USDT-M (archives mensuelles fundingRate).

Seules la période de développement et l'historique antérieur (amorçage, univers, stops)
sont téléchargés : aucune archive postérieure au 2023-06 n'est demandée ici.
"""
from __future__ import annotations

import hashlib
import io
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import DEV, RAW_DIR
from ..data import binance
from ..data.http import fetch
from ..data.store import load_bars, save_bars

SPOT = "https://data.binance.vision/data/spot/monthly/klines"
FUND = "https://data.binance.vision/data/futures/um/monthly/fundingRate"

# Même actif, ticker différent selon la date (renommage par Binance). Essayés dans l'ordre, mois par mois.
ALIASES = {"BCHUSDT": ["BCHUSDT", "BCHABCUSDT"]}
LAST_MONTH = "2023-07"   # borne exclusive : rien après la période de développement


def _get(url: str, path: Path) -> bool:
    if path.exists():
        return True
    blob = fetch(url)
    if blob is None:
        return False
    chk = fetch(url + ".CHECKSUM")
    if chk is None or chk.decode().split()[0] != hashlib.sha256(blob).hexdigest():
        raise RuntimeError(f"somme de contrôle invalide ou absente : {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    time.sleep(0.15)
    return True


def spot_month_path(symbol: str, ticker: str, y: int, m: int, interval: str) -> Path:
    return RAW_DIR / "binance_p4" / symbol / interval / f"{ticker}-{interval}-{y:04d}-{m:02d}.zip"


def download_spot(symbol: str, start: str, end: str, interval: str) -> dict:
    """Télécharge chaque mois sous tous les tickers de l'actif (un renommage peut tomber en cours de mois)."""
    if pd.Period(end, "M") > pd.Period(LAST_MONTH, "M"):
        raise PermissionError("phase 4 : téléchargement limité à la période de développement")
    got, missing = 0, []
    for y, m in binance.months(start, end):
        ok = False
        for t in ALIASES.get(symbol, [symbol]):
            url = f"{SPOT}/{t}/{interval}/{t}-{interval}-{y:04d}-{m:02d}.zip"
            ok = _get(url, spot_month_path(symbol, t, y, m, interval)) or ok
        got += ok
        if not ok:
            missing.append(f"{y}-{m:02d}")
    return {"months": got, "missing": missing}


def read_spot(symbol: str, interval: str, start: str, end: str) -> pd.DataFrame:
    """Fusionne les tickers d'un même actif : prix du ticker prioritaire (1er de ALIASES) quand
    plusieurs cotent la même bougie, volumes additionnés."""
    frames = []
    tickers = ALIASES.get(symbol, [symbol])
    for y, m in binance.months(start, end):
        for rank, t in enumerate(tickers):
            p = spot_month_path(symbol, t, y, m, interval)
            if p.exists():
                d = binance.read_month(p)
                with zipfile.ZipFile(p) as z:
                    raw = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None, names=binance.COLS)
                d["quote_volume"] = raw["quote_v"].astype(float).to_numpy()
                d["_rank"] = rank
                frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["ts", "o", "h", "l", "c", "volume", "trades", "quote_volume"])
    d = pd.concat(frames, ignore_index=True).sort_values(["ts", "_rank"])
    vol = d.groupby("ts")[["volume", "trades", "quote_volume"]].sum()
    px = d.drop_duplicates("ts", keep="first").set_index("ts")[["o", "h", "l", "c"]]
    return px.join(vol).reset_index()[["ts", "o", "h", "l", "c", "volume", "trades", "quote_volume"]]


def download_funding(symbol: str, start: str, end: str) -> dict:
    if pd.Period(end, "M") > pd.Period(LAST_MONTH, "M"):
        raise PermissionError("phase 4 : téléchargement limité à la période de développement")
    got, missing = 0, []
    for y, m in binance.months(start, end):
        p = RAW_DIR / "binance_p4" / symbol / "funding" / f"{symbol}-fundingRate-{y:04d}-{m:02d}.zip"
        ok = _get(f"{FUND}/{symbol}/{symbol}-fundingRate-{y:04d}-{m:02d}.zip", p)
        got += ok
        if not ok:
            missing.append(f"{y}-{m:02d}")
    return {"months": got, "missing": missing}


def read_funding(symbol: str, start: str, end: str) -> pd.DataFrame:
    frames = []
    for y, m in binance.months(start, end):
        p = RAW_DIR / "binance_p4" / symbol / "funding" / f"{symbol}-fundingRate-{y:04d}-{m:02d}.zip"
        if p.exists():
            with zipfile.ZipFile(p) as z:
                d = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
            frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["ts", "rate"])
    d = pd.concat(frames, ignore_index=True)
    # Horodatage arrondi à l'heure (certains enregistrements portent quelques millisecondes).
    ts = pd.to_datetime(d["calc_time"].astype(np.int64), unit="ms", utc=True).dt.round("h")
    return pd.DataFrame({"ts": ts, "rate": d["last_funding_rate"].astype(float)}).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)


def store_h1(symbol: str, start: str = "2019-01", end: str = LAST_MONTH) -> int:
    """Écrit les bougies H1 dans le magasin Parquet (verrous de période hérités de store.py)."""
    df = read_spot(symbol, "1h", start, end)
    df = df[df["ts"] < DEV[1]]
    save_bars(f"{symbol}_1h", df.drop(columns=["quote_volume"]))
    return len(df)


def load_h1(symbol: str, start="2019-01-01", end=None) -> pd.DataFrame:
    return load_bars(f"{symbol}_1h", pd.Timestamp(start, tz="UTC"), end or DEV[1])


def daily_from_h1(h1: pd.DataFrame) -> pd.DataFrame:
    """Bougies D1 UTC reconstruites depuis H1 (identiques aux bougies D1 de l'exchange à
    l'agrégation près ; un jour sans aucune bougie H1 est absent)."""
    g = h1.set_index("ts").resample("1D", label="left", closed="left")
    d = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last(),
                      "n_h1": g["c"].count()}).dropna(subset=["c"])
    return d
