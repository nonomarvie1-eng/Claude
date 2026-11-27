"""Construit les fichiers Parquet M1 depuis le cache brut et écrit un rapport qualité.

    python scripts/build_bars.py BTCUSDT
    python scripts/build_bars.py EURUSD 2019-12-01 2023-07-01

Pour la période du test final verrouillé, le rapport ne contient que la couverture.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from nexus.config import FINAL_TEST, ROOT  # noqa: E402
from nexus.data import binance, dukascopy  # noqa: E402
from nexus.data.quality import quality_report  # noqa: E402
from nexus.data.store import save_bars  # noqa: E402


def main(argv):
    symbol = argv[0]
    if symbol == "BTCUSDT":
        df = binance.build_bars(symbol, argv[1] if len(argv) > 1 else "2020-01", argv[2] if len(argv) > 2 else "2026-07")
        market = "crypto"
    else:
        df = dukascopy.build_bars(symbol, date.fromisoformat(argv[1]), date.fromisoformat(argv[2]))
        market = "fx"
    save_bars(symbol, df)
    f0, f1 = FINAL_TEST
    open_part = df[df["ts"] < f0]
    locked = df[(df["ts"] >= f0) & (df["ts"] < f1)]
    rep = {"symbol": symbol, "source": "binance_data_vision" if market == "crypto" else "dukascopy_datafeed",
           "open_periods": quality_report(open_part, market=market)}
    if len(locked):
        rep["final_test_locked"] = quality_report(locked, market=market, coverage_only=True)
    out = ROOT / "reports" / "data_quality" / f"{symbol}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # fusion avec un rapport existant (constructions par morceaux)
    if out.exists():
        old = json.loads(out.read_text())
        old.setdefault("chunks", []).append(rep)
        rep = old
    out.write_text(json.dumps(rep, indent=2, default=str, ensure_ascii=False))
    print(json.dumps(rep, indent=2, default=str, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main(sys.argv[1:])
