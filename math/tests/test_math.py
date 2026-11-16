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
        hi = [C.PAYTABLE[f"H{i}"][k] for i in range(1, 5)]
        assert hi == sorted(hi, reverse=True)
    assert all(v >= 0 for v in C.FINAL_SET["COURT_VALUE"].values())


@pytest.mark.parametrize("rs", [BASE, FREE, C.bonus_chance_reels()])
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
        s += sum(e["win"] for e in b["events"] if e["type"] == "shot")
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
    for name, m in exact["modes"].items():
        assert 0.960 <= m["rtp"] <= 0.967, (name, m["rtp"])
    for k, v in exact["bonus_by_trigger"].items():
        assert v["se_x"] < 0.06, (k, v["se_x"])  # bonus values measured precisely enough
    # every mode within 0.5 percentage point of the base game
    rtps = [m["rtp"] for m in exact["modes"].values()]
    assert max(rtps) - min(rtps) < 0.005


@pytest.mark.parametrize("mode,n", [("base", 4_000_000), ("bonus_chance", 4_000_000), ("buy_rally", 300_000), ("buy_final", 300_000)])
def test_simulation_consistent_with_exact(exact, mode, n):
    from rally_math.simulate import run

    e = exact["modes"][mode]
    rep = run(mode, n, seed=99, procs=os.cpu_count() or 2)
    z = (rep["rtp_observed"] - e["rtp"]) / rep["rtp_std_error"]
    assert abs(z) < 4, (mode, z)
    if mode in ("base", "bonus_chance"):
        assert rep["bonus_1_in"] == pytest.approx(e["bonus_1_in"], rel=0.06)
        assert rep["tiebreak_1_in"] == pytest.approx(e["rally_1_in"], rel=0.06)


# ---------------------------------------------------------------- export

def test_small_export_is_valid(tmp_path, exact):
    from rally_math.export_stake import export

    p = tmp_path / "exact.json"
    p.write_text(json.dumps(exact))
    plan = {3: [200, 20, 5, 2], 4: [60, 10, 5, 2], 5: [30, 5, 3, 2], 6: [20, 5, 3, 2]}
    s = export(str(tmp_path / "pub"), 2000, plan, 20000, 1, str(p))
    idx = json.load(open(tmp_path / "pub" / "index.json"))
    assert [m["name"] for m in idx["modes"]] == list(C.mode_costs())
    for m in idx["modes"]:
        assert m["cost"] == C.mode_costs()[m["name"]]
        sm = s["modes"][m["name"]]
        assert sm["lut_rtp"] == pytest.approx(exact["modes"][m["name"]]["rtp"], abs=1e-9)
        rows = list(csv.reader(open(tmp_path / "pub" / m["weights"])))
        with open(tmp_path / "pub" / m["events"], "rb") as f:
            data = zstd.ZstdDecompressor().stream_reader(f).read().decode()
        books = [json.loads(l) for l in data.splitlines() if l]
        assert len(rows) == len(books)
        for row, bk in zip(rows, books):
            assert int(row[0]) == bk["id"] and int(row[2]) == bk["payoutMultiplier"] and int(row[1]) > 0
            if m["name"] in C.BUY_SCATTERS:
                trig = [e for e in bk["events"] if e["type"] == "bonusStart"]
                assert len(trig) == 1 and trig[0]["bonus"] == C.bonus_level(C.BUY_SCATTERS[m["name"]])


# ---------------------------------------------------------------- bonus levels, buys, bonus chance

def test_buy_modes_guarantee_their_level():
    rng = np.random.default_rng(21)
    for mode, k in C.BUY_SCATTERS.items():
        r = play_round(numpy_drawer(rng), BASE, FREE, forced_base_stops=_base_with_scatters(k), mode=mode)
        trig = [e for e in r.events if e["type"] == "bonusStart"][0]
        assert trig["bought"] is True and trig["bonus"] == C.bonus_level(k) and trig["exchanges"] == C.FS_AWARD[k]
        with pytest.raises(AssertionError):
            play_round(numpy_drawer(rng), BASE, FREE, forced_base_stops=_base_with_scatters(k + 1), mode=mode)


def test_buy_conditional_draw_has_exact_scatter_count():
    from rally_math.export_stake import conditional_base_stops

    rng = np.random.default_rng(3)
    for k in (3, 4):
        bs, _ = conditional_base_stops(BASE.strips, k, rng, 2000)
        for row in bs:
            assert len(E.positions_of(E.window(BASE.strips, list(row)), C.SCATTER)) == k


def test_bonus_chance_raises_bonus_probability(exact):
    b, c = exact["modes"]["base"], exact["modes"]["bonus_chance"]
    assert c["p_bonus"] > 1.5 * b["p_bonus"] and c["p_final"] > b["p_final"]
    assert c["cost"] == C.BONUS_CHANCE_COST > 1
    # same symbols and pays: only the scatter count per reel differs
    bc = C.bonus_chance_reels()
    for r in range(C.NUM_REELS):
        nb = {s: BASE.strips[r].count(C.SYM[s]) for s in C.SYMBOLS}
        nc = {s: bc.strips[r].count(C.SYM[s]) for s in C.SYMBOLS}
        assert {k: v for k, v in nb.items() if k != "S"} == {k: v for k, v in nc.items() if k != "S"}
        assert nc["S"] >= nb["S"]


def test_buy_prices_derived_from_exact_expectation(exact):
    for mode in C.BUY_SCATTERS:
        m = exact["modes"][mode]
        assert m["cost"] == C.mode_costs()[mode]
        assert abs(m["cost"] - m["fair_cost_at_96_5"]) / m["fair_cost_at_96_5"] < 0.005


# ---------------------------------------------------------------- THE FINAL SET (Court Control, Power Shots, Hawk-Eye)

from rally_math import bonus as B  # noqa: E402

FS = C.FINAL_SET


def test_court_geometry():
    cells = [c for z in range(6) for c in B.zone_cells(z)]
    assert sorted(cells) == [(r, row) for r in range(6) for row in range(5)]  # 6 zones partition the 30 cells
    assert [len(B.zone_cells(z)) for z in range(6)] == [6, 6, 6, 4, 4, 4]
    assert B.neighbours(1) == [0, 2, 4] and B.neighbours(3) == [4, 0]
    for path in B.PASS_PATHS:  # diagonal: crosses the court, both depths, three different columns
        assert len({z % 3 for z in path}) == 3 and {z // 3 for z in path} == {0, 1}


def test_shot_tables():
    for k in ("RALLY_TABLE", "FINAL_TABLE", "CP_TABLE"):
        assert sum(FS[k].values()) == FS["SHOT_ROLL"]
    assert FS["CP_TABLE"]["RALLY"] == 0  # championship point = power shots only
    power = lambda t: FS["SHOT_ROLL"] - FS[t]["RALLY"]  # noqa: E731
    assert power("FINAL_TABLE") > power("RALLY_TABLE")


def _free_zero():
    stops = [0] * C.NUM_REELS
    board = E.window(FREE.strips, stops)
    vals, scs = B.court_values(board)
    return stops, vals, scs


def _aux(shot, **kw):
    a = [0] * len(B.AUX_LEN)
    a[0] = kw.pop("roll")
    names = [n for n, _ in B.AUX]
    for k, v in kw.items():
        a[names.index(k)] = v
    return a


def _roll(table, shot):
    acc = 0
    for sname in B.SHOTS:
        if sname == shot:
            return acc
        acc += FS[table][sname]


def _play(level, exchanges_aux, monkeypatch, exchanges=None):
    monkeypatch.setattr(C, "WINCAP_T", 10 ** 12)
    stops, vals, scs = _free_zero()
    k = 3 if level == "rally" else 4
    seq = []
    for aux in exchanges_aux:
        seq += [stops, aux]
    # pad with plain RALLY shots on a zone without scatter until the round ends
    z0 = next(z for z in range(6) if scs[z] == 0)
    pad = _aux("RALLY", roll=_roll("RALLY_TABLE" if level == "rally" else "FINAL_TABLE", "RALLY"), zone6=z0, line=999)
    seq += [stops, pad] * 60
    cp_pad = _aux("ACE", roll=_roll("CP_TABLE", "ACE"), deep3=0, line=999)
    r = play_round(list_drawer(seq), BASE, FREE, forced_base_stops=_base_with_scatters(k))
    return r, vals, scs, cp_pad


def test_each_shot_hits_the_rule_zones(monkeypatch):
    stops, vals, scs = _free_zero()
    rt = "RALLY_TABLE"
    cases = [
        ("RALLY", dict(zone6=4), [4]),
        ("ACE", dict(deep3=2), [2]),
        ("SMASH", dict(zone6=1), [1, 0, 2, 4]),
        ("PASSING", dict(path4=3), [5, 4, 0]),
        ("DROP", dict(short3=1), [4]),
        ("GOLDEN", dict(gr_n=1, gr1=0, gr2=5, gr3=5, gr4=2, gr5=3), [0, 5, 5, 2, 3]),
    ]
    for shot, kw, zones in cases:
        aux = _aux(shot, roll=_roll(rt, shot), line=999, **kw)
        r, *_ = _play("rally", [aux], monkeypatch)
        ev = [e for e in r.events if e["type"] == "shot"][0]
        assert ev["shot"] == shot and ev["path"] == zones, (shot, ev["path"])
        expect = sum(vals[z] for z in zones) * 10
        expect += (FS["ACE_PRIZE"] * 10 if shot == "ACE" else 0)
        assert ev["win"] == expect + (FS["SLAM_PRIZE"] * 10 if ev["grandSlam"] else 0), shot
        assert [h["value"] for h in ev["hits"]] == [vals[z] * 10 for z in zones]
        assert [h["cells"] for h in ev["hits"]] == [[{"reel": a, "row": b} for a, b in B.zone_cells(z)] for z in zones]


def test_marks_prize_and_expiry(monkeypatch):
    rt = "RALLY_TABLE"
    ace = _aux("ACE", roll=_roll(rt, "ACE"), deep3=1, line=999)          # marks DC for ACE_MARK exchanges
    stops, vals, scs = _free_zero()
    other = next(z for z in (0, 2, 3, 5) if scs[z] == 0)
    miss = _aux("RALLY", roll=_roll(rt, "RALLY"), zone6=other, line=999)
    hit = _aux("RALLY", roll=_roll(rt, "RALLY"), zone6=1, line=999)
    # mark still alive after ACE_MARK - 1 misses -> the hit pays MARK_PRIZE
    r, *_ = _play("rally", [ace] + [miss] * (FS["ACE_MARK"] - 1) + [hit], monkeypatch)
    shots = [e for e in r.events if e["type"] == "shot"]
    assert shots[FS["ACE_MARK"]]["hits"][0]["markPrize"] == FS["MARK_PRIZE"] * 10
    # after ACE_MARK misses the mark has expired -> no prize, and a markExpire event was emitted
    r, *_ = _play("rally", [ace] + [miss] * FS["ACE_MARK"] + [hit], monkeypatch)
    shots = [e for e in r.events if e["type"] == "shot"]
    assert shots[FS["ACE_MARK"] + 1]["hits"][0]["markPrize"] == 0
    assert any(e["type"] == "markExpire" and 1 in e["zones"] for e in r.events)


def test_drop_shot_doubles_scatter_extensions(monkeypatch):
    stops, vals, scs = _free_zero()
    rt = "RALLY_TABLE"
    for z in (3, 4, 5):
        aux = _aux("DROP", roll=_roll(rt, "DROP"), short3=z - 3, line=999)
        r, *_ = _play("rally", [aux], monkeypatch)
        ev = [e for e in r.events if e["type"] == "shot"][0]
        assert ev["hits"][0]["extraExchanges"] == 2 * scs[z]
        assert ev["marksSet"] == [{"zone": z, "duration": FS["DROP_MARK"]}]


def test_hawk_eye_in_and_out(monkeypatch):
    ft = "FINAL_TABLE"
    stops, vals, scs = _free_zero()
    base_ex = C.FS_AWARD[4]
    aux_in = _aux("RALLY", roll=_roll(ft, "RALLY"), zone6=0, line=0, call=0)
    r, *_ = _play("final", [aux_in], monkeypatch)
    ev = [e for e in r.events if e["type"] == "shot"][0]
    he = [e for e in r.events if e["type"] == "hawkEye"][0]
    assert he["call"] == "in" and ev["win"] == (vals[0] + FS["HAWK_PRIZE"]) * 10 and ev["marksSet"][0]["zone"] == 0
    aux_out = _aux("RALLY", roll=_roll(ft, "RALLY"), zone6=0, line=0, call=999)
    r, *_ = _play("final", [aux_out], monkeypatch)
    ev = [e for e in r.events if e["type"] == "shot"][0]
    he = [e for e in r.events if e["type"] == "hawkEye"][0]
    assert he["call"] == "out" and ev["win"] == 0 and ev["hits"] == [] and he["replay"] is True
    assert r.fs_spins == base_ex + 1  # the point is replayed
    # never in the Rally Challenge
    r, *_ = _play("rally", [_aux("RALLY", roll=_roll("RALLY_TABLE", "RALLY"), zone6=0, line=0, call=0)], monkeypatch)
    assert not [e for e in r.events if e["type"] == "hawkEye"]


def test_grand_slam_pays_and_clears(monkeypatch):
    rt = "RALLY_TABLE"
    gold = _aux("GOLDEN", roll=_roll(rt, "GOLDEN"), gr_n=FS["GR_MAX"] - FS["GR_MIN"], line=999,
                **{f"gr{i + 1}": i % 6 for i in range(FS["GR_MAX"])})
    r, *_ = _play("rally", [gold], monkeypatch)
    ev = [e for e in r.events if e["type"] == "shot"][0]
    assert ev["grandSlam"] is True and any(e["type"] == "grandSlam" for e in r.events)
    end = [e for e in r.events if e["type"] == "exchangeEnd"][0]
    assert end["marks"] == [0] * 6


def test_championship_point_uses_power_table(monkeypatch):
    monkeypatch.setattr(C, "WINCAP_T", 10 ** 12)
    rng = np.random.default_rng(12)
    for _ in range(30):
        r = play_round(numpy_drawer(rng), BASE, FREE, forced_base_stops=_base_with_scatters(4))
        starts = [e for e in r.events if e["type"] == "exchangeStart"]
        shots = [e for e in r.events if e["type"] == "shot"]
        for s0, sh in zip(starts, shots):
            assert s0["championshipPoint"] == (s0["remaining"] == 0)
            if s0["championshipPoint"]:
                assert sh["shot"] != "RALLY"
        assert starts[-1]["championshipPoint"]  # the last exchange is always a championship point


def test_vectorised_bonus_equals_reference_engine():
    from rally_math.export_stake import conditional_base_stops, stops_of
    from rally_math.simulate import play_vec

    rng = np.random.Generator(np.random.PCG64(77))
    bc, fc = E.count_tables(BASE.strips), E.count_tables(FREE.strips)
    for k in (3, 4, 5):
        bs, _ = conditional_base_stops(BASE.strips, k, rng, 400)
        log = []
        r = play_vec(rng, bs, bc, fc, FREE.lengths, log, free=FREE)
        for i in range(400):
            seq = stops_of(i, bs, log)
            res = play_round(list_drawer(seq[1:]), BASE, FREE, True, forced_base_stops=seq[0])
            assert res.total_t == int(r["total"][i])
            assert res.bonus_stats["slam"] == int(r["bonus_stats"]["slam"][np.searchsorted(r["bonus_idx"], i)])


def test_seeded_rounds_are_reproducible():
    a = play_round(numpy_drawer(np.random.default_rng(2024)), BASE, FREE, forced_base_stops=_base_with_scatters(4))
    b = play_round(numpy_drawer(np.random.default_rng(2024)), BASE, FREE, forced_base_stops=_base_with_scatters(4))
    assert a.events == b.events
    c = play_round(list_drawer(a.stops[1:]), BASE, FREE, forced_base_stops=a.stops[0])
    assert c.events == a.events  # exact replay from the recorded draws


def test_event_frequencies_match_tables():
    from rally_math.bonus import play_bonus_vec

    rng = np.random.Generator(np.random.PCG64(5))
    n = 200_000
    r = play_bonus_vec(rng, np.zeros(n, dtype=np.int64), np.full(n, C.FS_AWARD[3]), np.zeros(n, dtype=np.int64), FREE)
    ex = r["played"].sum()
    for sname in B.SHOTS:
        p = FS["RALLY_TABLE"][sname] / FS["SHOT_ROLL"]
        assert abs(r[sname].sum() / ex - p) < 5 * (p * (1 - p) / ex) ** 0.5, sname
    assert r["hawk"].sum() == 0
    r = play_bonus_vec(rng, np.ones(n, dtype=np.int64), np.full(n, C.FS_AWARD[4]), np.zeros(n, dtype=np.int64), FREE)
    ex, cp = r["played"].sum(), r["cp"].sum()
    for sname in B.SHOTS:
        p = ((ex - cp) * FS["FINAL_TABLE"][sname] + cp * FS["CP_TABLE"][sname]) / ex / FS["SHOT_ROLL"]
        assert abs(r[sname].sum() / ex - p) < 5 * (p * (1 - p) / ex) ** 0.5, sname
    eligible = r["RALLY"].sum() + r["ACE"].sum() + r["DROP"].sum()
    q = FS["P_LINE"] / 1000
    assert abs(r["hawk"].sum() / eligible - q) < 5 * (q * (1 - q) / eligible) ** 0.5
    qi = FS["P_IN"] / 1000
    h = r["hawk"].sum()
    assert abs(r["hawk_in"].sum() / h - qi) < 5 * (qi * (1 - qi) / h) ** 0.5


def test_grand_final_more_favourable(exact):
    bt = exact["bonus_by_trigger"]
    assert bt["4"]["E_x"] > 1.8 * bt["3"]["E_x"]
    assert bt["4"]["exchanges"] > bt["3"]["exchanges"]
