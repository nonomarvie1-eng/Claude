"""Tests phase 2C : stop suiveur, valorisation quotidienne, régimes, stratégies H1/H4/D1,
budgets d'expériences, walk-forward de la sélection."""
import numpy as np
import pandas as pd
import pytest

from nexus.config import RISK_PROFILES
from nexus.engine.backtest import FxConverter, run_backtest
from nexus.engine.execution import ExecFrame, simulate
from nexus.features.regime import daily_regimes, regime_at, trailing_percentile
from nexus.research.lab import walk_forward_selection
from nexus.research.registry import Registry
from nexus.stats.metrics import exposure_stats
from nexus.strategies import trend
from nexus.strategies.base import Signal

from helpers import T0, ZERO_COST, m1_from_bid

FAR = T0 + pd.Timedelta(days=30)


def test_trailing_stop_applies_only_after_its_decision_time_and_ratchets():
    rows = [(1.0, 1.0, 1.0, 1.0)] * 3 + [(1.0, 1.0, 0.97, 0.98)] + [(0.98, 0.98, 0.95, 0.96)]
    ex = ExecFrame.from_m1(m1_from_bid(rows), ZERO_COST)
    # stop initial 0.90 ; à partir de la minute 4, stop relevé à 0.955 ; une baisse ultérieure à 0.92 est ignorée
    path = ([int((T0 + pd.Timedelta(minutes=4)).value), int((T0 + pd.Timedelta(minutes=5)).value)], [0.955, 0.92])
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.90, target=None, time_exit=FAR, stop_path=path)
    assert f.reason == "stop" and f.exit_idx == 4          # minute 3 (plus bas 0,97) n'est pas touchée
    assert f.exit_price == pytest.approx(0.955)


def test_trailing_stop_gap_fills_at_open():
    rows = [(1.0, 1.0, 1.0, 1.0)] * 2 + [(0.94, 0.95, 0.93, 0.94)]
    ex = ExecFrame.from_m1(m1_from_bid(rows), ZERO_COST)
    path = ([int((T0 + pd.Timedelta(minutes=2)).value)], [0.97])
    f = simulate(ex, ZERO_COST, side=1, signal_avail=T0, stop=0.90, target=None, time_exit=FAR, stop_path=path)
    assert f.reason == "stop" and f.exit_price == pytest.approx(0.94)


def test_daily_mark_to_market_for_multi_day_position():
    # Position ouverte 3 jours : latent négatif le 1er soir, visible dans la courbe quotidienne
    day = pd.Timedelta(days=1)
    rows = [(1.0, 1.0, 1.0, 1.0)] * 3 + [(0.95, 0.95, 0.95, 0.95)] * 3 + [(1.05, 1.05, 1.05, 1.05)] * 3
    df = m1_from_bid(rows)
    df["ts"] = [T0 + i // 3 * day + pd.Timedelta(minutes=i % 3) for i in range(len(rows))]
    from dataclasses import replace
    spec = replace(ZERO_COST, min_qty=1.0, qty_step=1.0)
    ex = ExecFrame.from_m1(df, spec)
    sig = Signal(avail=T0, side=1, stop=0.5, time_exit=T0 + 2 * day + pd.Timedelta(minutes=2), entry_est=1.0)
    res = run_backtest([sig], ex, spec, RISK_PROFILES["dynamique"], FxConverter(constant=1.0))
    eq = res.equity_daily
    q = res.trades["qty"].iloc[0]
    assert eq.iloc[0] == pytest.approx(1000 + q * (0.95 - 1.0) * 0 + q * (1.0 - 1.0))  # fin du 1er jour : prix 1,0
    assert eq.iloc[1] == pytest.approx(1000 + q * (0.95 - 1.0))                         # fin du 2e jour : latent −
    assert res.final_equity == pytest.approx(1000 + q * 0.05)


def _synthetic_m1(days=500, seed=0):
    rng = np.random.default_rng(seed)
    n = days * 1440
    p = 100 * np.exp(np.cumsum(rng.normal(0.00001, 0.0008, n)))
    ts = pd.date_range("2020-01-01", periods=n, freq="1min", tz="UTC")
    return pd.DataFrame({"ts": ts, "o": p, "h": p * 1.0003, "l": p * 0.9997, "c": p})


def test_regimes_are_causal_truncation():
    m1 = _synthetic_m1(420)
    full = daily_regimes(m1)
    cut = daily_regimes(m1[m1["ts"] < pd.Timestamp("2020-12-01", tz="UTC")])
    k = len(cut)
    pd.testing.assert_frame_equal(cut.reset_index(drop=True), full.iloc[:k].reset_index(drop=True))
    # le régime du jour D n'est connu qu'à D+1 00:00
    t = int(full["day"].iat[300].value) + 3600 * 10**9
    assert regime_at(full, t)["trend"] == full["trend"].iat[299]


def test_trailing_percentile_uses_only_past():
    x = np.arange(400, dtype=float)
    pct = trailing_percentile(x, window=365, min_periods=10)
    assert pct[200] == 1.0 and np.isnan(pct[5])


@pytest.mark.parametrize("fn,kw", [(trend.nexus_c, {}), (trend.nexus_c, {"exit_mode": "trailing", "confirmation": True}),
                                   (trend.nexus_f_tsmom, {"lookback": 20}), (trend.nexus_f_donchian, {"n": 20}),
                                   (trend.ref_sma, {}), (trend.nexus_d, {}), (trend.nexus_e, {"mode": "zscore"}),
                                   (trend.nexus_e, {"mode": "atr"}), (trend.nexus_e, {"mode": "shock"}),
                                   (trend.nexus_e, {"mode": "zscore", "consolidation_filter": True})])
def test_trend_strategies_signals_do_not_depend_on_future(fn, kw):
    """Les signaux émis avant une date ne changent pas si l'on retire les données postérieures
    (hors heure de sortie, qui dépend par nature de la suite)."""
    m1 = _synthetic_m1(400, seed=3)
    cut_t = pd.Timestamp("2020-10-01", tz="UTC")
    tf = "H4"
    full = fn(trend.TFContext.build(m1, tf), **kw)
    part = fn(trend.TFContext.build(m1[m1["ts"] < cut_t], tf), **kw)
    f_before = [(s.avail, round(s.stop, 10)) for s in full if s.time_exit < cut_t - pd.Timedelta(days=2)]
    p_before = [(s.avail, round(s.stop, 10)) for s in part if s.time_exit < cut_t - pd.Timedelta(days=2)]
    assert f_before == p_before
    for s in full:
        assert s.avail.value % (240 * 60 * 10**9) == 0   # décision à une clôture H4
        assert s.stop < s.entry_est and s.side == 1


def test_exposure_stats():
    tr = pd.DataFrame({"duration_h": [24.0, 24.0], "exposure_frac": [0.5, 0.1]})
    e = exposure_stats(tr, "2021-01-01", "2021-01-11")
    assert e["time_in_market_pct"] == pytest.approx(20.0)
    assert e["avg_exposure_pct"] == pytest.approx((24 * 0.5 + 24 * 0.1) / 240 * 100)


def test_budget_enforced_and_extensions_logged(tmp_path):
    reg = Registry(tmp_path / "r.sqlite")
    spec = {"key": "X1", "family": "Z", "statement": "s", "rationale": "r", "params": {}, "data": {},
            "metrics": [], "rejection": {}}
    reg.register_hypothesis(spec)
    reg.set_budget("Z", 2, "test")
    reg.start_trial("X1", {"a": 1}, "BTC", "dev", 1.0)
    reg.start_trial("X1", {"a": 2}, "BTC", "dev", 1.0)
    with pytest.raises(PermissionError):
        reg.start_trial("X1", {"a": 3}, "BTC", "dev", 1.0)
    reg.set_budget("Z", 3, "extension documentée")
    assert reg.con.execute("SELECT COUNT(*) FROM budget_changes").fetchone()[0] == 1
    reg.start_trial("X1", {"a": 3}, "BTC", "dev", 1.0)


def test_walk_forward_selection_uses_only_past():
    t = pd.date_range("2020-01-01", "2021-12-31", freq="7D", tz="UTC")
    good_past = pd.DataFrame({"entry_time": t, "exit_time": t, "r_net": np.where(t < pd.Timestamp("2021-01-01", tz="UTC"), 1.0, -1.0)})
    flat = pd.DataFrame({"entry_time": t, "exit_time": t, "r_net": np.zeros(len(t))})
    wf = walk_forward_selection({"A": good_past, "B": flat}, "2020-01-01", "2022-01-01")
    # au pli 2021-01, A est choisi (bon passé) et son résultat futur négatif est bien compté
    f = [x for x in wf["folds"] if x["fold"].startswith("2021-01")][0]
    assert f["choice"] == "A" and f["mean_r"] == -1.0
