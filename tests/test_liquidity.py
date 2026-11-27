"""Phase 3 : détecteurs de liquidité causaux et moteur d'études événementielles."""
import numpy as np
import pandas as pd
import pytest

from nexus.liquidity.events import controls_for, evaluate, delta_test
from nexus.liquidity.levels import Level, Market, fvg_records, pd_levels, session_levels, swing_levels, ny


def _m1(prices, start="2021-03-01 00:00"):
    p = np.asarray(prices, float)
    ts = pd.date_range(start, periods=len(p), freq="1min", tz="UTC")
    return pd.DataFrame({"ts": ts, "o": p, "h": p + 0.5, "l": p - 0.5, "c": p})


def _rw(days=20, seed=0):
    rng = np.random.default_rng(seed)
    return _m1(30000 + np.cumsum(rng.normal(0, 5, days * 1440)))


def test_pdh_pdl_available_only_at_next_ny_midnight():
    mk = Market(_rw(6))
    lv = pd_levels(mk)
    for x in lv:
        assert x.avail.tz_convert("America/New_York").hour == 0
        assert x.avail > x.created
        # le niveau ne contient que des minutes antérieures à sa disponibilité
        i = mk.idx(x.created); j = mk.idx(x.avail)
        ext = mk.h[i:j].max() if x.kind == "PDH" else mk.l[i:j].min()
        assert ext == pytest.approx(x.price)


def test_session_window_respects_dst():
    # 2021-03-15 : New York en heure d'été → 02:00 NY = 06:00 UTC ; 2021-03-08 : 07:00 UTC
    assert ny(pd.Timestamp("2021-03-15"), "02:00") == pd.Timestamp("2021-03-15 06:00", tz="UTC")
    assert ny(pd.Timestamp("2021-03-08"), "02:00") == pd.Timestamp("2021-03-08 07:00", tz="UTC")


def test_session_levels_touch_window_after_formation():
    mk = Market(_rw(5, seed=1))
    for x in session_levels(mk, "02:00", "05:00", "LONDON", 0, "05:00", "16:00"):
        assert x.touch_from >= x.avail


def test_swings_never_available_before_confirmation():
    mk = Market(_rw(15, seed=2))
    res = swing_levels(mk, 2, 2)
    for x in res["swing"]:
        # disponibilité = clôture de la 2e bougie H1 après le pivot
        assert x.avail >= x.created + pd.Timedelta(hours=3)
    for x in res["eq"] + res["lrl"] + res["hrl"]:
        assert x.avail > x.created


def test_fvg_records_causal_truncation():
    df = _rw(10, seed=3)
    full = fvg_records(Market(df))
    cut_t = df["ts"].iloc[len(df) // 2]
    part = fvg_records(Market(df[df["ts"] < cut_t]))
    a = full[full["avail"] < cut_t - pd.Timedelta(minutes=5)][["t", "lo", "hi", "avail"]].reset_index(drop=True)
    b = part[part["avail"] < cut_t - pd.Timedelta(minutes=5)][["t", "lo", "hi", "avail"]].reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)


PRE = 1200   # 20 h d'historique pour amorcer l'ATR14 H1


def _flat_then(path):
    return _m1([100.0] * PRE + list(path))


def test_reversal_race_and_ambiguity():
    # support à 99 ; ATR H1 ≈ 1 (barres de ±0,5) ; touche puis rebondit de +1 ATR
    df = _flat_then([99.4] * 5 + [100.5] * 60)
    mk = Market(df)
    t0 = df["ts"].iloc[PRE]
    lv = Level("TEST", 99.0, +1, t0, t0, "test", t0, t0 + pd.Timedelta(hours=2))
    r = evaluate(mk, lv)
    assert r["touched"] and r["race"] in ("rev", "cont")
    # niveau déjà franchi à la disponibilité → exclu
    lv2 = Level("TEST", 101.0, +1, t0, t0, "test", t0, t0 + pd.Timedelta(hours=2))
    assert evaluate(mk, lv2)["status"] == "deja_atteint"


def test_same_minute_both_barriers_counts_as_continuation():
    p = [100.0] * PRE + [100.0, 99.0, 99.0]
    df = _m1(p)
    df.loc[PRE + 2, "h"] = 120.0; df.loc[PRE + 2, "l"] = 80.0     # minute qui touche les deux barrières
    mk = Market(df)
    t0 = df["ts"].iloc[PRE]
    lv = Level("TEST", 99.0, +1, t0, t0, "test", t0, t0 + pd.Timedelta(hours=1))
    r = evaluate(mk, lv)
    assert r["race"] == "cont"


def test_controls_same_side_and_separated():
    mk = Market(_rw(5, seed=4))
    t0 = mk.m1["ts"].iloc[3000]
    ref = mk.o[mk.idx(t0)]
    lv = Level("PDL", ref - 50, +1, t0, t0, "test", t0, t0 + pd.Timedelta(hours=24))
    cs = controls_for(mk, lv, 5, np.random.default_rng(0))
    a = mk.atr_h1_at(t0)
    assert len(cs) == 5
    for c in cs:
        assert c.price < ref and abs(c.price - lv.price) >= 0.25 * a and c.avail == lv.avail


def test_delta_test_detects_difference():
    rng = np.random.default_rng(0)
    t = pd.date_range("2021-01-01", periods=600, freq="6h", tz="UTC")
    real = pd.DataFrame({"status": "ok", "touched": True, "avail": t, "race": np.where(rng.random(600) < 0.65, "rev", "cont")})
    ctrl = pd.DataFrame({"status": "ok", "touched": True, "avail": t, "race": np.where(rng.random(600) < 0.45, "rev", "cont")})
    d = delta_test(real, ctrl, "reversal", n_boot=1000)
    assert d["delta"] > 0.1 and d["p"] < 0.01


def test_null_calibration_touch_and_reversal_unbiased_on_random_walk():
    """Sous H0 (marche aléatoire), les deux métriques ne doivent pas montrer d'effet :
    garde-fou contre un biais de construction des contrôles (amendement 3-01a)."""
    from nexus.liquidity.events import run_levels
    rng = np.random.default_rng(11)
    n = 120 * 1440
    p = 30000 * np.exp(np.cumsum(rng.normal(0, 0.0008, n)))
    w = np.abs(rng.normal(0, 0.0004, n)) * p
    ts = pd.date_range("2021-01-01", periods=n, freq="1min", tz="UTC")
    mk = Market(pd.DataFrame({"ts": ts, "o": p, "h": p + w, "l": p - w, "c": p}))
    lv = swing_levels(mk)["swing"]
    r_t, c_t = run_levels(mk, lv, control_mode="timeshift")
    r_d, c_d = run_levels(mk, lv, control_mode="distance")
    dt = delta_test(r_t, c_t, "touch", n_boot=500)
    dr = delta_test(r_d, c_d, "reversal", n_boot=500)
    assert dt["ci95"][0] < 0 < dt["ci95"][1] or abs(dt["delta"]) < 0.03
    assert dr["ci95"][0] < 0 < dr["ci95"][1] or abs(dr["delta"]) < 0.03
