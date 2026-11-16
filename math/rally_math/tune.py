"""Exploration helper for balancing v3 (11 symbols, two bonus levels, 4 modes).

Everything here is computed with the EXACT method (generating polynomials +
Markov chain); nothing is guessed.  Usage:

    python -m rally_math.tune            # prints the candidate table
"""

from __future__ import annotations

import numpy as np

from . import config as C
from .exact import base_mode_stats, bonus_chain, buy_mode_stats, joint_stats
from .reels import BASE_COUNTS, BC_COUNTS, FREE_COUNTS, STACK, build_reelset


def to_ids(strips):
    return [[C.SYM[s] for s in st] for st in strips]


def evaluate(base_counts=BASE_COUNTS, free_counts=FREE_COUNTS, bc_counts=None, seed=1, stack=STACK, bc_seed=None):
    base = to_ids(build_reelset(base_counts, seed, stack))
    free = to_ids(build_reelset(free_counts, seed + 1, stack))
    Pf, E1f = joint_stats(free)
    ch = bonus_chain(Pf, E1f)
    b = base_mode_stats(base, ch, 1.0)
    out = {"base": b, "chain": ch}
    for name, k in C.BUY_SCATTERS.items():
        out[name] = buy_mode_stats(b, ch, k, 1.0)
    if bc_counts is not None:
        bc = to_ids(build_reelset(bc_counts, bc_seed or seed + 2, stack))
        out["bonus_chance"] = base_mode_stats(bc, ch, 1.0)
    return out


def summary(r):
    b = r["base"]
    s = (f"base RTP {b['rtp']:.4f} (ways {b['rtp_base_ways']:.3f} sc {b['rtp_base_scatter']:.3f} "
         f"TB {b['rtp_tiebreak']:.3f} STB {b['rtp_super']:.3f}) TB 1/{b['tiebreak_1_in']:.0f} STB 1/{b['super_1_in']:.0f} | "
         f"E[TB]={r['chain']['by_trigger'][3]['E'] / 10:.1f}x E[STB4]={r['chain']['by_trigger'][4]['E'] / 10:.1f}x | "
         f"buyTB {r['buy_tiebreak']['mean_x']:.1f}x buySTB {r['buy_super']['mean_x']:.1f}x")
    if "bonus_chance" in r:
        c = r["bonus_chance"]
        s += f" | BC mean {c['mean_x']:.4f}x bonus 1/{c['bonus_1_in']:.0f} STB 1/{c['super_1_in']:.0f}"
    return s


if __name__ == "__main__":
    print(summary(evaluate(bc_counts=BC_COUNTS)))
