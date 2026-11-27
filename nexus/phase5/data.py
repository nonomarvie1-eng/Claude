"""Données d'indices de la phase 5 : Kenneth R. French Data Library (recherche, citation, pas de
redistribution ; données dérivées de CRSP).

Les fichiers contiennent tout l'historique jusqu'à la dernière mise à jour. Pour respecter les
périodes verrouillées, toute observation >= fin de la période de développement est écartée dès la
lecture, et seule la partie autorisée est stockée (Parquet, non versionné). Le fichier brut est
supprimé après extraction, son empreinte SHA-256 est conservée.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile

import numpy as np
import pandas as pd

from ..config import DATA_DIR, DEV
from ..data.http import fetch

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES = {"US": "F-F_Research_Data_Factors_daily_CSV.zip", "Europe": "Europe_3_Factors_Daily_CSV.zip",
         "Japan": "Japan_3_Factors_Daily_CSV.zip", "AsiaPacExJapan": "Asia_Pacific_ex_Japan_3_Factors_Daily_CSV.zip"}
STORE = DATA_DIR / "french"


def parse(blob: bytes, cutoff=DEV[1]) -> pd.DataFrame:
    """Section quotidienne : lignes « AAAAMMJJ, Mkt-RF, SMB, HML, RF » (en %), s'arrête à la 1re ligne non conforme."""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        txt = z.read(z.namelist()[0]).decode("latin-1")
    rows, started = [], False
    for line in txt.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5 and len(parts[0]) == 8 and parts[0].isdigit():
            started = True
            rows.append(parts[:5])
        elif started:
            break
    df = pd.DataFrame(rows, columns=["date", "mkt_rf", "smb", "hml", "rf"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", utc=True)
    for c in ("mkt_rf", "smb", "hml", "rf"):
        df[c] = df[c].astype(float) / 100.0
    df = df[df["date"] < cutoff].reset_index(drop=True)          # verrou : rien après la période de dév.
    df["ret"] = df["mkt_rf"] + df["rf"]
    return df[["date", "ret", "rf"]]


def download_all() -> dict:
    STORE.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for market, fname in FILES.items():
        blob = fetch(BASE + fname)
        if blob is None:
            raise FileNotFoundError(fname)
        df = parse(blob)
        df.to_parquet(STORE / f"{market}.parquet", index=False)
        manifest[market] = {"file": fname, "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                            "first": str(df["date"].min().date()), "last_kept": str(df["date"].max().date()), "rows": len(df)}
    (STORE / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def load(market: str) -> pd.DataFrame:
    """Indice de rendement total (base 100) et taux sans risque quotidien."""
    df = pd.read_parquet(STORE / f"{market}.parquet")
    if df["date"].max() >= DEV[1]:
        raise PermissionError("données postérieures à la période de développement : refus")
    df = df.set_index("date")
    df["close"] = 100 * np.cumprod(1 + df["ret"].to_numpy())
    return df
