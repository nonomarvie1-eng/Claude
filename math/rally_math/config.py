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
GAME_NAME = "Golden Rally — The Final Set"
MATH_VERSION = "4.0.0"

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

# THE FINAL SET (v6): the two bonuses are tennis matches played on the grid
# (Court Control + Power Shots), not free spins with a multiplier.  Rules in
# bonus.py; every number below is part of the published maths and is tuned and
# verified with simulate.py / tests (see docs/MATH_REPORT.md).
FINAL_SET = {
    # court value of each symbol when its zone is hit (t-units = 0.1 x bet)
    "COURT_VALUE": {"W": 100, "S": 0, "H1": 5, "H2": 4, "H3": 3, "H4": 3, "L1": 2, "L2": 1, "L3": 1, "L4": 1, "L5": 1},
    "SHOT_ROLL": 1000,
    "RALLY_TABLE": {"RALLY": 470, "ACE": 150, "SMASH": 120, "PASSING": 120, "DROP": 80, "GOLDEN": 60},
    "FINAL_TABLE": {"RALLY": 340, "ACE": 160, "SMASH": 160, "PASSING": 160, "DROP": 100, "GOLDEN": 80},
    "CP_TABLE": {"RALLY": 0, "ACE": 300, "SMASH": 250, "PASSING": 250, "DROP": 120, "GOLDEN": 80},
    "ACE_PRIZE": 30,
    "MARK_PRIZE": 60,
    "HAWK_PRIZE": 80,
    "ACE_MARK": 3,
    "DROP_MARK": 2,
    "HAWK_MARK": 3,
    "P_LINE": 150,   # per mille: single-landing shot of the Grand Final lands on a line
    "P_IN": 600,     # per mille: the Hawk-Eye call is IN
    "MAX_REMAINING": 30,
    "GR_MIN": 4,     # Golden Rally: number of shots, uniform in [GR_MIN, GR_MAX]
    "GR_MAX": 8,
    "GOLDEN_MARK": 2,
    "SLAM_PRIZE": 1500,  # GRAND SLAM (whole court marked): 150 x bet
}
# exchanges awarded by the trigger: 3 scatters -> RALLY CHALLENGE, 4+ -> THE GRAND FINAL
FS_AWARD = {3: 8, 4: 12, 5: 14, 6: 16}
CEREMONY_X = {"trophy": 75, "grand": 200}  # bonus total (x bet) needed for each ceremony level

BONUS_LEVELS = {
    "rally": {"fr": "RALLY CHALLENGE", "en": "RALLY CHALLENGE"},
    "final": {"fr": "THE GRAND FINAL", "en": "THE GRAND FINAL"},
}


def bonus_level(n_scatters: int) -> str | None:
    """Exactly 3 scatters -> Rally Challenge; 4, 5 or 6 -> The Grand Final."""
    if n_scatters < 3:
        return None
    return "rally" if n_scatters == 3 else "final"

# RALLY PATH — EXPERIMENTAL PROTOTYPE (rules in rally_path.py).  Used only by
# the prototype mode / dev scenarios: the normal game, its reels and its RTP
# are NOT affected.  Every value below is experimental and is evaluated with
# the exact model in rally_path.py before any adoption.
CHAMPIONSHIP_DUEL = {
    # experimental (see championship_duel.py): probabilities out of 1000, prizes in x bet
    "LEVELS": {
        "tiebreak": {
            "POINTS": 4,
            "RALLY_SHOTS": [2, 4],
            "SERVE1": {"ACE": 90, "FAULT": 350, "IN": 560},
            "SERVE2": {"ACE": 30, "DOUBLE_FAULT": 200, "IN": 770},
            "RALLY": {"LOST": 380, "RALLY_WON": 370, "WINNER": 220, "GOLDEN": 30},
            "PRIZES": {
                "ACE": [[15, 350], [20, 300], [30, 200], [50, 100], [100, 50]],
                "RALLY_WON": [[2, 400], [3, 350], [5, 250]],
                "WINNER": [[12, 350], [15, 300], [22, 200], [35, 100], [60, 50]],
                "GOLDEN": [[70, 500], [125, 300], [250, 150], [600, 40], [1200, 10]],
            },
        },
        "final": {
            "POINTS": 6,
            "RALLY_SHOTS": [3, 5],
            "P_GMP": 25,
            "SERVE1": {"ACE": 100, "FAULT": 330, "IN": 570},
            "SERVE2": {"ACE": 30, "DOUBLE_FAULT": 180, "IN": 790},
            "RALLY": {"LOST": 350, "RALLY_WON": 360, "WINNER": 250, "GOLDEN": 40},
            "PRIZES": {
                "ACE": [[15, 350], [20, 300], [30, 200], [50, 100], [80, 50]],
                "RALLY_WON": [[3, 400], [4, 350], [6, 250]],
                "WINNER": [[12, 350], [18, 300], [25, 200], [40, 100], [75, 50]],
                "GOLDEN": [[80, 450], [150, 300], [300, 170], [600, 60], [1500, 15], [3000, 5]],
            },
        },
    },
    # GOLDEN MATCH POINT (Grand Final): prize of a WON golden match point; no minimum guaranteed
    "GMP_TABLE": [[50, 400], [100, 300], [250, 180], [500, 80], [1000, 30], [2500, 8], [5000, 2]],
}

GOLDEN_SERVE_PROTO = {
    # experimental: concepts A (Cross-Court) and B (Court Switch), see golden_serve.py
    "G_ON_REEL1": {"base": 1, "free": 6},
    # prototype base reels (no Wild, stacked like v6, seed 71): ways part measured exactly
    "BASE_COUNTS": {"W": [0] * 6, "S": [1, 2, 1, 2, 1, 2], "H1": [7] * 6, "H2": [8] * 6, "H3": [9] * 6, "H4": [10] * 6,
                    "L1": [12] * 6, "L2": [12] * 6, "L3": [13] * 6, "L4": [13] * 6, "L5": [15] * 6},
    "BASE_SEED": 71,
    "TARGET_SYMS": ["H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4", "L5"],
    "TARGET_W": {
        "base": [2, 6, 12, 30, 150, 190, 200, 205, 205],
        "rally": [30, 60, 90, 120, 130, 140, 140, 145, 145],
        "final": [80, 110, 130, 140, 110, 110, 110, 105, 105],
    },
    "P_SMASH": {"base": 5, "rally": 40, "final": 100},
    "P_DOUBLE": {"base": 0, "rally": 60, "final": 150},
    "BONUS": {"rally": {"spins": 8}, "final": {"spins": 12}},
}

RALLY_PATH_PROTO = {
    "RACKET": "H4",                  # return points: the racket symbol only (no Wild)
    # In the prototype the racket is "the rally symbol": its own ways pay is
    # reduced to the minimum (its value comes from Rally Path) -- see
    # docs/RALLY_PATH_PROTOTYPE.md for why (dense rackets would explode ways wins).
    "RACKET_WAYS_PAY": {"3": 1, "4": 1, "5": 1, "6": 2},
    "G_ON_REEL1": {"base": 2, "free": 6},   # Golden Balls added to reel 1 of the prototype strips
    "FREE_RACKETS": 35,              # racket count per bonus reel (normal bonus reels: 11)
    "MAX_SHOTS": 6,
    # reward by rally length in shots (t-units = 0.1 x bet); 6 shots = Championship Shot
    "REWARD": {"1": 0, "2": 20, "3": 80, "4": 300, "5": 1000},
    "CS_ROLL": 1000,
    "CS_TABLE": [[1500, 450], [3000, 300], [7500, 170], [15000, 60], [40000, 20]],
    "BONUS": {
        "rally": {"spins": 8, "second_serve": False},
        "final": {"spins": 12, "second_serve": True, "second_serve_max_len": 2},
    },
}

# Bet modes (Stake Engine "modes").  Costs of the buy / bonus-chance modes are
# DERIVED from the exact maths (see tune.py / reports/exact.json) and written
# here once validated; they are not guesses.
#   base          normal spin, BASE reels
#   bonus_chance  same rules, BASE_BC reels (more scatters), higher cost
#   buy_rally     bought spin shows exactly 3 scatters -> Rally Challenge
#   buy_final     bought spin shows exactly 4 scatters -> The Grand Final
BONUS_CHANCE_COST = 1.4
BUY_RALLY_COST = 48.8
BUY_FINAL_COST = 106.8
BUY_SCATTERS = {"buy_rally": 3, "buy_final": 4}

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
    return {"base": 1.0, "bonus_chance": BONUS_CHANCE_COST, "buy_rally": BUY_RALLY_COST, "buy_final": BUY_FINAL_COST}
