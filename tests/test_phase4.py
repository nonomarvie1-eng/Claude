"""Tests du simulateur de la phase 4 (sémantique Cubrik), sur données synthétiques."""
import numpy as np
import pandas as pd
import pytest

from nexus.phase4.data import daily_from_h1
from nexus.phase4.sim import PERP, SPOT, AssetData, Costs, cross_above, random_trades_R, signals, simulate

T0 = pd.Timestamp("2020-01-01", tz="UTC")


def h1_from_daily_closes(closes, start=T0, wiggle=0.0):
    """Bougies H1 dont le prix va linéairement de la clôture précédente à la clôture du jour."""
    rows, prev = [], closes[0]
    for d, c in enumerate(closes):
        path = np.linspace(prev, c, 25)
        for k in range(24):
            o, cc = path[k], path[k + 1]
            rows.append({"ts": start + pd.Timedelta(hours=24 * d + k), "o": o, "h": max(o, cc) * (1 + wiggle),
                         "l": min(o, cc) * (1 - wiggle), "c": cc})
        prev = c
    return pd.DataFrame(rows)


def asset(closes, **kw):
    h1 = h1_from_daily_closes(closes, **kw)
    return AssetData(h1=h1, d1=daily_from_h1(h1))


def test_cross_requires_previous_bar():
    a = pd.Series([3.0, 3.0, 1.0]); b = pd.Series([np.nan, 2.5, 2.5])
    assert not cross_above(a, b).any()                       # pas de barre précédente valide au 1er point
    a = pd.Series([1.0, 2.0, 3.0]); b = pd.Series([1.5, 2.5, 2.5])
    assert cross_above(a, b).tolist() == [False, False, True]


def test_signals_are_causal():
    rng = np.random.default_rng(1)
    closes = 100 * np.exp(np.cumsum(rng.normal(0, 0.03, 400)))
    a = asset(list(closes))
    for rule in ({"kind": "donch", "entry_n": 55, "exit_n": 20}, {"kind": "sma", "sma_n": 100},
                 {"kind": "tsmom", "roc_n": 90}, {"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200, "exit_sma": 5}):
        full = signals(a.d1, rule)
        cut = signals(a.d1.iloc[:300], rule)
        pd.testing.assert_frame_equal(full.iloc[:300], cut)       # aucune donnée future


def test_entry_next_open_and_costs_spot():
    closes = [100.0] * 60 + [101.0] + [101.0] * 10          # cassure du plus haut 55 au jour 60
    a = asset(closes)
    start, end = T0 + pd.Timedelta(days=1), T0 + pd.Timedelta(days=len(closes))
    res = simulate({"X": a}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.10}, start=start, end=end,
                   risk=0.01, costs=SPOT, initial=1000.0)
    t = res.trades.iloc[0]
    assert t["entry_ts"] == T0 + pd.Timedelta(days=61)        # ouverture du jour suivant le signal
    assert t["entry"] == pytest.approx(101.0 * 1.0005)
    assert t["risk_amt"] == pytest.approx(10.0, rel=1e-6)    # 1 % de 1 000
    assert t["qty"] * t["entry"] == pytest.approx(100.0, rel=1e-6)   # 10 / 10 %
    # prix inchangé ensuite : perte = frais + glissement uniquement
    assert t["reason"] == "end"
    assert res.equity.iloc[-1] < 1000.0
    assert res.equity.iloc[-1] == pytest.approx(1000.0 + t["pnl"], rel=1e-9)


def test_stop_and_gap_fill():
    closes = [100.0] * 60 + [101.0, 101.0, 80.0, 80.0]
    a = asset(closes)
    # gap : la bougie H1 du jour 63 ouvre déjà sous le stop
    a.h1.loc[a.h1["ts"] == T0 + pd.Timedelta(days=63), ["o", "h", "l", "c"]] = [70.0, 70.0, 70.0, 70.0]
    res = simulate({"X": a}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.10},
                   start=T0 + pd.Timedelta(days=1), end=T0 + pd.Timedelta(days=len(closes)), risk=0.01, costs=Costs(0, 0))
    t = res.trades.iloc[0]
    assert t["reason"] == "stop"
    stop_px = 101.0 * 0.9
    # le prix descend linéairement le jour 62 et franchit le stop avant le gap
    assert t["exit"] == pytest.approx(stop_px) and t["R"] == pytest.approx(-1.0)


def test_gap_beyond_stop_fills_at_open():
    closes = [100.0] * 60 + [101.0, 101.0, 101.0]
    a = asset(closes)
    a.h1.loc[a.h1["ts"] == T0 + pd.Timedelta(days=62, hours=5), ["o", "h", "l", "c"]] = [60.0, 101.0, 60.0, 101.0]
    res = simulate({"X": a}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.10},
                   start=T0 + pd.Timedelta(days=1), end=T0 + pd.Timedelta(days=len(closes)), risk=0.01, costs=Costs(0, 0))
    t = res.trades.iloc[0]
    assert t["exit"] == pytest.approx(60.0)                  # pas au stop : à l'ouverture du gap
    assert t["R"] < -1.0


def test_perp_short_and_funding_sign():
    closes = list(np.linspace(100, 200, 100)) + list(np.linspace(200, 100, 100))
    a = asset(closes)
    ts = pd.date_range(T0, periods=200 * 3, freq="8h")
    a.funding = pd.Series(0.001, index=ts)                  # taux positif : les shorts reçoivent
    res = simulate({"X": a}, {"kind": "tsmom", "roc_n": 90}, {"X": 0.5}, start=T0, end=T0 + pd.Timedelta(days=200),
                   risk=0.01, costs=Costs(0, 0, perp=True))
    t = res.trades[res.trades["side"] == "short"].iloc[0]
    assert t["side"] == "short"
    assert t["funding"] < 0                                  # financement reçu
    assert t["pnl"] > 0


def test_spot_never_shorts_and_capacity_cap():
    closes = list(np.linspace(200, 100, 200))
    res = simulate({"X": asset(closes)}, {"kind": "tsmom", "roc_n": 90}, {"X": 0.05}, start=T0,
                   end=T0 + pd.Timedelta(days=200), risk=0.01, costs=SPOT)
    assert res.trades.empty
    # risque 10 % avec stop 5 % => notionnel 200 % : refusé (pas de levier)
    closes = [100.0] * 60 + [101.0] * 5
    res = simulate({"X": asset(closes)}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.05},
                   start=T0 + pd.Timedelta(days=1), end=T0 + pd.Timedelta(days=65), risk=0.10, costs=SPOT)
    assert res.trades.empty and res.info["n_skipped_capacity"] == 1


def test_daily_loss_rule_closes_positions():
    closes = [100.0] * 60 + [101.0, 101.0, 95.0, 95.0]
    res = simulate({"X": asset(closes)}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.10},
                   start=T0 + pd.Timedelta(days=1), end=T0 + pd.Timedelta(days=64), risk=0.05, costs=Costs(0, 0),
                   rules_mode=True)
    assert res.trades.iloc[0]["reason"] == "daily_loss"


def test_random_baseline_zero_drift_has_negative_mean_after_costs():
    rng = np.random.default_rng(3)
    closes = list(100 * np.exp(np.cumsum(rng.normal(0, 0.02, 500))))
    a = asset(closes, wiggle=0.002)
    m = random_trades_R(a, T0, T0 + pd.Timedelta(days=500), [10] * 50, ["long"] * 50, 0.1, SPOT, 20)
    assert np.isfinite(m).all()
