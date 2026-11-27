"""Scénarios d'exécution à résultat connu."""
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from nexus.engine.execution import ExecFrame, simulate
from nexus.instruments import BTCUSDT_SPOT

from helpers import T0, ZERO_COST, m1_from_bid

FAR = T0 + pd.Timedelta(hours=10)


def ex_of(rows, spread=0.0, spec=ZERO_COST, **kw):
    return ExecFrame.from_m1(m1_from_bid(rows, spread, **kw), spec)


def test_market_entry_uses_next_bar_open_not_signal_close():
    # Signal connu à la clôture de la minute 0 (avail = T0+1min) : exécution à l'OUVERTURE de la minute 1.
    rows = [(1.0, 1.0, 1.0, 1.10), (1.20, 1.25, 1.19, 1.21), (1.21, 1.22, 1.20, 1.21)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0 + pd.Timedelta(minutes=1), stop=1.0, target=None, time_exit=FAR)
    assert f.entry_idx == 1
    assert f.entry_price == pytest.approx(1.20)  # et non 1.10 (clôture du signal)


def test_long_entry_pays_ask_and_exits_on_bid():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
    ex = ex_of(rows, spread=0.0002)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.9, target=None, time_exit=T0 + pd.Timedelta(minutes=2))
    assert f.entry_price == pytest.approx(1.0002)
    assert f.reason == "time" and f.exit_price == pytest.approx(1.0)


def test_same_bar_stop_and_target_is_resolved_as_stop():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.1, 0.9, 1.0)]  # minute 1 touche SL 0.95 ET TP 1.05
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.95, target=1.05, time_exit=FAR)
    assert f.reason == "stop" and f.ambiguous_bar
    assert f.exit_price == pytest.approx(0.95)


def test_target_requires_trade_through_by_one_tick():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.05, 1.0, 1.0), (1.0, 1.0501, 1.0, 1.0)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.9, target=1.05, time_exit=FAR)
    assert f.reason == "target" and f.exit_idx == 2  # le simple contact à 1.05 (minute 1) ne suffit pas


def test_gap_through_stop_fills_at_open():
    rows = [(1.0, 1.0, 1.0, 1.0), (0.90, 0.91, 0.89, 0.90)]  # ouverture sous le stop 0.95
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.95, target=None, time_exit=FAR)
    assert f.reason == "stop" and f.exit_price == pytest.approx(0.90)  # perte > 1R : gap subi


def test_short_stop_and_target():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 0.94, 0.95)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=-1, signal_avail=T0, stop=1.05, target=0.95, time_exit=FAR)
    assert f.reason == "target" and f.exit_price == pytest.approx(0.95)


def test_limit_not_filled_on_touch_and_expires():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 0.99, 1.0), (1.0, 1.0, 0.99, 1.0)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.95, target=None, time_exit=FAR,
                 entry_type="limit", limit_price=0.99, expiry=T0 + pd.Timedelta(minutes=3))
    assert not f.filled and f.reason == "unfilled"


def test_limit_filled_when_traded_through_and_no_target_on_fill_bar():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.10, 0.98, 1.0), (1.0, 1.10, 1.0, 1.05)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.95, target=1.05, time_exit=FAR,
                 entry_type="limit", limit_price=0.99)
    assert f.entry_idx == 1 and f.entry_price == pytest.approx(0.99)
    assert f.reason == "target" and f.exit_idx == 2  # objectif ignoré dans la minute de remplissage


def test_limit_fill_bar_can_be_stopped_conservatively():
    rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 0.94, 0.96)]
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.95, target=None, time_exit=FAR,
                 entry_type="limit", limit_price=0.99)
    assert f.reason == "stop" and f.exit_idx == 1


def test_time_exit_at_first_bar_at_or_after_exit_time():
    rows = [(1.0, 1.0, 1.0, 1.0)] * 5
    ex = ex_of(rows)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.5, target=None, time_exit=T0 + pd.Timedelta(minutes=3))
    assert f.reason == "time" and f.exit_idx == 3


def test_data_gap_during_trade_is_flagged():
    df = m1_from_bid([(1.0, 1.0, 1.0, 1.0)] * 4)
    df.loc[2:, "ts"] = df.loc[2:, "ts"] + pd.Timedelta(hours=2)
    ex = ExecFrame.from_m1(df, ZERO_COST)
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.5, target=None, time_exit=FAR)
    assert f.gap_during_trade


def test_short_refused_on_spot():
    df = m1_from_bid([(100.0, 100, 100, 100)] * 3).rename(columns={f"bid_{k}": k for k in "ohlc"})
    ex = ExecFrame.from_m1(df, BTCUSDT_SPOT)
    with pytest.raises(ValueError):
        simulate(ex, BTCUSDT_SPOT, side=-1, signal_avail=T0, stop=110, target=None, time_exit=FAR)


def test_non_monotonic_timestamps_raise_anomaly():
    df = m1_from_bid([(1.0, 1.0, 1.0, 1.0)] * 3)
    df.loc[2, "ts"] = df.loc[0, "ts"]
    with pytest.raises(ValueError):
        ExecFrame.from_m1(df, ZERO_COST)


def test_cost_multiplier_widens_spread():
    rows = [(1.0, 1.0, 1.0, 1.0)] * 3
    spec2 = ZERO_COST.stressed(2.0)
    ex = ExecFrame.from_m1(m1_from_bid(rows, 0.0002), spec2)
    f = simulate(ex, spec2, side=1, signal_avail=T0, stop=0.9, target=None, time_exit=T0 + pd.Timedelta(minutes=2))
    # spread 2 pips doublé à 4 pips : achat à mid + 2 pips, vente à mid - 2 pips
    assert f.entry_price - f.exit_price == pytest.approx(0.0004)


def test_random_walk_expectancy_is_minus_costs():
    """Contrôle global : entrées aléatoires sur une marche aléatoire → espérance ≈ −coûts."""
    rng = np.random.default_rng(1)
    n = 200_000
    p = 1.0 + np.cumsum(rng.normal(0, 0.0001, n))
    rows = np.column_stack([p, p + 0.00005, p - 0.00005, p])
    ex = ExecFrame.from_m1(m1_from_bid(rows, spread=0.0001), ZERO_COST)
    r_net = []
    for k in rng.integers(100, n - 2000, 1500):
        t = pd.Timestamp(int(ex.ts[k]), tz="UTC")
        mid = (ex.bid_c[k - 1] + ex.ask_c[k - 1]) / 2
        side = int(rng.choice([-1, 1]))
        stop = mid - side * 0.002
        f = simulate(ex, ZERO_COST, side=side, signal_avail=t, stop=stop, target=None, target_r=2.0,
                     time_exit=t + pd.Timedelta(hours=20))
        r_net.append(side * (f.exit_price - f.entry_price) / abs(f.entry_price - stop))
    m = float(np.mean(r_net))
    se = float(np.std(r_net) / np.sqrt(len(r_net)))
    # coût attendu ≈ spread / distance du stop = 0.0001/0.002 = 0.05R
    assert abs(m - (-0.05)) < 3 * se + 0.02
