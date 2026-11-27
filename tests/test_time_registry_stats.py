"""Fuseaux/DST, verrou du test final, registre, statistiques."""
import numpy as np
import pandas as pd
import pytest

from nexus.data.store import LockedPeriodError, load_bars
from nexus.research.registry import Registry
from nexus.stats.inference import (benjamini_hochberg, binary_trade_sigma, block_bootstrap_mean,
                                   deflated_sharpe, required_trades, verdict, CATEGORIES)
from nexus.timeutils import SESSION_HYPOTHESES, local_to_utc


def test_paris_midnight_in_winter_and_summer():
    assert local_to_utc(pd.Timestamp("2021-01-15"), "00:00", "Europe/Paris") == pd.Timestamp("2021-01-14 23:00", tz="UTC")
    assert local_to_utc(pd.Timestamp("2021-07-15"), "00:00", "Europe/Paris") == pd.Timestamp("2021-07-14 22:00", tz="UTC")


def test_us_eu_dst_mismatch_week():
    # 2021-03-15 : New York déjà en heure d'été, Paris pas encore → 09:30 NY = 14:30 Paris
    ny = local_to_utc(pd.Timestamp("2021-03-15"), "09:30", "America/New_York")
    assert ny.tz_convert("Europe/Paris").hour == 14 and ny.tz_convert("Europe/Paris").minute == 30


def test_session_hypotheses_are_iana():
    from zoneinfo import ZoneInfo
    for h in SESSION_HYPOTHESES.values():
        ZoneInfo(h.tz)


def test_final_test_is_locked():
    with pytest.raises(LockedPeriodError):
        load_bars("BTCUSDT", "2024-12-01", "2025-02-01")


def test_registry_requires_preregistration(tmp_path):
    reg = Registry(tmp_path / "r.sqlite")
    with pytest.raises(PermissionError):
        reg.start_trial("inconnue", {}, "EURUSD", "dev", 1.0)
    spec = {"key": "H1", "family": "A", "statement": "s", "rationale": "r", "params": {}, "data": {},
            "metrics": [], "rejection": {}}
    reg.register_hypothesis(spec)
    tid = reg.start_trial("H1", {"v": 1}, "EURUSD", "dev", 1.0)
    reg.finish_trial(tid, status="done", n_trades=10, mean_r=0.1)
    assert reg.n_trials() == 1
    spec2 = dict(spec, statement="modifiée")
    with pytest.raises(ValueError):
        reg.register_hypothesis(spec2)   # modification silencieuse interdite


def test_required_trades_reproduces_documented_numbers():
    s4 = binary_trade_sigma(4.0)
    assert s4 == pytest.approx(2.0)
    # Phase 1 : n = (z * sigma / mu)^2 avec z = 1,96 et puissance 50 %
    assert required_trades(0.10, s4, alpha=0.025, power=0.5) == 1537
    # Puissance 80 %, unilatéral 5 %
    assert required_trades(0.10, s4, alpha=0.05, power=0.8) == 2474


def test_block_bootstrap_detects_strong_positive_mean():
    rng = np.random.default_rng(0)
    v = rng.normal(0.3, 1, 2000)
    g = np.repeat(np.arange(400), 5)
    m, lo, hi, p = block_bootstrap_mean(v, g, n_boot=2000)
    assert lo > 0 and p < 0.01


def test_bh_and_dsr_sanity():
    adj = benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert adj[0] == pytest.approx(0.04) and adj[3] == 0.5
    assert deflated_sharpe(0.0, 500, 0, 3, 100, 0.01) < 0.5


def test_verdict_cannot_be_demonstrated_on_dev():
    v = verdict(0.3, 0.1, 0.5, 0.001, mean_r_2x_costs=0.2, p_random_adj=0.001, phase="dev")
    assert v == CATEGORIES[1]
    assert verdict(-0.2, -0.3, -0.1, 1.0, mean_r_2x_costs=-0.3, p_random_adj=1, phase="dev") == CATEGORIES[3]
