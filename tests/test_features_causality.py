"""Tests de troncature : une valeur calculée à t ne doit pas changer quand on
ajoute des données postérieures à t (absence de look-ahead)."""
import numpy as np
import pandas as pd

from nexus.features.core import atr, ema, fvg, last_confirmed_level, resample, structure_events, swings

rng = np.random.default_rng(7)
N = 600
C = 100 + np.cumsum(rng.normal(0, 1, N))
H = C + rng.uniform(0, 1, N)
L = C - rng.uniform(0, 1, N)
O = np.concatenate([[C[0]], C[:-1]])


def test_ema_atr_truncation():
    full_e, full_a = ema(C, 50), atr(H, L, C, 14)
    for t in (60, 200, 599):
        np.testing.assert_allclose(ema(C[: t + 1], 50), full_e[: t + 1])
        np.testing.assert_allclose(atr(H[: t + 1], L[: t + 1], C[: t + 1], 14), full_a[: t + 1])


def test_swing_only_available_after_right_bars():
    h = np.array([1, 2, 5, 3, 2, 1, 1], float)
    l = h - 0.5
    sh, _ = swings(h, l, 1, 2)
    assert list(sh) == [2]
    lvl = last_confirmed_level(len(h), sh, h, right=2)
    assert np.isnan(lvl[2]) and np.isnan(lvl[3])   # pas encore confirmé à t=2 ni t=3
    assert lvl[4] == 5                              # confirmé à la clôture de t = 2 + 2


def test_swing_levels_truncation():
    sh, sl = swings(H, L, 2, 2)
    full = last_confirmed_level(N, sh, H, 2)
    for t in (50, 300, 598):
        sh_t, _ = swings(H[: t + 1], L[: t + 1], 2, 2)
        part = last_confirmed_level(t + 1, sh_t, H[: t + 1], 2)
        np.testing.assert_array_equal(np.nan_to_num(part, nan=-1), np.nan_to_num(full[: t + 1], nan=-1))


def test_structure_truncation():
    full = structure_events(O, H, L, C, 2, 2)
    for t in (100, 350, 599):
        part = structure_events(O[: t + 1], H[: t + 1], L[: t + 1], C[: t + 1], 2, 2)
        pd.testing.assert_frame_equal(part, full.iloc[: t + 1].reset_index(drop=True))


def test_fvg_definition_and_truncation():
    h = np.array([1.0, 1.5, 2.5, 2.6]); l = np.array([0.5, 1.0, 1.2, 2.0])
    f = fvg(h, l)
    assert f["fvg_bull"].iat[2] and f["fvg_lo"].iat[2] == 1.0 and f["fvg_hi"].iat[2] == 1.2
    full = fvg(H, L)
    pd.testing.assert_frame_equal(fvg(H[:300], L[:300]), full.iloc[:300].reset_index(drop=True))


def test_resample_avail_is_bar_close():
    ts = pd.date_range("2021-01-04 00:00", periods=10, freq="1min", tz="UTC")
    m1 = pd.DataFrame({"ts": ts, "o": range(10), "h": range(10), "l": range(10), "c": range(10)})
    m5 = resample(m1, 5)
    assert m5["avail"].iat[0] == ts[0] + pd.Timedelta(minutes=5)
    assert m5["c"].iat[0] == 4 and m5["h"].iat[1] == 9
