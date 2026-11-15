"""Monte-Carlo verification of the exact model, using the reference engine.

Each worker owns an independent PCG64 stream spawned from one SeedSequence,
so the run is reproducible and streams never overlap.  Rounds are i.i.d.:
nothing carries over between rounds.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import time

import numpy as np

from . import config as C
from .engine import numpy_drawer, play_round

MULT_BUCKETS = [0, 0.0001, 0.5, 1, 2, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 5000, 1e12]


def _worker(args: tuple[int, np.random.SeedSequence]) -> dict:
    n, ss = args
    rng = np.random.Generator(np.random.PCG64(ss))
    draw = numpy_drawer(rng)
    base, free = C.base_reels(), C.free_reels()
    tot = np.zeros(n, dtype=np.int64)
    trig = 0
    fs_spins = 0
    retr = 0
    capped = 0
    free_sum = 0
    base_sum = 0
    maxmult_hits = 0
    max_t = 0
    for i in range(n):
        r = play_round(draw, base, free, record_events=False)
        tot[i] = r.total_t
        base_sum += r.base_t
        if r.triggered:
            trig += 1
            fs_spins += r.fs_spins
            retr += r.retriggers
            free_sum += r.free_t
            if r.final_multiplier == C.RALLY_LADDER[-1]:
                maxmult_hits += 1
        if r.capped:
            capped += 1
        if r.total_t > max_t:
            max_t = r.total_t
    return {
        "n": n,
        "sum": int(tot.sum()),
        "sum2": float((tot.astype(np.float64) ** 2).sum()),
        "hits": int((tot > 0).sum()),
        "trig": trig,
        "fs_spins": fs_spins,
        "retr": retr,
        "capped": capped,
        "free_sum": free_sum,
        "base_sum": base_sum,
        "maxmult": maxmult_hits,
        "max_t": max_t,
        "hist": np.histogram(tot / 10.0, bins=MULT_BUCKETS)[0].tolist(),
        "batch_rtps": [float(x) for x in (tot.reshape(-1, 10_000).sum(axis=1) / 1e5)] if n % 10_000 == 0 else [],
    }


def run(n_rounds: int, seed: int, procs: int) -> dict:
    t0 = time.time()
    chunks = procs * 4
    per = n_rounds // chunks
    seqs = np.random.SeedSequence(seed).spawn(chunks)
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        parts = pool.map(_worker, [(per, s) for s in seqs])
    N = sum(p["n"] for p in parts)
    S = sum(p["sum"] for p in parts)
    S2 = sum(p["sum2"] for p in parts)
    mean = S / N / 10
    var = S2 / N / 100 - mean ** 2
    sd = var ** 0.5
    se = sd / N ** 0.5
    hist = np.sum([p["hist"] for p in parts], axis=0)
    trig = sum(p["trig"] for p in parts)
    batch = [x for p in parts for x in p["batch_rtps"]]
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
        "rtp_base_observed": sum(p["base_sum"] for p in parts) / N / 10,
        "rtp_free_observed": sum(p["free_sum"] for p in parts) / N / 10,
        "mean_fs_spins": sum(p["fs_spins"] for p in parts) / trig if trig else None,
        "mean_retriggers": sum(p["retr"] for p in parts) / trig if trig else None,
        "p_bonus_ends_at_max_multiplier": sum(p["maxmult"] for p in parts) / trig if trig else None,
        "capped_rounds": sum(p["capped"] for p in parts),
        "max_win_observed_x": max(p["max_t"] for p in parts) / 10,
        "distribution_buckets_x": MULT_BUCKETS[:-1],
        "distribution_counts": hist.tolist(),
        "batch_rtps_10k": batch,
        "elapsed_s": time.time() - t0,
    }


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(C.HERE), "reports", "montecarlo.json"))
    a = ap.parse_args()
    rep = run(a.n, a.seed, a.procs)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    for k in ["rounds", "rtp_observed", "rtp_ci95", "std_dev", "hit_frequency", "trigger_1_in", "rtp_base_observed", "rtp_free_observed", "capped_rounds", "max_win_observed_x", "elapsed_s"]:
        print(f"{k:>22}: {rep[k]}")


if __name__ == "__main__":
    main()
