"""Le simulateur vectorisé doit donner exactement le même résultat qu'une
implémentation de référence naïve, minute par minute (ordres au marché)."""
import numpy as np
import pandas as pd

from nexus.engine.execution import ExecFrame, simulate
from nexus.instruments import EURUSD_CFD

from helpers import m1_from_bid


def reference(ex, spec, side, k, stop, target_r, end):
    slip_m, slip_s, tick = spec.slippage_market_frac, spec.slippage_stop_frac, spec.price_tick
    entry = ex.ask_o[k] * (1 + slip_m) if side == 1 else ex.bid_o[k] * (1 - slip_m)
    if (side == 1 and stop >= entry) or (side == -1 and stop <= entry):
        return "stop", k
    target = entry + side * target_r * abs(entry - stop)
    for j in range(k, end):
        if side == 1:
            hs, ht, o = ex.bid_l[j] <= stop, ex.bid_h[j] >= target + tick, ex.bid_o[j]
            if hs:
                return "stop", j, min(stop, o) * (1 - slip_s)
            if ht:
                return "target", j, max(target, o)
        else:
            hs, ht, o = ex.ask_h[j] >= stop, ex.ask_l[j] <= target - tick, ex.ask_o[j]
            if hs:
                return "stop", j, max(stop, o) * (1 + slip_s)
            if ht:
                return "target", j, min(target, o)
    return "time", end, (ex.bid_o[end] * (1 - slip_m) if side == 1 else ex.ask_o[end] * (1 + slip_m))


def test_vectorized_matches_reference():
    rng = np.random.default_rng(3)
    n = 20_000
    p = 1.1 + np.cumsum(rng.normal(0, 0.0002, n))
    w = np.abs(rng.normal(0, 0.0002, (n, 2)))
    o = np.concatenate([[p[0]], p[:-1]])
    rows = np.column_stack([o, np.maximum(o, p) + w[:, 0], np.minimum(o, p) - w[:, 1], p])
    df = m1_from_bid(rows, spread=0.00008)
    ex = ExecFrame.from_m1(df, EURUSD_CFD)
    for _ in range(3000):
        k = int(rng.integers(1, n - 400))
        side = int(rng.choice([-1, 1]))
        mid = (ex.bid_c[k - 1] + ex.ask_c[k - 1]) / 2
        stop = mid - side * rng.uniform(0.0005, 0.004)
        tr = float(rng.choice([1.0, 2.0, 4.0]))
        end = k + int(rng.integers(5, 300))
        f = simulate(ex, EURUSD_CFD, side=side, signal_avail=pd.Timestamp(int(ex.ts[k]), tz="UTC"), stop=stop,
                     target=None, target_r=tr, time_exit=pd.Timestamp(int(ex.ts[end]), tz="UTC"))
        ref = reference(ex, EURUSD_CFD, side, k, stop, tr, end)
        assert f.reason == ref[0] and f.exit_idx == ref[1]
        if len(ref) == 3:
            assert abs(f.exit_price - ref[2]) < 1e-12
