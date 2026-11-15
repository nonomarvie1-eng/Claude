"""GOLDEN RALLY — single source of truth for the game rules.

All monetary values inside the math engine are integers expressed in
*tenths of the total bet* ("t-units").  1 t-unit = 0.1x bet.
Stake Engine `payoutMultiplier` values are bet multiples x100, so
payoutMultiplier = t_units * 10  (always a multiple of 10, as required by the
RGS verifier in engineio/math-sdk `utils/rgs_verification.py`).

Everything the frontend needs (symbols, paytable, paylines, reel strips,
feature parameters) is exported to `shared/game-config.json` by
`rally_math.export_config` so that the TypeScript demo engine uses exactly
the same rules.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

GAME_ID = "golden_rally"
GAME_NAME = "Golden Rally"
MATH_VERSION = "1.0.0"

HERE = os.path.dirname(os.path.abspath(__file__))
REELS_DIR = os.path.join(os.path.dirname(HERE), "reels")

NUM_REELS = 5
NUM_ROWS = 3

# --------------------------------------------------------------------------
# Symbols  (id order matters: it is used for lookup tables)
# --------------------------------------------------------------------------
SYMBOLS = ["W", "S", "H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4"]
SYM = {name: i for i, name in enumerate(SYMBOLS)}
WILD = SYM["W"]
SCATTER = SYM["S"]

SYMBOL_INFO = {
    "W": {"label": "Golden Racket", "fr": "Raquette d'Or", "role": "wild"},
    "S": {"label": "Trophy", "fr": "Trophée", "role": "scatter"},
    "H1": {"label": "Golden Ball", "fr": "Balle d'Or", "role": "high"},
    "H2": {"label": "Umpire Chair", "fr": "Chaise d'arbitre", "role": "high"},
    "H3": {"label": "Ball Tube", "fr": "Tube de balles", "role": "high"},
    "H4": {"label": "Club Cap", "fr": "Casquette du club", "role": "high"},
    "L1": {"label": "Advantage", "fr": "Avantage", "role": "low"},
    "L2": {"label": "Forty", "fr": "Quarante", "role": "low"},
    "L3": {"label": "Thirty", "fr": "Trente", "role": "low"},
    "L4": {"label": "Fifteen", "fr": "Quinze", "role": "low"},
}

# Line pays, in t-units (tenths of TOTAL bet), for 3 / 4 / 5 of a kind.
# 20 fixed lines; the total bet is the only bet the player chooses.
PAYTABLE: dict[str, dict[int, int]] = {
    "W": {3: 20, 4: 100, 5: 500},
    "H1": {3: 20, 4: 100, 5: 500},
    "H2": {3: 15, 4: 60, 5: 250},
    "H3": {3: 12, 4: 40, 5: 150},
    "H4": {3: 10, 4: 30, 5: 100},
    "L1": {3: 5, 4: 15, 5: 50},
    "L2": {3: 4, 4: 12, 5: 40},
    "L3": {3: 3, 4: 10, 5: 30},
    "L4": {3: 2, 4: 8, 5: 22},
}

# Scatter pays (t-units of total bet) — paid anywhere, never multiplied.
SCATTER_PAY = {3: 20, 4: 100, 5: 500}
# Free spins awarded by scatters in the base game.
FS_AWARD = {3: 10, 4: 12, 5: 15}
# Retrigger inside the bonus: 3+ scatters add this many spins.
FS_RETRIGGER = 5
FS_MAX_REMAINING = 50  # remaining free spins can never exceed this value

# "Rally" ladder: multiplier applied to line wins during free spins,
# indexed by the number of Golden Racket wilds collected so far (persistent
# for the whole bonus).  Wilds landing on a spin extend the rally
# BEFORE that spin's line wins are evaluated.
RALLY_LADDER = [1, 2, 3, 4, 5, 6, 8, 10]

WINCAP_X = 5000  # maximum total win per round, in multiples of the bet
WINCAP_T = WINCAP_X * 10

# 20 fixed paylines (row index per reel, 0 = top).
PAYLINES: list[list[int]] = [
    [1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2],
    [0, 1, 2, 1, 0],
    [2, 1, 0, 1, 2],
    [1, 0, 0, 0, 1],
    [1, 2, 2, 2, 1],
    [0, 0, 1, 2, 2],
    [2, 2, 1, 0, 0],
    [1, 2, 1, 0, 1],
    [1, 0, 1, 2, 1],
    [0, 1, 1, 1, 0],
    [2, 1, 1, 1, 2],
    [0, 1, 0, 1, 0],
    [2, 1, 2, 1, 2],
    [1, 1, 0, 1, 1],
    [1, 1, 2, 1, 1],
    [0, 0, 2, 0, 0],
    [2, 2, 0, 2, 2],
    [0, 2, 2, 2, 0],
]

# Win-level thresholds (multiples of bet) used only for presentation.
WIN_LEVELS = [
    {"name": "small", "min": 0.0},
    {"name": "nice", "min": 2.0},
    {"name": "big", "min": 10.0},
    {"name": "mega", "min": 50.0},
    {"name": "epic", "min": 200.0},
    {"name": "max", "min": float(WINCAP_X)},
]


def win_level(x: float) -> str:
    name = "none"
    if x <= 0:
        return name
    for lv in WIN_LEVELS:
        if x >= lv["min"]:
            name = lv["name"]
    return name


@dataclass
class ReelSet:
    name: str
    strips: list[list[int]] = field(default_factory=list)

    @property
    def lengths(self) -> list[int]:
        return [len(s) for s in self.strips]


def load_reelset(name: str) -> ReelSet:
    """Load a reel set CSV: one column per reel, symbol names, ragged allowed."""
    path = os.path.join(REELS_DIR, f"{name}.csv")
    cols: list[list[int]] = [[] for _ in range(NUM_REELS)]
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            for r, cell in enumerate(row[:NUM_REELS]):
                cell = cell.strip()
                if cell:
                    cols[r].append(SYM[cell])
    return ReelSet(name=name, strips=cols)


def base_reels() -> ReelSet:
    return load_reelset("BASE")


def free_reels() -> ReelSet:
    return load_reelset("FREE")
