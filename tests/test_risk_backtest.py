"""Gestionnaire de risque, dimensionnement, limites et boucle de backtest."""
from dataclasses import replace

import pandas as pd
import pytest

from nexus.config import RISK_PROFILES, RiskProfile
from nexus.engine.backtest import FxConverter, run_backtest
from nexus.engine.execution import ExecFrame
from nexus.engine.risk import RiskManager, est_cost_per_unit
from nexus.instruments import BTCUSDT_SPOT, EURUSD_CFD
from nexus.strategies.base import Signal

from helpers import T0, ZERO_COST, m1_from_bid


def test_sizing_uses_current_equity_and_rounds_down():
    rm = RiskManager(RISK_PROFILES["equilibre"]); rm.start(1000)
    # 0,5 % de 1 000 € = 5 € ; 1 EUR = 1,10 USD → 5,50 USD ; stop 0,0020 → 2 750 unités → arrondi à 2 000
    d = rm.size(ZERO_COST, equity_eur=1000, quote_per_eur=1.10, entry_est=1.1000, stop=1.0980)
    assert d.accepted and d.qty == 2000
    d2 = rm.size(ZERO_COST, equity_eur=2000, quote_per_eur=1.10, entry_est=1.1000, stop=1.0980)
    assert d2.qty == 5000  # 11 USD / 0,002 = 5 500 → 5 000


def test_fees_are_included_in_risk_budget():
    rm = RiskManager(RISK_PROFILES["dynamique"]); rm.start(1000)
    d = rm.size(EURUSD_CFD, equity_eur=1000, quote_per_eur=1.0, entry_est=1.1, stop=1.098)
    cost_u = est_cost_per_unit(EURUSD_CFD, 1.1, 1.098)
    assert d.risk_quote == pytest.approx(d.qty * (0.002 + cost_u))
    assert d.risk_quote <= 10.0 + 1e-9


def test_min_size_rejection():
    rm = RiskManager(RISK_PROFILES["prudent"]); rm.start(1000)
    # 2,50 € de risque, stop 50 pips : 0,01 lot (1 000 u.) risquerait 5 USD > budget → refus
    d = rm.size(ZERO_COST, equity_eur=1000, quote_per_eur=1.0, entry_est=1.1, stop=1.095)
    assert not d.accepted and "minimum" in d.reason


def test_cost_share_rejection():
    rm = RiskManager(RISK_PROFILES["equilibre"]); rm.start(1000)
    d = rm.size(BTCUSDT_SPOT, equity_eur=1000, quote_per_eur=1.0, entry_est=50_000, stop=49_950)  # stop 0,1 %
    assert not d.accepted and "coûts" in d.reason


def test_spot_has_no_leverage():
    rm = RiskManager(RiskProfile("x", 0.5, daily_loss_limit=1.0)); rm.start(1000)   # risque absurde pour forcer le plafond
    d = rm.size(BTCUSDT_SPOT, equity_eur=1000, quote_per_eur=1.0, entry_est=50_000, stop=40_000)
    assert d.accepted, d.reason
    assert d.qty * 50_000 <= 1000 + 1e-6


def test_daily_loss_limit_blocks_new_trades():
    rm = RiskManager(RISK_PROFILES["dynamique"]); rm.start(1000)
    rm.on_new_day("d1", 1000)
    rm.on_trade_closed(-10, 990); rm.on_trade_closed(-10, 980)
    d = rm.size(ZERO_COST, equity_eur=980, quote_per_eur=1.0, entry_est=1.1, stop=1.095)
    assert not d.accepted and "journalière" in d.reason
    rm.on_new_day("d2", 980)
    assert rm.size(ZERO_COST, equity_eur=980, quote_per_eur=1.0, entry_est=1.1, stop=1.095).accepted


def test_drawdown_halt_is_permanent():
    rm = RiskManager(RISK_PROFILES["dynamique"]); rm.start(1000)
    rm.on_trade_closed(100, 1100)
    rm.on_trade_closed(-111, 989)   # -10,09 % depuis le sommet de 1 100
    assert rm.halted
    rm.on_new_day("autre jour", 989)
    d = rm.size(ZERO_COST, equity_eur=989, quote_per_eur=1.0, entry_est=1.1, stop=1.095)
    assert not d.accepted and "arrêté" in d.reason


def test_risk_never_increases_after_loss():
    """Anti-martingale : à capital plus faible, taille plus faible ou égale."""
    rm = RiskManager(RISK_PROFILES["dynamique"]); rm.start(1000)
    q1 = rm.size(ZERO_COST, equity_eur=1000, quote_per_eur=1.0, entry_est=1.1, stop=1.099).qty
    rm.on_new_day("x", 1000); rm.on_trade_closed(-10, 990)
    q2 = rm.size(ZERO_COST, equity_eur=990, quote_per_eur=1.0, entry_est=1.1, stop=1.099).qty
    assert 0 < q2 <= q1


def _flat_then(rows_after, n_flat=3):
    return [(1.1, 1.1, 1.1, 1.1)] * n_flat + rows_after


def test_backtest_pnl_by_hand():
    # Achat à 1,1000, stop 1,0980, objectif 2R = 1,1040, frappé minute 4.
    rows = _flat_then([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1041, 1.1, 1.104)])
    ex = ExecFrame.from_m1(m1_from_bid(rows), ZERO_COST)
    sig = Signal(avail=T0 + pd.Timedelta(minutes=3), side=1, stop=1.098, target_r=2.0,
                 time_exit=T0 + pd.Timedelta(hours=1), entry_est=1.1)
    res = run_backtest([sig], ex, ZERO_COST, RISK_PROFILES["dynamique"], FxConverter(constant=1.25))
    t = res.trades.iloc[0]
    # risque 10 € = 12,5 USD / 0,002 = 6 250 → 6 000 unités ; gain 6 000 × 0,004 = 24 USD = 19,20 €
    assert t["qty"] == 6000 and t["exit_reason"] == "target"
    assert t["pnl_eur"] == pytest.approx(19.2)
    assert t["r_net"] == pytest.approx(2.0)
    assert res.final_equity == pytest.approx(1019.2)


def test_one_position_at_a_time():
    rows = [(1.1, 1.1, 1.1, 1.1)] * 30
    ex = ExecFrame.from_m1(m1_from_bid(rows), ZERO_COST)
    s1 = Signal(avail=T0 + pd.Timedelta(minutes=1), side=1, stop=1.099, time_exit=T0 + pd.Timedelta(minutes=20), entry_est=1.1)
    s2 = Signal(avail=T0 + pd.Timedelta(minutes=5), side=1, stop=1.099, time_exit=T0 + pd.Timedelta(minutes=25), entry_est=1.1)
    res = run_backtest([s1, s2], ex, ZERO_COST, RISK_PROFILES["prudent"], FxConverter(constant=1.0))
    assert len(res.trades) == 1
    assert res.rejections.iloc[0]["reason"] == "position déjà ouverte"


def test_fx_converter_never_uses_future_rate():
    # Bougie horaire ouverte à 00:00 : sa clôture n'est connue qu'à 01:00.
    h1 = pd.DataFrame({"ts": pd.date_range("2021-01-01", periods=3, freq="1h", tz="UTC"), "c": [1.1, 1.2, 1.3]})
    fx = FxConverter.build(eurusdt_h1=h1)
    t = lambda s: pd.Timestamp(s, tz="UTC").value
    assert fx.quote_per_eur("USDT", t("2021-01-01 01:30")) == 1.1
    assert fx.quote_per_eur("USDT", t("2021-01-01 02:00")) == 1.2
    with pytest.raises(ValueError):
        fx.quote_per_eur("USDT", t("2021-01-01 00:30"))
