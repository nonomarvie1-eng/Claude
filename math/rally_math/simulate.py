"""Monte-Carlo verification of every bet mode (vectorised, rounds i.i.d.).

Each worker owns an independent PCG64 stream spawned from one SeedSequence.
Base spins are evaluated in large numpy batches; all bonuses of a batch are
then played in lock-step (one free spin per iteration for every active
bonus).  The rules are those of engine.py; test_math.py checks that this fast
path and the reference engine give identical results on the same stops.

Modes:
  base          BASE reels, cost 1
  bonus_chance  BASE_BC reels, cost BONUS_CHANCE_COST
  buy_rally     bought spin = BASE board with exactly 3 scatters (exact conditional law)
  buy_final     bought spin = BASE board with exactly 4 scatters
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import time

import numpy as np

from . import config as C
from .engine import count_tables, ways_win_vec

MULT_BUCKETS = [0, 0.0001, 0.5, 1, 2, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 5000, 1e12]


def _arr(d):
    a = np.zeros(C.NUM_REELS + 1, dtype=np.int64)
    for k, v in d.items():
        a[k] = v
    return a


def play_vec(rng: np.random.Generator, stops: np.ndarray, base_cnt, free_cnt, free_len, log: list | None = None, free=None) -> dict:
    """Plays complete rounds whose base stops are given (bonus = THE FINAL SET).
    If `log` is a list, every bonus iteration appends (round indices, stops, aux)."""
    from .bonus import play_bonus_vec

    n = stops.shape[0]
    free = free or C.free_reels()
    scpay, award = _arr(C.SCATTER_PAY), _arr(C.FS_AWARD)
    lw, _w, sc = ways_win_vec(base_cnt, stops)
    base_t = lw + scpay[sc]
    capped = base_t >= C.WINCAP_T
    trig = (sc >= 3) & ~capped
    idx = np.nonzero(trig)[0]
    level = (sc[idx] >= 4).astype(np.int64)
    r = play_bonus_vec(rng, level, award[sc[idx]], base_t[idx], free, log, idx)
    total = base_t.copy()
    total[idx] += r["win_t"]
    total = np.minimum(total, C.WINCAP_T)
    full = np.zeros(n, dtype=np.int64)
    full[idx] = r["win_t"]
    capped = capped.copy()
    capped[idx] |= r["capped"]
    stats = {k: v for k, v in r.items() if k not in ("win_t", "capped")}
    return {"total": total, "base": base_t, "free": full, "sc": sc, "trig": trig, "capped": capped, "bonus_idx": idx, "bonus_stats": stats,
            "bonus_level": level}


def mode_reels(mode: str):
    base = C.bonus_chance_reels() if mode == "bonus_chance" else C.base_reels()
    return base, C.free_reels()


def draw_stops(rng, mode, base, n):
    if mode in C.BUY_SCATTERS:
        from .export_stake import conditional_base_stops

        return conditional_base_stops(base.strips, C.BUY_SCATTERS[mode], rng, n)[0]
    return np.stack([rng.integers(0, L, n) for L in base.lengths], axis=1)


SHOTS = ["RALLY", "ACE", "SMASH", "PASSING", "DROP", "GOLDEN"]
BSTAT = SHOTS + ["hawk", "hawk_in", "marks_set", "mark_hits", "mark_expired", "cp", "extensions", "played", "slam"]
BONUS_BUCKETS = [0, 5, 10, 20, 50, 100, 200, 500, 1000, 5000, 1e12]


def _worker(args):
    mode, n, ss, batch = args
    rng = np.random.Generator(np.random.PCG64(ss))
    base, free = mode_reels(mode)
    bc, fc = count_tables(base.strips), count_tables(free.strips)
    acc = {"n": 0, "sum": 0, "sum2": 0.0, "hits": 0, "sc3": 0, "sc4p": 0, "tb": 0, "stb": 0, "capped": 0,
           "base": 0, "free_tb": 0, "free_stb": 0, "max_t": 0, "max_bonus_t": 0, "hist": np.zeros(len(MULT_BUCKETS) - 1, dtype=np.int64),
           "bstat": {lv: {k: 0 for k in BSTAT} for lv in ("rally", "final")},
           "bonus_sum2": {"rally": 0.0, "final": 0.0},
           "bonus_hist": {lv: np.zeros(len(BONUS_BUCKETS) - 1, dtype=np.int64) for lv in ("rally", "final")},
           "ceremony": {lv: {"none": 0, "trophy": 0, "grand": 0} for lv in ("rally", "final")}, "batch": []}
    done = 0
    while done < n:
        m = min(batch, n - done)
        r = play_vec(rng, draw_stops(rng, mode, base, m), bc, fc, free.lengths, free=free)
        t = r["total"]
        tb = r["trig"] & (r["sc"] == 3)
        stb = r["trig"] & (r["sc"] >= 4)
        acc["n"] += m
        acc["sum"] += int(t.sum())
        acc["sum2"] += float((t.astype(np.float64) ** 2).sum())
        acc["hits"] += int((t > 0).sum())
        acc["sc3"] += int((r["sc"] == 3).sum())
        acc["sc4p"] += int((r["sc"] >= 4).sum())
        acc["tb"] += int(tb.sum())
        acc["stb"] += int(stb.sum())
        acc["capped"] += int(r["capped"].sum())
        acc["base"] += int(r["base"].sum())
        acc["free_tb"] += int(r["free"][tb].sum())
        acc["free_stb"] += int(r["free"][stb].sum())
        acc["max_t"] = max(acc["max_t"], int(t.max()))
        acc["hist"] += np.histogram(t / 10.0, bins=MULT_BUCKETS)[0]
        bwin = r["free"][r["bonus_idx"]]
        if len(bwin):
            acc["max_bonus_t"] = max(acc["max_bonus_t"], int(bwin.max()))
        for li, lv in enumerate(("rally", "final")):
            sel = r["bonus_level"] == li
            for k in BSTAT:
                acc["bstat"][lv][k] += int(r["bonus_stats"][k][sel].sum())
            bx = bwin[sel] / 10
            acc["bonus_sum2"][lv] += float((bx ** 2).sum())
            acc["bonus_hist"][lv] += np.histogram(bx, bins=BONUS_BUCKETS)[0]
            acc["ceremony"][lv]["grand"] += int((bx >= C.CEREMONY_X["grand"]).sum())
            acc["ceremony"][lv]["trophy"] += int(((bx >= C.CEREMONY_X["trophy"]) & (bx < C.CEREMONY_X["grand"])).sum())
            acc["ceremony"][lv]["none"] += int((bx < C.CEREMONY_X["trophy"]).sum())
        if m % 10_000 == 0:
            acc["batch"] += [float(x) for x in t.reshape(-1, 10_000).sum(axis=1) / 1e5]
        done += m
    acc["hist"] = acc["hist"].tolist()
    acc["bonus_hist"] = {k: v.tolist() for k, v in acc["bonus_hist"].items()}
    return acc


def run(mode: str, n_rounds: int, seed: int, procs: int, batch: int = 200_000) -> dict:
    t0 = time.time()
    cost = C.mode_costs()[mode]
    chunks = procs * 4
    per = max(10_000, (n_rounds // chunks) // 10_000 * 10_000)
    seqs = np.random.SeedSequence(seed).spawn(chunks)
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        parts = pool.map(_worker, [(mode, per, s, batch) for s in seqs])
    g = lambda k: sum(p[k] for p in parts)  # noqa: E731
    N = g("n")
    mean = g("sum") / N / 10  # in base-bet units
    sd = (g("sum2") / N / 100 - mean ** 2) ** 0.5
    se = sd / N ** 0.5
    trig = g("tb") + g("stb")
    one_in = lambda k: (N / g(k)) if g(k) else None  # noqa: E731
    bonus = {}
    for lv, cnt_key, win_key in (("rally", "tb", "free_tb"), ("final", "stb", "free_stb")):
        nb = g(cnt_key)
        if not nb:
            continue
        bs = {k: sum(p["bstat"][lv][k] for p in parts) for k in BSTAT}
        bmean = g(win_key) / nb / 10
        sd_b = (sum(p["bonus_sum2"][lv] for p in parts) / nb - bmean ** 2) ** 0.5
        ex = bs["played"]
        bonus[lv] = {
            "count": nb, "mean_bonus_win_x": bmean, "se_x": sd_b / nb ** 0.5, "std_dev_x": sd_b,
            "mean_exchanges": ex / nb, "mean_extensions": bs["extensions"] / nb,
            "shot_freq_per_exchange": {k: bs[k] / ex for k in SHOTS},
            "hawk_per_exchange": bs["hawk"] / ex, "hawk_in_share": bs["hawk_in"] / bs["hawk"] if bs["hawk"] else None,
            "hawk_per_bonus": bs["hawk"] / nb,
            "marks_set_per_bonus": bs["marks_set"] / nb, "mark_hits_per_bonus": bs["mark_hits"] / nb,
            "marks_expired_per_bonus": bs["mark_expired"] / nb, "championship_points_per_bonus": bs["cp"] / nb,
            "grand_slam_per_bonus": bs["slam"] / nb,
            "ceremony_share": {k: v / nb for k, v in {kk: sum(p["ceremony"][lv][kk] for p in parts) for kk in ("none", "trophy", "grand")}.items()},
            "bonus_win_buckets_x": BONUS_BUCKETS[:-1],
            "bonus_win_counts": np.sum([p["bonus_hist"][lv] for p in parts], axis=0).tolist(),
        }
    return {
        "mode": mode,
        "cost": cost,
        "rounds": N,
        "seed": seed,
        "rng": "numpy PCG64, SeedSequence.spawn per worker",
        "mean_win_x": mean,
        "rtp_observed": mean / cost,
        "rtp_std_error": se / cost,
        "rtp_ci95": [(mean - 1.96 * se) / cost, (mean + 1.96 * se) / cost],
        "std_dev_x": sd,
        "std_dev_per_cost": sd / cost,
        "hit_frequency": g("hits") / N,
        "p_3_scatters": g("sc3") / N,
        "p_4plus_scatters": g("sc4p") / N,
        "p_bonus": trig / N,
        "bonus_1_in": N / trig if trig else None,
        "tiebreak_1_in": one_in("tb"),
        "super_1_in": one_in("stb"),
        "rtp_base_observed": g("base") / N / 10 / cost,
        "rtp_tiebreak_observed": g("free_tb") / N / 10 / cost,
        "rtp_super_observed": g("free_stb") / N / 10 / cost,
        "bonus": bonus,
        "max_bonus_win_observed_x": max(p["max_bonus_t"] for p in parts) / 10,
        "capped_rounds": g("capped"),
        "max_win_observed_x": max(p["max_t"] for p in parts) / 10,
        "distribution_buckets_x": MULT_BUCKETS[:-1],
        "distribution_counts": np.sum([p["hist"] for p in parts], axis=0).tolist(),
        "batch_means_10k_x": [x for p in parts for x in p["batch"]][:2000],
        "elapsed_s": time.time() - t0,
    }


DEFAULT_ROUNDS = {"base": 20_000_000, "bonus_chance": 20_000_000, "buy_rally": 2_000_000, "buy_final": 2_000_000}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="base,bonus_chance,buy_rally,buy_final")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply the default round counts")
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(C.HERE), "reports", "montecarlo.json"))
    a = ap.parse_args()
    out = {}
    if os.path.exists(a.out):
        try:
            out = json.load(open(a.out, encoding="utf-8")).get("modes", {})
        except Exception:
            out = {}
    for i, mode in enumerate(a.modes.split(",")):
        rep = run(mode, int(DEFAULT_ROUNDS[mode] * a.scale), a.seed + 1000 * i, a.procs)
        out[mode] = rep
        print(mode, {k: rep[k] for k in ("rounds", "rtp_observed", "rtp_ci95", "std_dev_x", "hit_frequency", "bonus_1_in",
                                         "tiebreak_1_in", "super_1_in", "max_win_observed_x", "elapsed_s")})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"modes": out}, f, indent=2)


if __name__ == "__main__":
    main()
