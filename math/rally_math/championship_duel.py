"""CHAMPIONSHIP DUEL — bonus made of tennis points (experimental).

Base game: unchanged v6 6x5 ways reels and paytable.  3 scatters -> TIE-BREAK
DUEL (4 points), 4+ scatters -> THE GRAND FINAL (6 points).  The bonus leaves
the reels: each point is played on a court.  No skill, no player choice.

One point (all draws made by the engine, always the same 6 numbers per point:
[gmp, serve1, serve2, rally, prize, presentation], each uniform in [0, 1000)):

  0. GRAND FINAL only: GOLDEN MATCH POINT if gmp < P_GMP.  The point is played
     normally; if it is WON, its prize is drawn from the GMP table instead of
     the outcome's table; if it is lost, it pays 0.
  1. First serve (serve1): ACE / FAULT / IN.
  2. After a FAULT, second serve (serve2): ACE / DOUBLE FAULT / IN.
     (A second-serve ace pays like an ace.)  Double fault: point lost, 0.
  3. Serve IN -> rally (rally): LOST (0) / RALLY WON (small prize) / WINNER /
     GOLDEN (TIE-BREAK: GOLDEN WINNER, GRAND FINAL: GOLDEN SMASH).
  4. Prize of a won point: drawn from the table of its outcome with `prize`.
  5. `presentation` only selects how the point is drawn (serve target, number
     of shots, shot direction).  It never changes a prize.

Bonus win = sum of the point prizes (no multiplier, no carry-over, no minimum).
Round win (base spin + bonus) capped at WINCAP_X.

Points are independent with identical laws inside a bonus -> the exact
distribution of a bonus is the n-fold convolution of the point distribution.
"""

from __future__ import annotations

import numpy as np

from . import config as C

D = C.CHAMPIONSHIP_DUEL
OUTCOMES = ["DOUBLE_FAULT", "ACE", "LOST", "RALLY_WON", "WINNER", "GOLDEN"]
WON = {"ACE", "RALLY_WON", "WINNER", "GOLDEN"}


def _pick(table, roll):
    """table: [[value, weight], ...] weights summing to 1000 -> value"""
    acc = 0
    for v, w in table:
        acc += w
        if roll < acc:
            return v
    raise ValueError("roll outside table")


def _pick3(probs: dict, roll):
    acc = 0
    for k, w in probs.items():
        acc += w
        if roll < acc:
            return k
    raise ValueError("roll outside table")


def presentation(level, outcome, serve_fault, roll, point_index):
    """Deterministic drawing details (no influence on prizes)."""
    side = "deuce" if point_index % 2 == 0 else "ad"
    target = ["T", "wide", "body"][roll % 3]
    if outcome in ("ACE", "DOUBLE_FAULT"):
        shots = 1
    else:
        lo, hi = D["LEVELS"][level]["RALLY_SHOTS"]
        shots = lo + (roll // 3) % (hi - lo + 1)
    finish = ["cross", "line", "inside-out"][(roll // 20) % 3]
    return {"side": side, "target": target, "shots": shots, "finish": finish}


def play_point(level: str, draws: list[int], point_index: int) -> dict:
    L = D["LEVELS"][level]
    gmp_r, s1, s2, rr, pr, pres = draws
    gmp = L.get("P_GMP", 0) > gmp_r
    first = _pick3(L["SERVE1"], s1)
    second = None
    if first == "ACE":
        outcome = "ACE"
    elif first == "FAULT":
        second = _pick3(L["SERVE2"], s2)
        outcome = "ACE" if second == "ACE" else "DOUBLE_FAULT" if second == "DOUBLE_FAULT" else None
    else:
        outcome = None
    if outcome is None:
        outcome = _pick3(L["RALLY"], rr)
    if outcome in WON:
        prize = _pick(D["GMP_TABLE"] if gmp else L["PRIZES"][outcome], pr)
    else:
        prize = 0
    return {
        "point": point_index + 1, "goldenMatchPoint": gmp, "firstServe": first, "secondServe": second,
        "outcome": outcome, "won": outcome in WON, "prize": prize,
        **presentation(level, outcome, first == "FAULT", pres, point_index),
    }


# ------------------------------------------------------------------ round (base spin + bonus), events

def play_round(draw) -> dict:
    from .engine import _win_list, evaluate_ways, positions_of, window

    ev: list[dict] = []

    def emit(e):
        ev.append({"index": len(ev), **e})

    base = C.base_reels()
    stops = draw(base.lengths)
    board = window(base.strips, stops)
    names = [[C.SYMBOLS[s] for s in col] for col in board]
    emit({"type": "reveal", "gameType": "basegame", "board": names, "stops": list(stops), "anticipation": [0] * C.NUM_REELS})
    wins = evaluate_ways(board)
    t = sum(w.base_pay for w in wins)
    pos = positions_of(board, C.SCATTER)
    n_sc = len(pos)
    sc = C.SCATTER_PAY.get(n_sc, 0)
    if t:
        emit({"type": "winInfo", "gameType": "basegame", "multiplier": 1, "totalWin": t * 10, "wins": _win_list(wins, board, 1)})
    if sc:
        emit({"type": "scatterPay", "count": n_sc, "amount": sc * 10, "positions": pos})
    total = t + sc
    emit({"type": "setWin", "amount": min(total, C.WINCAP_T) * 10})
    level = None
    if n_sc >= 3:
        level = "tiebreak" if n_sc == 3 else "final"
        n = D["LEVELS"][level]["POINTS"]
        emit({"type": "duelStart", "level": level, "points": n, "positions": pos})
        bt = 0
        for i in range(n):
            p = play_point(level, draw([1000] * 6), i)
            bt += p["prize"] * 10  # t-units (prizes are in x bet)
            emit({"type": "duelPoint", **p, "prize": p["prize"] * 100, "bonusTotal": min(bt, C.WINCAP_T) * 10})
        total += bt
        emit({"type": "duelEnd", "level": level, "bonusWin": min(bt, C.WINCAP_T) * 10, "amount": min(total, C.WINCAP_T) * 10})
    total = min(total, C.WINCAP_T)
    emit({"type": "finalWin", "amount": total * 10})
    return {"total_t": total, "events": ev, "level": level}


def play_single_point(level: str, draws: list[int], point_index: int = 0) -> dict:
    """Demo lab: one point, as a book of its own (never credited)."""
    p = play_point(level, draws, point_index)
    ev = [{"index": 0, "type": "duelStart", "level": level, "points": 1, "positions": [], "single": True},
          {"index": 1, "type": "duelPoint", **p, "prize": p["prize"] * 100, "bonusTotal": p["prize"] * 100},
          {"index": 2, "type": "duelEnd", "level": level, "bonusWin": p["prize"] * 100, "amount": p["prize"] * 100},
          {"index": 3, "type": "finalWin", "amount": p["prize"] * 100}]
    return {"point": p, "events": ev}


# ------------------------------------------------------------------ exact maths

def outcome_table(level: str) -> dict:
    """Exact probability of each (gmp, outcome) and the full point prize law (x bet)."""
    L = D["LEVELS"][level]
    pg = L.get("P_GMP", 0) / 1000
    s1 = {k: v / 1000 for k, v in L["SERVE1"].items()}
    s2 = {k: v / 1000 for k, v in L["SERVE2"].items()}
    ra = {k: v / 1000 for k, v in L["RALLY"].items()}
    p_out = {o: 0.0 for o in OUTCOMES}
    p_out["ACE"] = s1["ACE"] + s1["FAULT"] * s2["ACE"]
    p_out["DOUBLE_FAULT"] = s1["FAULT"] * s2["DOUBLE_FAULT"]
    p_in = s1["IN"] + s1["FAULT"] * s2["IN"]
    for k, v in ra.items():
        p_out[k] += p_in * v
    law: dict[float, float] = {}

    def add(v, p):
        if p > 0:
            law[v] = law.get(v, 0.0) + p

    for o, p in p_out.items():
        if o in WON:
            for v, w in L["PRIZES"][o]:
                add(v, (1 - pg) * p * w / 1000)
            for v, w in D["GMP_TABLE"]:
                add(v, pg * p * w / 1000)
        else:
            add(0, p)
    return {"p_outcome": p_out, "p_won": sum(p for o, p in p_out.items() if o in WON), "p_gmp": pg,
            "law": dict(sorted(law.items()))}


def bonus_distribution(level: str) -> dict:
    """Exact distribution of a whole bonus (convolution), on a grid of 0.5x."""
    tab = outcome_table(level)
    n = D["LEVELS"][level]["POINTS"]
    step = 0.5
    vals = list(tab["law"].items())
    assert all(abs(v / step - round(v / step)) < 1e-9 for v, _ in vals)
    m = int(max(v for v, _ in vals) / step)
    point = np.zeros(m + 1)
    for v, p in vals:
        point[int(round(v / step))] += p
    dist = np.array([1.0])
    for _ in range(n):
        dist = np.convolve(dist, point)
    x = np.arange(len(dist)) * step
    capped = np.minimum(x, C.WINCAP_X)
    mean = float((dist * capped).sum())
    var = float((dist * capped ** 2).sum() - mean ** 2)
    cdf = np.cumsum(dist)

    def q(a):
        return float(x[np.searchsorted(cdf, a)])

    return {
        "points": n, "mean_x": mean, "mean_uncapped_x": float((dist * x).sum()), "std_x": var ** 0.5,
        "p_zero": float(dist[0]), "p_lt_10x": float(dist[x < 10].sum()), "p_ge_100x": float(dist[x >= 100].sum()),
        "p_ge_1000x": float(dist[x >= 1000].sum()), "p_capped": float(dist[x >= C.WINCAP_X].sum()),
        "max_x": float(min(x[-1], C.WINCAP_X)), "max_uncapped_x": float(x[-1]),
        "quantiles_x": {str(a): q(a) for a in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999)},
        "p_at_least_one_gmp": 1 - (1 - tab["p_gmp"]) ** n,
        "p_at_least_one_golden": 1 - (1 - tab["p_outcome"]["GOLDEN"]) ** n,
    }


def exact_report() -> dict:
    from .exact import joint_stats

    Pm, E1 = joint_stats(C.base_reels().strips)
    ps = Pm.sum(axis=0)
    ways = float(E1.sum()) / 10
    scat = float(sum(ps[k] * C.SCATTER_PAY.get(k, 0) for k in range(len(ps)))) / 10
    p3 = float(ps[3])
    p4 = float(ps[4:].sum())
    rep = {"experimental": True, "rules": D, "base_ways_x": ways, "scatter_pays_x": scat, "p_tiebreak": p3, "p_final": p4}
    for lv in ("tiebreak", "final"):
        t = outcome_table(lv)
        pmean = sum(v * p for v, p in t["law"].items())
        rep[lv] = {"point": {"p_outcome": t["p_outcome"], "p_won": t["p_won"], "p_gmp": t["p_gmp"], "mean_x": pmean,
                             "std_x": (sum(v * v * p for v, p in t["law"].items()) - pmean ** 2) ** 0.5},
                   "bonus": bonus_distribution(lv)}
    rep["rtp"] = {
        "base_ways": ways, "scatter_pays": scat,
        "tiebreak": p3 * rep["tiebreak"]["bonus"]["mean_x"], "final": p4 * rep["final"]["bonus"]["mean_x"],
    }
    rep["rtp"]["total"] = sum(rep["rtp"].values())
    rep["rtp_note"] = ("exact for every component; the bonus is capped alone at the win cap, the extra effect of "
                       "the trigger spin's own win on the cap is below 1e-6 of RTP (P(bonus >= 4 900x) is shown).")
    return rep


# ------------------------------------------------------------------ Monte-Carlo (independent check)

def simulate_bonus(level: str, n: int, seed: int) -> dict:
    rng = np.random.Generator(np.random.PCG64(seed))
    k = D["LEVELS"][level]["POINTS"]
    tot = np.zeros(n)
    for i in range(k):
        dr = rng.integers(0, 1000, size=(n, 6))
        tot += np.array([play_point(level, list(map(int, d)), i)["prize"] for d in dr])
    x = np.minimum(tot, C.WINCAP_X)
    se = x.std() / n ** 0.5
    return {"n": n, "seed": seed, "mean_x": float(x.mean()), "ci95": [float(x.mean() - 1.96 * se), float(x.mean() + 1.96 * se)],
            "p_zero": float((x == 0).mean()), "p_ge_100x": float((x >= 100).mean())}
