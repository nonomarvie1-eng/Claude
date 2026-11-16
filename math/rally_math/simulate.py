"""Monte-Carlo verification of every bet mode (vectorised, rounds i.i.d.).

Each worker owns an independent PCG64 stream spawned from one SeedSequence.
Base spins are evaluated in large numpy batches; all bonuses of a batch are
then played in lock-step (one free spin per iteration for every active
bonus).  The rules are those of engine.py; test_math.py checks that this fast
path and the reference engine give identical results on the same stops.

Modes:
  base          BASE reels, cost 1
  bonus_chance  BASE_BC reels, cost BONUS_CHANCE_COST
  buy_tiebreak  bought spin = BASE board with exactly 3 scatters (exact conditional law)
  buy_super     bought spin = BASE board with exactly 4 scatters
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


def play_vec(rng: np.random.Generator, stops: np.ndarray, base_cnt, free_cnt, free_len, log: list | None = None) -> dict:
    """Plays complete rounds whose base stops are given.  If `log` is a list,
    the free-spin stops of every iteration are appended to it as (indices, stops)."""
    n = stops.shape[0]
    scpay, award = _arr(C.SCATTER_PAY), _arr(C.FS_AWARD)
    ladder = np.array(C.RALLY_LADDER, dtype=np.int64)
    top = len(C.RALLY_LADDER) - 1
    lw, _w, sc = ways_win_vec(base_cnt, stops)
    base_t = lw + scpay[sc]
    capped = base_t >= C.WINCAP_T
    trig = (sc >= 3) & ~capped
    idx = np.nonzero(trig)[0]
    start = np.where(sc[idx] == 3, C.BONUS_LEVELS["tiebreak"]["start_index"], C.BONUS_LEVELS["super"]["start_index"])
    remaining = award[sc[idx]]
    pos = start.copy()  # ladder position = start + wilds collected
    free_t = np.zeros(len(idx), dtype=np.int64)
    run_total = base_t[idx].copy()
    active = np.ones(len(idx), dtype=bool)
    nspin = np.zeros(len(idx), dtype=np.int64)
    nretr = np.zeros(len(idx), dtype=np.int64)
    cap_hit = np.zeros(len(idx), dtype=bool)
    while active.any():
        a = np.nonzero(active)[0]
        remaining[a] -= 1
        nspin[a] += 1
        st = np.stack([rng.integers(0, L, len(a)) for L in free_len], axis=1)
        if log is not None:
            log.append((idx[a], st))
        flw, fw, fsc = ways_win_vec(free_cnt, st)
        pos[a] += fw
        spin = flw * ladder[np.minimum(pos[a], top)] + scpay[fsc]
        free_t[a] += spin
        run_total[a] += spin
        hit_cap = run_total[a] >= C.WINCAP_T
        cap_hit[a[hit_cap]] = True
        add = np.where(fsc >= 3, np.minimum(C.FS_RETRIGGER, C.FS_MAX_REMAINING - remaining[a]), 0)
        add = np.where(hit_cap, 0, np.maximum(add, 0))
        remaining[a] += add
        nretr[a] += add > 0
        active[a] = (remaining[a] > 0) & ~hit_cap
    total = base_t.copy()
    total[idx] = run_total
    total = np.minimum(total, C.WINCAP_T)
    full = lambda v, fill=0: (lambda z: (z.__setitem__(idx, v), z)[1])(np.full(n, fill, dtype=np.int64))  # noqa: E731
    capped = capped.copy()
    capped[idx] |= cap_hit
    return {"total": total, "base": base_t, "free": full(free_t), "sc": sc, "trig": trig,
            "fs_spins": full(nspin), "retr": full(nretr), "final_mult": full(ladder[np.minimum(pos, top)], 1), "capped": capped}


def mode_reels(mode: str):
    base = C.bonus_chance_reels() if mode == "bonus_chance" else C.base_reels()
    return base, C.free_reels()


def draw_stops(rng, mode, base, n):
    if mode in C.BUY_SCATTERS:
        from .export_stake import conditional_base_stops

        return conditional_base_stops(base.strips, C.BUY_SCATTERS[mode], rng, n)[0]
    return np.stack([rng.integers(0, L, n) for L in base.lengths], axis=1)


def _worker(args):
    mode, n, ss, batch = args
    rng = np.random.Generator(np.random.PCG64(ss))
    base, free = mode_reels(mode)
    bc, fc = count_tables(base.strips), count_tables(free.strips)
    nl = len(C.RALLY_LADDER)
    acc = {"n": 0, "sum": 0, "sum2": 0.0, "hits": 0, "sc3": 0, "sc4p": 0, "tb": 0, "stb": 0, "fs": 0, "retr": 0, "capped": 0,
           "base": 0, "free_tb": 0, "free_stb": 0, "max_t": 0, "hist": np.zeros(len(MULT_BUCKETS) - 1, dtype=np.int64),
           "mult_tb": np.zeros(nl, dtype=np.int64), "mult_stb": np.zeros(nl, dtype=np.int64), "batch": []}
    done = 0
    while done < n:
        m = min(batch, n - done)
        r = play_vec(rng, draw_stops(rng, mode, base, m), bc, fc, free.lengths)
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
        acc["fs"] += int(r["fs_spins"].sum())
        acc["retr"] += int(r["retr"].sum())
        acc["capped"] += int(r["capped"].sum())
        acc["base"] += int(r["base"].sum())
        acc["free_tb"] += int(r["free"][tb].sum())
        acc["free_stb"] += int(r["free"][stb].sum())
        acc["max_t"] = max(acc["max_t"], int(t.max()))
        acc["hist"] += np.histogram(t / 10.0, bins=MULT_BUCKETS)[0]
        lad = {v: i for i, v in enumerate(C.RALLY_LADDER)}
        for mv in r["final_mult"][tb]:
            acc["mult_tb"][lad[int(mv)]] += 1
        for mv in r["final_mult"][stb]:
            acc["mult_stb"][lad[int(mv)]] += 1
        if m % 10_000 == 0:
            acc["batch"] += [float(x) for x in t.reshape(-1, 10_000).sum(axis=1) / 1e5]
        done += m
    for k in ("hist", "mult_tb", "mult_stb"):
        acc[k] = acc[k].tolist()
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
    mult_tb = np.sum([p["mult_tb"] for p in parts], axis=0)
    mult_stb = np.sum([p["mult_stb"] for p in parts], axis=0)
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
        "mean_fs_spins": g("fs") / trig if trig else None,
        "mean_retriggers": g("retr") / trig if trig else None,
        "final_multiplier_ladder": C.RALLY_LADDER,
        "final_multiplier_tiebreak": (mult_tb / max(1, mult_tb.sum())).tolist(),
        "final_multiplier_super": (mult_stb / max(1, mult_stb.sum())).tolist(),
        "bonus_counts": {"tiebreak": int(mult_tb.sum()), "super": int(mult_stb.sum())},
        "capped_rounds": g("capped"),
        "max_win_observed_x": max(p["max_t"] for p in parts) / 10,
        "distribution_buckets_x": MULT_BUCKETS[:-1],
        "distribution_counts": np.sum([p["hist"] for p in parts], axis=0).tolist(),
        "batch_means_10k_x": [x for p in parts for x in p["batch"]][:2000],
        "elapsed_s": time.time() - t0,
    }


DEFAULT_ROUNDS = {"base": 20_000_000, "bonus_chance": 20_000_000, "buy_tiebreak": 2_000_000, "buy_super": 2_000_000}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="base,bonus_chance,buy_tiebreak,buy_super")
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
