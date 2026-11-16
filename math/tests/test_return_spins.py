"""GOLDEN SERVE — RETURN SPINS: rules, accounting, state, replay, law."""

from __future__ import annotations

import numpy as np
import pytest

from rally_math import config as C
from rally_math import return_spins as RS
from rally_math.engine import evaluate_ways, list_drawer, numpy_drawer

R = C.RETURN_SPINS
S = C.SYM


def _rec(rng):
    rec = []

    def draw(lengths):
        v = [int(rng.integers(0, n)) for n in lengths]
        rec.append(v)
        return v

    return draw, rec


def test_strike_zones_and_smash():
    for zr in range(0, 1000, 7):
        z, reels, sm = RS.strike("base", None, zr, 999)
        assert not sm and reels == RS.ZONES[z]
        # a return never strikes a zone covered by the previous strike
        z2, reels2, _ = RS.strike("base", z, zr, 999)
        assert z2 != z and not set(reels2) & set(RS.ZONES[z])
        zs, rs_, sm2 = RS.strike("final", None, zr, 0)
        assert sm2 and len(rs_) == 4 and rs_ in ([0, 1, 2, 3], [2, 3, 4, 5])
    # after a smash only the uncovered zone remains
    assert RS.strike("final", "left+center", 500, 999)[0] == "right"
    assert RS.strike("final", "center+right", 0, 999)[0] == "left"
    assert R["P_SMASH"]["rally"] == 0 and R["P_SMASH"]["final"] > R["P_SMASH"]["base"]


def test_golden_ball_is_not_a_wild_and_pays_nothing():
    G = RS.G
    b = [[S["H1"]] * 5, [G] * 5, [S["H1"]] * 5, [S["H1"]] * 5, [S["L5"]] * 5, [S["L5"]] * 5]
    assert all(w.symbol != S["H1"] for w in evaluate_ways(b))  # G breaks the H1 ways like an empty reel


@pytest.mark.parametrize("seed", [1, 2])
def test_round_rules_accounting_state(seed):
    rng = np.random.Generator(np.random.PCG64(seed))
    for _ in range(6000):
        draw, rec = _rec(rng)
        r = RS.play_round(draw)
        ev = r["events"]
        # accounting: stage wins + scatter = final (capped); no other payment
        paid = sum(e["stageWin"] for e in ev if e["type"] == "stageWin") + sum(e["amount"] for e in ev if e["type"] == "scatterPay")
        assert min(paid, C.WINCAP_T * 10) == ev[-1]["amount"] == r["total_t"] * 10
        board = None
        stops = None
        phase_returns = 0
        phase = "base"
        for e in ev:
            if e["type"] == "rsBonusStart":
                phase = e["bonus"]
            if e["type"] == "reveal":
                board, stops = e["board"], e["stops"]
                phase_returns = 0
            if e["type"] == "serve":
                if e["kind"] == "return":
                    phase_returns += 1
                    assert phase_returns <= R["MAX_RETURNS"][phase]
                    assert board[e["origin"]["reel"]][e["origin"]["row"]] == "G" and e["origin"]["reel"] in prev_reels
                else:
                    assert board[e["origin"]["reel"]][e["origin"]["row"]] == "G"
                prev_reels = e["reels"]
            if e["type"] == "respin":
                # only the struck reels moved
                for i in range(6):
                    if i not in e["reels"]:
                        assert e["stops"][i] == stops[i] and e["board"][i] == board[i]
                board, stops = e["board"], e["stops"]
            if e["type"] == "stageWin":
                nb = [[S[x] if x != "G" else RS.G for x in col] for col in board]
                assert e["stageWin"] == sum(w.base_pay for w in evaluate_ways(nb)) * 10
        assert RS.play_round(list_drawer(rec))["events"] == ev  # exact replay


def test_first_stop_win_is_the_ordinary_slot_win():
    """the first stage of a base spin is exactly the v6 ways evaluation of that grid"""
    rng = np.random.Generator(np.random.PCG64(4))
    for _ in range(2000):
        r = RS.play_round(numpy_drawer(rng))
        rv = r["events"][0]
        st0 = [e for e in r["events"] if e["type"] == "stageWin"][0]
        nb = [[S[x] if x != "G" else RS.G for x in col] for col in rv["board"]]
        assert st0["stage"] == 0 and st0["stageWin"] == sum(w.base_pay for w in evaluate_ways(nb)) * 10


def test_scalar_and_vectorised_engines_have_the_same_law():
    rng = np.random.Generator(np.random.PCG64(5))
    n = 60000
    xs = np.array([RS.play_spin(numpy_drawer(rng), "final", lambda e: None, "freegame")["t"] for _ in range(n)]) / 10
    t, *_ = RS.spins_vec(np.random.Generator(np.random.PCG64(6)), "final", 400000)
    v = t / 10
    se = (xs.var() / n + v.var() / len(v)) ** 0.5
    assert abs(xs.mean() - v.mean()) < 4 * se, (xs.mean(), v.mean(), se)


def test_bonus_by_scatter_count_and_strips():
    for k in ("base", "free"):
        st = RS.strips_of(k)
        assert [s.count(RS.G) for s in st] == R["G_PER_REEL"][k]
    rng = np.random.Generator(np.random.PCG64(7))
    seen = set()
    for _ in range(40000):
        r = RS.play_round(numpy_drawer(rng))
        if r["bonus"]:
            n = [e for e in r["events"] if e["type"] == "scatterPay"][0]["count"]
            assert r["bonus"] == ("rally" if n == 3 else "final")
            assert sum(e["type"] == "spinStart" for e in r["events"]) == R["BONUS"][r["bonus"]]["spins"]
            seen.add(r["bonus"])
    assert "rally" in seen
