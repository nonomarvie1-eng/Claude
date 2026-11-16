"""Export the rules to shared/game-config.json (consumed by the TS frontend)
and parity fixtures (recorded stops + Python books) for the TS engine tests."""

from __future__ import annotations

import json
import os

import numpy as np

from . import config as C
from .engine import make_book, numpy_drawer, play_round, list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))


def _modes(exact: dict | None, mc: dict | None) -> dict:
    """Per bet mode: cost and the validated statistics shown to the player."""
    out = {}
    mcm = (mc or {}).get("modes", {})
    for name, cost in C.mode_costs().items():
        e = (exact or {}).get("modes", {}).get(name, {})
        m = mcm.get(name, {})
        out[name] = {
            "cost": cost,
            "kind": "buy" if name in C.BUY_SCATTERS else "spin",
            "scatters": C.BUY_SCATTERS.get(name),
            "level": C.bonus_level(C.BUY_SCATTERS[name]) if name in C.BUY_SCATTERS else None,
            "spins": C.FS_AWARD[C.BUY_SCATTERS[name]] if name in C.BUY_SCATTERS else None,
            "rtp": e.get("rtp"),
            "bonusOneIn": e.get("bonus_1_in"),
            "tiebreakOneIn": e.get("tiebreak_1_in"),
            "superOneIn": e.get("super_1_in"),
            "hitFrequency": m.get("hit_frequency"),
            "stdDevX": m.get("std_dev_x"),
            "meanX": e.get("mean_x"),
        }
    return out


def game_config(exact: dict | None, mc: dict | None = None) -> dict:
    base, free = C.base_reels(), C.free_reels()
    bc = C.bonus_chance_reels()
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
        "minKind": C.MIN_KIND,
        "bonusLevels": {k: {**v, "startMultiplier": C.RALLY_LADDER[v["start_index"]]} for k, v in C.BONUS_LEVELS.items()},
        "modes": _modes(exact, mc),
        "payModel": "ways",
        "winLevels": C.WIN_LEVELS[:-1] + [{"name": "max", "min": C.WINCAP_X}],
        "reelStrips": {
            "base": [[C.SYMBOLS[s] for s in strip] for strip in base.strips],
            "free": [[C.SYMBOLS[s] for s in strip] for strip in free.strips],
            "bonusChance": [[C.SYMBOLS[s] for s in strip] for strip in bc.strips],
        },
        "units": "pay values are payoutMultiplier units: bet multiple x100",
    }
    if exact:
        b = (mc or {}).get("modes", {}).get("base", {})
        cfg["stats"] = {
            "rtp": exact["rtp"],
            "hitFrequency": b.get("hit_frequency"),
            "bonusOneIn": exact["trigger_1_in"],
            "stdDev": b.get("std_dev_x"),
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
    # bonus chance + buy rounds
    from .export_stake import conditional_base_stops

    bcr = C.bonus_chance_reels()
    j = 0
    while j < 20:
        res = play_round(numpy_drawer(rng), bcr, free, record_events=True, mode="bonus_chance")
        if j % 2 == 1 and not res.triggered:
            continue
        out.append({"stops": res.stops, "mode": "bonus_chance", "book": make_book(len(out) + 1, res)})
        j += 1
    for mode, k in C.BUY_SCATTERS.items():
        bs, _ = conditional_base_stops(base.strips, k, rng, 15)
        for row in bs:
            res = play_round(numpy_drawer(rng), base, free, record_events=True, forced_base_stops=[int(x) for x in row], mode=mode)
            out.append({"stops": res.stops, "mode": mode, "book": make_book(len(out) + 1, res)})
    return out


def main() -> None:
    exact_path = os.path.join(ROOT, "math", "reports", "exact.json")
    exact = json.load(open(exact_path)) if os.path.exists(exact_path) else None
    mc_path = os.path.join(ROOT, "math", "reports", "montecarlo.json")
    mc = json.load(open(mc_path)) if os.path.exists(mc_path) else None
    os.makedirs(os.path.join(ROOT, "shared"), exist_ok=True)
    with open(os.path.join(ROOT, "shared", "game-config.json"), "w", encoding="utf-8") as f:
        json.dump(game_config(exact, mc), f, indent=1)
    with open(os.path.join(ROOT, "shared", "parity-fixtures.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures(200, 4242), f, separators=(",", ":"))
    print("wrote shared/game-config.json and shared/parity-fixtures.json")


if __name__ == "__main__":
    main()
