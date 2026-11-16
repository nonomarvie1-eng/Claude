"""GOLDEN SERVE — RETURN SPINS (experimental vertical slice).

The game stays a 6x5 / 15,625-ways slot at all times.

One spin
--------
1. The six reels stop (stage 0).  The full grid is evaluated (ways); its win
   is paid.
2. GOLDEN SERVE: if the grid shows at least one GOLDEN BALL (G), the topmost
   G of the leftmost reel serves.  G is neither a Wild nor a Scatter, pays
   nothing and substitutes for nothing (it is an empty cell for the ways).
   Every G visible at that moment is "used": it can never serve again.
3. The engine draws the struck ZONE.  Zones: LEFT = reels 1-2, CENTRE =
   reels 3-4, RIGHT = reels 5-6.  GOLDEN SMASH (probability P_SMASH per
   strike, phase dependent) strikes a wide zone of four reels: LEFT+CENTRE
   (reels 1-4) or CENTRE+RIGHT (reels 3-6).
4. Only the struck reels spin again (new uniform stops on the same strips);
   the other reels do not move.  The full grid is evaluated again and its win
   is paid as well: EVERY STOP IS PAID ON ITS OWN, including combinations
   that were already present before the respin.  Round win = sum of the
   stop wins (+ scatter pay on the first stop) — each stop is shown apart.
5. RETURN SPIN: if the respin landed at least one NEW G on the struck reels
   and the return limit of the phase is not reached, that G returns the
   ball: new strike (step 3) aimed at a zone not covered by the previous
   strike.  Limits: base game MAX_RETURNS["base"], Rally Challenge 2,
   Championship Night 3.  Hence at most 1 + MAX_RETURNS respins per spin.

Draws (always in this order, recorded for exact replay): 6 stops; per strike
[zone_roll, smash_roll] (0..999); then the stops of the struck reels.

Bonuses: scatters on the FIRST stop of a base spin: 3 -> RALLY CHALLENGE
(8 free spins), 4+ -> CHAMPIONSHIP NIGHT (12 free spins), on the bonus reels.
Scatter pay on that first stop only.  In free spins scatters pay nothing and
do not retrigger.  Win cap WINCAP_X on the whole round.
"""

from __future__ import annotations

import numpy as np

from . import config as C

R = C.RETURN_SPINS
G = len(C.SYMBOLS)
NAMES = C.SYMBOLS + ["G"]
NR, ROWS = C.NUM_REELS, C.NUM_ROWS
W, S = C.WILD, C.SCATTER
PAYING = [C.SYM[s] for s in C.SYMBOLS if s not in ("W", "S")]
ZONES = {"left": [0, 1], "center": [2, 3], "right": [4, 5]}
ZONE_ORDER = ["left", "center", "right"]


def _insert_g(strip, n):
    s = list(strip)
    L = len(s)
    for p in sorted({int(round((i + 0.5) * L / n)) for i in range(n)}, reverse=True):
        s.insert(p, G)
    return s


_REELS: dict = {}


def strips_of(kind: str):
    if kind not in _REELS:
        if kind == "base":
            base = C.base_reels().strips
        else:
            from .reels import STACK, build_reelset

            base = [[C.SYM[x] for x in st] for st in build_reelset(R["FREE_COUNTS"], R["FREE_SEED"], STACK)]
        _REELS[kind] = [_insert_g(st, n) if n else list(st) for st, n in zip(base, R["G_PER_REEL"][kind])]
    return _REELS[kind]


def window(strips, stops):
    return [[st[(stops[r] + k) % len(st)] for k in range(ROWS)] for r, st in enumerate(strips)]


def strike(phase: str, prev: str | None, zone_roll: int, smash_roll: int):
    """-> (zone name, reels).  Candidates: zones not covered by the previous strike."""
    covered = set()
    if prev:
        for z in prev.split("+"):
            covered.add(z)
    cand = [z for z in ZONE_ORDER if z not in covered]
    z = cand[zone_roll * len(cand) // 1000]
    smash = smash_roll < R["P_SMASH"][phase]
    if smash:
        if z == "left":
            z2 = "left+center"
        elif z == "right":
            z2 = "center+right"
        else:
            z2 = "left+center" if zone_roll % 2 == 0 else "center+right"
        reels = sorted(r for part in z2.split("+") for r in ZONES[part])
        return z2, reels, True
    return z, ZONES[z], False


# ------------------------------------------------------------------ ways (G = blank)

def ways_wins(board):
    from .engine import evaluate_ways

    return evaluate_ways(board)


def _names(board):
    return [[NAMES[s] for s in col] for col in board]


def play_spin(draw, phase: str, emit, game_type: str, total_before: int = 0) -> dict:
    from .engine import _win_list

    kind = "base" if phase == "base" else "free"
    strips = strips_of(kind)
    stops = list(draw([len(s) for s in strips]))
    board = window(strips, stops)
    first_board = board
    emit({"type": "reveal", "gameType": game_type, "board": _names(board), "stops": list(stops), "anticipation": [0] * NR})
    spin_t = 0
    stage = 0
    stage_wins = []

    def evaluate():
        nonlocal spin_t
        wins = ways_wins(board)
        t = sum(w.base_pay for w in wins)
        spin_t += t
        stage_wins.append(t)
        emit({"type": "stageWin", "gameType": game_type, "stage": stage, "stageWin": t * 10,
              "spinTotal": spin_t * 10, "runningTotal": (total_before + spin_t) * 10,
              "wins": _win_list(wins, board, 1) if t else []})

    evaluate()
    # serve
    gpos = [(r, row) for r in range(NR) for row in range(ROWS) if board[r][row] == G]
    returns = 0
    prev = None
    origin = gpos[0] if gpos else None
    kindev = "serve"
    smashes = 0
    while origin is not None:
        zone_roll, smash_roll = draw([1000, 1000])
        zone, reels, smash = strike(phase, prev, zone_roll, smash_roll)
        smashes += smash
        emit({"type": "serve", "kind": kindev, "smash": smash, "origin": {"reel": origin[0], "row": origin[1]},
              "zone": zone, "reels": reels, "returnIndex": returns, "maxReturns": R["MAX_RETURNS"][phase]})
        new = draw([len(strips[r]) for r in reels])
        for r, s in zip(reels, new):
            stops[r] = s
        board = window(strips, stops)
        stage += 1
        emit({"type": "respin", "gameType": game_type, "stage": stage, "reels": reels, "stops": list(stops), "board": _names(board)})
        evaluate()
        prev = zone
        newg = [(r, row) for r in reels for row in range(ROWS) if board[r][row] == G]
        if newg and returns < R["MAX_RETURNS"][phase]:
            returns += 1
            origin = newg[0]
            kindev = "return"
        else:
            origin = None
    return {"t": spin_t, "first": first_board, "stages": stage_wins, "returns": returns, "served": bool(gpos), "smashes": smashes}


def play_round(draw) -> dict:
    from .engine import positions_of

    ev: list[dict] = []

    def emit(e):
        ev.append({"index": len(ev), **e})

    s = play_spin(draw, "base", emit, "basegame")
    pos = positions_of(s["first"], S)
    n_sc = len(pos)
    sc = C.SCATTER_PAY.get(n_sc, 0)
    if sc:
        emit({"type": "scatterPay", "count": n_sc, "amount": sc * 10, "positions": pos})
    total = s["t"] + sc
    emit({"type": "setWin", "amount": min(total, C.WINCAP_T) * 10})
    bonus = None
    info = {"base_t": s["t"], "served": s["served"], "returns": s["returns"], "stages": s["stages"], "smashes": s["smashes"]}
    if n_sc >= 3:
        bonus = "rally" if n_sc == 3 else "final"
        n = R["BONUS"][bonus]["spins"]
        emit({"type": "rsBonusStart", "bonus": bonus, "spins": n, "positions": pos})
        bt = 0
        for k in range(1, n + 1):
            emit({"type": "spinStart", "spin": k, "total": n})
            f = play_spin(draw, bonus, emit, "freegame", total + bt)
            bt += f["t"]
            emit({"type": "setTotalWin", "amount": min(total + bt, C.WINCAP_T) * 10})
        total += bt
        emit({"type": "rsBonusEnd", "bonus": bonus, "bonusWin": min(bt, C.WINCAP_T) * 10, "amount": min(total, C.WINCAP_T) * 10})
    total = min(total, C.WINCAP_T)
    emit({"type": "finalWin", "amount": total * 10})
    return {"total_t": total, "events": ev, "bonus": bonus, **info}


# ------------------------------------------------------------------ vectorised simulation (same law)

def _ways_t(b):
    m = b.shape[0]
    tot = np.zeros(m, dtype=np.int64)
    isw = b == W
    for s in PAYING:
        cnt = ((b == s) | isw).sum(axis=2)
        ways = np.ones(m, dtype=np.int64)
        alive = np.ones(m, dtype=bool)
        k = np.zeros(m, dtype=np.int64)
        for i in range(NR):
            alive &= cnt[:, i] > 0
            ways = np.where(alive, ways * np.maximum(cnt[:, i], 1), ways)
            k += alive
        pay = np.zeros(NR + 1, dtype=np.int64)
        for kk, v in C.PAYTABLE[C.SYMBOLS[s]].items():
            pay[kk] = v
        tot += pay[k] * ways
    return tot


def _win(arr, stops):
    idx = stops[:, :, None] + np.arange(ROWS)[None, None, :]
    return np.stack([arr[i][idx[:, i, :] % len(arr[i])] for i in range(NR)], 1)


def spins_vec(rng, phase, m):
    """m independent spins of a phase -> (spin_t, first-stop scatter count, served, returns, respins, smashes)."""
    kind = "base" if phase == "base" else "free"
    arr = [np.array(s) for s in strips_of(kind)]
    lens = np.array([len(a) for a in arr])
    stops = np.stack([rng.integers(0, len(a), m) for a in arr], 1)
    b = _win(arr, stops)
    sc = (b == S).sum(axis=(1, 2))
    t = _ways_t(b)
    active = (b == G).any(axis=(1, 2))
    served = active.copy()
    prev_cov = np.zeros((m, 3), dtype=bool)
    returns = np.zeros(m, dtype=np.int64)
    respins = np.zeros(m, dtype=np.int64)
    smashes = np.zeros(m, dtype=np.int64)
    maxr = R["MAX_RETURNS"][phase]
    ps = R["P_SMASH"][phase]
    while active.any():
        a = np.nonzero(active)[0]
        zr = rng.integers(0, 1000, len(a))
        sr = rng.integers(0, 1000, len(a))
        cand = ~prev_cov[a]
        ncand = cand.sum(1)
        pick = zr * ncand // 1000
        order = np.cumsum(cand, 1) - 1
        zone = np.argmax(cand & (order == pick[:, None]), 1)  # 0 left 1 center 2 right
        smash = sr < ps
        cov = np.zeros((len(a), 3), dtype=bool)
        cov[np.arange(len(a)), zone] = True
        wide_right = np.where(zone == 0, False, np.where(zone == 2, True, zr % 2 == 1))
        cov[smash & ~wide_right, 0] = True
        cov[smash & ~wide_right, 1] = True
        cov[smash & wide_right, 1] = True
        cov[smash & wide_right, 2] = True
        reel_mask = np.repeat(cov, 2, axis=1)  # (len(a), 6)
        smashes[a] += smash
        # new stops for the struck reels, drawn reel by reel in increasing order (same as scalar)
        st = stops[a].copy()
        for r in range(NR):
            sel = np.nonzero(reel_mask[:, r])[0]
            if len(sel):
                st[sel, r] = rng.integers(0, lens[r], len(sel))
        stops[a] = st
        nb = _win(arr, st)
        t[a] += _ways_t(nb)
        respins[a] += 1
        newg = ((nb == G).any(axis=2) & reel_mask).any(axis=1)
        cont = newg & (returns[a] < maxr)
        returns[a] += cont
        prev_cov[a] = cov
        active[a] = cont
    return t, sc, served, returns, respins, smashes


def simulate(n: int, seed: int, n_bonus: int = 200_000) -> dict:
    """NOTE: the vectorised draw order differs from the scalar engine (batched), the LAW is identical."""
    rng = np.random.Generator(np.random.PCG64(seed))
    out = {"seed": seed, "n": n, "n_bonus": n_bonus}

    def bonus(phase, k):
        tot = np.zeros(k, dtype=np.int64)
        st = {"served": 0, "returns": 0, "smashes": 0, "respins": 0}
        for _ in range(R["BONUS"][phase]["spins"]):
            t, _, sv, rt, rs, sm = spins_vec(rng, phase, k)
            tot += t
            st["served"] += int(sv.sum()); st["returns"] += int(rt.sum()); st["smashes"] += int(sm.sum()); st["respins"] += int(rs.sum())
        return tot, {k2: v / k for k2, v in st.items()}

    for phase in ("rally", "final"):
        tt, st = bonus(phase, n_bonus)
        x = np.minimum(tt, C.WINCAP_T) / 10
        se = x.std() / n_bonus ** 0.5
        out[f"bonus_{phase}"] = {
            "mean_x": float(x.mean()), "ci95": [float(x.mean() - 1.96 * se), float(x.mean() + 1.96 * se)], "std_x": float(x.std()),
            "median_x": float(np.median(x)), "p_zero": float((x == 0).mean()), "p_lt_10x": float((x < 10).mean()),
            "p_ge_100x": float((x >= 100).mean()), "p_ge_1000x": float((x >= 1000).mean()), "max_x": float(x.max()),
            "per_bonus": st, "quantiles_x": {str(q): float(np.quantile(x, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99)},
        }
    scp = np.zeros(NR * ROWS + 1, dtype=np.int64)
    for k, v in C.SCATTER_PAY.items():
        scp[k] = v
    s1 = s2 = 0.0
    hits = big = 0
    agg = {"served": 0, "returns": 0, "smashes": 0, "respins": 0, "returns_hist": np.zeros(R["MAX_RETURNS"]["base"] + 1), "trig3": 0, "trig4": 0}
    base_feature_t = 0.0
    done = 0
    while done < n:
        m = min(400_000, n - done)
        t, sc, sv, rt, rs, sm = spins_vec(rng, "base", m)
        base_feature_t += float(t.sum())
        x = t + scp[sc]
        for phase, sel in (("rally", sc == 3), ("final", sc >= 4)):
            idx = np.nonzero(sel)[0]
            if len(idx):
                bt, _ = bonus(phase, len(idx))
                x[idx] += bt
        x = np.minimum(x, C.WINCAP_T) / 10
        s1 += x.sum(); s2 += (x * x).sum()
        hits += int((x > 0).sum()); big += int((x >= 100).sum())
        agg["served"] += int(sv.sum()); agg["returns"] += int(rt.sum()); agg["smashes"] += int(sm.sum()); agg["respins"] += int(rs.sum())
        agg["returns_hist"] += np.bincount(rt[sv], minlength=len(agg["returns_hist"]))
        agg["trig3"] += int((sc == 3).sum()); agg["trig4"] += int((sc >= 4).sum())
        done += m
    mean = s1 / n
    sd = (s2 / n - mean * mean) ** 0.5
    out["game"] = {"rtp": mean, "ci95": [mean - 1.96 * sd / n ** .5, mean + 1.96 * sd / n ** .5], "std_x": sd,
                   "hit_frequency": hits / n, "p_ge_100x": big / n, "base_spin_ways_x": base_feature_t / n / 10,
                   "serve_1_in": n / max(agg["served"], 1), "smash_per_serve": agg["smashes"] / max(agg["served"], 1),
                   "returns_given_serve": (agg["returns_hist"] / max(agg["served"], 1)).tolist(),
                   "respins_per_serve": agg["respins"] / max(agg["served"], 1),
                   "rally_1_in": n / max(agg["trig3"], 1), "final_1_in": n / max(agg["trig4"], 1)}
    return out
