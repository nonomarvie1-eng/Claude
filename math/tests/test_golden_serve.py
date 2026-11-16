"""Golden Serve prototypes A (Cross-Court) and B (Court Switch)."""

from __future__ import annotations

import collections

import numpy as np
import pytest

from rally_math import config as C
from rally_math import golden_serve as GS
from rally_math.engine import evaluate_ways, list_drawer, numpy_drawer

S = C.SYM
G = GS.G


def test_trajectory_rules():
    assert GS.path_rows(0, 4) == [0, 1, 2, 2, 3, 4]  # floor(x + 0.5): 2.4 -> 2, 2.5 -> 3? check below
    assert GS.path_rows(4, 0)[0] == 4 and GS.path_rows(4, 0)[-1] == 0
    for r0 in range(5):
        for rt in range(5):
            p = GS.path_rows(r0, rt)
            assert p[0] == r0 and p[-1] == rt
            assert all(abs(a - b) <= 1 for a, b in zip(p, p[1:]))  # a continuous line
    t = GS.trajectories(2, "smash", 0, 0)
    assert len(t) == 2 and all(abs(a[1] - b[1]) == 1 for a, b in zip(t[0][1:], t[1][1:]))
    assert len(GS.trajectories(2, "double", 0, 4)) == 2 and len(GS.trajectories(2, "serve", 0, 4)) == 1


def test_shot_and_target_tables():
    P = C.GOLDEN_SERVE_PROTO
    for ph in ("base", "rally", "final"):
        assert sum(P["TARGET_W"][ph]) == 1000
        assert P["P_SMASH"][ph] + P["P_DOUBLE"][ph] < 1000
        c = collections.Counter(GS.shot_of(ph, r) for r in range(1000))
        assert c["smash"] == P["P_SMASH"][ph] and c["double"] == P["P_DOUBLE"][ph]
    assert P["P_SMASH"]["base"] < P["P_SMASH"]["final"]  # smash is rarer outside the Grand Final


def _rand_board(rng, with_g=True):
    syms = [S[x] for x in ("H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4", "L5", "W", "S")]
    b = [[int(rng.choice(syms)) for _ in range(5)] for _ in range(6)]
    if with_g:
        b[0][int(rng.integers(0, 5))] = G
    return b


def test_cross_court_transforms_exactly_the_hit_cells():
    rng = np.random.default_rng(1)
    for _ in range(2000):
        b = _rand_board(rng)
        serve = [int(rng.integers(0, 5)), int(rng.integers(0, 1000)), int(rng.integers(0, 1000)), int(rng.integers(0, 5))]
        nb, ev = GS.apply_shot(b, "A", "final", serve)
        hit = {(c["reel"], c["row"]) for p in ev["paths"] for c in p}
        T = S[ev["target"]]
        changed = {(c["reel"], c["row"]) for c in ev["changes"]}
        for i in range(6):
            for r in range(5):
                if (i, r) in hit and b[i][r] not in (C.WILD, C.SCATTER):
                    assert nb[i][r] == T
                else:
                    assert nb[i][r] == b[i][r]
                assert ((i, r) in changed) == (nb[i][r] != b[i][r])
        assert G not in nb[0]


def test_court_switch_only_moves_symbols():
    rng = np.random.default_rng(2)
    for _ in range(2000):
        b = _rand_board(rng)
        serve = [int(rng.integers(0, 5)), 0, int(rng.integers(0, 1000)), int(rng.integers(0, 5))]
        nb, ev = GS.apply_shot(b, "B", "final", serve)
        before = collections.Counter(x for col in b[1:] for x in col)
        after = collections.Counter(x for col in nb[1:] for x in col)
        assert before == after  # reels 2..6: exchanges only
        assert G not in nb[0] and all(s["a"]["reel"] in (1, 2) and s["b"]["reel"] == s["a"]["reel"] + 3 for s in ev["swaps"])


def test_no_golden_ball_no_shot():
    rng = np.random.default_rng(3)
    b = _rand_board(rng, with_g=False)
    for c in "AB":
        assert GS.apply_shot(b, c, "base", [0, 0, 0, 0]) == (b, None)


@pytest.mark.parametrize("concept", ["A", "B"])
def test_vectorised_equals_scalar(concept):
    for phase, game_type in (("base", "basegame"), ("final", "freegame")):
        r1 = np.random.Generator(np.random.PCG64(9))
        r2 = np.random.Generator(np.random.PCG64(9))
        for _ in range(1500):
            t, sc, hg, sh = GS._spins(r1, concept, phase, 1)
            s = GS.play_spin(numpy_drawer(r2), concept, phase, lambda e: None, game_type)
            assert int(t[0]) == s["t"] and bool(hg[0]) == (s["shot"] is not None)


@pytest.mark.parametrize("concept", ["A", "B"])
def test_round_accounting_events_and_replay(concept):
    rng = np.random.Generator(np.random.PCG64(10 + ord(concept)))
    bonuses = set()
    for _ in range(1500):
        rec = []

        def draw(lengths):
            v = [int(rng.integers(0, n)) for n in lengths]
            rec.append(v)
            return v

        r = GS.play_round(draw, concept)
        ev = r["events"]
        assert not {e["type"] for e in ev} & {"bonusStart", "hawkEye", "shot", "exchangeStart", "rallyPath"}
        s = sum(e["totalWin"] for e in ev if e["type"] == "winInfo") + sum(e["amount"] for e in ev if e["type"] == "scatterPay")
        assert min(s, C.WINCAP_T * 10) == ev[-1]["amount"] == r["total_t"] * 10
        for e in ev:
            if e["type"] == "goldenServe":  # wins are evaluated on the transformed board published in the event
                nb = [[S[x] for x in col] for col in e["board"]]
                nxt = ev[e["index"] + 1] if e["index"] + 1 < len(ev) else None
                t = sum(w.base_pay for w in evaluate_ways(nb))
                assert (nxt["totalWin"] if nxt and nxt["type"] == "winInfo" else 0) == t * 10
        bonuses.add(r["bonus"])
        assert GS.play_round(list_drawer(rec), concept)["events"] == ev
    assert None in bonuses


def test_bonus_level_by_scatter_count():
    rng = np.random.Generator(np.random.PCG64(77))
    seen = {}
    for _ in range(20000):
        r = GS.play_round(numpy_drawer(rng), "A")
        if r["bonus"]:
            n_sc = [e for e in r["events"] if e["type"] == "scatterPay"][0]["count"]
            assert r["bonus"] == ("rally" if n_sc == 3 else "final")
            spins = sum(e["type"] == "spinStart" for e in r["events"])
            assert spins == C.GOLDEN_SERVE_PROTO["BONUS"][r["bonus"]]["spins"]
            seen[r["bonus"]] = True
    assert seen.get("rally")


def test_golden_ball_only_reel1_and_normal_game_untouched():
    for k in ("base", "free"):
        st = GS.strips_of(k)
        assert st[0].count(G) == C.GOLDEN_SERVE_PROTO["G_ON_REEL1"][k] and all(G not in s for s in st[1:])
    assert all(G not in s for s in C.base_reels().strips)
