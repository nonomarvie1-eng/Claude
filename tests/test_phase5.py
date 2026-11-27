"""Tests de la phase 5 : simulateur journalier de retour à la moyenne, bases aléatoires, Monte Carlo,
paliers « lock », verrou de lecture des données French."""
import io
import zipfile

import numpy as np
import pandas as pd
import pytest

from nexus.phase4.sim import Costs
from nexus.phase4.sim import simulate as sim4
from nexus.phase5 import data as p5d
from nexus.phase5.montecarlo import path_stats, removal, shuffle
from nexus.phase5.mr import flags, random_entries, simulate
from tests.test_phase4 import T0, asset


def frame(closes, rf=0.0):
    idx = pd.bdate_range("2000-01-03", periods=len(closes), tz="UTC")
    return pd.DataFrame({"close": np.asarray(closes, float), "rf": rf}, index=idx)


def test_flags_are_causal():
    rng = np.random.default_rng(0)
    df = frame(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, 800))))
    for rule in ({"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200},
                 {"kind": "rsi3050", "rsi_n": 5, "entry_th": 30, "exit_th": 50, "trend_sma": 200},
                 {"kind": "double", "n": 5, "trend_sma": 200}):
        e1, x1 = flags(df["close"], rule)
        e2, x2 = flags(df["close"].iloc[:600], rule)
        pd.testing.assert_series_equal(e1.iloc[:600], e2)
        pd.testing.assert_series_equal(x1.iloc[:600], x2)


def test_trade_costs_and_financing():
    # tendance haussière (au-dessus de la SMA200), puis 2 baisses (RSI2 < 10), puis rebond
    closes = list(np.linspace(100, 150, 250)) + [140.0, 130.0, 135.0, 150.0]
    df = frame(closes, rf=0.0)
    res = simulate(df, {"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200}, df.index[220], df.index[-1] + pd.Timedelta(days=1),
                   stop=None, fraction=1.0, cost_side=0.001, fin_spread=0.036)
    t = res.trades.iloc[0]
    assert t["entry"] == pytest.approx(140.0)            # achat à la clôture du signal
    assert t["exit"] == pytest.approx(135.0) or t["exit"] == pytest.approx(150.0)
    nights = (t["exit_date"] - t["entry_date"]).days
    assert t["financing"] == pytest.approx(t["notional"] / 140.0 * sum(
        df["close"].loc[t["entry_date"]:t["exit_date"]].iloc[:-1] * 0.036 / 360 *
        np.diff(df.loc[t["entry_date"]:t["exit_date"]].index).astype("timedelta64[D]").astype(int))), nights
    assert t["pnl"] == pytest.approx(t["notional"] * (t["exit"] / t["entry"] - 1) - t["fees"] - t["financing"])
    assert res.equity.iloc[-1] == pytest.approx(1000.0 + res.trades["pnl"].sum())


def test_stop_at_close_and_delay():
    closes = list(np.linspace(100, 150, 250)) + [140.0, 125.0, 110.0, 160.0]
    df = frame(closes)
    rule = {"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200}
    r0 = simulate(df, rule, df.index[220], df.index[-1] + pd.Timedelta(days=1), stop=0.10, fraction=1.0, cost_side=0)
    assert r0.trades.iloc[0]["reason"] == "stop" and r0.trades.iloc[0]["exit"] == pytest.approx(125.0)   # 140 × 0,9 = 126 franchi à 125
    r1 = simulate(df, rule, df.index[220], df.index[-1] + pd.Timedelta(days=1), stop=None, fraction=1.0, cost_side=0, delay=1)
    assert r1.trades.iloc[0]["entry_date"] == df.index[251]       # exécution à la clôture suivante


def test_random_entries_zero_drift_lose_costs():
    rng = np.random.default_rng(1)
    df = frame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 3000))) * np.linspace(1, 3, 3000))
    m = random_entries(df, {"trend_sma": 200}, df.index[300], df.index[-1], np.full(50, 3), 200, stop=None,
                       cost_side=0.001, fin_spread=0.0)
    assert np.isfinite(m).all()


def test_montecarlo_conventions():
    r = np.array([0.02, -0.01, 0.03, -0.02, 0.01] * 20)
    tot, dd = path_stats(r, 1.0)
    s = shuffle(r, 1.0, n=200)
    assert s["median_return_pct"] == pytest.approx(tot * 100)       # l'ordre ne change pas le total composé
    assert 0 <= dd <= 1 and s["p95_drawdown_pct"] <= 100
    assert path_stats(np.array([-0.99] * 5), 1.0)[1] <= 1.0         # jamais plus de 100 %
    assert removal(r, 1.0, 0.2, n=100)["median_return_pct"] < tot * 100


def test_lock_tiers_protect_half_the_gain():
    closes = [100.0] * 60 + [101.0, 130.0, 170.0, 120.0, 110.0]
    a = asset(closes)
    kw = dict(start=T0 + pd.Timedelta(days=1), end=T0 + pd.Timedelta(days=len(closes)), risk=0.01, costs=Costs(0, 0))
    base = sim4({"X": a}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.25}, **kw)
    lock = sim4({"X": a}, {"kind": "donch", "entry_n": 55, "exit_n": 20}, {"X": 0.25}, tiers=[(0.5, 0.25)], **kw)
    t = lock.trades.iloc[0]
    assert t["reason"] == "stop" and t["exit"] == pytest.approx(t["entry"] * 1.25)
    assert lock.trades["pnl"].sum() > base.trades["pnl"].sum()


def test_french_parse_drops_locked_periods():
    lines = ["header", ",Mkt-RF,SMB,HML,RF"] + [f"{d},0.10,0.0,0.0,0.01" for d in ("20230629", "20230630", "20230703", "20240102")]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.csv", "\n".join(lines) + "\n\nAnnual,\n")
    df = p5d.parse(buf.getvalue())
    assert df["date"].max() < pd.Timestamp("2023-07-01", tz="UTC") and len(df) == 2
    assert df["ret"].iloc[0] == pytest.approx(0.0011)
