"""GOLDEN RALLY — single source of truth for the game rules (v2: 6x5 ways).

All monetary values inside the math engine are integers expressed in
*tenths of the total bet* ("t-units").  1 t-unit = 0.1x bet.
Stake Engine `payoutMultiplier` values are bet multiples x100, so
payoutMultiplier = t_units * 10  (always a multiple of 10, as required by the
RGS verifier in engineio/math-sdk `utils/rgs_verification.py`).

Pay model: "ways" — 6 reels x 5 rows, 5^6 = 15,625 ways.  A symbol pays when
it (or a Wild) appears on adjacent reels starting from reel 1; the win is
pay[symbol][reels] x (number of ways = product of matching symbols per reel).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

GAME_ID = "golden_rally"
GAME_NAME = "Golden Rally"
MATH_VERSION = "2.0.0"

HERE = os.path.dirname(os.path.abspath(__file__))
REELS_DIR = os.path.join(os.path.dirname(HERE), "reels")

NUM_REELS = 6
NUM_ROWS = 5
MIN_KIND = 3

SYMBOLS = ["W", "S", "H1", "H2", "H3", "H4", "H5", "L1", "L2", "L3", "L4", "L5"]
SYM = {name: i for i, name in enumerate(SYMBOLS)}
WILD = SYM["W"]
SCATTER = SYM["S"]
PAYING = [s for s in SYMBOLS if s not in ("W", "S")]

SYMBOL_INFO = {
    "W": {"label": "Smash", "fr": "Smash", "role": "wild"},
    "S": {"label": "Trophy", "fr": "Trophée", "role": "scatter"},
    "H1": {"label": "The President", "fr": "Le Président", "role": "high"},
    "H2": {"label": "The Champion", "fr": "La Championne", "role": "high"},
    "H3": {"label": "The Umpire", "fr": "L'Arbitre", "role": "high"},
    "H4": {"label": "The Ball Kid", "fr": "Le Ramasseur", "role": "high"},
    "H5": {"label": "The Club Bulldog", "fr": "Le Bulldog", "role": "high"},
    "L1": {"label": "Advantage", "fr": "Avantage", "role": "low"},
    "L2": {"label": "Forty", "fr": "Quarante", "role": "low"},
    "L3": {"label": "Thirty", "fr": "Trente", "role": "low"},
    "L4": {"label": "Fifteen", "fr": "Quinze", "role": "low"},
    "L5": {"label": "Love", "fr": "Zéro", "role": "low"},
}

# Pay per way, in t-units (tenths of TOTAL bet), for 3..6 reels.
PAYTABLE: dict[str, dict[int, int]] = {
    "H1": {3: 5, 4: 10, 5: 20, 6: 50},
    "H2": {3: 4, 4: 8, 5: 15, 6: 30},
    "H3": {3: 3, 4: 5, 5: 12, 6: 25},
    "H4": {3: 2, 4: 4, 5: 10, 6: 20},
    "H5": {3: 2, 4: 3, 5: 8, 6: 15},
    "L1": {3: 1, 4: 2, 5: 4, 6: 7},
    "L2": {3: 1, 4: 2, 5: 3, 6: 6},
    "L3": {3: 1, 4: 1, 5: 3, 6: 5},
    "L4": {3: 1, 4: 1, 5: 2, 6: 4},
    "L5": {3: 1, 4: 1, 5: 2, 6: 4},
}

# Scatter (Trophy) pays, anywhere, never multiplied.
SCATTER_PAY = {3: 20, 4: 50, 5: 200, 6: 1000}
FS_AWARD = {3: 9, 4: 12, 5: 15, 6: 20}
FS_RETRIGGER = 5            # 3+ trophies during the bonus
FS_MAX_REMAINING = 50

# "Rally" ladder (Tie-Break free spins): multiplier applied to way wins,
# indexed by the number of Smash wilds collected since the bonus started.
# Wilds landing on a spin extend the rally BEFORE that spin's wins are
# evaluated.  The multiplier never goes down during the bonus.
RALLY_LADDER = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]

WINCAP_X = 5000
WINCAP_T = WINCAP_X * 10

WIN_LEVELS = [
    {"name": "small", "min": 0.0},
    {"name": "nice", "min": 2.0},
    {"name": "big", "min": 10.0},
    {"name": "mega", "min": 50.0},
    {"name": "epic", "min": 200.0},
    {"name": "max", "min": float(WINCAP_X)},
]


def win_level(x: float) -> str:
    if x <= 0:
        return "none"
    name = "none"
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
