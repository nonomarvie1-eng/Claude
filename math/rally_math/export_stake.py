"""Export Stake Engine static math files (index.json, lookup table CSV,
zstd JSON-lines books) — format of engineio/math-sdk docs/rgs_docs/data_format.md.

Lookup-table construction (stratified, calibrated, tail-complete)
----------------------------------------------------------------
On Stake Engine the RGS draws one book proportionally to its weight, so the
published table *is* the game's distribution.

1. Strata with exactly known probabilities (full-cycle exact computation):
   no bonus, and bonus triggered with 3, 4, 5, 6 Trophies.
2. Inside each bonus stratum, rounds are split into payout bands
   (< 500x, 500x-2000x, >= 2000x).  Band probabilities P(band | k) are
   estimated by a large vectorised Monte-Carlo pilot (reported with counts);
   books for each band are drawn by rejection from that pilot, so the rare
   big wins (up to the 5,000x cap) really exist in the table.
3. Every book is rebuilt by the reference engine from its recorded stops and
   must reproduce the pilot payout exactly (fast path == reference path).
4. Minimal exponential tilting inside each scatter stratum makes its mean
   equal to the exact conditional mean (KL divergence reported).
5. Weights are uint64 integers summing to ~1e15.
"""

from __future__ import annotations

import hashlib
import json
import math
import os

import numpy as np
import zstandard as zstd

from . import config as C
from .engine import count_tables, list_drawer, make_book, play_round, positions_of, window, ways_win_vec

WEIGHT_TOTAL = 10 ** 15
BANDS_X = [0, 500, 2000, 4000, 10 ** 9]


def _scatter_classes(strips):
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
    with_s, without_s = _scatter_classes(strips)
    pats, probs = [], []
    for m in range(1 << C.NUM_REELS):
        bits = [(m >> r) & 1 for r in range(C.NUM_REELS)]
        if sum(bits) != k:
            continue
        p = 1.0
        for r, b in enumerate(bits):
            p *= (len(with_s[r]) if b else len(without_s[r])) / len(strips[r])
        if p > 0:
            pats.append(bits)
            probs.append(p)
    return pats, np.array(probs), with_s, without_s


def conditional_base_stops(strips, k, rng, n):
    """n base-stop vectors with exactly k scatters, drawn with the exact conditional law."""
    pats, probs, with_s, without_s = _patterns(strips, k)
    choice = rng.choice(len(pats), size=n, p=probs / probs.sum())
    out = np.zeros((n, C.NUM_REELS), dtype=np.int64)
    for r in range(C.NUM_REELS):
        bits = np.array([pats[c][r] for c in choice])
        a = rng.choice(with_s[r], size=n)
        b = rng.choice(without_s[r], size=n)
        out[:, r] = np.where(bits == 1, a, b)
    return out, float(probs.sum())


def bonus_pilot(rng, base_stops, base_cnt, free_cnt, free_len, award_override=None):
    """Vectorised play of bonus rounds whose base stops are given; records free stops."""
    n = base_stops.shape[0]
    scpay = np.zeros(C.NUM_REELS + 1, dtype=np.int64)
    for kk, v in C.SCATTER_PAY.items():
        scpay[kk] = v
    award = np.zeros(C.NUM_REELS + 1, dtype=np.int64)
    for kk, v in C.FS_AWARD.items():
        award[kk] = v
    ladder = np.array(C.RALLY_LADDER, dtype=np.int64)
    top = len(C.RALLY_LADDER) - 1
    lw, _w, sc = ways_win_vec(base_cnt, base_stops)
    total = lw + scpay[sc]
    remaining = award[sc] if award_override is None else np.full(n, award_override, dtype=np.int64)
    collected = np.zeros(n, dtype=np.int64)
    active = remaining > 0
    log: list[tuple[np.ndarray, np.ndarray]] = []
    while active.any():
        a = np.nonzero(active)[0]
        remaining[a] -= 1
        st = np.stack([rng.integers(0, L, len(a)) for L in free_len], axis=1)
        log.append((a, st))
        flw, fw, fsc = ways_win_vec(free_cnt, st)
        collected[a] += fw
        total[a] += flw * ladder[np.minimum(collected[a], top)] + scpay[fsc]
        hit = total[a] >= C.WINCAP_T
        add = np.where(fsc >= 3, np.minimum(C.FS_RETRIGGER, C.FS_MAX_REMAINING - remaining[a]), 0)
        add = np.where(hit, 0, np.maximum(add, 0))
        remaining[a] += add
        active[a] = (remaining[a] > 0) & ~hit
    return np.minimum(total, C.WINCAP_T), log


def stops_of(i, base_stops, log):
    seq = [list(map(int, base_stops[i]))]
    for a, st in log:
        j = np.searchsorted(a, i)
        if j < len(a) and a[j] == i:
            seq.append(list(map(int, st[j])))
    return seq


def _tilt(x: np.ndarray, w0: np.ndarray, target: float):
    """Weights w ∝ w0·exp(λx), Σw=1, weighted mean == target (min KL to w0)."""
    x = x.astype(np.float64)
    w0 = w0 / w0.sum()
    scale = x.std() or 1.0

    def weights(lam):
        z = lam * x / scale
        z = z - z.max()
        w = w0 * np.exp(z)
        return w / w.sum()

    lo, hi = -60.0, 60.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if (weights(mid) * x).sum() < target:
            lo = mid
        else:
            hi = mid
    w = weights((lo + hi) / 2)
    kl = float((w * np.log(w / w0 + 1e-300)).sum())
    return w, (lo + hi) / 2, kl


def export(out_dir, n_base, plan, pilot_n, seed, exact_path):
    ex = json.load(open(exact_path, encoding="utf-8"))
    base, free = C.base_reels(), C.free_reels()
    bc, fc = count_tables(base.strips), count_tables(free.strips)
    rng = np.random.Generator(np.random.PCG64(seed))
    ks = [k for k in sorted(C.FS_AWARD) if ex["p_scatter"].get(str(k), 0) > 0]
    p_k = {k: ex["p_scatter"][str(k)] for k in ks}
    p0 = 1.0 - sum(p_k.values())
    EB = ex["rtp_base"] * 10
    cond = {k: ex["cond_base_mean_t"][str(k)] for k in ks}
    os.makedirs(out_dir, exist_ok=True)
    books_path = os.path.join(out_dir, "books_base.jsonl.zst")
    lut_path = os.path.join(out_dir, "lookUpTable_base_0.csv")
    cctx = zstd.ZstdCompressor(level=19, threads=-1)
    payouts, weights = [], []
    rep_strata = []
    book_id = 1
    with open(books_path, "wb") as fbin, cctx.stream_writer(fbin) as wtr:
        def write(res):
            nonlocal book_id
            b = make_book(book_id, res)
            wtr.write((json.dumps(b, separators=(",", ":")) + "\n").encode())
            book_id += 1
            return res.total_t

        # ---- stratum 0: no bonus
        xs = []
        while len(xs) < n_base:
            s = [int(rng.integers(0, L)) for L in base.lengths]
            if len(positions_of(window(base.strips, s), C.SCATTER)) >= 3:
                continue
            xs.append(write(play_round(None, base, free, True, forced_base_stops=s)))
        xs = np.array(xs)
        target0 = (EB - sum(p_k[k] * cond[k] for k in ks)) / p0
        w, lam, kl = _tilt(xs, np.ones(len(xs)), target0)
        payouts += (xs * 10).tolist()
        weights += [max(1, int(round(v))) for v in w * p0 * WEIGHT_TOTAL]
        rep_strata.append({"name": "no_bonus", "probability": p0, "books": len(xs), "target_mean_x": target0 / 10,
                           "sample_mean_x": float(xs.mean() / 10), "kl": kl, "max_payout_x": float(xs.max() / 10), "bands": None})

        # ---- bonus strata
        for k in ks:
            target = cond[k] + ex["bonus_by_trigger"][str(k)]["E"]
            bs, pk_check = conditional_base_stops(base.strips, k, rng, pilot_n)
            assert abs(pk_check - p_k[k]) < 1e-12
            tot, log = bonus_pilot(rng, bs, bc, fc, free.lengths)
            band_of = np.digitize(tot / 10, BANDS_X) - 1
            xs_all, w0_all, band_rep = [], [], []
            for b in range(len(BANDS_X) - 1):
                members = np.nonzero(band_of == b)[0]
                p_band = len(members) / pilot_n
                want = plan[k][b]
                if len(members) == 0 or want == 0:
                    band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "books": 0})
                    continue
                pick = members if len(members) <= want else rng.choice(members, size=want, replace=False)
                for i in pick:
                    seq = stops_of(int(i), bs, log)
                    res = play_round(list_drawer(seq[1:]), base, free, True, forced_base_stops=seq[0])
                    assert res.total_t == int(tot[i]), "fast path and reference engine disagree"
                    xs_all.append(write(res))
                    w0_all.append(p_band / len(pick))
                band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "p_band": p_band, "books": int(len(pick))})
            xs = np.array(xs_all)
            w, lam, kl = _tilt(xs, np.array(w0_all), target)
            payouts += (xs * 10).tolist()
            weights += [max(1, int(round(v))) for v in w * p_k[k] * WEIGHT_TOTAL]
            rep_strata.append({"name": f"bonus_{k}_trophies", "probability": p_k[k], "books": len(xs), "target_mean_x": target / 10,
                               "sample_mean_x": float((xs * np.array(w0_all)).sum() / np.sum(w0_all) / 10), "kl": kl,
                               "max_payout_x": float(xs.max() / 10), "pilot_rounds": pilot_n, "bands": band_rep})

    with open(lut_path, "w", encoding="utf-8", newline="\n") as f:
        for i, (wt, po) in enumerate(zip(weights, payouts), start=1):
            f.write(f"{i},{wt},{int(po)}\n")
    bonus_summary = export_buy_mode(out_dir, ex, base, free, bc, fc, rng, pilot_n, BUY_PLAN)
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"modes": [
            {"name": "base", "cost": 1.0, "events": "books_base.jsonl.zst", "weights": "lookUpTable_base_0.csv"},
            {"name": "bonus", "cost": float(C.BUY_COST), "events": "books_bonus.jsonl.zst", "weights": "lookUpTable_bonus_0.csv"},
        ]}, f, indent=4)
    W = np.array(weights, dtype=np.float64)
    P = np.array(payouts, dtype=np.float64) / 100
    rtp = float((W * P).sum() / W.sum())
    summary = {
        "mode": "base", "books": len(payouts), "lut_rtp": rtp, "exact_model_rtp_uncapped": ex["rtp"],
        "lut_minus_exact": rtp - ex["rtp"], "lut_std_dev": float(math.sqrt((W * P * P).sum() / W.sum() - rtp ** 2)),
        "lut_hit_rate": float(W[P > 0].sum() / W.sum()), "lut_max_payout_x": float(P.max()),
        "weight_sum": int(sum(weights)), "strata": rep_strata, "sha256_books": _sha(books_path), "sha256_lut": _sha(lut_path),
        "seed": seed, "math_version": C.MATH_VERSION, "bonus": bonus_summary,
    }
    json.dump(summary, open(os.path.join(out_dir, "export_summary.json"), "w"), indent=2)
    return summary


def export_buy_mode(out_dir, ex, base, free, bc, fc, rng, pilot_n, plan_row):
    """Bet mode 'bonus' (cost BUY_COST): base board with exactly BUY_SCATTERS
    trophies (exact conditional law), Tie-Break of BUY_SPINS spins."""
    k = C.BUY_SCATTERS
    target = ex["buy"]["E_x"] * 10  # exact E[payout | bought round], t-units
    books_path = os.path.join(out_dir, "books_bonus.jsonl.zst")
    lut_path = os.path.join(out_dir, "lookUpTable_bonus_0.csv")
    cctx = zstd.ZstdCompressor(level=19, threads=-1)
    bs, _ = conditional_base_stops(base.strips, k, rng, pilot_n)
    tot, log = bonus_pilot(rng, bs, bc, fc, free.lengths, award_override=C.BUY_SPINS)
    band_of = np.digitize(tot / 10, BANDS_X) - 1
    xs, w0, band_rep = [], [], []
    book_id = 1
    with open(books_path, "wb") as fbin, cctx.stream_writer(fbin) as wtr:
        for b in range(len(BANDS_X) - 1):
            members = np.nonzero(band_of == b)[0]
            p_band = len(members) / pilot_n
            want = plan_row[b]
            if len(members) == 0 or want == 0:
                band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "books": 0})
                continue
            pick = members if len(members) <= want else rng.choice(members, size=want, replace=False)
            for i in pick:
                seq = stops_of(int(i), bs, log)
                res = play_round(list_drawer(seq[1:]), base, free, True, forced_base_stops=seq[0], bought=True)
                assert res.total_t == int(tot[i]), "fast path and reference engine disagree (buy mode)"
                book = make_book(book_id, res)
                wtr.write((json.dumps(book, separators=(",", ":")) + "\n").encode())
                book_id += 1
                xs.append(res.total_t)
                w0.append(p_band / len(pick))
            band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "p_band": p_band, "books": int(len(pick))})
    xs = np.array(xs)
    w, lam, kl = _tilt(xs, np.array(w0), target)
    weights = [max(1, int(round(v))) for v in w * WEIGHT_TOTAL]
    with open(lut_path, "w", encoding="utf-8", newline="\n") as f:
        for i, (wt, po) in enumerate(zip(weights, xs * 10), start=1):
            f.write(f"{i},{wt},{int(po)}\n")
    W = np.array(weights, dtype=np.float64)
    P = xs.astype(np.float64) / 10
    mean = float((W * P).sum() / W.sum())
    return {"mode": "bonus", "cost": C.BUY_COST, "books": len(xs), "lut_mean_x": mean, "lut_rtp": mean / C.BUY_COST,
            "exact_rtp": ex["buy"]["rtp"], "lut_minus_exact": mean / C.BUY_COST - ex["buy"]["rtp"], "kl": kl,
            "lut_max_payout_x": float(P.max()), "lut_std_dev_x": float(math.sqrt((W * P * P).sum() / W.sum() - mean ** 2)),
            "pilot_rounds": pilot_n, "bands": band_rep, "sha256_books": _sha(books_path), "sha256_lut": _sha(lut_path)}


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


DEFAULT_PLAN = {3: [8000, 300, 120, 40], 4: [2500, 200, 100, 40], 5: [800, 120, 60, 40], 6: [300, 80, 60, 40]}
BUY_PLAN = [10000, 600, 200, 60]


def main():
    import argparse

    root = os.path.dirname(C.HERE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(root), "stake", "publish_files"))
    ap.add_argument("--n-base", type=int, default=100_000)
    ap.add_argument("--pilot", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--exact", default=os.path.join(root, "reports", "exact.json"))
    a = ap.parse_args()
    s = export(a.out, a.n_base, DEFAULT_PLAN, a.pilot, a.seed, a.exact)
    print(json.dumps({k: v for k, v in s.items() if k not in ("strata", "bonus")}, indent=2))
    print("bonus mode:", {k: v for k, v in s["bonus"].items() if k != "bands"})
    for st in s["strata"]:
        print(st["name"], st["books"], round(st["target_mean_x"], 3), round(st["sample_mean_x"], 3), f"kl={st['kl']:.2e}", st["max_payout_x"], st["bands"])


if __name__ == "__main__":
    main()
