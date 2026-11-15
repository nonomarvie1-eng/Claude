"""Export Stake Engine static math files: index.json, lookup table CSV and
zstd-compressed JSON-lines books, following the format documented in
engineio/math-sdk `docs/rgs_docs/data_format.md`.

How the lookup-table weights are built (stratified + calibrated)
----------------------------------------------------------------
On Stake Engine the RGS draws one book at random, proportionally to its
lookup-table weight.  The published table therefore *is* the game's
probability distribution, so its RTP must match the exact model.

1. Rounds are split into 4 strata whose probabilities are known exactly from
   the full-cycle enumeration: no bonus, bonus with 3, 4 and 5 scatters.
2. Inside each stratum, rounds are sampled with the exact conditional law
   (per-reel scatter patterns drawn with exact weights, then a uniform stop
   among the stops of that pattern), using the reference engine.
3. Sampling noise is removed by minimal exponential tilting inside each
   stratum (w_i ∝ exp(λ x_i), λ solved so that the stratum mean equals its
   exact conditional mean).  The KL divergence from uniform weights is
   reported for every stratum, so the size of the adjustment is visible.
   The adjustment depends only on payouts, never on players or history.
4. Weights are written as uint64 integers whose sum is ~1e15.
"""

from __future__ import annotations

import hashlib
import json
import math
import os

import numpy as np
import zstandard as zstd

from . import config as C
from .engine import make_book, play_round, numpy_drawer, window, positions_of

WEIGHT_TOTAL = 10 ** 15


def _scatter_classes(strips):
    """Per reel: list of stops whose window contains a scatter / not."""
    with_s, without_s = [], []
    for strip in strips:
        n = len(strip)
        ws, wo = [], []
        for s in range(n):
            has = any(strip[(s + k) % n] == C.SCATTER for k in range(C.NUM_ROWS))
            (ws if has else wo).append(s)
        with_s.append(np.array(ws))
        without_s.append(np.array(wo))
    return with_s, without_s


def _patterns(strips, k):
    """All 5-bit scatter patterns with exactly k reels showing a scatter, with
    their exact probabilities (windows show at most one scatter per reel)."""
    with_s, without_s = _scatter_classes(strips)
    pats, probs = [], []
    for m in range(1 << C.NUM_REELS):
        bits = [(m >> r) & 1 for r in range(C.NUM_REELS)]
        if sum(bits) != k:
            continue
        p = 1.0
        for r, b in enumerate(bits):
            n = len(strips[r])
            p *= (len(with_s[r]) if b else len(without_s[r])) / n
        if p > 0:
            pats.append(bits)
            probs.append(p)
    return pats, np.array(probs), with_s, without_s


def _conditional_stop_drawer(strips, k, rng):
    pats, probs, with_s, without_s = _patterns(strips, k)
    cdf = probs / probs.sum()

    def draw():
        bits = pats[rng.choice(len(pats), p=cdf)]
        return [int(rng.choice(with_s[r] if bits[r] else without_s[r])) for r in range(C.NUM_REELS)]

    return draw, float(probs.sum())


def _tilt(x: np.ndarray, target: float) -> tuple[np.ndarray, float, float]:
    """Return weights (sum 1) with weighted mean == target, minimal KL to uniform."""
    x = x.astype(np.float64)
    if not (x.min() < target < x.max()):
        raise ValueError(f"target {target} outside sample range [{x.min()}, {x.max()}]")
    scale = x.std() or 1.0

    def mean_for(lam):
        z = lam * (x - x.max()) / scale
        w = np.exp(z)
        return (w * x).sum() / w.sum()

    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mean_for(mid) < target:
            lo = mid
        else:
            hi = mid
    lam = (lo + hi) / 2
    w = np.exp(lam * (x - x.max()) / scale)
    w /= w.sum()
    n = len(x)
    kl = float((w * np.log(w * n + 1e-300)).sum())
    return w, lam, kl


def export(out_dir: str, n_base: int, n_fs: dict[int, int], seed: int, exact_path: str) -> dict:
    with open(exact_path, encoding="utf-8") as f:
        ex = json.load(f)
    base, free = C.base_reels(), C.free_reels()
    rng = np.random.Generator(np.random.PCG64(seed))
    p_k = {k: ex["p_scatter"][str(k)] for k in (3, 4, 5)}
    p0 = 1.0 - sum(p_k.values())

    # exact conditional means (t-units)
    EB = ex["rtp_base"] * 10
    # E[B * 1{k}] is not stored directly; recompute from enumeration-free formula:
    # E[X | k] = E[B | k] + E[bonus | k]; E[B|k] is computed by sampling-free
    # exact means below.
    cond_B = _exact_cond_base_means()
    strata = []
    # stratum 0: no trigger
    t0 = (EB - sum(p_k[k] * cond_B[k] for k in p_k)) / p0
    strata.append({"name": "no_bonus", "k": 0, "prob": p0, "target_t": t0, "n": n_base})
    for k in (3, 4, 5):
        strata.append({
            "name": f"bonus_{k}_scatters",
            "k": k,
            "prob": p_k[k],
            "target_t": cond_B[k] + ex["bonus_by_trigger"][str(k)]["E"],
            "n": n_fs[k],
        })

    os.makedirs(out_dir, exist_ok=True)
    books_path = os.path.join(out_dir, "books_base.jsonl.zst")
    lut_path = os.path.join(out_dir, "lookUpTable_base_0.csv")
    cctx = zstd.ZstdCompressor(level=19, threads=-1)
    payouts: list[int] = []
    weights_all: list[int] = []
    draw_fs = numpy_drawer(rng)
    book_id = 1
    report_strata = []
    with open(books_path, "wb") as fbin, cctx.stream_writer(fbin) as w:
        for st in strata:
            k = st["k"]
            if k == 0:
                def draw_base():
                    while True:
                        s = [int(rng.integers(0, n)) for n in base.lengths]
                        b = window(base.strips, s)
                        if len(positions_of(b, C.SCATTER)) < 3:
                            return s
            else:
                draw_base, pk_check = _conditional_stop_drawer(base.strips, k, rng)
                assert abs(pk_check - st["prob"]) < 1e-12, (pk_check, st["prob"])
            xs = []
            ids = []
            for _ in range(st["n"]):
                res = play_round(draw_fs, base, free, record_events=True, forced_base_stops=draw_base())
                book = make_book(book_id, res)
                w.write((json.dumps(book, separators=(",", ":")) + "\n").encode("utf-8"))
                xs.append(res.total_t)
                ids.append(book_id)
                book_id += 1
            xs = np.array(xs)
            wts, lam, kl = _tilt(xs, st["target_t"])
            int_w = np.maximum(1, np.round(wts * st["prob"] * WEIGHT_TOTAL)).astype(np.uint64)
            payouts.extend((xs * 10).astype(int).tolist())
            weights_all.extend(int(v) for v in int_w)
            report_strata.append({
                "name": st["name"],
                "probability": st["prob"],
                "books": st["n"],
                "target_mean_x": st["target_t"] / 10,
                "sample_mean_x": float(xs.mean() / 10),
                "tilt_lambda": lam,
                "kl_divergence_from_uniform": kl,
                "max_weight_ratio_vs_uniform": float(wts.max() * len(wts)),
                "min_weight_ratio_vs_uniform": float(wts.min() * len(wts)),
                "max_payout_x": float(xs.max() / 10),
            })

    with open(lut_path, "w", encoding="utf-8", newline="\n") as f:
        for i, (wt, po) in enumerate(zip(weights_all, payouts), start=1):
            f.write(f"{i},{wt},{po}\n")

    index = {"modes": [{"name": "base", "cost": 1.0, "events": "books_base.jsonl.zst", "weights": "lookUpTable_base_0.csv"}]}
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    W = np.array(weights_all, dtype=np.float64)
    P = np.array(payouts, dtype=np.float64) / 100.0
    lut_rtp = float((W * P).sum() / W.sum())
    lut_sd = float(math.sqrt((W * P * P).sum() / W.sum() - lut_rtp ** 2))
    summary = {
        "mode": "base",
        "books": len(payouts),
        "lut_rtp": lut_rtp,
        "exact_model_rtp_uncapped": ex["rtp"],
        "lut_minus_exact": lut_rtp - ex["rtp"],
        "lut_std_dev": lut_sd,
        "lut_hit_rate": float(W[P > 0].sum() / W.sum()),
        "lut_max_payout_x": float(P.max()),
        "weight_sum": int(sum(weights_all)),
        "strata": report_strata,
        "sha256_books": _sha(books_path),
        "sha256_lut": _sha(lut_path),
        "seed": seed,
        "math_version": C.MATH_VERSION,
    }
    with open(os.path.join(out_dir, "export_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _exact_cond_base_means() -> dict[int, float]:
    """E[base spin payout | k scatters] computed by exact enumeration."""
    from .exact import base_stats

    bs = base_stats()
    return {k: bs.sc_EB[k] / bs.sc_prob[k] for k in (3, 4, 5)}


def main() -> None:
    import argparse

    root = os.path.dirname(C.HERE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(root), "stake", "publish_files"))
    ap.add_argument("--n-base", type=int, default=100_000)
    ap.add_argument("--n3", type=int, default=8_000)
    ap.add_argument("--n4", type=int, default=2_000)
    ap.add_argument("--n5", type=int, default=500)
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--exact", default=os.path.join(root, "reports", "exact.json"))
    a = ap.parse_args()
    s = export(a.out, a.n_base, {3: a.n3, 4: a.n4, 5: a.n5}, a.seed, a.exact)
    print(json.dumps({k: v for k, v in s.items() if k != "strata"}, indent=2))
    for st in s["strata"]:
        print(st)


if __name__ == "__main__":
    main()
