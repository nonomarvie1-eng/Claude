"""Balancing helper for v6 (THE FINAL SET).

Base game: exact (generating polynomials).  Bonuses: simulated values from
exact.bonus_values.  Used to choose reel-strip layouts and prices; nothing
here is published directly.
"""

from __future__ import annotations

from . import config as C
from .exact import base_mode_stats, buy_mode_stats  # noqa: F401
from .reels import BASE_COUNTS, BC_COUNTS, FREE_COUNTS, STACK, build_reelset  # noqa: F401


def to_ids(strips):
    return [[C.SYM[s] for s in st] for st in strips]


def layout_search(counts, cost, bv, seeds=range(1, 120), lo=0.9645, hi=0.9658):
    out = []
    for s in seeds:
        m = base_mode_stats(to_ids(build_reelset(counts, s, STACK)), bv, cost)
        if lo <= m["rtp"] <= hi:
            out.append((s, m["rtp"]))
    return out
