"""Exact (closed-form) analysis of MIDNIGHT ATELIER.

Method
------
1. Base game: full-cycle enumeration of every combination of reel stops
   (prod(len(strip)) equiprobable boards).  For each board we compute the line
   win and the number of scatters exactly.  This yields the exact
   distribution of the base-spin payout, the exact hit frequency and the
   exact trigger probabilities.
2. Free spins: full-cycle enumeration of the free-game strips, aggregated by
   (wilds landed, scatters landed) -> probability, E[line win], E[line win^2].
3. The bonus is a finite absorbing Markov chain on
   (remaining spins <= 50, wilds collected <= ladder top).  First and second
   moments of the total bonus win are obtained by solving linear systems
   (I - P) v = b exactly in float64 (residuals reported).
4. RTP = (E[base spin] + sum_k P(k scatters) * E[bonus | k]) / bet.

The 5,000x win cap is NOT included in the closed form (it would require the
full distribution of the bonus total).  Its effect is measured by Monte-Carlo
in `simulate.py` and reported separately; it is orders of magnitude below the
statistical noise of any realistic sample.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import time
from dataclasses import dataclass, asdict

import numpy as np

from . import config as C
from .engine import LINE_PAY, PAY_BASES

_G: dict = {}


def _prep(strips: list[list[int]]) -> dict:
    R, ROWS = C.NUM_REELS, C.NUM_ROWS
    lengths = [len(s) for s in strips]
    # sym_at[r][row] -> array over stops
    sym_at = []
    wcnt, scnt = [], []
    for r, strip in enumerate(strips):
        a = np.array(strip, dtype=np.int64)
        n = len(a)
        rows = [np.roll(a, -k)[:n] for k in range(ROWS)]  # rows[k][stop] = strip[(stop+k)%n]
        sym_at.append(rows)
        win = np.stack(rows)  # ROWS x n
        wcnt.append((win == C.WILD).sum(axis=0).astype(np.int64))
        scnt.append((win == C.SCATTER).sum(axis=0).astype(np.int64))
    # mesh over reels 1..4 (0-based reels 1..R-1)
    grids = np.meshgrid(*[np.arange(lengths[r]) for r in range(1, R)], indexing="ij")
    idxs = [g.ravel() for g in grids]
    part_line = []
    for line in C.PAYLINES:
        acc = np.zeros(idxs[0].shape, dtype=np.int32)
        for j, r in enumerate(range(1, R)):
            acc += (sym_at[r][line[r]][idxs[j]] * PAY_BASES[r]).astype(np.int32)
        part_line.append(acc)
    w_part = sum(wcnt[r][idxs[j]] for j, r in enumerate(range(1, R)))
    s_part = sum(scnt[r][idxs[j]] for j, r in enumerate(range(1, R)))
    return {
        "lengths": lengths,
        "sym_at": sym_at,
        "wcnt": wcnt,
        "scnt": scnt,
        "part_line": part_line,
        "w_part": w_part.astype(np.int64),
        "s_part": s_part.astype(np.int64),
    }


def _lw_for_stop0(s0: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    g = _G
    lw = np.zeros(g["part_line"][0].shape, dtype=np.int64)
    for li, line in enumerate(C.PAYLINES):
        idx = g["part_line"][li] + int(g["sym_at"][0][line[0]][s0] * PAY_BASES[0])
        lw += LINE_PAY[idx]
    w = g["w_part"] + g["wcnt"][0][s0]
    sc = g["s_part"] + g["scnt"][0][s0]
    return lw, w, sc


MAXB = 20 * 500 + 600


def _base_worker(s0: int) -> dict:
    lw, _w, sc = _lw_for_stop0(s0)
    scpay = np.zeros(6, dtype=np.int64)
    for k, v in C.SCATTER_PAY.items():
        scpay[k] = v
    B = lw + scpay[sc]
    hist = np.bincount(B, minlength=MAXB)
    sc_count = np.bincount(sc, minlength=6)
    sc_sumB = np.bincount(sc, weights=B.astype(np.float64), minlength=6)
    lw_hit = int((lw > 0).sum())
    return {"hist": hist, "sc_count": sc_count, "sc_sumB": sc_sumB, "lw_hit": lw_hit, "sumB2": float((B.astype(np.float64) ** 2).sum())}


def _free_worker(s0: int) -> dict:
    lw, w, sc = _lw_for_stop0(s0)
    key = w * 6 + sc
    K = 10 * 6
    cnt = np.bincount(key, minlength=K)
    s1 = np.bincount(key, weights=lw.astype(np.float64), minlength=K)
    s2 = np.bincount(key, weights=lw.astype(np.float64) ** 2, minlength=K)
    hist = np.bincount(lw, minlength=MAXB)
    return {"cnt": cnt, "s1": s1, "s2": s2, "hist": hist}


def _run(strips: list[list[int]], worker, procs: int) -> list[dict]:
    global _G
    _G = _prep(strips)
    n0 = len(strips[0])
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        return pool.map(worker, range(n0))


@dataclass
class BaseStats:
    total_boards: int
    hist: list  # count of boards per base payout (t-units)
    sc_prob: list  # P(k scatters)
    sc_EB: list  # E[B * 1{sc=k}]  (t-units)
    EB: float
    EB2: float
    hit: float
    line_hit: float


@dataclass
class FreeStats:
    total_boards: int
    p: list  # p[w][sc]
    e1: list  # E[LW | w, sc]
    e2: list  # E[LW^2 | w, sc]
    E_lw: float
    p_line_hit: float


def base_stats(procs: int = 4) -> BaseStats:
    strips = C.base_reels().strips
    parts = _run(strips, _base_worker, procs)
    hist = sum(p["hist"] for p in parts)
    sc_count = sum(p["sc_count"] for p in parts)
    sc_sumB = sum(p["sc_sumB"] for p in parts)
    total = int(np.prod([len(s) for s in strips]))
    assert int(hist.sum()) == total
    vals = np.arange(len(hist))
    EB = float((hist * vals).sum() / total)
    EB2 = float(sum(p["sumB2"] for p in parts) / total)
    return BaseStats(
        total_boards=total,
        hist=hist.tolist(),
        sc_prob=(sc_count / total).tolist(),
        sc_EB=(sc_sumB / total).tolist(),
        EB=EB,
        EB2=EB2,
        hit=float(1 - hist[0] / total),
        line_hit=float(sum(p["lw_hit"] for p in parts) / total),
    )


def free_stats(procs: int = 4) -> FreeStats:
    strips = C.free_reels().strips
    parts = _run(strips, _free_worker, procs)
    cnt = sum(p["cnt"] for p in parts).reshape(10, 6)
    s1 = sum(p["s1"] for p in parts).reshape(10, 6)
    s2 = sum(p["s2"] for p in parts).reshape(10, 6)
    hist = sum(p["hist"] for p in parts)
    total = int(np.prod([len(s) for s in strips]))
    assert int(cnt.sum()) == total
    with np.errstate(invalid="ignore", divide="ignore"):
        e1 = np.where(cnt > 0, s1 / np.maximum(cnt, 1), 0.0)
        e2 = np.where(cnt > 0, s2 / np.maximum(cnt, 1), 0.0)
    return FreeStats(
        total_boards=total,
        p=(cnt / total).tolist(),
        e1=e1.tolist(),
        e2=e2.tolist(),
        E_lw=float(s1.sum() / total),
        p_line_hit=float(1 - hist[0] / total),
    )


# --------------------------------------------------------------------------
# Bonus Markov chain
# --------------------------------------------------------------------------

def bonus_chain(fs: FreeStats) -> dict:
    RMAX = C.FS_MAX_REMAINING
    NL = len(C.MAINSPRING_LADDER)
    top = NL - 1
    states = [(r, n) for r in range(1, RMAX + 1) for n in range(NL)]
    sid = {s: i for i, s in enumerate(states)}
    S = len(states)
    P = np.zeros((S, S))
    a1 = np.zeros(S)  # expected spin win
    a2 = np.zeros(S)  # expected spin win^2
    cross = []  # (i, j, prob, E[spin]) for second-moment cross term
    p = np.array(fs.p)
    e1 = np.array(fs.e1)
    e2 = np.array(fs.e2)
    reach_top_a = np.zeros(S)
    for (r, n) in states:
        i = sid[(r, n)]
        for w in range(p.shape[0]):
            for sc in range(p.shape[1]):
                pk = p[w, sc]
                if pk == 0:
                    continue
                n2 = min(n + w, top)
                m = C.MAINSPRING_LADDER[n2]
                sp = C.SCATTER_PAY.get(sc, 0)
                Es = m * e1[w, sc] + sp
                Es2 = m * m * e2[w, sc] + 2 * m * sp * e1[w, sc] + sp * sp
                a1[i] += pk * Es
                a2[i] += pk * Es2
                r2 = r - 1
                if sc >= 3:
                    r2 += min(C.FS_RETRIGGER, RMAX - r2)
                if r2 > 0:
                    j = sid[(r2, n2)]
                    P[i, j] += pk
                    cross.append((i, j, pk, Es))
    I = np.eye(S)
    A = I - P
    V1 = np.linalg.solve(A, a1)
    b2 = a2.copy()
    for i, j, pk, Es in cross:
        b2[i] += 2 * pk * Es * V1[j]
    V2 = np.linalg.solve(A, b2)
    T = np.linalg.solve(A, np.ones(S))  # expected number of spins
    # probability of reaching the top multiplier at some point
    reach = np.zeros(S)
    # absorbing: once n == top it's reached
    Pm = P.copy()
    b = np.zeros(S)
    for (r, n) in states:
        i = sid[(r, n)]
        if n == top:
            Pm[i, :] = 0
            b[i] = 1.0
    # for non-top states, transitions into top states count via V
    reach = np.linalg.solve(I - Pm, b)
    # expected number of retriggers
    retr_a = np.zeros(S)
    p_sc3 = p[:, 3:].sum()
    for (r, n) in states:
        i = sid[(r, n)]
        r2 = r - 1
        if min(C.FS_RETRIGGER, RMAX - r2) > 0:
            retr_a[i] = p_sc3
    RT = np.linalg.solve(A, retr_a)
    # expected final multiplier
    fm_a = np.zeros(S)
    fm = np.zeros(S)
    # E[final multiplier] = E[ladder[n_end]] ; compute via chain: value at absorption
    term = np.zeros(S)
    for (r, n) in states:
        i = sid[(r, n)]
        for w in range(p.shape[0]):
            for sc in range(p.shape[1]):
                pk = p[w, sc]
                if pk == 0:
                    continue
                n2 = min(n + w, top)
                r2 = r - 1
                if sc >= 3:
                    r2 += min(C.FS_RETRIGGER, RMAX - r2)
                if r2 <= 0:
                    term[i] += pk * C.MAINSPRING_LADDER[n2]
    fm = np.linalg.solve(A, term)
    resid = float(np.abs(A @ V1 - a1).max())
    out = {}
    for k, spins in C.FS_AWARD.items():
        i = sid[(spins, 0)]
        out[k] = {
            "spins": spins,
            "E": float(V1[i]),
            "E2": float(V2[i]),
            "E_spins": float(T[i]),
            "P_reach_max_mult": float(reach[i]),
            "E_retriggers": float(RT[i]),
            "E_final_multiplier": float(fm[i]),
        }
    return {"by_trigger": out, "residual": resid, "states": S}


def full_report(procs: int = 4) -> dict:
    t0 = time.time()
    bs = base_stats(procs)
    t1 = time.time()
    fs = free_stats(procs)
    t2 = time.time()
    ch = bonus_chain(fs)
    t3 = time.time()

    EB = bs.EB
    fs_contrib = 0.0
    EX2 = bs.EB2
    p_trig = 0.0
    E_bonus_given_trigger_num = 0.0
    for k in (3, 4, 5):
        pk = bs.sc_prob[k] if k < len(bs.sc_prob) else 0.0
        if pk == 0:
            continue
        v = ch["by_trigger"][k]
        fs_contrib += pk * v["E"]
        EX2 += 2 * bs.sc_EB[k] * v["E"] + pk * v["E2"]
        p_trig += pk
        E_bonus_given_trigger_num += pk * v["E"]
    mean_t = EB + fs_contrib
    var_t = EX2 - mean_t ** 2
    rtp = mean_t / 10.0
    sd = (var_t ** 0.5) / 10.0
    scatter_rtp = sum(bs.sc_prob[k] * C.SCATTER_PAY.get(k, 0) for k in range(len(bs.sc_prob))) / 10
    rep = {
        "game": C.GAME_ID,
        "math_version": C.MATH_VERSION,
        "method": "full-cycle enumeration + absorbing Markov chain (no win cap)",
        "base_cycle_boards": bs.total_boards,
        "free_cycle_boards": fs.total_boards,
        "rtp": rtp,
        "rtp_base_lines": (EB / 10) - scatter_rtp,
        "rtp_base_scatter": scatter_rtp,
        "rtp_base": EB / 10,
        "rtp_free": fs_contrib / 10,
        "std_dev": sd,
        "base_std_dev": ((bs.EB2 - EB ** 2) ** 0.5) / 10,
        "hit_frequency": bs.hit,
        "line_hit_frequency": bs.line_hit,
        "p_trigger": p_trig,
        "trigger_1_in": 1 / p_trig if p_trig else None,
        "p_scatter": {str(k): bs.sc_prob[k] for k in range(len(bs.sc_prob))},
        "bonus_by_trigger": {str(k): {**v, "E_x": v["E"] / 10, "SD_x": ((v["E2"] - v["E"] ** 2) ** 0.5) / 10} for k, v in ch["by_trigger"].items()},
        "bonus_mean_x": (E_bonus_given_trigger_num / p_trig) / 10 if p_trig else None,
        "free_spin_E_line_win_x": fs.E_lw / 10,
        "free_spin_line_hit": fs.p_line_hit,
        "free_spin_p_wild_count": [float(sum(row)) for row in fs.p],
        "free_spin_p_retrigger": float(np.array(fs.p)[:, 3:].sum()),
        "markov_states": ch["states"],
        "markov_residual": ch["residual"],
        "base_payout_distribution": {str(i): c for i, c in enumerate(bs.hist) if c > 0},
        "timing_s": {"base": t1 - t0, "free": t2 - t1, "chain": t3 - t2},
    }
    return rep


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(C.HERE), "reports", "exact.json"))
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    rep = full_report(a.procs)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    keys = ["rtp", "rtp_base", "rtp_free", "std_dev", "base_std_dev", "hit_frequency", "trigger_1_in", "bonus_mean_x", "markov_residual", "timing_s"]
    for k in keys:
        print(f"{k:>16}: {rep[k]}")
    print("bonus:", json.dumps(rep["bonus_by_trigger"], indent=1))


if __name__ == "__main__":
    main()
