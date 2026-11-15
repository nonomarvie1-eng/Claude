"""Automated QA for the math engine."""

from __future__ import annotations

import csv
import json
import os

import numpy as np
import pytest
import zstandard as zstd

from atelier_math import config as C
from atelier_math import engine as E
from atelier_math.engine import list_drawer, numpy_drawer, play_round

S = C.SYM
BASE, FREE = C.base_reels(), C.free_reels()


def line(*names):
    return E._line_eval(tuple(S[n] for n in names))


# ---------------------------------------------------------------- paytable

@pytest.mark.parametrize(
    "seq,expected",
    [
        (("H1", "H1", "H1", "H1", "H1"), (500, S["H1"], 5)),
        (("H1", "H1", "H1", "L1", "L1"), (20, S["H1"], 3)),
        (("H1", "H1", "L1", "H1", "H1"), (0, -1, 0)),
        (("W", "H2", "H2", "L1", "L1"), (15, S["H2"], 3)),
        (("H2", "W", "W", "W", "H2"), (250, S["H2"], 5)),
        (("W", "W", "W", "W", "W"), (500, S["W"], 5)),
        (("W", "W", "W", "H4", "L1"), (30, S["H4"], 4)),  # 4x H4 (30) beats 3x W (20)
        (("W", "W", "W", "L4", "H1"), (20, S["W"], 3)),  # 3x W (20) beats 4x L4 (8)
        (("W", "W", "S", "H1", "H1"), (0, -1, 0)),  # scatter breaks the line
        (("S", "S", "S", "S", "S"), (0, -1, 0)),  # scatters never pay on lines
        (("L4", "L4", "W", "L4", "L4"), (22, S["L4"], 5)),
    ],
)
def test_line_evaluation(seq, expected):
    assert line(*seq) == expected


def test_all_pays_are_rgs_compatible():
    # payoutMultiplier = t*10 must be a multiple of 10 and >= 10 when non-zero
    for p in C.PAYTABLE.values():
        for v in p.values():
            assert isinstance(v, int) and v >= 1
    for v in C.SCATTER_PAY.values():
        assert isinstance(v, int) and v >= 1
    assert all(isinstance(m, int) and m >= 1 for m in C.MAINSPRING_LADDER)
    assert C.MAINSPRING_LADDER == sorted(C.MAINSPRING_LADDER)


def test_paytable_monotonic():
    for s, p in C.PAYTABLE.items():
        assert p[3] < p[4] < p[5], s
    order = ["H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4"]
    for k in (3, 4, 5):
        vals = [C.PAYTABLE[s][k] for s in order]
        assert vals == sorted(vals, reverse=True)


def test_paylines_valid_and_unique():
    assert len(C.PAYLINES) == 20
    assert len({tuple(l) for l in C.PAYLINES}) == 20
    for l in C.PAYLINES:
        assert len(l) == 5 and all(0 <= r < 3 for r in l)


# ---------------------------------------------------------------- reels

@pytest.mark.parametrize("rs", [BASE, FREE])
def test_reel_strip_constraints(rs):
    for r, strip in enumerate(rs.strips):
        n = len(strip)
        for i in range(n):
            win = [strip[(i + k) % n] for k in range(3)]
            assert win.count(S["S"]) <= 1, "at most one scatter per reel window"
        if r in (0, 4):
            assert S["W"] not in strip, "wilds only on reels 2-4"


# ---------------------------------------------------------------- rounds

def test_determinism_and_replay():
    rng = np.random.default_rng(1)
    for _ in range(300):
        r1 = play_round(numpy_drawer(rng), BASE, FREE)
        r2 = play_round(list_drawer(r1.stops), BASE, FREE)
        assert r1.events == r2.events and r1.total_t == r2.total_t


def test_independence_of_rounds_order():
    """A round's result depends only on its own stops: replaying rounds in a
    different order gives identical results (no hidden state)."""
    rng = np.random.default_rng(2)
    rounds = [play_round(numpy_drawer(rng), BASE, FREE) for _ in range(200)]
    shuffled = list(reversed(rounds))
    for r in shuffled:
        again = play_round(list_drawer(r.stops), BASE, FREE)
        assert again.total_t == r.total_t


def test_book_consistency():
    """setWin/finalWin/winInfo amounts are consistent with the payout."""
    rng = np.random.default_rng(3)
    n_bonus = 0
    for i in range(3000):
        r = play_round(numpy_drawer(rng), BASE, FREE)
        book = E.make_book(i, r)
        assert book["payoutMultiplier"] % 10 == 0
        final = [e for e in book["events"] if e["type"] == "finalWin"]
        assert len(final) == 1 and final[0]["amount"] == book["payoutMultiplier"]
        win_sum = sum(e["totalWin"] for e in book["events"] if e["type"] == "winInfo")
        assert min(win_sum, C.WINCAP_T * 10) == book["payoutMultiplier"]
        for e in book["events"]:
            if e["type"] == "winInfo":
                assert sum(w["win"] for w in e["wins"]) == e["totalWin"]
                for w in e["wins"]:
                    assert w["win"] == w["basePay"] * w["multiplier"]
            if e["type"] == "reveal":
                # the board in the book is exactly the window of the recorded stops
                strips = BASE.strips if e["gameType"] == "basegame" else FREE.strips
                board = E.window(strips, e["stops"])
                assert [[C.SYMBOLS[s] for s in reel] for reel in board] == e["board"]
        assert [e["index"] for e in book["events"]] == list(range(len(book["events"])))
        if r.triggered:
            n_bonus += 1
            fs = [e for e in book["events"] if e["type"] == "reveal" and e["gameType"] == "freegame"]
            assert len(fs) == r.fs_spins >= 10
    assert n_bonus > 5


def test_mainspring_multiplier_applies_to_line_wins():
    """Construct a free spin with a wild and check the multiplier is applied
    to that very spin (wild winds before evaluation)."""
    # find a free-game stop combination with exactly one wild and a line win
    rng = np.random.default_rng(4)
    for _ in range(100000):
        stops = [int(rng.integers(0, n)) for n in FREE.lengths]
        board = E.window(FREE.strips, stops)
        if len(E.positions_of(board, C.WILD)) == 1 and E.evaluate_lines(board) and not E.positions_of(board, C.SCATTER):
            break
    base_trigger = _find_base_with_scatters(3)
    seq = [base_trigger] + [stops] * 10
    r = play_round(list_drawer(seq), BASE, FREE)
    lw = sum(w.base_pay for w in E.evaluate_lines(board))
    expected = sum(lw * C.MAINSPRING_LADDER[min(i, 7)] for i in range(1, 11))
    base_t = r.base_t
    assert r.free_t == expected
    assert r.total_t == min(base_t + expected, C.WINCAP_T)
    assert r.final_multiplier == C.MAINSPRING_LADDER[7]


def _find_base_with_scatters(k):
    rng = np.random.default_rng(5)
    while True:
        stops = [int(rng.integers(0, n)) for n in BASE.lengths]
        if len(E.positions_of(E.window(BASE.strips, stops), C.SCATTER)) == k:
            return stops


def test_retrigger_and_max_remaining(monkeypatch):
    """12 free spins with 3 scatters, then spins without scatters.
    Remaining spins: 10 -> +4 per retrigger -> capped at 50, so the bonus lasts
    exactly 12 + 50 = 62 spins with 12 retrigger events (the last two add 1)."""
    rng = np.random.default_rng(6)
    sc_stops = no_sc = None
    while sc_stops is None or no_sc is None:
        stops = [int(rng.integers(0, n)) for n in FREE.lengths]
        n_sc = len(E.positions_of(E.window(FREE.strips, stops), C.SCATTER))
        if n_sc >= 3 and sc_stops is None:
            sc_stops = stops
        if n_sc == 0 and no_sc is None:
            no_sc = stops
    monkeypatch.setattr(C, "WINCAP_T", 10 ** 12)
    seq = [_find_base_with_scatters(3)] + [sc_stops] * 12 + [no_sc] * 50
    r = play_round(list_drawer(seq), BASE, FREE)
    assert r.fs_spins == 62
    assert r.retriggers == 12
    adds = [e["added"] for e in r.events if e["type"] == "freeSpinRetrigger"]
    assert adds == [5] * 10 + [1, 1]


def test_wincap(monkeypatch):
    monkeypatch.setattr(C, "WINCAP_T", 30)
    rng = np.random.default_rng(7)
    seen = 0
    for _ in range(20000):
        r = play_round(numpy_drawer(rng), BASE, FREE)
        assert r.total_t <= 30
        if r.capped:
            seen += 1
            assert any(e["type"] == "wincap" for e in r.events) or r.base_t >= 30
    assert seen > 0


# ---------------------------------------------------------------- exact vs MC

@pytest.fixture(scope="module")
def exact():
    from atelier_math.exact import full_report

    return full_report(procs=os.cpu_count() or 2)


def test_exact_rtp_in_stake_limits(exact):
    assert 0.960 <= exact["rtp"] <= 0.967
    assert exact["base_std_dev"] >= 0.6
    assert exact["markov_residual"] < 1e-8


def test_exact_base_lines_by_independent_method(exact):
    """Cross-check base line RTP with a completely different algorithm:
    linearity of expectation over lines using per-reel symbol marginals."""
    n_sym = len(C.SYMBOLS)
    marg = []
    for strip in BASE.strips:
        m = np.bincount(strip, minlength=n_sym) / len(strip)
        marg.append(m)
    total = 0.0
    # every row of a reel has the same marginal law, so every line has the same expectation
    it = np.ndindex(*(n_sym,) * 5)
    for idx in it:
        p = marg[0][idx[0]] * marg[1][idx[1]] * marg[2][idx[2]] * marg[3][idx[3]] * marg[4][idx[4]]
        if p:
            total += p * E._line_eval(idx)[0]
    lines_rtp = 20 * total / 10
    assert lines_rtp == pytest.approx(exact["rtp_base_lines"], rel=1e-9)


def test_scatter_distribution_matches_simulation(exact):
    """Chi-square goodness-of-fit of scatter counts (exact vs 200k simulated base spins)."""
    from scipy.stats import chisquare

    rng = np.random.default_rng(8)
    n = 200_000
    counts = np.zeros(6)
    for _ in range(n):
        stops = [int(rng.integers(0, L)) for L in BASE.lengths]
        counts[len(E.positions_of(E.window(BASE.strips, stops), C.SCATTER))] += 1
    p = np.array([exact["p_scatter"][str(k)] for k in range(6)])
    # merge rare classes 3,4,5
    obs = np.array([counts[0], counts[1], counts[2], counts[3:].sum()])
    exp = np.array([p[0], p[1], p[2], p[3:].sum()]) * n
    assert chisquare(obs, exp).pvalue > 0.001


def test_simulated_rtp_consistent_with_exact(exact):
    from atelier_math.simulate import run

    rep = run(400_000, seed=99, procs=os.cpu_count() or 2)
    z = (rep["rtp_observed"] - exact["rtp"]) / rep["rtp_std_error"]
    assert abs(z) < 4.0, z
    assert rep["hit_frequency"] == pytest.approx(exact["hit_frequency"], abs=0.004)


# ---------------------------------------------------------------- export

def test_small_export_is_valid(tmp_path, exact):
    from atelier_math.export_stake import export

    ex_path = tmp_path / "exact.json"
    ex_path.write_text(json.dumps(exact))
    s = export(str(tmp_path / "pub"), 3000, {3: 400, 4: 100, 5: 40}, seed=1, exact_path=str(ex_path))
    assert s["lut_rtp"] == pytest.approx(exact["rtp"], abs=1e-9)
    idx = json.loads((tmp_path / "pub" / "index.json").read_text())
    assert idx["modes"][0]["cost"] == 1.0
    rows = list(csv.reader(open(tmp_path / "pub" / "lookUpTable_base_0.csv")))
    with open(tmp_path / "pub" / "books_base.jsonl.zst", "rb") as f:
        data = zstd.ZstdDecompressor().stream_reader(f).read().decode()
    books = [json.loads(l) for l in data.splitlines() if l]
    assert len(rows) == len(books)
    for row, b in zip(rows, books):
        assert int(row[0]) == b["id"] and int(row[2]) == b["payoutMultiplier"]
        assert int(row[1]) > 0
        assert b["payoutMultiplier"] % 10 == 0
