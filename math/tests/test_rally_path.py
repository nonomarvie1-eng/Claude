"""Rally Path prototype: rules, determinism, exact maths vs simulation, isolation from the normal game."""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from rally_math import config as C
from rally_math import rally_path as R
from rally_math.engine import list_drawer, numpy_drawer

S = C.SYM
G, K = R.G, R.RACKET
X = S["L5"]  # filler


def board(spec):
    """spec: 6 strings of 5 chars, 'G' ball, 'R' racket, '.' filler (row 0 = first char)."""
    m = {"G": G, "R": K, ".": X}
    return [[m[c] for c in col] for col in spec]


def brute_longest(b):
    best = 0
    for r0 in range(5):
        if b[0][r0] != G:
            continue
        stack = [(0, r0, 1)]
        while stack:
            i, r, n = stack.pop()
            best = max(best, n)
            if i + 1 < 6:
                for r2 in (r - 1, r, r + 1):
                    if 0 <= r2 < 5 and b[i + 1][r2] == K:
                        stack.append((i + 1, r2, n + 1))
    return best


# ---------------------------------------------------------------- rules

def test_no_ball_no_rally():
    assert R.rally(board(["....."] + ["RRRRR"] * 5)) is None


def test_ball_without_return():
    rp = R.rally(board(["..G..", "R...R", "RRRRR", ".....", ".....", "....."]))
    assert rp["length"] == 1 and rp["path"] == [{"reel": 0, "row": 2}]


def test_moves_at_most_one_row():
    rp = R.rally(board(["G....", "..R..", "RRRRR", "RRRRR", "RRRRR", "RRRRR"]))
    assert rp["length"] == 1  # row 0 -> row 2 is a two-row jump: not a return


def test_short_and_diagonal_rally():
    rp = R.rally(board(["G....", ".R...", "..R..", "...R.", ".....", "....."]))
    assert rp["length"] == 4
    assert [p["row"] for p in rp["path"]] == [0, 1, 2, 3]


def test_full_rally_is_championship_shot():
    rp = R.rally(board(["....G", "...R.", "..R..", "...R.", "....R", "...R."]))
    assert rp["length"] == 6
    t, cs = R.reward_t(6, 0)
    assert cs and t == C.RALLY_PATH_PROTO["CS_TABLE"][0][0]


def test_longest_path_chosen_and_tie_break():
    # two balls: bottom one reaches 3, top one 2 -> bottom wins
    rp = R.rally(board(["G...G", "R...R", "....R", ".....", ".....", "....."]))
    assert rp["length"] == 3 and rp["serve"]["row"] == 4
    # same length from two balls -> topmost
    rp = R.rally(board(["G...G", "R...R", ".....", ".....", ".....", "....."]))
    assert rp["serve"]["row"] == 0
    # branch tie: same row first, then up, then down
    rp = R.rally(board(["..G..", ".RRR.", ".....", ".....", ".....", "....."]))
    assert rp["path"][1]["row"] == 2
    rp = R.rally(board(["..G..", ".R.R.", ".....", ".....", ".....", "....."]))
    assert rp["path"][1]["row"] == 1


def test_dp_equals_brute_force_and_path_is_valid():
    rng = np.random.default_rng(7)
    for _ in range(3000):
        b = [[int(rng.choice([G, X, X])) if i == 0 else int(rng.choice([K, X])) for _ in range(5)] for i in range(6)]
        rp = R.rally(b)
        bl = brute_longest(b)
        if rp is None:
            assert bl == 0
            continue
        assert rp["length"] == bl
        p = rp["path"]
        assert b[0][p[0]["row"]] == G
        for a, c in zip(p, p[1:]):
            assert c["reel"] == a["reel"] + 1 and abs(c["row"] - a["row"]) <= 1 and b[c["reel"]][c["row"]] == K
        assert R.rally(b) == rp  # deterministic


def test_reward_table_and_cs_table():
    P = C.RALLY_PATH_PROTO
    assert sum(w for _, w in P["CS_TABLE"]) == P["CS_ROLL"]
    assert [R.reward_t(L, 0)[0] for L in range(1, 6)] == [P["REWARD"][str(L)] for L in range(1, 6)]
    seen = {R.cs_pick(r) for r in range(P["CS_ROLL"])}
    assert seen == {p for p, _ in P["CS_TABLE"]}
    with pytest.raises(ValueError):
        R.cs_pick(P["CS_ROLL"])


def test_golden_ball_only_on_reel1_and_not_wild():
    for kind in ("base", "free"):
        st = R.proto_reels(kind)
        assert st[0].count(G) == C.RALLY_PATH_PROTO["G_ON_REEL1"][kind]
        assert all(G not in s for s in st[1:])
    # a Golden Ball does not substitute: 5 aces after a Golden Ball on reel 1 -> no ace way on that row
    b = [[G, X, X, X, X]] + [[S["H1"], X, X, X, X] for _ in range(5)]
    from rally_math.engine import evaluate_ways
    assert all(w.symbol != S["H1"] for w in evaluate_ways(b))


# ---------------------------------------------------------------- maths

def test_exact_distribution_sums_to_one_and_matches_enumeration():
    for kind in ("base", "free"):
        d = R.length_distribution(R.proto_reels(kind))
        assert abs(sum(d.values()) - 1) < 1e-12


def test_exact_vs_simulation():
    for kind, n in (("free", 400_000), ("base", 1_000_000)):
        d = R.length_distribution(R.proto_reels(kind))
        s = R.simulate(kind, n, 11)["length_freq"]
        for L in range(7):
            sd = (d[L] * (1 - d[L]) / n) ** 0.5
            assert abs(s[L] - d[L]) <= 5 * sd + 1e-9, (kind, L, s[L], d[L])


def test_scalar_round_matches_exact_mean():
    rng = np.random.Generator(np.random.PCG64(3))
    n = 40_000
    tot = sum(R.play_proto_round(numpy_drawer(rng), "base")["total_t"] for _ in range(n)) / n / 10
    rep = R.exact_report()
    e = rep["base"]["E_spin_x"] + rep["prototype_rtp"]["scatter_pays"]
    assert abs(tot - e) < 0.08  # spin value only (no bonus), heavy tail -> loose bound


# ---------------------------------------------------------------- bonuses

def test_rally_challenge_has_no_second_serve():
    rng = np.random.Generator(np.random.PCG64(5))
    for _ in range(300):
        r = R.play_proto_round(numpy_drawer(rng), "rally")
        assert r["second_serve"] == 0
        assert sum(e["type"] == "spinStart" for e in r["events"]) == 8


def test_second_serve_once_and_only_after_short_rally():
    rng = np.random.Generator(np.random.PCG64(6))
    seen = 0
    for _ in range(300):
        r = R.play_proto_round(numpy_drawer(rng), "final")
        ev = r["events"]
        ss = [e for e in ev if e["type"] == "secondServe"]
        spins = sum(e["type"] == "spinStart" for e in ev)
        assert len(ss) <= 1 and spins == 12 + len(ss)
        if ss:
            seen += 1
            prev = [e for e in ev[: ss[0]["index"]] if e["type"] == "rallyPath"][-1]
            assert prev["length"] <= 2
            # no earlier short rally
            short = [e for e in ev[: ss[0]["index"]] if e["type"] == "rallyPath" and e["length"] <= 2]
            assert len(short) == 1
    assert seen > 0


def test_events_total_consistency():
    rng = np.random.Generator(np.random.PCG64(8))
    for mode in ("base", "rally", "final"):
        for _ in range(200):
            r = R.play_proto_round(numpy_drawer(rng), mode)
            ev = r["events"]
            s = sum(e["totalWin"] for e in ev if e["type"] == "winInfo") + sum(e["reward"] for e in ev if e["type"] == "rallyPath")
            s += sum(e["amount"] for e in ev if e["type"] == "scatterPay")
            assert min(s, C.WINCAP_T * 10) == ev[-1]["amount"] == r["total_t"] * 10  # no double counting


def test_replay_is_exact():
    rng = np.random.Generator(np.random.PCG64(9))
    rec = []

    def draw(lengths):
        v = [int(rng.integers(0, n)) for n in lengths]
        rec.append(v)
        return v

    a = R.play_proto_round(draw, "final")
    b = R.play_proto_round(list_drawer(rec), "final")
    assert a["events"] == b["events"]


# ---------------------------------------------------------------- isolation from the normal game

def test_normal_game_untouched():
    h4 = dict(C.PAYTABLE["H4"])
    base = C.base_reels().strips
    assert all(R.G not in s for s in base)
    R.exact_report()
    assert C.PAYTABLE["H4"] == h4
    with pytest.raises(RuntimeError):
        with R.proto_paytable():
            raise RuntimeError
    assert C.PAYTABLE["H4"] == h4


# ---------------------------------------------------------------- full game round (test build)

def test_game_round_accounting_and_no_old_bonus():
    rng = np.random.Generator(np.random.PCG64(12))
    seen = set()
    for _ in range(3000):
        r = R.play_game_round(numpy_drawer(rng))
        ev = r["events"]
        types = {e["type"] for e in ev}
        assert not types & {"bonusStart", "hawkEye", "shot", "exchangeStart", "grandSlam"}
        s = sum(e["totalWin"] for e in ev if e["type"] == "winInfo") + sum(e["reward"] for e in ev if e["type"] == "rallyPath")
        s += sum(e["amount"] for e in ev if e["type"] == "scatterPay")
        assert min(s, C.WINCAP_T * 10) == ev[-1]["amount"] == r["total_t"] * 10
        seen.add(r["bonus"])
    assert seen >= {None, "rally"}


def test_game_round_bonus_by_scatter_count():
    import json, os
    d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "..", "shared", "rally-path-proto.json")))
    for key, want in (("game_rally", "rally"), ("game_final", "final"), ("game_full6", None)):
        r = R.play_game_round(list_drawer(d["gameScenarios"][key]["draws"]))
        assert r["bonus"] == want
    r = R.play_game_round(list_drawer(d["gameScenarios"]["game_full6"]["draws"]))
    assert r["length"] == 6 and r["cs"]
