"""Automated QA for the GOLDEN RALLY math engine (6x5 ways)."""

from __future__ import annotations

import csv
import itertools
import json
import os

import numpy as np
import pytest
import zstandard as zstd

from rally_math import config as C
from rally_math import engine as E
from rally_math.engine import list_drawer, numpy_drawer, play_round

S = C.SYM
BASE, FREE = C.base_reels(), C.free_reels()


def board_of(cols):
    return [[S[x] for x in col] for col in cols]


# ---------------------------------------------------------------- ways evaluation

def test_ways_basic():
    filler = ["L5", "L4", "L3", "L2", "L1"]
    b = [list(filler) for _ in range(6)]
    for r in range(3):
        b[r][0] = "H1"
    wins = {C.SYMBOLS[w.symbol]: w for w in E.evaluate_ways(board_of(b))}
    assert wins["H1"].reels == 3 and wins["H1"].ways == 1 and wins["H1"].base_pay == C.PAYTABLE["H1"][3]


def test_ways_multiply_and_wild():
    b = [["H2", "H2", "L1", "L1", "L1"],
         ["W", "L2", "L2", "L2", "L2"],
         ["H2", "H2", "H2", "L3", "L3"],
         ["H2", "L4", "L4", "L4", "L4"],
         ["L5", "L5", "L5", "L5", "L5"],
         ["H2", "H2", "H2", "H2", "H2"]]
    wins = {C.SYMBOLS[w.symbol]: w for w in E.evaluate_ways(board_of(b))}
    w = wins["H2"]
    assert (w.reels, w.ways) == (4, 2 * 1 * 3 * 1)
    assert w.base_pay == C.PAYTABLE["H2"][4] * 6


def test_scatter_never_pays_as_way():
    b = [["S", "L1", "L1", "L2", "L3"]] + [["L1", "L2", "L3", "L4", "L5"]] * 5
    wins = {C.SYMBOLS[w.symbol] for w in E.evaluate_ways(board_of(b))}
    assert "S" not in wins and "L1" in wins


def test_vectorised_matches_reference():
    rng = np.random.default_rng(11)
    cnt = E.count_tables(FREE.strips)
    stops = np.stack([rng.integers(0, L, 3000) for L in FREE.lengths], axis=1)
    lw, w, sc = E.ways_win_vec(cnt, stops)
    for i in range(3000):
        b = E.window(FREE.strips, list(stops[i]))
        assert lw[i] == sum(x.base_pay for x in E.evaluate_ways(b))
        assert w[i] == len(E.positions_of(b, C.WILD))
        assert sc[i] == len(E.positions_of(b, C.SCATTER))


# ---------------------------------------------------------------- tables & strips

def test_pays_rgs_compatible_and_monotonic():
    for s, p in C.PAYTABLE.items():
        assert all(isinstance(v, int) and v >= 1 for v in p.values())
        assert [p[k] for k in range(3, 7)] == sorted(p[k] for k in range(3, 7)), s
    for k in range(3, 7):
        hi = [C.PAYTABLE[f"H{i}"][k] for i in range(1, 6)]
        assert hi == sorted(hi, reverse=True)
    assert C.RALLY_LADDER == sorted(C.RALLY_LADDER) and C.RALLY_LADDER[0] == 1


@pytest.mark.parametrize("rs", [BASE, FREE])
def test_strip_constraints(rs):
    for r, strip in enumerate(rs.strips):
        n = len(strip)
        for i in range(n):
            assert [strip[(i + k) % n] for k in range(C.NUM_ROWS)].count(S["S"]) <= 1
        if r == 0:
            assert S["W"] not in strip


# ---------------------------------------------------------------- rounds

def test_determinism_replay_and_independence():
    rng = np.random.default_rng(1)
    rounds = [play_round(numpy_drawer(rng), BASE, FREE) for _ in range(300)]
    for r in reversed(rounds):
        again = play_round(list_drawer(r.stops), BASE, FREE)
        assert again.events == r.events and again.total_t == r.total_t


def test_book_consistency():
    rng = np.random.default_rng(3)
    nb = 0
    for i in range(2000):
        r = play_round(numpy_drawer(rng), BASE, FREE)
        b = E.make_book(i, r)
        assert b["payoutMultiplier"] % 10 == 0
        fin = [e for e in b["events"] if e["type"] == "finalWin"]
        assert len(fin) == 1 and fin[0]["amount"] == b["payoutMultiplier"]
        s = sum(e["totalWin"] for e in b["events"] if e["type"] == "winInfo")
        assert min(s, C.WINCAP_T * 10) == b["payoutMultiplier"]
        for e in b["events"]:
            if e["type"] == "winInfo":
                assert sum(w["win"] for w in e["wins"]) == e["totalWin"]
                for w in e["wins"]:
                    assert w["win"] == w["basePay"] * w["ways"] * w["multiplier"]
            if e["type"] == "reveal":
                strips = BASE.strips if e["gameType"] == "basegame" else FREE.strips
                assert [[C.SYMBOLS[x] for x in col] for col in E.window(strips, e["stops"])] == e["board"]
        nb += r.triggered
    assert nb > 3


def _base_with_scatters(k, seed=5):
    rng = np.random.default_rng(seed)
    while True:
        s = [int(rng.integers(0, n)) for n in BASE.lengths]
        if len(E.positions_of(E.window(BASE.strips, s), C.SCATTER)) == k:
            return s


def _free_stops(pred, seed=4):
    rng = np.random.default_rng(seed)
    while True:
        s = [int(rng.integers(0, n)) for n in FREE.lengths]
        if pred(E.window(FREE.strips, s)):
            return s


def test_rally_multiplier_applies_on_same_spin(monkeypatch):
    monkeypatch.setattr(C, "WINCAP_T", 10 ** 12)
    st = _free_stops(lambda b: len(E.positions_of(b, C.WILD)) == 1 and E.evaluate_ways(b) and not E.positions_of(b, C.SCATTER))
    b = E.window(FREE.strips, st)
    lw = sum(w.base_pay for w in E.evaluate_ways(b))
    n = C.FS_AWARD[3]
    r = play_round(list_drawer([st] * n), BASE, FREE, forced_base_stops=_base_with_scatters(3))
    top = len(C.RALLY_LADDER) - 1
    assert r.free_t == sum(lw * C.RALLY_LADDER[min(i, top)] for i in range(1, n + 1))
    assert r.final_multiplier == C.RALLY_LADDER[min(n, top)]


def test_retrigger_and_max_remaining(monkeypatch):
    monkeypatch.setattr(C, "WINCAP_T", 10 ** 12)
    sc = _free_stops(lambda b: len(E.positions_of(b, C.SCATTER)) >= 3)
    no = _free_stops(lambda b: len(E.positions_of(b, C.SCATTER)) == 0)
    rem, adds = C.FS_AWARD[3], []
    for _ in range(12):
        rem -= 1
        a = min(C.FS_RETRIGGER, C.FS_MAX_REMAINING - rem)
        rem += max(a, 0)
        adds.append(a)
    r = play_round(list_drawer([sc] * 12 + [no] * rem), BASE, FREE, forced_base_stops=_base_with_scatters(3))
    assert r.fs_spins == 12 + rem
    assert [e["added"] for e in r.events if e["type"] == "freeSpinRetrigger"] == [a for a in adds if a > 0]


def test_wincap(monkeypatch):
    monkeypatch.setattr(C, "WINCAP_T", 30)
    rng = np.random.default_rng(7)
    seen = 0
    for _ in range(5000):
        r = play_round(numpy_drawer(rng), BASE, FREE)
        assert r.total_t <= 30
        seen += r.capped
    assert seen > 0


# ---------------------------------------------------------------- exact method

def test_polynomial_method_equals_brute_force_enumeration():
    """Independent check of the exact method on tiny strips: enumerate ALL
    boards with the reference engine and compare the joint law of
    (wilds, scatters) and the expected ways win per cell."""
    from rally_math.exact import joint_stats

    reel0 = ["H1", "L1", "S", "L2", "H2", "L1", "H1", "L3"]
    reelx = ["H1", "L1", "S", "L2", "H2", "L1", "W", "L1"]
    strips = [[S[x] for x in (reel0 if r == 0 else reelx)] for r in range(6)]
    P, E1 = joint_stats(strips)
    L = [len(s) for s in strips]
    N = float(np.prod(L))
    Pb = np.zeros_like(P)
    Eb = np.zeros_like(E1)
    for stops in itertools.product(*[range(n) for n in L]):
        b = E.window(strips, list(stops))
        w = len(E.positions_of(b, C.WILD))
        c = len(E.positions_of(b, C.SCATTER))
        Pb[w, c] += 1 / N
        Eb[w, c] += sum(x.base_pay for x in E.evaluate_ways(b)) / N
    np.testing.assert_allclose(P, Pb, atol=1e-12)
    np.testing.assert_allclose(E1, Eb, rtol=1e-10, atol=1e-10)


@pytest.fixture(scope="module")
def exact():
    from rally_math.exact import full_report

    return full_report()


def test_exact_rtp_in_stake_limits(exact):
    assert 0.960 <= exact["rtp"] <= 0.967
    assert exact["markov_residual"] < 1e-8


def test_simulation_consistent_with_exact(exact):
    from rally_math.simulate import run

    rep = run(4_000_000, seed=99, procs=os.cpu_count() or 2)
    z = (rep["rtp_observed"] - exact["rtp"]) / rep["rtp_std_error"]
    assert abs(z) < 4, z
    assert rep["trigger_1_in"] == pytest.approx(exact["trigger_1_in"], rel=0.05)
    assert rep["rtp_base_observed"] == pytest.approx(exact["rtp_base"], abs=0.004)


# ---------------------------------------------------------------- export

def test_small_export_is_valid(tmp_path, exact):
    from rally_math.export_stake import export

    p = tmp_path / "exact.json"
    p.write_text(json.dumps(exact))
    plan = {3: [200, 20, 5, 2], 4: [60, 10, 5, 2], 5: [30, 5, 3, 2], 6: [20, 5, 3, 2]}
    s = export(str(tmp_path / "pub"), 2000, plan, 20000, 1, str(p))
    assert s["lut_rtp"] == pytest.approx(exact["rtp"], abs=1e-9)
    rows = list(csv.reader(open(tmp_path / "pub" / "lookUpTable_base_0.csv")))
    with open(tmp_path / "pub" / "books_base.jsonl.zst", "rb") as f:
        data = zstd.ZstdDecompressor().stream_reader(f).read().decode()
    books = [json.loads(l) for l in data.splitlines() if l]
    assert len(rows) == len(books)
    for row, b in zip(rows, books):
        assert int(row[0]) == b["id"] and int(row[2]) == b["payoutMultiplier"] and int(row[1]) > 0


# ---------------------------------------------------------------- bonus buy

def test_buy_mode_round(monkeypatch):
    rng = np.random.default_rng(21)
    for k in C.BUY_SCATTER_WEIGHTS:
        st = _base_with_scatters(k)
        r = play_round(numpy_drawer(rng), BASE, FREE, forced_base_stops=st, bought=True)
        trig = [e for e in r.events if e["type"] == "freeSpinTrigger"][0]
        assert trig["totalFs"] == C.FS_AWARD[k] and trig["bought"] is True
    with pytest.raises(AssertionError):
        play_round(numpy_drawer(rng), BASE, FREE, forced_base_stops=_base_with_scatters(5), bought=True)


def test_buy_rtp_exact_and_simulated(exact):
    from rally_math.simulate import run_buy

    assert 0.960 <= exact["buy"]["rtp"] <= 0.967
    rep = run_buy(400_000, seed=5)
    z = (rep["rtp_observed"] - exact["buy"]["rtp"]) / rep["rtp_std_error"]
    assert abs(z) < 4, z
