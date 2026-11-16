"""GOLDEN SERVE — two experimental bonus mechanics on the 6x5 ways grid.

Common trigger
--------------
* GOLDEN BALL (G) only lands on reel 1.  It is neither a Wild nor a Scatter,
  pays nothing and substitutes for nothing.  If several land, the topmost serves.
* Each spin always draws, after its 6 reel stops, one "serve" vector
  [target_row(5), symbol_roll(1000), special_roll(1000), target_row2(5)]
  (drawn even when no Golden Ball lands, so every spin consumes the same
  number of draws: exact replay, Python == TypeScript).
* Shot type from special_roll (per game phase): SMASH if roll < P_SMASH,
  DOUBLE SERVE if roll < P_SMASH + P_DOUBLE, otherwise SERVE.
* Trajectory: from (reel 0, row r0) to (reel 5, target_row): the row on reel i
  is floor(r0 + (target - r0) * i / 5 + 0.5)  (a straight cross-court line).
  SMASH also hits the neighbouring row on reels 1..5 (row+1, or row-1 on the
  bottom row): a 2-row band.  DOUBLE SERVE adds a second trajectory to
  target_row2 from the same server.

CONCEPT A — CROSS-COURT (transformation)
  Every cell hit on reels 1..5 and the Golden Ball itself become the drawn
  TARGET symbol (TARGET weights per phase).  Wilds and Scatters that are hit
  stay as they are.  Ways are evaluated on the transformed grid.

CONCEPT B — COURT SWITCH (exchange)
  The ball's bounces exchange symbols across the net: path cell on reel 1 <->
  path cell on reel 4, reel 2 <-> reel 5 (each trajectory row); the Golden
  Ball cell takes the symbol of the reel-3 cell it returns (the net cell).
  Nothing is created: symbols only change place.  Ways evaluated afterwards.

Bonuses (same for both concepts): 3 scatters -> RALLY CHALLENGE (8 spins on
the bonus reels, phase 'rally'); 4+ -> THE GRAND FINAL (12 spins, phase
'final': higher Smash / Double Serve chances, more premium targets).  Scatter
pays on the triggering spin only; no retrigger.  Win cap WINCAP_X.

The engine fixes everything (board, shot, path, hits, transformed board, wins)
before any presentation.
"""

from __future__ import annotations

import numpy as np

from . import config as C
from .engine import evaluate_ways, positions_of, window, _win_list

P = C.GOLDEN_SERVE_PROTO
G = len(C.SYMBOLS)
NAMES = C.SYMBOLS + ["G"]
ROWS, NR = C.NUM_ROWS, C.NUM_REELS
W, S = C.WILD, C.SCATTER
PAYING = [C.SYM[s] for s in C.SYMBOLS if s not in ("W", "S")]
TARGET_SYMS = list(P["TARGET_SYMS"])
SERVE_DRAW = [ROWS, 1000, 1000, ROWS]


def with_golden_balls(strips, n):
    out = [list(s) for s in strips]
    L = len(out[0])
    for p in sorted({int(round((i + 0.5) * L / n)) for i in range(n)}, reverse=True):
        out[0].insert(p, G)
    return out


def reels(kind: str):
    if kind == "base":
        from .reels import STACK, build_reelset

        base = [[C.SYM[x] for x in st] for st in build_reelset(P["BASE_COUNTS"], P["BASE_SEED"], STACK)]
    else:
        base = C.free_reels().strips
    return with_golden_balls(base, P["G_ON_REEL1"][kind])


_REELS: dict = {}


def strips_of(kind):
    if kind not in _REELS:
        _REELS[kind] = reels(kind)
    return _REELS[kind]


def target_of(phase: str, roll: int) -> int:
    acc = 0
    for s, w in zip(TARGET_SYMS, P["TARGET_W"][phase]):
        acc += w
        if roll < acc:
            return C.SYM[s]
    raise ValueError("target roll outside table")


def shot_of(phase: str, roll: int) -> str:
    ps, pd = P["P_SMASH"][phase], P["P_DOUBLE"][phase]
    return "smash" if roll < ps else "double" if roll < ps + pd else "serve"


def path_rows(r0: int, rt: int) -> list[int]:
    return [int(np.floor(r0 + (rt - r0) * i / 5 + 0.5)) for i in range(NR)]


def trajectories(r0, shot, rt, rt2):
    """list of trajectories; each = list of (reel,row) cells on reels 0..5."""
    t1 = [(i, r) for i, r in enumerate(path_rows(r0, rt))]
    out = [t1]
    if shot == "smash":
        out.append([(0, r0)] + [(i, r + 1 if r < ROWS - 1 else r - 1) for i, r in t1[1:]])
    elif shot == "double":
        out.append([(i, r) for i, r in enumerate(path_rows(r0, rt2))])
    return out


def apply_shot(board, concept, phase, serve):
    """board: list of reel columns (ints).  Returns (new_board, shot_event or None)."""
    starts = [r for r in range(ROWS) if board[0][r] == G]
    if not starts:
        return board, None
    rt, sym_roll, sp_roll, rt2 = serve
    r0 = starts[0]
    shot = shot_of(phase, sp_roll)
    trajs = trajectories(r0, shot, rt, rt2)
    b = [list(c) for c in board]
    changes = []  # {reel,row,from,to}
    if concept == "A":
        T = target_of(phase, sym_roll)
        cells = sorted({c for t in trajs for c in t})
        for (i, r) in cells:
            fr = b[i][r]
            if fr in (W, S) or fr == T:
                continue
            b[i][r] = T
            changes.append({"reel": i, "row": r, "from": NAMES[fr], "to": NAMES[T]})
        ev = {"concept": "A", "shot": shot, "origin": {"reel": 0, "row": r0}, "target": NAMES[T],
              "paths": [[{"reel": i, "row": r} for i, r in t] for t in trajs], "changes": changes}
    else:
        swaps = []
        for t in trajs:
            row = dict(t)
            for a, c in ((1, 4), (2, 5)):
                ra, rc = row[a], row[c]
                sa, sc = b[a][ra], b[c][rc]
                b[a][ra], b[c][rc] = sc, sa
                swaps.append({"a": {"reel": a, "row": ra, "sym": NAMES[sa]}, "b": {"reel": c, "row": rc, "sym": NAMES[sc]}})
        net = b[3][dict(trajs[0])[3]]
        b[0][r0] = net
        changes = [{"reel": 0, "row": r0, "from": "G", "to": NAMES[net]}]
        ev = {"concept": "B", "shot": shot, "origin": {"reel": 0, "row": r0},
              "paths": [[{"reel": i, "row": r} for i, r in t] for t in trajs], "swaps": swaps, "changes": changes}
    return b, ev


def _names(board):
    return [[NAMES[s] for s in col] for col in board]


def play_spin(draw, concept, phase, emit, game_type):
    kind = "base" if phase == "base" else "free"
    strips = strips_of(kind)
    stops = draw([len(s) for s in strips])
    serve = draw(SERVE_DRAW)
    board = window(strips, stops)
    emit({"type": "reveal", "gameType": game_type, "board": _names(board), "stops": list(stops), "anticipation": [0] * NR})
    nb, shot = apply_shot(board, concept, phase, serve)
    if shot:
        emit({"type": "goldenServe", **shot, "board": _names(nb)})
    wins = evaluate_ways(nb)
    t = sum(w.base_pay for w in wins)
    if t:
        emit({"type": "winInfo", "gameType": game_type, "multiplier": 1, "totalWin": t * 10, "wins": _win_list(wins, nb, 1)})
    return {"t": t, "board": nb, "orig": board, "shot": shot}


def play_round(draw, concept: str = "A") -> dict:
    """One complete paid round (base spin + triggered bonus), stateless."""
    ev: list[dict] = []

    def emit(e):
        ev.append({"index": len(ev), **e})

    s = play_spin(draw, concept, "base", emit, "basegame")
    pos = positions_of(s["orig"], S)
    n_sc = len(pos)
    sc_pay = C.SCATTER_PAY.get(n_sc, 0)
    if sc_pay:
        emit({"type": "scatterPay", "count": n_sc, "amount": sc_pay * 10, "positions": pos})
    total = s["t"] + sc_pay
    emit({"type": "setWin", "amount": min(total, C.WINCAP_T) * 10})
    bonus = None
    shots = [s["shot"]["shot"]] if s["shot"] else []
    if n_sc >= 3:
        bonus = "rally" if n_sc == 3 else "final"
        n = P["BONUS"][bonus]["spins"]
        emit({"type": "gsBonusStart", "bonus": bonus, "spins": n, "positions": pos})
        bt = 0
        for k in range(1, n + 1):
            emit({"type": "spinStart", "spin": k, "total": n})
            f = play_spin(draw, concept, bonus, emit, "freegame")
            bt += f["t"]
            if f["shot"]:
                shots.append(f["shot"]["shot"])
            emit({"type": "setTotalWin", "amount": min(total + bt, C.WINCAP_T) * 10})
        total += bt
        emit({"type": "gsBonusEnd", "bonus": bonus, "amount": min(total, C.WINCAP_T) * 10, "bonusWin": min(bt, C.WINCAP_T) * 10})
    total = min(total, C.WINCAP_T)
    emit({"type": "finalWin", "amount": total * 10})
    return {"total_t": total, "events": ev, "bonus": bonus, "shots": shots}


# ------------------------------------------------------------------ vectorised simulation (same law)

def _table(phase):
    w = np.array(P["TARGET_W"][phase])
    return np.cumsum(w), np.array([C.SYM[s] for s in TARGET_SYMS])


def _ways_t(b):
    """b: (m, NR, ROWS) int boards -> ways win in t-units (m,)"""
    m = b.shape[0]
    tot = np.zeros(m, dtype=np.int64)
    isw = b == W
    for s in PAYING:
        cnt = ((b == s) | isw).sum(axis=2)  # (m, NR)
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


def _spins(rng, concept, phase, m):
    kind = "base" if phase == "base" else "free"
    strips = strips_of(kind)
    arr = [np.array(s) for s in strips]
    stops = np.stack([rng.integers(0, len(s), m) for s in strips], 1)
    sv = np.stack([rng.integers(0, n, m) for n in SERVE_DRAW], 1)
    idx = (stops[:, :, None] + np.arange(ROWS)[None, None, :])
    b = np.stack([arr[i][idx[:, i, :] % len(arr[i])] for i in range(NR)], 1)  # (m,NR,ROWS)
    orig_sc = (b == S).sum(axis=(1, 2))
    isg = b[:, 0, :] == G
    hasg = isg.any(1)
    r0 = np.argmax(isg, axis=1)
    ps, pd = P["P_SMASH"][phase], P["P_DOUBLE"][phase]
    shot = np.where(sv[:, 2] < ps, 2, np.where(sv[:, 2] < ps + pd, 1, 0))  # 0 serve 1 double 2 smash
    i5 = np.arange(NR)
    rows1 = np.floor(r0[:, None] + (sv[:, 0:1] - r0[:, None]) * i5[None, :] / 5 + 0.5).astype(int)
    rows2 = np.floor(r0[:, None] + (sv[:, 3:4] - r0[:, None]) * i5[None, :] / 5 + 0.5).astype(int)
    band = np.where(rows1 < ROWS - 1, rows1 + 1, rows1 - 1)
    band[:, 0] = r0
    rowsB = np.where((shot == 2)[:, None], band, np.where((shot == 1)[:, None], rows2, -1))
    g = np.nonzero(hasg)[0]
    nb = b.copy()
    if concept == "A":
        cum, syms = _table(phase)
        T = syms[(sv[:, 1][:, None] >= cum[None, :]).sum(1)]
        for rows in (rows1, rowsB):
            for i in range(NR):
                rr = rows[g, i]
                ok = rr >= 0
                gi, ri = g[ok], rr[ok]
                cur = nb[gi, i, ri]
                keep = (cur == W) | (cur == S)
                nb[gi[~keep], i, ri[~keep]] = T[gi[~keep]]
    else:
        for rows in (rows1, rowsB):
            ok = rows[g, 0] >= 0
            gi = g[ok]
            for a, c in ((1, 4), (2, 5)):
                ra, rc = rows[gi, a], rows[gi, c]
                sa, sc = nb[gi, a, ra].copy(), nb[gi, c, rc].copy()
                nb[gi, a, ra], nb[gi, c, rc] = sc, sa
        nb[g, 0, r0[g]] = nb[g, 3, rows1[g, 3]]
    t = _ways_t(nb)
    return t, orig_sc, hasg, shot


def simulate(concept: str, n: int, seed: int, n_bonus: int = 200_000) -> dict:
    rng = np.random.Generator(np.random.PCG64(seed))
    out = {"concept": concept, "seed": seed, "n": n, "n_bonus": n_bonus}

    def bonus(phase, k):
        nsp = P["BONUS"][phase]["spins"]
        tot = np.zeros(k, dtype=np.int64)
        nsh = np.zeros(k, dtype=np.int64)
        nsm = np.zeros(k, dtype=np.int64)
        for _ in range(nsp):
            t, _, hg, sh = _spins(rng, concept, phase, k)
            tot += t
            nsh += hg
            nsm += hg & (sh == 2)
        return tot, nsh, nsm

    for phase in ("rally", "final"):
        t, nsh, nsm = bonus(phase, n_bonus)
        x = np.minimum(t, C.WINCAP_T) / 10
        se = x.std() / n_bonus ** .5
        out[f"bonus_{phase}"] = {
            "mean_x": float(x.mean()), "ci95": [float(x.mean() - 1.96 * se), float(x.mean() + 1.96 * se)],
            "std_x": float(x.std()), "median_x": float(np.median(x)), "p_lt_10x": float((x < 10).mean()),
            "p_ge_100x": float((x >= 100).mean()), "p_ge_1000x": float((x >= 1000).mean()), "max_x": float(x.max()),
            "serves_per_bonus": float(nsh.mean()), "p_smash": float((nsm > 0).mean()),
            "quantiles_x": {str(q): float(np.quantile(x, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99)},
        }
    scp = np.zeros(NR * ROWS + 1, dtype=np.int64)
    for k, v in C.SCATTER_PAY.items():
        scp[k] = v
    s1 = s2 = 0.0
    hits = big = ng = 0
    feat = 0.0
    done = 0
    while done < n:
        m = min(400_000, n - done)
        t, sc, hg, _ = _spins(rng, concept, "base", m)
        x = t + scp[sc]
        for phase, sel in (("rally", sc == 3), ("final", sc >= 4)):
            idx = np.nonzero(sel)[0]
            if len(idx):
                bt, _, _ = bonus(phase, len(idx))
                x[idx] += bt
        x = np.minimum(x, C.WINCAP_T) / 10
        s1 += x.sum()
        s2 += (x * x).sum()
        hits += int((x > 0).sum())
        big += int((x >= 100).sum())
        ng += int(hg.sum())
        done += m
    mean = s1 / n
    sd = (s2 / n - mean * mean) ** .5
    out["game"] = {"rtp": mean, "ci95": [mean - 1.96 * sd / n ** .5, mean + 1.96 * sd / n ** .5], "std_x": sd,
                   "hit_frequency": hits / n, "p_ge_100x": big / n, "golden_ball_1_in": n / max(ng, 1)}
    return out


def component_report(concept: str, n: int, seed: int) -> dict:
    """Base-spin decomposition: ways without feature vs with feature (same draws)."""
    rng = np.random.Generator(np.random.PCG64(seed))
    t, sc, hg, sh = _spins(rng, concept, "base", n)
    return {"E_spin_x": float(t.mean() / 10), "p_golden_ball": float(hg.mean()),
            "E_spin_given_ball_x": float(t[hg].mean() / 10), "E_spin_no_ball_x": float(t[~hg].mean() / 10)}
