"""Téléchargement des données historiques NEXUS (cloud ou Windows).

Exemples :
    python scripts/download_data.py binance BTCUSDT 2020-01 2026-07
    python scripts/download_data.py dukascopy EURUSD 2020-01-01 2026-07-01

Reprend automatiquement là où il s'est arrêté (cache dans data/raw/).
Bibliothèque standard + numpy/pandas uniquement.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nexus.data import binance, dukascopy  # noqa: E402


def main(argv: list[str]) -> None:
    if len(argv) != 4:
        print(__doc__)
        raise SystemExit(2)
    source, symbol, start, end = argv
    if source == "binance":
        print(binance.download_range(symbol, start, end))
    elif source == "dukascopy":
        print(dukascopy.download_range(symbol, date.fromisoformat(start), date.fromisoformat(end)))
    else:
        raise SystemExit(f"source inconnue : {source}")


if __name__ == "__main__":
    main(sys.argv[1:])
