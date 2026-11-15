"""Exact RTP of GOLDEN RALLY (6x5 ways) — no simulation involved.

Why it is exact
---------------
Reels are independent and every stop is equiprobable.  For a symbol s paying
on k reels, the ways win is  pay[s][k] * prod_{r<k} m_r * 1{m_k = 0}, where
m_r = number of s-or-Wild cells on reel r.  The expectation of a product of
functions of independent reels is the product of their expectations, so
every quantity below is a finite sum over individual reel stops.

To get the *joint* law needed by the bonus (how many Wilds landed, how many
Trophies landed), each reel contributes a bivariate generating polynomial in
z (wild count) and y (scatter count); multiplying the six polynomials gives
E[ways win * 1{W=w, S=c}] and P(W=w, S=c) exactly.

The Tie-Break bonus is then a finite absorbing Markov chain on
(remaining spins <= 50, wilds collected <= ladder top) solved with linear
algebra.  The 5,000x cap and the second moments are not part of the closed
form: standard deviation, hit frequency and cap effect come from the
Monte-Carlo run (simulate.py).
"""

from __future__ import annotations

import json
import os
import time

import numpy as np
from scipy.signal import convolve2d

from . import config as C
from .engine import count_tables, PAY_IDX

WMAX = 24  # max wilds per board + margin
CMAX = 7


def _reel_polys(cnt_r: np.ndarray):
    """Per reel: dict of 2-D arrays (z^w y^c) for the needed per-stop weights."""
    L = cnt_r.shape[0]
    w = cnt_r[:, C.WILD]
    c = cnt_r[:, C.SCATTER]

    def poly(weights):
        P = np.zeros((WMAX, CMAX))
        np.add.at(P, (w, c), weights / L)
        return P

    ones = poly(np.ones(L))
    per_sym = {}
    for s in PAY_IDX:
        m = cnt_r[:, s] + w
        per_sym[s] = (poly(m.astype(float)), poly((m == 0).astype(float)))
    return ones, per_sym


def _mul(a, b):
    return convolve2d(a, b)[:WMAX, :CMAX]


def joint_stats(strips) -> tuple[np.ndarray, np.ndarray]:
    """Returns (P[w,c], E1[w,c]) with E1 = E[ways win (t-units) * 1{W=w,S=c}]."""
    cnt = count_tables(strips)
    polys = [_reel_polys(cnt[r]) for r in range(C.NUM_REELS)]
    P = polys[0][0]
    for r in range(1, C.NUM_REELS):
        P = _mul(P, polys[r][0])
    E1 = np.zeros((WMAX, CMAX))
    for s in PAY_IDX:
        name = C.SYMBOLS[s]
        for k in range(C.MIN_KIND, C.NUM_REELS + 1):
            acc = None
            for r in range(C.NUM_REELS):
                ones, per = polys[r]
                if r < k:
                    f = per[s][0]
                elif r == k:
                    f = per[s][1]
                else:
                    f = ones
                acc = f if acc is None else _mul(acc, f)
            E1 += C.PAYTABLE[name][k] * acc
    return P, E1


def bonus_chain(Pf: np.ndarray, E1f: np.ndarray) -> dict:
    RMAX = C.FS_MAX_REMAINING
    NL = len(C.RALLY_LADDER)
    top = NL - 1
    states = [(r, n) for r in range(1, RMAX + 1) for n in range(NL)]
    sid = {s: i for i, s in enumerate(states)}
    S = len(states)
    M = np.zeros((S, S))
    a1 = np.zeros(S)
    term_mult = np.zeros(S)
    retr = np.zeros(S)
    cells = [(w, c, Pf[w, c], E1f[w, c]) for w in range(WMAX) for c in range(CMAX) if Pf[w, c] > 0]
    for (r, n) in states:
        i = sid[(r, n)]
        for w, c, p, e in cells:
            n2 = min(n + w, top)
            m = C.RALLY_LADDER[n2]
            a1[i] += m * e + p * C.SCATTER_PAY.get(c, 0)
            r2 = r - 1
            if c >= 3:
                add = min(C.FS_RETRIGGER, RMAX - r2)
                if add > 0:
                    retr[i] += p
                r2 += add
            if r2 > 0:
                M[i, sid[(r2, n2)]] += p
            else:
                term_mult[i] += p * m
    A = np.eye(S) - M
    V1 = np.linalg.solve(A, a1)
    T = np.linalg.solve(A, np.ones(S))
    RT = np.linalg.solve(A, retr)
    FM = np.linalg.solve(A, term_mult)
    Mt = M.copy()
    b = np.zeros(S)
    for (r, n) in states:
        if n == top:
            Mt[sid[(r, n)], :] = 0
            b[sid[(r, n)]] = 1
    reach = np.linalg.solve(np.eye(S) - Mt, b)
    out = {}
    for k, spins in C.FS_AWARD.items():
        i = sid[(spins, 0)]
        out[k] = {"spins": spins, "E": float(V1[i]), "E_spins": float(T[i]), "E_retriggers": float(RT[i]),
                  "E_final_multiplier": float(FM[i]), "P_reach_max_mult": float(reach[i])}
    return {"by_trigger": out, "residual": float(np.abs(A @ V1 - a1).max()), "states": S}


def _buy(cond_base: dict, ch: dict) -> dict:
    tot = sum(C.BUY_SCATTER_WEIGHTS.values())
    per = {str(k): (cond_base[str(k)] + ch["by_trigger"][k]["E"]) / 10 for k in C.BUY_SCATTER_WEIGHTS}
    E = sum(w / tot * per[str(k)] for k, w in C.BUY_SCATTER_WEIGHTS.items())
    return {"cost": C.BUY_COST, "scatter_weights": {str(k): w for k, w in C.BUY_SCATTER_WEIGHTS.items()},
            "weights_total": tot, "E_x_by_scatters": per, "E_x": E, "rtp": E / C.BUY_COST}


def full_report() -> dict:
    t0 = time.time()
    base, free = C.base_reels(), C.free_reels()
    Pb, E1b = joint_stats(base.strips)
    Pf, E1f = joint_stats(free.strips)
    ch = bonus_chain(Pf, E1f)
    p_sc = Pb.sum(axis=0)  # P(scatter count = c)
    ways_c = E1b.sum(axis=0)  # E[ways win * 1{S=c}]
    E_ways = float(ways_c.sum())
    E_sc_pay = float(sum(p_sc[c] * C.SCATTER_PAY.get(c, 0) for c in range(CMAX)))
    fs = 0.0
    p_trig = 0.0
    cond_base = {}
    for k in C.FS_AWARD:
        if k < CMAX and p_sc[k] > 0:
            fs += p_sc[k] * ch["by_trigger"][k]["E"]
            p_trig += p_sc[k]
            cond_base[str(k)] = float((ways_c[k] + p_sc[k] * C.SCATTER_PAY[k]) / p_sc[k])
    mean_t = E_ways + E_sc_pay + fs
    p_free_w = Pf.sum(axis=1)
    rep = {
        "game": C.GAME_ID,
        "math_version": C.MATH_VERSION,
        "method": "per-reel generating polynomials (exact) + absorbing Markov chain (no win cap)",
        "base_cycle_boards": int(np.prod(base.lengths, dtype=np.float64)),
        "free_cycle_boards": int(np.prod(free.lengths, dtype=np.float64)),
        "rtp": mean_t / 10,
        "rtp_base_ways": E_ways / 10,
        "rtp_base_scatter": E_sc_pay / 10,
        "rtp_base": (E_ways + E_sc_pay) / 10,
        "rtp_free": fs / 10,
        "p_trigger": p_trig,
        "trigger_1_in": 1 / p_trig if p_trig else None,
        "p_scatter": {str(c): float(p_sc[c]) for c in range(CMAX)},
        "cond_base_mean_t": cond_base,
        "bonus_by_trigger": {str(k): {**v, "E_x": v["E"] / 10} for k, v in ch["by_trigger"].items()},
        "bonus_mean_x": (fs / p_trig) / 10 if p_trig else None,
        "free_spin_E_ways_x": float(E1f.sum()) / 10,
        "free_spin_p_wild_count": [float(x) for x in p_free_w[:8]],
        "free_spin_p_retrigger": float(Pf[:, 3:].sum()),
        "buy": _buy(cond_base, ch),
        "markov_states": ch["states"],
        "markov_residual": ch["residual"],
        "timing_s": time.time() - t0,
    }
    return rep


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(C.HERE), "reports", "exact.json"))
    a = ap.parse_args()
    rep = full_report()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    print("buy:", rep["buy"])
    for k in ["rtp", "rtp_base_ways", "rtp_base_scatter", "rtp_free", "trigger_1_in", "bonus_mean_x", "free_spin_p_wild_count", "markov_residual", "timing_s"]:
        print(f"{k:>22}: {rep[k]}")
    print({k: (round(v["E_x"], 2), round(v["P_reach_max_mult"], 3), round(v["E_final_multiplier"], 2)) for k, v in rep["bonus_by_trigger"].items()})


if __name__ == "__main__":
    main()
