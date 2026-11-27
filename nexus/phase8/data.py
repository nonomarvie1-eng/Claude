"""Klines perpétuels USDT-M 1h (Binance Vision, recherche personnelle §4.1). Développement seulement :
aucune archive postérieure au 2023-06 n'est demandée ni lue."""
from __future__ import annotations

import hashlib
import io
import time
import zipfile

import numpy as np
import pandas as pd

from ..config import DEV, RAW_DIR
from ..data import binance
from ..data.http import fetch
from ..data.store import load_bars, save_bars

BASE = "https://data.binance.vision/data/futures/um/monthly/klines"
LAST = "2023-07"


def path(sym, y, m):
    return RAW_DIR / "binance_p8" / sym / f"{sym}-1h-{y:04d}-{m:02d}.zip"


def download(sym: str, start="2019-09", end=LAST) -> dict:
    if pd.Period(end, "M") > pd.Period(LAST, "M"):
        raise PermissionError("développement seulement")
    got, missing = 0, []
    for y, m in binance.months(start, end):
        p = path(sym, y, m)
        if p.exists():
            got += 1
            continue
        url = f"{BASE}/{sym}/1h/{sym}-1h-{y:04d}-{m:02d}.zip"
        blob = fetch(url)
        if blob is None:
            missing.append(f"{y}-{m:02d}")
            continue
        chk = fetch(url + ".CHECKSUM")
        if chk is None or chk.decode().split()[0] != hashlib.sha256(blob).hexdigest():
            raise RuntimeError(f"somme de contrôle invalide : {url}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(blob)
        got += 1
        time.sleep(0.1)
    return {"months": got, "missing": missing}


def read_month(p) -> pd.DataFrame:
    with zipfile.ZipFile(p) as z:
        raw = z.read(z.namelist()[0])
    first = raw.split(b"\n", 1)[0]
    header = 0 if first[:1].isalpha() else None                 # les archives récentes ont une ligne d'en-tête
    d = pd.read_csv(io.BytesIO(raw), header=header)
    d = d.iloc[:, :6]
    d.columns = ["open_time", "o", "h", "l", "c", "volume"]
    t = d["open_time"].to_numpy(np.int64)
    unit = "us" if t.max() > 10**14 else "ms"
    return pd.DataFrame({"ts": pd.to_datetime(t, unit=unit, utc=True), "o": d.o.astype(float), "h": d.h.astype(float),
                         "l": d.l.astype(float), "c": d.c.astype(float), "volume": d.volume.astype(float)})


def store(sym: str) -> int:
    frames = [read_month(path(sym, y, m)) for y, m in binance.months("2019-09", LAST) if path(sym, y, m).exists()]
    df = pd.concat(frames).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df = df[df.ts < DEV[1]]
    save_bars(f"{sym}_perp1h", df)
    return len(df)


def load(sym: str) -> pd.DataFrame:
    return load_bars(f"{sym}_perp1h", pd.Timestamp("2019-09-01", tz="UTC"), DEV[1])
