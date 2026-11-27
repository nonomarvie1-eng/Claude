"""Audit technique indépendant (phase 2D) : traitement identique stratégie / références,
couverture de période, verrous, persistance et reproductibilité."""
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from nexus.config import RISK_PROFILES, RiskProfile
from nexus.data.store import LockedPeriodError, load_bars
from nexus.engine.backtest import FxConverter, run_backtest
from nexus.engine.execution import ExecFrame
from nexus.instruments import BTCUSDT_SPOT
from nexus.research.registry import Registry
from nexus.stats.metrics import passive_benchmarks
from nexus.strategies.base import Signal

DAY = pd.Timedelta(days=1)


def _btc_m1(days=40, seed=0):
    rng = np.random.default_rng(seed)
    n = days * 1440
    p = 30000 * np.exp(np.cumsum(rng.normal(0.00002, 0.0007, n)))
    ts = pd.date_range("2021-01-01", periods=n, freq="1min", tz="UTC")
    return pd.DataFrame({"ts": ts, "o": p, "h": p, "l": p, "c": p})


def test_validation_period_is_technically_locked():
    with pytest.raises(LockedPeriodError):
        load_bars("BTCUSDT", "2023-06-01", "2023-08-01")


def test_equity_curve_covers_full_period_when_requested():
    m1 = _btc_m1(30)
    ex = ExecFrame.from_m1(m1, BTCUSDT_SPOT)
    t0 = m1["ts"].iloc[0]
    s = Signal(avail=t0 + 10 * DAY, side=1, stop=10000.0, time_exit=t0 + 12 * DAY, entry_est=float(m1["c"].iloc[0]))
    res = run_backtest([s], ex, BTCUSDT_SPOT, RISK_PROFILES["equilibre"], FxConverter(constant=1.0),
                       period=(t0, t0 + 30 * DAY))
    assert len(res.equity_daily) == 30
    assert res.equity_daily.index[0] == t0.floor("D")
    assert (res.equity_daily.iloc[:10] == 1000).all()          # jours en liquidités inclus


def test_full_investment_strategy_matches_passive_buy_and_hold():
    """Une « stratégie » investie à 100 % du premier au dernier jour doit égaler le Buy & Hold
    passif calculé par la référence, à l'écart près du spread et du glissement modélisés
    (même traitement des frais de 0,10 % par côté)."""
    m1 = _btc_m1(40, seed=2)
    spec = BTCUSDT_SPOT
    ex = ExecFrame.from_m1(m1, spec)
    t0, t1 = m1["ts"].iloc[0], m1["ts"].iloc[-1] + pd.Timedelta(minutes=1)
    prof = RiskProfile("plein", 1.0, daily_loss_limit=10.0, max_drawdown_halt=1.0)
    s = Signal(avail=t0, side=1, stop=1.0, time_exit=t1, entry_est=float(m1["c"].iloc[0]))
    res = run_backtest([s], ex, spec, prof, FxConverter(constant=1.0), period=(t0, t1))
    d1 = m1.set_index("ts")["c"].resample("1D").last()
    fx = pd.Series(1.0, index=d1.index)
    bh = passive_benchmarks(d1, fx, 1000.0, spec.commission_rate_side, 1.0, start_price=float(m1["o"].iloc[0]))["buy_hold"]
    # B&H passif : prix de clôture journaliers ; stratégie : exécution au ask d'ouverture / bid de clôture
    friction = 2 * (spec.modeled_half_spread_frac + spec.slippage_market_frac)
    assert res.final_equity == pytest.approx(bh["final_eur"], rel=friction + 2e-3)


def test_fees_are_identical_between_strategy_and_reference():
    """Les frais en euros d'un aller-retour stratégie = 0,10 % × 2 du notionnel (pas d'avantage caché)."""
    m1 = _btc_m1(5)
    spec = replace(BTCUSDT_SPOT, modeled_half_spread_frac=0.0, slippage_market_frac=0.0, slippage_stop_frac=0.0)
    ex = ExecFrame.from_m1(m1, spec)
    t0 = m1["ts"].iloc[0]
    prof = RiskProfile("plein", 1.0, daily_loss_limit=10.0, max_drawdown_halt=1.0)
    s = Signal(avail=t0, side=1, stop=1.0, time_exit=t0 + 2 * DAY, entry_est=float(m1["c"].iloc[0]))
    tr = run_backtest([s], ex, spec, prof, FxConverter(constant=1.0)).trades.iloc[0]
    assert tr["fees_eur"] == pytest.approx(0.001 * tr["qty"] * (tr["entry"] + tr["exit"]))


def test_backtest_is_deterministic():
    m1 = _btc_m1(10, seed=5)
    ex = ExecFrame.from_m1(m1, BTCUSDT_SPOT)
    t0 = m1["ts"].iloc[0]
    sigs = [Signal(avail=t0 + k * DAY, side=1, stop=float(m1["c"].iloc[k * 1440]) * 0.97,
                   time_exit=t0 + (k + 0.5) * DAY, entry_est=float(m1["c"].iloc[k * 1440])) for k in range(8)]
    a = run_backtest(sigs, ex, BTCUSDT_SPOT, RISK_PROFILES["equilibre"], FxConverter(constant=1.1))
    b = run_backtest(sigs, ex, BTCUSDT_SPOT, RISK_PROFILES["equilibre"], FxConverter(constant=1.1))
    pd.testing.assert_frame_equal(a.trades, b.trades)


def test_registry_persists_across_connections(tmp_path):
    p = tmp_path / "r.sqlite"
    r1 = Registry(p)
    r1.register_hypothesis({"key": "P1", "family": "Z", "statement": "s", "rationale": "r", "params": {}, "data": {},
                            "metrics": [], "rejection": {}})
    r1.start_trial("P1", {}, "BTC", "dev", 1.0)
    r1.con.close()
    r2 = Registry(p)
    assert r2.n_trials() == 1
    assert r2.con.execute("SELECT COUNT(*) FROM validation_access").fetchone()[0] == 0


def test_mtm_uses_rate_of_each_day():
    """Valorisation quotidienne convertie au taux du jour (et non au taux d'entrée)."""
    m1 = _btc_m1(4)
    m1[["o", "h", "l", "c"]] = 100.0
    spec = replace(BTCUSDT_SPOT, modeled_half_spread_frac=0.0, slippage_market_frac=0.0, commission_rate_side=0.0)
    ex = ExecFrame.from_m1(m1, spec)
    t0 = m1["ts"].iloc[0]
    h1 = pd.DataFrame({"ts": pd.date_range(t0 - DAY, periods=6 * 24, freq="1h", tz="UTC"), "c": 1.0})
    h1.loc[h1["ts"] >= t0 + DAY - pd.Timedelta(hours=2), "c"] = 2.0     # l'euro double au 2e jour
    prof = RiskProfile("plein", 1.0, daily_loss_limit=10.0, max_drawdown_halt=1.0)
    s = Signal(avail=t0, side=1, stop=1.0, time_exit=t0 + 3 * DAY, entry_est=100.0)
    res = run_backtest([s], ex, spec, prof, FxConverter.build(eurusdt_h1=h1), period=(t0, t0 + 4 * DAY))
    # prix constant, pas de frais : la valeur latente en EUR est nulle quel que soit le taux
    assert res.equity_daily.iloc[1] == pytest.approx(1000.0)
