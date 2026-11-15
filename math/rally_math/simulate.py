"""Monte-Carlo verification (vectorised, rounds i.i.d.).

Each worker owns an independent PCG64 stream spawned from one SeedSequence.
Base spins are evaluated in large numpy batches; all bonuses of a batch are
then played in lock-step (one free spin per iteration for every active
bonus).  The rules are those of engine.py; test_math.py checks that this fast
path and the reference engine give identical results on the same stops.
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


def _scpay_arr():
    a = np.zeros(C.NUM_REELS + 1, dtype=np.int64)
    for k, v in C.SCATTER_PAY.items():
        a[k] = v
    return a


def simulate_batch(rng: np.random.Generator, n: int, base_cnt, free_cnt, base_len, free_len, forced_base=None):
    """Returns dict of per-round arrays for n rounds."""
    scpay = _scpay_arr()
    ladder = np.array(C.RALLY_LADDER, dtype=np.int64)
    top = len(C.RALLY_LADDER) - 1
    if forced_base is None:
        stops = np.stack([rng.integers(0, L, n) for L in base_len], axis=1)
    else:
        stops = forced_base
    lw, _w, sc = ways_win_vec(base_cnt, stops)
    base_t = lw + scpay[sc]
    trig = sc >= 3
    total = base_t.copy()
    fs_spins = np.zeros(n, dtype=np.int64)
    retr = np.zeros(n, dtype=np.int64)
    final_mult = np.ones(n, dtype=np.int64)
    capped = base_t >= C.WINCAP_T
    idx = np.nonzero(trig & ~capped)[0]
    award = np.zeros(C.NUM_REELS + 1, dtype=np.int64)
    for k, v in C.FS_AWARD.items():
        award[k] = v
    remaining = award[sc[idx]]
    collected = np.zeros(len(idx), dtype=np.int64)
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
        flw, fw, fsc = ways_win_vec(free_cnt, st)
        collected[a] += fw
        mult = ladder[np.minimum(collected[a], top)]
        spin = flw * mult + scpay[fsc]
        free_t[a] += spin
        run_total[a] += spin
        hit_cap = run_total[a] >= C.WINCAP_T
        cap_hit[a[hit_cap]] = True
        add = np.where(fsc >= 3, np.minimum(C.FS_RETRIGGER, C.FS_MAX_REMAINING - remaining[a]), 0)
        add = np.where(hit_cap, 0, np.maximum(add, 0))
        remaining[a] += add
        nretr[a] += (add > 0)
        active[a] = (remaining[a] > 0) & ~hit_cap
    total[idx] = np.minimum(run_total, C.WINCAP_T)
    fs_spins[idx] = nspin
    retr[idx] = nretr
    final_mult[idx] = ladder[np.minimum(collected, top)]
    capped[idx] |= cap_hit
    free_full = np.zeros(n, dtype=np.int64)
    free_full[idx] = free_t
    return {"total": np.minimum(total, C.WINCAP_T), "base": base_t, "free": free_full, "trig": trig,
            "fs_spins": fs_spins, "retr": retr, "final_mult": final_mult, "capped": capped}


def _worker(args):
    n, ss, batch = args
    rng = np.random.Generator(np.random.PCG64(ss))
    base, free = C.base_reels(), C.free_reels()
    bc, fc = count_tables(base.strips), count_tables(free.strips)
    acc = {"n": 0, "sum": 0, "sum2": 0.0, "hits": 0, "trig": 0, "fs": 0, "retr": 0, "capped": 0, "base": 0, "free": 0,
           "maxmult": 0, "max_t": 0, "hist": np.zeros(len(MULT_BUCKETS) - 1, dtype=np.int64), "batch": []}
    done = 0
    while done < n:
        m = min(batch, n - done)
        r = simulate_batch(rng, m, bc, fc, base.lengths, free.lengths)
        t = r["total"]
        acc["n"] += m
        acc["sum"] += int(t.sum())
        acc["sum2"] += float((t.astype(np.float64) ** 2).sum())
        acc["hits"] += int((t > 0).sum())
        acc["trig"] += int(r["trig"].sum())
        acc["fs"] += int(r["fs_spins"].sum())
        acc["retr"] += int(r["retr"].sum())
        acc["capped"] += int(r["capped"].sum())
        acc["base"] += int(r["base"].sum())
        acc["free"] += int(r["free"].sum())
        acc["maxmult"] += int(((r["final_mult"] == C.RALLY_LADDER[-1]) & r["trig"]).sum())
        acc["max_t"] = max(acc["max_t"], int(t.max()))
        acc["hist"] += np.histogram(t / 10.0, bins=MULT_BUCKETS)[0]
        if m % 10_000 == 0:
            acc["batch"] += [float(x) for x in t.reshape(-1, 10_000).sum(axis=1) / 1e5]
        done += m
    acc["hist"] = acc["hist"].tolist()
    return acc


def run(n_rounds: int, seed: int, procs: int, batch: int = 200_000) -> dict:
    t0 = time.time()
    chunks = procs * 4
    per = max(10_000, (n_rounds // chunks) // 10_000 * 10_000)
    seqs = np.random.SeedSequence(seed).spawn(chunks)
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        parts = pool.map(_worker, [(per, s, batch) for s in seqs])
    N = sum(p["n"] for p in parts)
    S = sum(p["sum"] for p in parts)
    S2 = sum(p["sum2"] for p in parts)
    mean = S / N / 10
    sd = (S2 / N / 100 - mean ** 2) ** 0.5
    se = sd / N ** 0.5
    trig = sum(p["trig"] for p in parts)
    return {
        "rounds": N,
        "seed": seed,
        "rng": "numpy PCG64, SeedSequence.spawn per worker",
        "rtp_observed": mean,
        "rtp_std_error": se,
        "rtp_ci95": [mean - 1.96 * se, mean + 1.96 * se],
        "std_dev": sd,
        "hit_frequency": sum(p["hits"] for p in parts) / N,
        "p_trigger": trig / N,
        "trigger_1_in": N / trig if trig else None,
        "rtp_base_observed": sum(p["base"] for p in parts) / N / 10,
        "rtp_free_observed": sum(p["free"] for p in parts) / N / 10,
        "mean_fs_spins": sum(p["fs"] for p in parts) / trig if trig else None,
        "mean_retriggers": sum(p["retr"] for p in parts) / trig if trig else None,
        "p_bonus_ends_at_max_multiplier": sum(p["maxmult"] for p in parts) / trig if trig else None,
        "capped_rounds": sum(p["capped"] for p in parts),
        "max_win_observed_x": max(p["max_t"] for p in parts) / 10,
        "distribution_buckets_x": MULT_BUCKETS[:-1],
        "distribution_counts": np.sum([p["hist"] for p in parts], axis=0).tolist(),
        "batch_rtps_10k": [x for p in parts for x in p["batch"]],
        "elapsed_s": time.time() - t0,
    }


def run_buy(n_rounds: int, seed: int) -> dict:
    """Monte-Carlo of the bonus-buy mode (independent check of exact buy RTP)."""
    from .export_stake import bonus_pilot, conditional_base_stops

    rng = np.random.Generator(np.random.PCG64(seed))
    base, free = C.base_reels(), C.free_reels()
    bc, fc = count_tables(base.strips), count_tables(free.strips)
    tot_sum = 0.0
    tot_sq = 0.0
    done = 0
    mx = 0
    ks = list(C.BUY_SCATTER_WEIGHTS)
    q = np.array([C.BUY_SCATTER_WEIGHTS[k] for k in ks], dtype=float)
    q /= q.sum()
    while done < n_rounds:
        m = min(500_000, n_rounds - done)
        counts = rng.multinomial(m, q)
        parts = []
        for k, c in zip(ks, counts):
            if c:
                bs, _ = conditional_base_stops(base.strips, k, rng, int(c))
                parts.append(bonus_pilot(rng, bs, bc, fc, free.lengths)[0])
        tot = np.concatenate(parts)
        x = tot.astype(np.float64) / 10
        tot_sum += x.sum()
        tot_sq += (x * x).sum()
        mx = max(mx, float(x.max()))
        done += m
    mean = tot_sum / n_rounds
    sd = (tot_sq / n_rounds - mean ** 2) ** 0.5
    return {"rounds": n_rounds, "cost": C.BUY_COST, "mean_x": mean, "rtp_observed": mean / C.BUY_COST,
            "rtp_std_error": sd / n_rounds ** 0.5 / C.BUY_COST, "std_dev_x": sd, "max_win_observed_x": mx}


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=50_000_000)
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(C.HERE), "reports", "montecarlo.json"))
    ap.add_argument("--buy", type=int, default=2_000_000, help="bonus-buy rounds to simulate")
    a = ap.parse_args()
    rep = run(a.n, a.seed, a.procs)
    rep["buy"] = run_buy(a.buy, a.seed + 1)
    print("buy:", rep["buy"])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    for k in ["rounds", "rtp_observed", "rtp_ci95", "std_dev", "hit_frequency", "trigger_1_in", "rtp_base_observed",
              "rtp_free_observed", "mean_fs_spins", "p_bonus_ends_at_max_multiplier", "capped_rounds", "max_win_observed_x", "elapsed_s"]:
        print(f"{k:>30}: {rep[k]}")


if __name__ == "__main__":
    main()
