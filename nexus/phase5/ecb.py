"""Taux de référence de la BCE (eurofxref-hist). Réutilisation libre en citant « Source : ECB statistics »,
sans altération des données publiées (les taux croisés sont un calcul dérivé, signalé comme tel).
Coupé à la fin de la période de développement ; le fichier brut n'est pas conservé."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile

import pandas as pd

from ..config import DATA_DIR, DEV
from ..data.http import fetch

URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
STORE = DATA_DIR / "ecb"


def download() -> dict:
    blob = fetch(URL)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    df["Date"] = pd.to_datetime(df["Date"], utc=True)
    df = df[df["Date"] < DEV[1]][["Date", "USD", "JPY"]].dropna().sort_values("Date").reset_index(drop=True)
    STORE.mkdir(parents=True, exist_ok=True)
    df.to_parquet(STORE / "eurofxref_usd_jpy.parquet", index=False)
    man = {"url": URL, "sha256": hashlib.sha256(blob).hexdigest(), "first": str(df.Date.min().date()),
           "last_kept": str(df.Date.max().date()), "rows": len(df), "source": "ECB statistics"}
    (STORE / "manifest.json").write_text(json.dumps(man, indent=2))
    return man


def usdjpy() -> pd.Series:
    df = pd.read_parquet(STORE / "eurofxref_usd_jpy.parquet").set_index("Date")
    if df.index.max() >= DEV[1]:
        raise PermissionError("données postérieures à la période de développement : refus")
    return (df["JPY"] / df["USD"]).rename("USDJPY")      # JPY par USD, calcul dérivé
