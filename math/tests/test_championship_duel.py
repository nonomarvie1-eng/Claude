"""CHAMPIONSHIP DUEL: point rules, exact maths vs enumeration and simulation, accounting, replay."""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from rally_math import championship_duel as CD
from rally_math import config as C
from rally_math.engine import list_drawer, numpy_drawer

D = C.CHAMPIONSHIP_DUEL


def test_tables_are_complete():
    for lv, L in D["LEVELS"].items():
        for k in ("SERVE1", "SERVE2", "RALLY"):
            assert sum(L[k].values()) == 1000
        for o, t in L["PRIZES"].items():
            assert sum(w for _, w in t) == 1000 and all(v > 0 for v, _ in t)
    assert sum(w for _, w in D["GMP_TABLE"]) == 1000
    assert "P_GMP" not in D["LEVELS"]["tiebreak"]


def test_point_rules():
    lv = "tiebreak"
    S1, S2, RA = (D["LEVELS"][lv][k] for k in ("SERVE1", "SERVE2", "RALLY"))
    ace1 = 0
    fault = S1["ACE"]
    inn = S1["ACE"] + S1["FAULT"]
    # first-serve ace: no second serve, no rally
    p = CD.play_point(lv, [999, ace1, 0, 0, 0, 0], 0)
    assert p["outcome"] == "ACE" and p["secondServe"] is None and p["prize"] == D["LEVELS"][lv]["PRIZES"]["ACE"][0][0]
    # fault then double fault: point lost, 0
    p = CD.play_point(lv, [999, fault, S2["ACE"], 0, 999, 0], 0)
    assert p["firstServe"] == "FAULT" and p["outcome"] == "DOUBLE_FAULT" and p["prize"] == 0 and not p["won"]
    # fault then second serve in, rally lost
    p = CD.play_point(lv, [999, fault, 999, 0, 999, 0], 0)
    assert p["secondServe"] == "IN" and p["outcome"] == "LOST" and p["prize"] == 0
    # first serve in, winner
    p = CD.play_point(lv, [999, inn, 0, RA["LOST"] + RA["RALLY_WON"], 0, 0], 0)
    assert p["outcome"] == "WINNER" and p["prize"] == D["LEVELS"][lv]["PRIZES"]["WINNER"][0][0]


def test_presentation_never_changes_the_prize():
    rng = np.random.default_rng(1)
    for lv in ("tiebreak", "final"):
        for _ in range(3000):
            d = [int(x) for x in rng.integers(0, 1000, 6)]
            a = CD.play_point(lv, d, 0)
            for pres in (0, 333, 999):
                b = CD.play_point(lv, d[:5] + [pres], 0)
                assert (a["outcome"], a["prize"], a["goldenMatchPoint"]) == (b["outcome"], b["prize"], b["goldenMatchPoint"])


def test_golden_match_point_only_in_final_and_lost_pays_zero():
    rng = np.random.default_rng(2)
    seen = 0
    for _ in range(20000):
        d = [int(x) for x in rng.integers(0, 1000, 6)]
        assert not CD.play_point("tiebreak", d, 0)["goldenMatchPoint"]
        p = CD.play_point("final", d, 0)
        if p["goldenMatchPoint"]:
            seen += 1
            if not p["won"]:
                assert p["prize"] == 0
            else:
                assert p["prize"] in [v for v, _ in D["GMP_TABLE"]]
    assert seen > 0


@pytest.mark.parametrize("lv", ["tiebreak", "final"])
def test_exact_point_law_equals_full_enumeration(lv):
    """enumerate all relevant rolls (coarse-grained on table boundaries) -> same law as outcome_table"""
    L = D["LEVELS"][lv]

    def cuts(weights):
        out, acc = [], 0
        for w in weights:
            out.append((acc, w))
            acc += w
        return out

    s1, s2, ra = cuts(L["SERVE1"].values()), cuts(L["SERVE2"].values()), cuts(L["RALLY"].values())
    g = [(0, L.get("P_GMP", 0)), (L.get("P_GMP", 0), 1000 - L.get("P_GMP", 0))]
    law = {}
    tables = [t for t in L["PRIZES"].values()] + [D["GMP_TABLE"]]
    pr_cuts = sorted({0} | {c for t in tables for c in itertools.accumulate(w for _, w in t)} - {1000})
    pr = [(a, b - a) for a, b in zip(pr_cuts, pr_cuts[1:] + [1000])]
    for (gr, gw), (r1, w1), (r2, w2), (r3, w3), (r4, w4) in itertools.product(g, s1, s2, ra, pr):
        if gw == 0:
            continue
        p = CD.play_point(lv, [gr, r1, r2, r3, r4, 0], 0)
        law[p["prize"]] = law.get(p["prize"], 0) + gw * w1 * w2 * w3 * w4 / 1000 ** 5
    exact = CD.outcome_table(lv)["law"]
    assert set(law) == set(exact)
    for v in law:
        assert abs(law[v] - exact[v]) < 1e-12


@pytest.mark.parametrize("lv,seed", [("tiebreak", 3), ("final", 4)])
def test_exact_bonus_mean_vs_simulation(lv, seed):
    b = CD.bonus_distribution(lv)
    s = CD.simulate_bonus(lv, 60000, seed)
    se = b["std_x"] / 60000 ** 0.5
    assert abs(s["mean_x"] - b["mean_x"]) < 4 * se


def test_rtp_components_and_target_window():
    r = CD.exact_report()
    assert abs(r["rtp"]["total"] - sum(v for k, v in r["rtp"].items() if k != "total")) < 1e-12
    assert 0.955 < r["rtp"]["total"] < 0.967  # experimental target ~96 %


def test_round_accounting_events_replay():
    rng = np.random.Generator(np.random.PCG64(5))
    levels = set()
    for _ in range(20000):
        rec = []

        def draw(lengths):
            v = [int(rng.integers(0, n)) for n in lengths]
            rec.append(v)
            return v

        r = CD.play_round(draw)
        ev = r["events"]
        s = sum(e["totalWin"] for e in ev if e["type"] == "winInfo") + sum(e["amount"] for e in ev if e["type"] == "scatterPay")
        s += sum(e["prize"] for e in ev if e["type"] == "duelPoint")
        assert min(s, C.WINCAP_T * 10) == ev[-1]["amount"] == r["total_t"] * 10  # no double counting
        assert not {e["type"] for e in ev} & {"bonusStart", "hawkEye", "goldenServe", "rallyPath", "protoBonusStart", "gsBonusStart"}
        if r["level"]:
            n_sc = [e for e in ev if e["type"] == "scatterPay"][0]["count"]
            assert r["level"] == ("tiebreak" if n_sc == 3 else "final")
            assert sum(e["type"] == "duelPoint" for e in ev) == D["LEVELS"][r["level"]]["POINTS"]
            levels.add(r["level"])
            assert CD.play_round(list_drawer(rec))["events"] == ev
    assert "tiebreak" in levels
