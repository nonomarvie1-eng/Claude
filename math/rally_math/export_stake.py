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


def bonus_pilot(rng, base_stops, base_cnt, free_cnt, free_len):
    """Vectorised play of complete rounds whose base stops are given; records free stops."""
    from .simulate import play_vec

    log: list = []
    r = play_vec(rng, base_stops, base_cnt, free_cnt, free_len, log)
    return r["total"], log


def stops_of(i, base_stops, log):
    """Every draw of round i in order: base stops, then (stops, aux) per exchange."""
    seq = [list(map(int, base_stops[i]))]
    for a, st, aux in log:
        j = np.searchsorted(a, i)
        if j < len(a) and a[j] == i:
            seq.append(list(map(int, st[j])))
            seq.append(list(map(int, aux[j])))
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


def _write_mode(out_dir, mode, strata_specs, base, free, bc, fc, rng, pilot_n, cost):
    """strata_specs: list of (name, probability, target_mean_t, kind, k, plan)
    kind 'nobonus' draws plain base spins without a trigger; kind 'k' draws
    base stops with exactly k scatters (exact conditional law) and plays the
    round; plan = books per payout band."""
    books_path = os.path.join(out_dir, f"books_{mode}.jsonl.zst")
    lut_path = os.path.join(out_dir, f"lookUpTable_{mode}_0.csv")
    cctx = zstd.ZstdCompressor(level=19, threads=-1)
    payouts, weights, rep = [], [], []
    book_id = 1
    with open(books_path, "wb") as fbin, cctx.stream_writer(fbin) as wtr:
        def write(res):
            nonlocal book_id
            b = make_book(book_id, res)
            wtr.write((json.dumps(b, separators=(",", ":")) + "\n").encode())
            book_id += 1
            return res.total_t

        for name, prob, target, kind, k, plan in strata_specs:
            if kind == "nobonus":
                xs = []
                while len(xs) < plan:
                    st = [int(rng.integers(0, L)) for L in base.lengths]
                    if len(positions_of(window(base.strips, st), C.SCATTER)) >= 3:
                        continue
                    xs.append(write(play_round(None, base, free, True, forced_base_stops=st, mode=mode)))
                xs = np.array(xs)
                w, lam, kl = _tilt(xs, np.ones(len(xs)), target)
                payouts += (xs * 10).tolist()
                weights += [max(1, int(round(v))) for v in w * prob * WEIGHT_TOTAL]
                rep.append({"name": name, "probability": prob, "books": len(xs), "target_mean_x": target / 10,
                            "sample_mean_x": float(xs.mean() / 10), "kl": kl, "max_payout_x": float(xs.max() / 10)})
                continue
            bs, pk = conditional_base_stops(base.strips, k, rng, pilot_n)
            tot, log = bonus_pilot(rng, bs, bc, fc, free.lengths)
            band_of = np.digitize(tot / 10, BANDS_X) - 1
            xs_all, w0_all, band_rep = [], [], []
            for b in range(len(BANDS_X) - 1):
                members = np.nonzero(band_of == b)[0]
                p_band = len(members) / pilot_n
                want = plan[b]
                if len(members) == 0 or want == 0:
                    band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "books": 0})
                    continue
                pick = members if len(members) <= want else rng.choice(members, size=want, replace=False)
                for i in pick:
                    seq = stops_of(int(i), bs, log)
                    res = play_round(list_drawer(seq[1:]), base, free, True, forced_base_stops=seq[0], mode=mode)
                    assert res.total_t == int(tot[i]), "fast path and reference engine disagree"
                    xs_all.append(write(res))
                    w0_all.append(p_band / len(pick))
                band_rep.append({"band_x": BANDS_X[b:b + 2], "pilot_count": int(len(members)), "p_band": p_band, "books": int(len(pick))})
            xs = np.array(xs_all)
            w, lam, kl = _tilt(xs, np.array(w0_all), target)
            payouts += (xs * 10).tolist()
            weights += [max(1, int(round(v))) for v in w * prob * WEIGHT_TOTAL]
            rep.append({"name": name, "probability": prob, "books": len(xs), "target_mean_x": target / 10,
                        "sample_mean_x": float((xs * np.array(w0_all)).sum() / np.sum(w0_all) / 10), "kl": kl,
                        "max_payout_x": float(xs.max() / 10), "pilot_rounds": pilot_n, "bands": band_rep})
    with open(lut_path, "w", encoding="utf-8", newline="\n") as f:
        for i, (wt, po) in enumerate(zip(weights, payouts), start=1):
            f.write(f"{i},{wt},{int(po)}\n")
    W = np.array(weights, dtype=np.float64)
    P = np.array(payouts, dtype=np.float64) / 100
    mean = float((W * P).sum() / W.sum())
    return {
        "mode": mode, "cost": cost, "books": len(payouts), "lut_mean_x": mean, "lut_rtp": mean / cost,
        "lut_std_dev_x": float(math.sqrt((W * P * P).sum() / W.sum() - mean ** 2)),
        "lut_hit_rate": float(W[P > 0].sum() / W.sum()), "lut_max_payout_x": float(P.max()),
        "weight_sum": int(sum(weights)), "strata": rep, "events": os.path.basename(books_path), "weights": os.path.basename(lut_path),
        "sha256_books": _sha(books_path), "sha256_lut": _sha(lut_path),
    }


def export(out_dir, n_base, plan, pilot_n, seed, exact_path, modes=None):
    ex = json.load(open(exact_path, encoding="utf-8"))
    free = C.free_reels()
    fc = count_tables(free.strips)
    rng = np.random.Generator(np.random.PCG64(seed))
    os.makedirs(out_dir, exist_ok=True)
    costs = C.mode_costs()
    modes = modes or list(costs)
    out = {}
    for mode in modes:
        em = ex["modes"][mode]
        if mode in C.BUY_SCATTERS:
            base = C.base_reels()
            k = C.BUY_SCATTERS[mode]
            specs = [(f"buy_{k}_scatters", 1.0, em["mean_x"] * 10, "k", k, BUY_PLAN)]
        else:
            base = C.bonus_chance_reels() if mode == "bonus_chance" else C.base_reels()
            ks = [k for k in sorted(C.FS_AWARD) if em["p_scatter"].get(str(k), 0) > 0]
            p_k = {k: em["p_scatter"][str(k)] for k in ks}
            capc = (ex.get("cap_correction") or {}).get(mode) or {}
            tgt = {k: em["cond_base_mean_t"][str(k)] + ex["bonus_by_trigger"][str(k)]["E"]
                   - 10 * capc.get(str(k), {}).get("overshoot_x", 0.0) for k in ks}
            p0 = 1.0 - sum(p_k.values())
            target0 = (em["mean_x"] * 10 - sum(p_k[k] * tgt[k] for k in ks)) / p0
            specs = [("no_bonus", p0, target0, "nobonus", None, n_base)]
            specs += [(f"bonus_{k}_scatters_{C.bonus_level(k)}", p_k[k], tgt[k], "k", k, plan[k]) for k in ks]
        bc = count_tables(base.strips)
        s = _write_mode(out_dir, mode, specs, base, free, bc, fc, rng, pilot_n, costs[mode])
        s["exact_rtp"] = em["rtp"]
        s["lut_minus_exact"] = s["lut_rtp"] - em["rtp"]
        out[mode] = s
        print(mode, {k: v for k, v in s.items() if k not in ("strata",)})
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"modes": [{"name": m, "cost": float(costs[m]), "events": out[m]["events"], "weights": out[m]["weights"]}
                             for m in modes]}, f, indent=4)
    summary = {"math_version": C.MATH_VERSION, "seed": seed, "modes": out}
    json.dump(summary, open(os.path.join(out_dir, "export_summary.json"), "w"), indent=2)
    return summary


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


DEFAULT_PLAN = {3: [6000, 300, 120, 40], 4: [2500, 200, 100, 40], 5: [800, 120, 60, 40], 6: [300, 80, 60, 40]}
BUY_PLAN = [6000, 500, 200, 60]


def main():
    import argparse

    root = os.path.dirname(C.HERE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(root), "stake", "publish_files"))
    ap.add_argument("--n-base", type=int, default=100_000)
    ap.add_argument("--pilot", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--modes", default=None)
    ap.add_argument("--exact", default=os.path.join(root, "reports", "exact.json"))
    a = ap.parse_args()
    export(a.out, a.n_base, DEFAULT_PLAN, a.pilot, a.seed, a.exact, a.modes.split(",") if a.modes else None)


if __name__ == "__main__":
    main()
