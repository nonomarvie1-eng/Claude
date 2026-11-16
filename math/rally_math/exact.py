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
    term_top = np.zeros(S)  # P(this spin ends the bonus AND lands on the ladder top)
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
                if n2 == top:
                    term_top[i] += p
    A = np.eye(S) - M
    V1 = np.linalg.solve(A, a1)
    T = np.linalg.solve(A, np.ones(S))
    RT = np.linalg.solve(A, retr)
    FM = np.linalg.solve(A, term_mult)
    Mt = M.copy()
    b = term_top.copy()
    for (r, n) in states:
        if n == top:
            Mt[sid[(r, n)], :] = 0
            b[sid[(r, n)]] = 1
    reach = np.linalg.solve(np.eye(S) - Mt, b)
    out = {}
    for k, spins in C.FS_AWARD.items():
        level = C.bonus_level(k)
        n0 = C.BONUS_LEVELS[level]["start_index"]
        i = sid[(spins, n0)]
        out[k] = {"spins": spins, "level": level, "start_multiplier": C.RALLY_LADDER[n0], "E": float(V1[i]),
                  "E_spins": float(T[i]), "E_retriggers": float(RT[i]),
                  "E_final_multiplier": float(FM[i]), "P_reach_max_mult": float(reach[i])}
    return {"by_trigger": out, "residual": float(np.abs(A @ V1 - a1).max()), "states": S}


def cap_overshoot(strips, free_strips, k: int, n: int, seed: int) -> dict:
    """E[(round total - WINCAP)+ | trigger with exactly k scatters] by targeted
    simulation (the only quantity of the model that is not closed-form)."""
    from .engine import count_tables
    from .export_stake import conditional_base_stops
    from .simulate import play_vec

    rng = np.random.Generator(np.random.PCG64(seed))
    bc, fc = count_tables(strips), count_tables(free_strips)
    fl = [len(s) for s in free_strips]
    ov, ov2, hits, done = 0.0, 0.0, 0, 0
    old = C.WINCAP_T
    try:
        C.WINCAP_T = 10 ** 12  # play uncapped, measure the part above the cap
        while done < n:
            m = min(250_000, n - done)
            st = conditional_base_stops(strips, k, rng, m)[0]
            t = play_vec(rng, st, bc, fc, fl)["total"].astype(np.float64)
            x = np.maximum(t - old, 0) / 10
            ov += x.sum()
            ov2 += (x * x).sum()
            hits += int((x > 0).sum())
            done += m
    finally:
        C.WINCAP_T = old
    mean = ov / n
    se = ((ov2 / n - mean ** 2) / n) ** 0.5
    return {"rounds": n, "overshoot_x": mean, "se_x": se, "p_cap": hits / n}


def base_mode_stats(strips, ch: dict, cost: float, cap: dict | None = None) -> dict:
    """Exact statistics of a spin-type mode (base or bonus_chance) whose base
    spin uses `strips` (both bonuses use the shared FREE reels)."""
    Pb, E1b = joint_stats(strips)
    p_sc = Pb.sum(axis=0)
    ways_c = E1b.sum(axis=0)
    E_ways = float(ways_c.sum())
    E_sc_pay = float(sum(p_sc[c] * C.SCATTER_PAY.get(c, 0) for c in range(CMAX)))
    fs = 0.0
    cond_base = {}
    p_level = {"tiebreak": 0.0, "super": 0.0}
    fs_level = {"tiebreak": 0.0, "super": 0.0}
    for k in C.FS_AWARD:
        if k < CMAX and p_sc[k] > 0:
            lv = C.bonus_level(k)
            e = p_sc[k] * ch["by_trigger"][k]["E"]
            fs += e
            fs_level[lv] += e
            p_level[lv] += p_sc[k]
            cond_base[str(k)] = float((ways_c[k] + p_sc[k] * C.SCATTER_PAY[k]) / p_sc[k])
    p_trig = sum(p_level.values())
    mean_unc = (E_ways + E_sc_pay + fs) / 10
    cap_loss = sum(p_sc[k] * cap[k]["overshoot_x"] for k in cap) if cap else 0.0
    cap_se = sum((p_sc[k] * cap[k]["se_x"]) ** 2 for k in cap) ** 0.5 if cap else 0.0
    mean_x = mean_unc - cap_loss
    return {
        "cost": cost,
        "mean_x": mean_x,
        "rtp": mean_x / cost,
        "rtp_uncapped": mean_unc / cost,
        "cap_loss_x": cap_loss,
        "cap_loss_se_x": cap_se,
        "rtp_base_ways": E_ways / 10 / cost,
        "rtp_base_scatter": E_sc_pay / 10 / cost,
        "rtp_tiebreak": fs_level["tiebreak"] / 10 / cost,
        "rtp_super": fs_level["super"] / 10 / cost,
        "p_scatter": {str(c): float(p_sc[c]) for c in range(CMAX)},
        "p_bonus": p_trig,
        "bonus_1_in": 1 / p_trig if p_trig else None,
        "p_tiebreak": p_level["tiebreak"],
        "tiebreak_1_in": 1 / p_level["tiebreak"] if p_level["tiebreak"] else None,
        "p_super": p_level["super"],
        "super_1_in": 1 / p_level["super"] if p_level["super"] else None,
        "cond_base_mean_t": cond_base,
        "cycle_boards": float(np.prod([len(x) for x in strips], dtype=np.float64)),
    }


def buy_mode_stats(base_stats: dict, ch: dict, k: int, cost: float, cap: dict | None = None) -> dict:
    """Bought spin = BASE board drawn with the exact conditional law given exactly
    k scatters, then the bonus of that level."""
    e_base = base_stats["cond_base_mean_t"][str(k)] / 10
    e_bonus = ch["by_trigger"][k]["E"] / 10
    unc = e_base + e_bonus
    loss = cap[k]["overshoot_x"] if cap else 0.0
    mean_x = unc - loss
    return {"cost": cost, "scatters": k, "mean_uncapped_x": unc, "cap_loss_x": loss,
            "cap_loss_se_x": cap[k]["se_x"] if cap else 0.0, "p_cap": cap[k]["p_cap"] if cap else None, "level": C.bonus_level(k), "spins": C.FS_AWARD[k],
            "start_multiplier": ch["by_trigger"][k]["start_multiplier"],
            "E_trigger_spin_x": e_base, "E_bonus_x": e_bonus, "mean_x": mean_x, "rtp": mean_x / cost,
            "fair_cost_at_96_5": mean_x / 0.965}


CAP_MC_ROUNDS = 2_000_000


def full_report(cap_rounds: int = CAP_MC_ROUNDS) -> dict:
    t0 = time.time()
    base, free = C.base_reels(), C.free_reels()
    Pf, E1f = joint_stats(free.strips)
    ch = bonus_chain(Pf, E1f)
    ks = sorted(C.FS_AWARD)
    cap_base = {k: cap_overshoot(base.strips, free.strips, k, cap_rounds, 1000 + k) for k in ks} if cap_rounds else None
    modes = {"base": base_mode_stats(base.strips, ch, 1.0, cap_base)}
    cap = {"base": cap_base}
    try:
        bc = C.bonus_chance_reels()
        cap_bc = {k: cap_overshoot(bc.strips, free.strips, k, cap_rounds, 2000 + k) for k in ks} if cap_rounds else None
        modes["bonus_chance"] = base_mode_stats(bc.strips, ch, C.BONUS_CHANCE_COST, cap_bc)
        cap["bonus_chance"] = cap_bc
    except FileNotFoundError:
        pass
    for name, k in C.BUY_SCATTERS.items():
        modes[name] = buy_mode_stats(modes["base"], ch, k, C.mode_costs()[name], cap_base)
    b = modes["base"]
    p_free_w = Pf.sum(axis=1)
    rep = {
        "game": C.GAME_ID,
        "math_version": C.MATH_VERSION,
        "method": ("per-reel generating polynomials (exact) + absorbing Markov chain (exact, uncapped); "
                   "the 5,000x cap correction E[(win-cap)+] is estimated per scatter count by targeted simulation"),
        "cap_correction": {m: ({str(k): v for k, v in c.items()} if c else None) for m, c in cap.items()},
        "modes": modes,
        # base-mode shortcuts (kept for older tooling)
        "rtp": b["rtp"], "rtp_base": b["rtp_base_ways"] + b["rtp_base_scatter"], "p_scatter": b["p_scatter"],
        "cond_base_mean_t": b["cond_base_mean_t"], "p_trigger": b["p_bonus"], "trigger_1_in": b["bonus_1_in"],
        "base_cycle_boards": b["cycle_boards"],
        "free_cycle_boards": float(np.prod(free.lengths, dtype=np.float64)),
        "bonus_by_trigger": {str(k): {**v, "E_x": v["E"] / 10} for k, v in ch["by_trigger"].items()},
        "free_spin_E_ways_x": float(E1f.sum()) / 10,
        "free_spin_p_wild_count": [float(x) for x in p_free_w[:8]],
        "free_spin_p_retrigger": float(Pf[:, 3:].sum()),
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
    for name, m in rep["modes"].items():
        print(name, {k: (round(v, 6) if isinstance(v, float) else v) for k, v in m.items() if k not in ("p_scatter", "cond_base_mean_t")})
    print({k: (round(v["E_x"], 2), v["level"], round(v["P_reach_max_mult"], 3), round(v["E_final_multiplier"], 2)) for k, v in rep["bonus_by_trigger"].items()})
    print("residual", rep["markov_residual"], "time", round(rep["timing_s"], 1))


if __name__ == "__main__":
    main()
