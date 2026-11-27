"""Tests de la phase 7 : équivalences IBS / Williams %R(1) / stochastique %K(1), conventions,
simulateur IBS causal, chargeur OHLC verrouillé, simulateur H4 (Bollinger + RSI + ADX)."""
import numpy as np
import pandas as pd
import pytest

from nexus.phase4.sim import AssetData, adx, signals, simulate as sim4
from nexus.phase4.data import daily_from_h1
from nexus.phase7.ibs import ibs, load_ohlc_csv, simulate, stoch_k, williams_r
from tests.test_phase4 import T0, h1_from_daily_closes


def ohlc(n=400, seed=0):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, n)))
    o = c * (1 + rng.normal(0, 0.003, n))
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.01, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.01, n))
    idx = pd.bdate_range("2001-01-02", periods=n, tz="UTC")
    return pd.DataFrame({"o": o, "h": h, "l": l, "c": c}, index=idx)


def test_williams_r1_and_stoch_k1_equal_ibs():
    d = ohlc()
    x = ibs(d)
    np.testing.assert_allclose(williams_r(d, 1), 100 * x - 100, atol=1e-9)
    np.testing.assert_allclose(stoch_k(d, 1), 100 * x, atol=1e-9)
    # seuils du document
    assert ((x < 0.1) == (williams_r(d, 1) < -90)).all()
    assert ((x > 0.9) == (stoch_k(d, 1) > 90)).all()


def test_smoothing_breaks_equivalence_and_flat_bar_is_undefined():
    d = ohlc()
    assert not np.allclose(stoch_k(d, 1, smooth=3).dropna(), (100 * ibs(d)).loc[stoch_k(d, 1, smooth=3).dropna().index])
    d.iloc[5, :] = 50.0                                   # H = L
    assert np.isnan(ibs(d).iloc[5]) and np.isnan(williams_r(d, 1).iloc[5])


def test_ibs_signals_are_causal_and_next_open_execution():
    d = ohlc(600, seed=2)
    rule = {"kind": "ibs", "ibs_entry": 0.1, "ibs_exit": 0.9}
    r = simulate(d, rule, d.index[10], d.index[-1], stop=None, fraction=1.0, cost_side=0.0)
    t = r.trades.iloc[0]
    sig_day = d.index[d.index.get_loc(t.entry_date) - 1]
    assert ibs(d).loc[sig_day] < 0.1                       # signal la veille
    assert t.entry == pytest.approx(d.loc[t.entry_date, "o"])   # exécution à l'ouverture
    full = simulate(d, rule, d.index[10], d.index[-1], stop=None, fraction=1.0, cost_side=0.0).trades
    cut = simulate(d.iloc[:400], rule, d.index[10], d.index[-1], stop=None, fraction=1.0, cost_side=0.0).trades
    pd.testing.assert_frame_equal(full[full.exit_date < d.index[398]].reset_index(drop=True),
                                  cut[cut.exit_date < d.index[398]].reset_index(drop=True))


def test_intraday_stop_and_gap():
    d = ohlc(60, seed=3)
    d.iloc[:, :] = 100.0
    d.loc[d.index[10], ["o", "h", "l", "c"]] = [100, 101, 95, 95.5]      # IBS ≈ 0,08 → achat à l'ouverture du jour 11
    d.loc[d.index[12], ["o", "h", "l", "c"]] = [99, 100, 88, 99]          # touche le stop de 10 % en séance
    r = simulate(d, {"kind": "ibs", "ibs_entry": 0.1, "ibs_exit": 0.9}, d.index[1], d.index[-1], stop=0.10, fraction=1.0, cost_side=0.0)
    t = r.trades.iloc[0]
    assert t.reason == "stop" and t.exit == pytest.approx(90.0)
    d.loc[d.index[12], ["o", "h", "l", "c"]] = [80, 82, 79, 81]           # gap sous le stop
    t = simulate(d, {"kind": "ibs", "ibs_entry": 0.1, "ibs_exit": 0.9}, d.index[1], d.index[-1], stop=0.10, fraction=1.0, cost_side=0.0).trades.iloc[0]
    assert t.exit == pytest.approx(80.0)


def test_loader_drops_locked_periods(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("<DATE>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n2023.06.29\t1\t2\t0.5\t1.5\n2023.06.30\t1\t2\t0.5\t1.5\n2023.07.03\t1\t2\t0.5\t1.5\n")
    d = load_ohlc_csv(p)
    assert len(d) == 2 and d.index.max() < pd.Timestamp("2023-07-01", tz="UTC")


def test_h4_bars_engine_and_bbmr_causal():
    rng = np.random.default_rng(5)
    closes = list(100 * np.exp(np.cumsum(rng.normal(0.002, 0.03, 120))))
    h1 = h1_from_daily_closes(closes, wiggle=0.004)
    g = h1.set_index("ts").resample("4h")
    h4 = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last()}).dropna()
    rule = {"kind": "bbmr", "bb_n": 20, "bb_k": 2.0, "rsi_n": 14, "rsi_th": 55, "adx_n": 14, "adx_th": 25}
    f1, f2 = signals(h4, rule), signals(h4.iloc[:400], rule)
    pd.testing.assert_frame_equal(f1.iloc[:400], f2)
    assert adx(h4).dropna().between(0, 100).all()
    r = sim4({"X": AssetData(h1=h1, d1=h4)}, rule, {"X": 0.1}, start=T0 + pd.Timedelta(days=10), end=T0 + pd.Timedelta(days=120),
             bar_hours=4)
    assert len(r.equity) == (110 * 6)
    if len(r.trades):
        assert all(pd.Timestamp(x).hour % 4 == 0 for x in r.trades.entry_ts if True)
