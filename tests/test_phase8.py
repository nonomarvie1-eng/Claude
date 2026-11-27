"""Tests du simulateur de portefeuille H1 de la phase 8."""
import numpy as np
import pandas as pd
import pytest

from nexus.phase8.sim import signals, simulate, vwap_daily

T0 = pd.Timestamp("2021-01-01", tz="UTC")


def bars(closes, vol=1.0, start=T0):
    c = np.asarray(closes, float)
    o = np.concatenate([[c[0]], c[:-1]])
    idx = pd.date_range(start, periods=len(c), freq="1h")
    return pd.DataFrame({"o": o, "h": np.maximum(o, c) * 1.001, "l": np.minimum(o, c) * 0.999, "c": c, "volume": vol}, index=idx)


def test_vwap_is_causal_and_resets_daily():
    rng = np.random.default_rng(0)
    d = bars(100 + np.cumsum(rng.normal(0, 1, 72)))
    v = vwap_daily(d)
    v2 = vwap_daily(d.iloc[:40])
    pd.testing.assert_series_equal(v.iloc[:40], v2)
    tp = (d.h + d.l + d.c) / 3
    assert v.iloc[24] == pytest.approx(tp.iloc[24])        # première bougie du jour 2


def test_breakout_channel_excludes_signal_bar_and_signals_causal():
    rng = np.random.default_rng(1)
    d = bars(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 600))))
    for rule in ({"kind": "breakout"}, {"kind": "bb_range"}, {"kind": "pullback"}, {"kind": "vwap_trend"}):
        pd.testing.assert_frame_equal(signals(d, rule).iloc[:500], signals(d.iloc[:500], rule))
    s = signals(d, {"kind": "breakout"})
    hh = d.h.rolling(24).max().shift(1)
    assert (d.c[s.long_entry] > hh[s.long_entry]).all()


def test_next_open_execution_stop_and_costs():
    closes = [100.0] * 30 + [105.0] + [105.0] * 5 + [90.0] * 5
    d = bars(closes)
    d.loc[d.index[33], ["o", "h", "l", "c"]] = [105, 105, 99, 104]       # touche le stop de 5 %
    res = simulate({"X": d}, {}, {"kind": "breakout"}, {"X": 0.05}, d.index[0], d.index[-1] + pd.Timedelta(hours=1),
                   fee=0.0, slip=0.0)
    t = res.trades.iloc[0]
    assert t.entry_ts == d.index[31] and t.entry == pytest.approx(105.0)  # ouverture suivant la clôture de cassure
    assert t.reason == "stop" and t.exit == pytest.approx(105 * 0.95) and t.R == pytest.approx(-1.0)


def test_max_positions_and_priority():
    c = [100.0] * 30 + [110.0] * 10
    b = {s: bars(c) for s in ("A", "B", "C")}
    res = simulate(b, {}, {"kind": "breakout"}, {s: 0.2 for s in b}, T0, T0 + pd.Timedelta(hours=40), fee=0, slip=0,
                   max_positions=2, priority=["C", "A", "B"])
    assert set(res.trades.symbol) == {"C", "A"} and res.info["skipped_capacity"] == 1


def test_daily_loss_blocks_new_entries():
    c = [100.0] * 30 + [110.0] * 3 + [104.0] * 10
    a, b = bars(c), bars([100.0] * 36 + [120.0] * 7)
    res = simulate({"A": a, "B": b}, {}, {"kind": "breakout"}, {"A": 0.5, "B": 0.5}, T0, T0 + pd.Timedelta(hours=43),
                   risk=0.2, fee=0, slip=0, daily_block=0.02)
    assert res.info["daily_block_days"] >= 1 and "B" not in set(res.trades.symbol)


def test_funding_sign_short_receives():
    c = [100.0] * 30 + [90.0] * 20
    d = bars(c)
    fund = pd.Series(0.001, index=pd.date_range(T0, periods=50, freq="8h"))
    res = simulate({"X": d}, {"X": fund}, {"kind": "breakout"}, {"X": 0.5}, T0, T0 + pd.Timedelta(hours=50), fee=0, slip=0)
    t = res.trades.iloc[0]
    assert t.side == "short" and t.funding < 0
