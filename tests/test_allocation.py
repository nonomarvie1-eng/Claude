"""NEXUS G : causalité, coûts identiques, passage en liquidités, arrêt global."""
import numpy as np
import pandas as pd
import pytest

from nexus.portfolio.allocation import Costs, metrics, simulate, weights

IDX = pd.date_range("2021-01-01", periods=300, freq="1D", tz="UTC")


def _d(prices):
    p = np.asarray(prices, float)
    return pd.DataFrame({"open": p, "high": p, "low": p, "close": p, "fx_open": 1.0, "fx_close": 1.0}, index=IDX[:len(p)])


def test_constant_zero_weight_is_cash():
    d = _d(np.linspace(100, 200, 50))
    r = simulate(d, pd.Series(0.0, index=d.index), d.index[0], d.index[-1] + pd.Timedelta(days=1))
    assert r.values.iloc[-1] == 1000 and r.n_trades == 0


def test_weight_executes_next_day_and_costs_applied():
    d = _d([100, 100, 110, 110])
    tgt = pd.Series([1.0, 1.0, 1.0, 1.0], index=d.index)
    c = Costs(btc_fee=0.001, conv_fee=0.001, half_spread=0.0, slippage=0.0, qty_step=1e-8, min_notional=0)
    r = simulate(d, tgt, d.index[0], d.index[-1] + pd.Timedelta(days=1), costs=c)
    assert r.values.iloc[0] == 1000                    # jour 0 : la cible n'est exécutée qu'au jour 1
    expected = 1000 * 0.999 * 0.999 * 1.10             # conversion + achat, puis +10 %
    assert r.values.iloc[2] == pytest.approx(expected, rel=1e-6)


def test_full_exit_to_cash_when_target_zero():
    d = _d([100] * 3 + [120] * 3)
    tgt = pd.Series([0.25, 0.25, 0.25, 0.0, 0.0, 0.0], index=d.index)
    r = simulate(d, tgt, d.index[0], d.index[-1] + pd.Timedelta(days=1), costs=Costs(qty_step=1e-8, min_notional=0), w_max=0.25)
    assert r.exposure.iloc[-1] == 0.0


def test_weights_are_causal():
    rng = np.random.default_rng(0)
    d = _d(100 * np.exp(np.cumsum(rng.normal(0, 0.03, 300))))
    for rule in ("G_MA", "G_TSMOM", "G_VOL", "G_PROG", "G_TSMOM_VOL"):
        full = weights(d, rule, 0.25)
        part = weights(d.iloc[:200], rule, 0.25)
        pd.testing.assert_series_equal(full.iloc[:200], part, check_names=False)
        assert (full.dropna() <= 0.25 + 1e-12).all() and (full.dropna() >= 0).all()


def test_global_halt_moves_to_cash():
    d = _d([100] * 3 + [50] * 5)
    tgt = pd.Series(1.0, index=d.index)
    r = simulate(d, tgt, d.index[0], d.index[-1] + pd.Timedelta(days=1), costs=Costs(qty_step=1e-8, min_notional=0),
                 global_halt=0.10)
    assert r.halted_on is not None and r.exposure.iloc[-1] == 0.0
    m = metrics(r)
    assert m["max_dd_pct"] > 10   # l'arrêt ne garantit pas la perte maximale (gap de −50 %)
