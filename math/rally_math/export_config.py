"""Export the rules to shared/game-config.json (consumed by the TS frontend)
and parity fixtures (recorded stops + Python books) for the TS engine tests."""

from __future__ import annotations

import json
import os

import numpy as np

from . import config as C
from .engine import make_book, numpy_drawer, play_round, list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))


def game_config(exact: dict | None) -> dict:
    base, free = C.base_reels(), C.free_reels()
    cfg = {
        "gameId": C.GAME_ID,
        "name": C.GAME_NAME,
        "mathVersion": C.MATH_VERSION,
        "reels": C.NUM_REELS,
        "rows": C.NUM_ROWS,
        "symbols": C.SYMBOLS,
        "symbolInfo": C.SYMBOL_INFO,
        "paytable": {s: {str(k): v * 10 for k, v in p.items()} for s, p in C.PAYTABLE.items()},
        "scatterPay": {str(k): v * 10 for k, v in C.SCATTER_PAY.items()},
        "fsAward": {str(k): v for k, v in C.FS_AWARD.items()},
        "fsRetrigger": C.FS_RETRIGGER,
        "fsMaxRemaining": C.FS_MAX_REMAINING,
        "rallyLadder": C.RALLY_LADDER,
        "wincapX": C.WINCAP_X,
        "paylines": C.PAYLINES,
        "winLevels": C.WIN_LEVELS[:-1] + [{"name": "max", "min": C.WINCAP_X}],
        "reelStrips": {
            "base": [[C.SYMBOLS[s] for s in strip] for strip in base.strips],
            "free": [[C.SYMBOLS[s] for s in strip] for strip in free.strips],
        },
        "units": "pay values are payoutMultiplier units: bet multiple x100",
    }
    if exact:
        cfg["stats"] = {
            "rtp": exact["rtp"],
            "hitFrequency": exact["hit_frequency"],
            "bonusOneIn": exact["trigger_1_in"],
            "stdDev": exact["std_dev"],
            "method": exact["method"],
        }
    return cfg


def fixtures(n: int, seed: int) -> list[dict]:
    """Rounds with recorded stops: TS must reproduce identical books."""
    base, free = C.base_reels(), C.free_reels()
    rng = np.random.Generator(np.random.PCG64(seed))
    out = []
    # make sure bonus rounds are represented: half normal, half forced triggers
    i = 0
    while len(out) < n:
        res = play_round(numpy_drawer(rng), base, free, record_events=True)
        want_bonus = len(out) % 2 == 1
        if want_bonus and not res.triggered:
            i += 1
            continue
        # replay check in python itself
        res2 = play_round(list_drawer(res.stops), base, free, record_events=True)
        assert res2.events == res.events
        out.append({"stops": res.stops, "book": make_book(len(out) + 1, res)})
    return out


def main() -> None:
    exact_path = os.path.join(ROOT, "math", "reports", "exact.json")
    exact = json.load(open(exact_path)) if os.path.exists(exact_path) else None
    os.makedirs(os.path.join(ROOT, "shared"), exist_ok=True)
    with open(os.path.join(ROOT, "shared", "game-config.json"), "w", encoding="utf-8") as f:
        json.dump(game_config(exact), f, indent=1)
    with open(os.path.join(ROOT, "shared", "parity-fixtures.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures(200, 4242), f, separators=(",", ":"))
    print("wrote shared/game-config.json and shared/parity-fixtures.json")


if __name__ == "__main__":
    main()
