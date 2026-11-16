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
GAME_NAME = "Golden Rally — Match Point"
MATH_VERSION = "3.0.0"

HERE = os.path.dirname(os.path.abspath(__file__))
REELS_DIR = os.path.join(os.path.dirname(HERE), "reels")

NUM_REELS = 6
NUM_ROWS = 5
MIN_KIND = 3

SYMBOLS = ["W", "S", "H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4", "L5"]
SYM = {name: i for i, name in enumerate(SYMBOLS)}
WILD = SYM["W"]
SCATTER = SYM["S"]
PAYING = [s for s in SYMBOLS if s not in ("W", "S")]

# v3 (11-symbol pack).  Old -> new mapping is documented in docs/GAME_MODES.md:
# the old H5 id is removed; every other id keeps its role (wild, scatter,
# premium H1..H4, classic L1..L5) with a new picture and new name.
SYMBOL_INFO = {
    "W": {"label": "Wild", "fr": "Wild", "role": "wild", "art": "wild_magenta"},
    "S": {"label": "Stadium Scatter", "fr": "Scatter Stade", "role": "scatter", "art": "scatter_blue"},
    "H1": {"label": "Ace, the mascot", "fr": "Ace, la mascotte", "role": "premium", "art": "ace_mascot"},
    "H2": {"label": "Trophy", "fr": "Trophée", "role": "premium", "art": "gold_trophy"},
    "H3": {"label": "Tennis bag", "fr": "Sac de tennis", "role": "premium", "art": "tennis_bag"},
    "H4": {"label": "Racket", "fr": "Raquette", "role": "premium", "art": "tennis_racket"},
    "L1": {"label": "Tennis ball", "fr": "Balle de tennis", "role": "classic", "art": "tennis_ball"},
    "L2": {"label": "Shoe", "fr": "Chaussure", "role": "classic", "art": "tennis_shoe"},
    "L3": {"label": "Cap", "fr": "Casquette", "role": "classic", "art": "tennis_cap"},
    "L4": {"label": "Water bottle", "fr": "Gourde", "role": "classic", "art": "water_bottle"},
    "L5": {"label": "Wristband", "fr": "Poignet éponge", "role": "classic", "art": "red_wristband"},
}

# Pay per way, in t-units (tenths of TOTAL bet), for 3..6 reels.
PAYTABLE: dict[str, dict[int, int]] = {
    "H1": {3: 5, 4: 10, 5: 20, 6: 50},
    "H2": {3: 3, 4: 6, 5: 12, 6: 25},
    "H3": {3: 2, 4: 4, 5: 8, 6: 15},
    "H4": {3: 2, 4: 3, 5: 6, 6: 12},
    "L1": {3: 1, 4: 2, 5: 3, 6: 4},
    "L2": {3: 1, 4: 1, 5: 2, 6: 3},
    "L3": {3: 1, 4: 1, 5: 2, 6: 3},
    "L4": {3: 1, 4: 1, 5: 2, 6: 3},
    "L5": {3: 1, 4: 1, 5: 2, 6: 2},
}

# Scatter pays, anywhere, never multiplied.
SCATTER_PAY = {3: 20, 4: 50, 5: 200, 6: 1000}
FS_RETRIGGER = 5            # 3+ scatters during either bonus
FS_MAX_REMAINING = 50

# Multiplier ladder shared by both bonuses: the ladder position is
# start_index + Wilds collected since the bonus started (capped at the top).
# Wilds landing on a spin move the ladder BEFORE that spin's wins are
# evaluated.  The multiplier never goes down during a bonus.
RALLY_LADDER = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]

# Two bonus levels chosen by the number of scatters on the triggering spin.
#   exactly 3 scatters      -> TIE-BREAK        (multiplier starts at x1)
#   4, 5 or 6 scatters      -> SUPER TIE-BREAK  (multiplier starts at x2)
# At most one scatter can show per reel (strip constraint), so 3..6 are the
# only possible trigger counts.  5 and 6 scatters give more spins and a
# bigger scatter pay, the bonus itself is the Super Tie-Break.
BONUS_LEVELS = {
    "tiebreak": {"start_index": 0, "fr": "TIE-BREAK", "en": "TIE-BREAK"},
    "super": {"start_index": 1, "fr": "SUPER TIE-BREAK", "en": "SUPER TIE-BREAK"},
}
FS_AWARD = {3: 9, 4: 12, 5: 15, 6: 20}


def bonus_level(n_scatters: int) -> str | None:
    if n_scatters < 3:
        return None
    return "tiebreak" if n_scatters == 3 else "super"


# Bet modes (Stake Engine "modes").  Costs of the buy / bonus-chance modes are
# DERIVED from the exact maths (see tune.py / reports/exact.json) and written
# here once validated; they are not guesses.
#   base          normal spin, BASE reels
#   bonus_chance  same rules, BASE_BC reels (more scatters), higher cost
#   buy_tiebreak  bought spin shows exactly 3 scatters -> Tie-Break
#   buy_super     bought spin shows exactly 4 scatters -> Super Tie-Break
BONUS_CHANCE_COST = 1.4
BUY_TIEBREAK_COST = 49.4
BUY_SUPER_COST = 105.0
BUY_SCATTERS = {"buy_tiebreak": 3, "buy_super": 4}

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


def bonus_chance_reels() -> ReelSet:
    return load_reelset("BASE_BC")


def mode_costs() -> dict[str, float]:
    return {"base": 1.0, "bonus_chance": BONUS_CHANCE_COST, "buy_tiebreak": BUY_TIEBREAK_COST, "buy_super": BUY_SUPER_COST}
