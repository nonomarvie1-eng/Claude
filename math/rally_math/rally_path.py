"""RALLY PATH — experimental prototype (GOLDEN RALLY: CHAMPIONSHIP NIGHT).

Rules
-----
* GOLDEN BALL (id G) is a special symbol that only exists on reel 1 of the
  prototype strips.  It is neither a Wild nor a Scatter, pays nothing in the
  ways evaluation and substitutes for nothing.
* A Golden Ball on reel 1 serves.  The ball travels reel by reel: from row r
  on reel i it can be returned on reel i+1 at row r, r-1 or r+1 (same row or
  one row up/down) by a RACKET symbol (config RACKET).  Without an eligible
  racket the rally stops.
* Rally length = number of shots, the serve included (1..6).  Only the longest
  rally of the spin is paid (one Rally Path per spin).
* Deterministic choice of the path drawn on screen (the length, hence the
  reward, does not depend on it):
    - among several Golden Balls: the one giving the longest rally, ties ->
      the topmost;
    - at each step: the continuation giving the longest rally, ties -> same
      row, then the row above, then the row below.
* Reward by length (REWARD table).  A 6-shot rally (all six reels) is a
  CHAMPIONSHIP SHOT: its reward is drawn from CS_TABLE with one extra draw
  made by the engine.  The Rally Path win is added to the normal ways win.
* Bonus prototypes: RALLY CHALLENGE = 8 free spins; THE GRAND FINAL = 12 free
  spins + SECOND SERVE once: the first time a spin shows a Golden Ball whose
  rally stops before the third shot (length <= 2), one independent extra free
  spin is added.

Randomness: a spin draws its reel stops, then one CS roll (always drawn, used
only for a Championship Shot): the scalar engine, the vectorised engine and
the TypeScript port consume the same numbers.

Maths: the rally length only depends on which rows of each reel hold a
racket, reels are independent -> the exact length distribution is a
propagation of the "reachable rows" set (32 states) reel by reel.
"""

from __future__ import annotations

import numpy as np

import contextlib

from . import config as C
from .engine import evaluate_ways, window

P = C.RALLY_PATH_PROTO
G = len(C.SYMBOLS)            # prototype-only symbol id
NAMES = C.SYMBOLS + ["G"]
RACKET = C.SYM[P["RACKET"]]
ROWS = C.NUM_ROWS
NR = C.NUM_REELS
FULLMASK = (1 << ROWS) - 1


# ------------------------------------------------------------------ prototype strips

def with_golden_balls(strips: list[list[int]], n: int) -> list[list[int]]:
    """Reel 1 + n Golden Balls inserted at evenly spaced positions (deterministic)."""
    out = [list(s) for s in strips]
    r0 = out[0]
    L = len(r0)
    pos = sorted({int(round((i + 0.5) * L / n)) for i in range(n)}, reverse=True)
    for p in pos:
        r0.insert(p, G)
    return out


@contextlib.contextmanager
def proto_paytable():
    """Racket ways pay of the prototype (restored afterwards: the normal game is untouched)."""
    old = dict(C.PAYTABLE[P["RACKET"]])
    C.PAYTABLE[P["RACKET"]] = {int(k): v for k, v in P["RACKET_WAYS_PAY"].items()}
    try:
        yield
    finally:
        C.PAYTABLE[P["RACKET"]] = old


def proto_reels(kind: str) -> list[list[int]]:
    """Prototype strips: normal base reels + Golden Balls on reel 1; bonus reels
    rebuilt with FREE_RACKETS rackets, no scatter, + Golden Balls on reel 1."""
    if kind == "base":
        strips = C.base_reels().strips
    else:
        from .reels import FREE_COUNTS, STACK, build_reelset

        counts = {**FREE_COUNTS, "H4": [P["FREE_RACKETS"]] * NR, "S": [0] * NR}
        strips = [[C.SYM[x] for x in st] for st in build_reelset(counts, 6, STACK)]
    return with_golden_balls(strips, P["G_ON_REEL1"][kind])


# ------------------------------------------------------------------ rally evaluation (scalar, deterministic)

def rally(board) -> dict | None:
    """Longest Rally Path of a board[reel][row]; None if no Golden Ball on reel 1."""
    starts = [r for r in range(ROWS) if board[0][r] == G]
    if not starts:
        return None
    # best[i][r]: rally length counted from position (i, r), assuming (i, r) is played
    best = [[0] * ROWS for _ in range(NR)]
    nxt = [[None] * ROWS for _ in range(NR)]
    for r in range(ROWS):
        best[NR - 1][r] = 1
    for i in range(NR - 2, -1, -1):
        for r in range(ROWS):
            b, choice = 1, None
            for r2 in (r, r - 1, r + 1):  # tie priority: same row, up, down
                if 0 <= r2 < ROWS and board[i + 1][r2] == RACKET and 1 + best[i + 1][r2] > b:
                    b, choice = 1 + best[i + 1][r2], r2
            best[i][r] = b
            nxt[i][r] = choice
    s = max(starts, key=lambda r: (best[0][r], -r))
    path = [{"reel": 0, "row": s}]
    r, i = s, 0
    while nxt[i][r] is not None:
        r = nxt[i][r]
        i += 1
        path.append({"reel": i, "row": r})
    length = len(path)
    assert length == best[0][s]
    return {"length": length, "path": path, "serve": {"reel": 0, "row": s}}


def reward_t(length: int, cs_roll: int) -> tuple[int, bool]:
    if length >= P["MAX_SHOTS"]:
        return cs_pick(cs_roll), True
    return P["REWARD"][str(length)], False


def cs_pick(roll: int) -> int:
    acc = 0
    for prize, w in P["CS_TABLE"]:
        acc += w
        if roll < acc:
            return prize
    raise ValueError("roll outside CS table")


# ------------------------------------------------------------------ one spin / one round (events)

def _names(board):
    return [[NAMES[s] for s in col] for col in board]


def play_spin(draw, strips, emit, game_type="basegame") -> dict:
    stops = draw([len(s) for s in strips])
    cs_roll = draw([P["CS_ROLL"]])[0]
    board = window(strips, stops)
    emit({"type": "reveal", "gameType": game_type, "board": _names(board), "stops": list(stops), "anticipation": [0] * NR})
    with proto_paytable():
        wins = evaluate_ways(board)
    ways_t = sum(w.base_pay for w in wins)
    if ways_t:
        from .engine import _win_list

        emit({"type": "winInfo", "gameType": game_type, "multiplier": 1, "totalWin": ways_t * 10, "wins": _win_list(wins, board, 1)})
    rp = rally(board)
    rp_t, cs = 0, False
    if rp is not None:
        rp_t, cs = reward_t(rp["length"], cs_roll)
        emit({"type": "rallyPath", "length": rp["length"], "path": rp["path"], "reward": rp_t * 10, "championshipShot": cs})
    return {"ways_t": ways_t, "rp": rp, "rp_t": rp_t, "cs": cs, "spin_t": ways_t + rp_t}


def play_proto_round(draw, mode: str = "base") -> dict:
    """mode 'base' (one prototype spin), 'rally' or 'final' (prototype bonus)."""
    ev: list[dict] = []

    def emit(e):
        ev.append({"index": len(ev), **e})

    if mode == "base":
        from .engine import positions_of

        strips = proto_reels("base")
        s = play_spin(draw, strips, emit)
        board = window(strips, ev[0]["stops"])
        n_sc = len(positions_of(board, C.SCATTER))
        sc_pay = C.SCATTER_PAY.get(n_sc, 0)
        total = s["spin_t"] + sc_pay
        if sc_pay:
            emit({"type": "scatterPay", "count": n_sc, "amount": sc_pay * 10})
        stats = {"rp": s["rp"] is not None, "length": s["rp"]["length"] if s["rp"] else 0, "cs": s["cs"], "rp_t": s["rp_t"]}
    else:
        cfg = P["BONUS"][mode]
        strips = proto_reels("free")
        spins = cfg["spins"]
        total_spins = spins
        emit({"type": "protoBonusStart", "bonus": mode, "spins": spins})
        done = 0
        total = 0
        ss_used = False
        stats = {"cs": 0, "rp": 0, "second_serve": 0, "lengths": []}
        while done < total_spins:
            done += 1
            emit({"type": "spinStart", "spin": done, "total": total_spins})
            s = play_spin(draw, strips, emit, "freegame")
            total += s["spin_t"]
            if s["rp"] is not None:
                stats["rp"] += 1
                stats["lengths"].append(s["rp"]["length"])
                stats["cs"] += s["cs"]
                if cfg["second_serve"] and not ss_used and s["rp"]["length"] <= cfg["second_serve_max_len"]:
                    ss_used = True
                    total_spins += 1
                    stats["second_serve"] = 1
                    emit({"type": "secondServe", "added": 1, "total": total_spins})
            emit({"type": "setTotalWin", "amount": total * 10})
        emit({"type": "protoBonusEnd", "bonus": mode, "amount": total * 10, "spins": done})
    total = min(total, C.WINCAP_T)
    emit({"type": "finalWin", "amount": total * 10})
    return {"total_t": total, "events": ev, **stats}


# ------------------------------------------------------------------ exact maths

def _row_masks(strip, sym) -> np.ndarray:
    a = np.array(strip)
    rows = np.stack([np.roll(a, -k) for k in range(ROWS)], axis=1) == sym
    return (rows * (1 << np.arange(ROWS))).sum(1)


def spread(m: int) -> int:
    return (m | (m << 1) | (m >> 1)) & FULLMASK


def length_distribution(strips) -> dict:
    """Exact P(rally length = L) for L = 0 (no Golden Ball) .. 6."""
    L0 = [len(s) for s in strips]
    g = _row_masks(strips[0], G)
    rk = [_row_masks(strips[i], RACKET) for i in range(NR)]
    dist = np.zeros(1 << ROWS)
    for m in g:
        dist[m] += 1 / L0[0]
    out = {0: float(dist[0])}
    dist[0] = 0.0
    cur = dist
    for i in range(1, NR):
        pm = np.bincount(rk[i], minlength=1 << ROWS) / L0[i]
        nd = np.zeros(1 << ROWS)
        stop = 0.0
        for s in range(1, 1 << ROWS):
            if cur[s] == 0:
                continue
            reach = spread(s)
            for m in range(1 << ROWS):
                if pm[m] == 0:
                    continue
                t = reach & m
                if t:
                    nd[t] += cur[s] * pm[m]
                else:
                    stop += cur[s] * pm[m]
        out[i] = stop
        cur = nd
    out[NR] = float(cur.sum())
    return {int(k): float(v) for k, v in out.items()}


def cs_mean_t() -> float:
    tot = sum(w for _, w in P["CS_TABLE"])
    return sum(p * w for p, w in P["CS_TABLE"]) / tot


def rp_expectation_t(dist: dict) -> float:
    e = sum(dist[L] * P["REWARD"][str(L)] for L in range(1, NR))
    return e + dist[NR] * cs_mean_t()


def exact_report() -> dict:
    """Exact statistics of the prototype (no simulation): rally length laws,
    Championship Shot frequency, spin values, both bonus prototypes and the
    resulting RTP of a prototype game (prototype base spin + prototype bonuses)."""
    from .exact import joint_stats

    rep = {"experimental": True, "rules": P}
    e_kind = {}
    for kind in ("base", "free"):
        strips = proto_reels(kind)
        d = length_distribution(strips)
        with proto_paytable():
            Pm, E1 = joint_stats(strips, n_sym=len(NAMES))
        ways = float(E1.sum())
        rp = rp_expectation_t(d)
        p_g = 1 - d[0]
        p_sc = Pm.sum(axis=0)
        rep[kind] = {
            "strip_lengths": [len(s) for s in strips],
            "p_golden_ball": p_g,
            "length_dist": d,
            "length_dist_given_ball": {L: d[L] / p_g for L in range(1, NR + 1)},
            "p_return": 1 - d[1] / p_g,
            "p_full_rally": d[NR],
            "championship_shot_1_in_spins": 1 / d[NR] if d[NR] else None,
            "E_ways_x": ways / 10,
            "E_rally_path_x": rp / 10,
            "E_spin_x": (ways + rp) / 10,
            "p_scatter": {str(c): float(p_sc[c]) for c in range(len(p_sc))},
        }
        e_kind[kind] = (ways + rp) / 10
    rep["cs_mean_x"] = cs_mean_t() / 10
    f = rep["free"]
    e_spin = f["E_spin_x"]
    q = sum(f["length_dist"][L] for L in range(1, P["BONUS"]["final"]["second_serve_max_len"] + 1))
    for mode, cfg in P["BONUS"].items():
        n = cfg["spins"]
        p_ss = 1 - (1 - q) ** n if cfg["second_serve"] else 0.0
        rep[f"bonus_{mode}"] = {"spins": n, "p_second_serve": p_ss, "E_spins": n + p_ss, "E_x": (n + p_ss) * e_spin,
                                "p_at_least_one_cs": 1 - (1 - f["length_dist"][NR]) ** (n + p_ss)}
    # prototype game RTP: base spin (ways + Rally Path + scatter pays) + bonuses
    b = rep["base"]
    psc = {int(k): v for k, v in b["p_scatter"].items()}
    sc_pay = sum(psc.get(k, 0) * C.SCATTER_PAY.get(k, 0) for k in range(7)) / 10
    p3 = psc.get(3, 0)
    p4 = sum(psc.get(k, 0) for k in (4, 5, 6))
    rep["prototype_rtp"] = {
        "base_ways": b["E_ways_x"], "base_rally_path": b["E_rally_path_x"], "scatter_pays": sc_pay,
        "rally_challenge": p3 * rep["bonus_rally"]["E_x"], "grand_final": p4 * rep["bonus_final"]["E_x"],
        "p_rally_challenge": p3, "p_grand_final": p4,
    }
    rep["prototype_rtp"]["total"] = sum(v for k, v in rep["prototype_rtp"].items() if not k.startswith("p_"))
    base = C.base_reels()
    _, E1 = joint_stats(base.strips)
    rep["normal_game_ways_x"] = float(E1.sum()) / 10
    return rep


# ------------------------------------------------------------------ vectorised simulation (validation)

def simulate(kind: str, n: int, seed: int) -> dict:
    """Monte-Carlo of prototype spins (lengths, rewards) with a reproducible seed."""
    strips = proto_reels(kind)
    rng = np.random.Generator(np.random.PCG64(seed))
    g = _row_masks(strips[0], G)
    rk = [_row_masks(strips[i], RACKET) for i in range(NR)]
    lengths = np.zeros(n, dtype=np.int64)
    done = 0
    while done < n:
        m = min(500_000, n - done)
        st = [rng.integers(0, len(s), m) for s in strips]
        cs = rng.integers(0, P["CS_ROLL"], m)
        cur = g[st[0]]
        L = (cur > 0).astype(np.int64)
        for i in range(1, NR):
            sp = (cur | (cur << 1) | (cur >> 1)) & FULLMASK
            cur = sp & rk[i][st[i]]
            L += cur > 0
        lengths[done:done + m] = L
        done += m
    return {"n": n, "seed": seed, "length_freq": {int(k): float((lengths == k).mean()) for k in range(NR + 1)}}


def _spin_vec(rng, strips, cnt, g, rk, m):
    """m prototype spins: (ways_t, rally length, rally reward_t, cs flag, stops)."""
    from .engine import ways_win_vec

    st = np.stack([rng.integers(0, len(s), m) for s in strips], axis=1)
    cs_roll = rng.integers(0, P["CS_ROLL"], m)
    with proto_paytable():
        lw, _w, sc = ways_win_vec(cnt, st)
    cur = g[st[:, 0]]
    L = (cur > 0).astype(np.int64)
    for i in range(1, NR):
        cur = ((cur | (cur << 1) | (cur >> 1)) & FULLMASK) & rk[i][st[:, i]]
        L += cur > 0
    rew = np.zeros(m, dtype=np.int64)
    for k in range(2, NR):
        rew[L == k] = P["REWARD"][str(k)]
    cum = np.cumsum([w for _, w in P["CS_TABLE"]])
    vals = np.array([p for p, _ in P["CS_TABLE"]])
    full = L == NR
    rew[full] = vals[(cs_roll[full][:, None] >= cum[None, :]).sum(1)]
    return lw, L, rew, full, sc


def simulate_game(n: int, seed: int, n_bonus: int = 200_000) -> dict:
    """Reproducible Monte-Carlo of the prototype game and of both prototype bonuses."""
    from .engine import count_tables

    rng = np.random.Generator(np.random.PCG64(seed))
    out = {"seed": seed}
    fs = proto_reels("free")
    fcnt = count_tables(fs, len(NAMES))
    fg, frk = _row_masks(fs[0], G), [_row_masks(fs[i], RACKET) for i in range(NR)]

    def bonuses(mode, k):
        cfg = P["BONUS"][mode]
        tot = np.zeros(k, dtype=np.int64)
        remaining = np.full(k, cfg["spins"], dtype=np.int64)
        ss = np.zeros(k, dtype=bool)
        ncs = np.zeros(k, dtype=np.int64)
        act = remaining > 0
        while act.any():
            a = np.nonzero(act)[0]
            remaining[a] -= 1
            lw, L, rew, full, _ = _spin_vec(rng, fs, fcnt, fg, frk, len(a))
            tot[a] += lw + rew
            ncs[a] += full
            if cfg["second_serve"]:
                trig = (L >= 1) & (L <= cfg["second_serve_max_len"]) & ~ss[a]
                ss[a[trig]] = True
                remaining[a[trig]] += 1
            act = remaining > 0
        return np.minimum(tot, C.WINCAP_T), ss, ncs

    for mode in ("rally", "final"):
        t, ss, ncs = bonuses(mode, n_bonus)
        x = t / 10
        out[f"bonus_{mode}"] = {
            "n": n_bonus, "mean_x": float(x.mean()), "ci95": [float(x.mean() - 1.96 * x.std() / n_bonus ** .5), float(x.mean() + 1.96 * x.std() / n_bonus ** .5)],
            "std_dev_x": float(x.std()), "median_x": float(np.median(x)), "p_below_10x": float((x < 10).mean()),
            "p_ge_100x": float((x >= 100).mean()), "p_ge_500x": float((x >= 500).mean()), "p_ge_1000x": float((x >= 1000).mean()),
            "max_x": float(x.max()), "p_second_serve": float(ss.mean()), "p_cs": float((ncs > 0).mean()),
            "quantiles_x": {q: float(np.quantile(x, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999)},
        }
    # full prototype game (base spins + triggered bonuses)
    bs = proto_reels("base")
    bcnt = count_tables(bs, len(NAMES))
    bg, brk = _row_masks(bs[0], G), [_row_masks(bs[i], RACKET) for i in range(NR)]
    scp = np.zeros(NR + 1, dtype=np.int64)
    for k2, v in C.SCATTER_PAY.items():
        scp[k2] = v
    s1 = s2 = 0.0
    hits = big = 0
    done = 0
    while done < n:
        m = min(500_000, n - done)
        lw, L, rew, full, sc = _spin_vec(rng, bs, bcnt, bg, brk, m)
        t = lw + rew + scp[sc]
        for mode, sel in (("rally", sc == 3), ("final", sc >= 4)):
            idx = np.nonzero(sel)[0]
            if len(idx):
                bt, _, _ = bonuses(mode, len(idx))
                t[idx] += bt
        t = np.minimum(t, C.WINCAP_T)
        x = t / 10
        s1 += x.sum()
        s2 += (x * x).sum()
        hits += int((x > 0).sum())
        big += int((x >= 100).sum())
        done += m
    mean = s1 / n
    sd = (s2 / n - mean ** 2) ** 0.5
    out["game"] = {"n": n, "rtp": mean, "ci95": [mean - 1.96 * sd / n ** .5, mean + 1.96 * sd / n ** .5], "std_dev_x": sd,
                   "hit_frequency": hits / n, "p_ge_100x": big / n}
    return out


# ------------------------------------------------------------------ full game round (test build RALLY-PATH-01)

def play_game_round(draw) -> dict:
    """One complete paid round of the Rally Path game: prototype base spin
    (ways + Rally Path + scatter pays); 3 scatters -> RALLY CHALLENGE,
    4+ -> THE GRAND FINAL, played inside the same round (same draw stream).
    Same law as simulate_game()."""
    from .engine import positions_of

    ev: list[dict] = []

    def emit(e):
        ev.append({"index": len(ev), **e})

    strips = proto_reels("base")
    s = play_spin(draw, strips, emit)
    board = window(strips, ev[0]["stops"])
    pos = positions_of(board, C.SCATTER)
    n_sc = len(pos)
    sc_pay = C.SCATTER_PAY.get(n_sc, 0)
    if sc_pay:
        emit({"type": "scatterPay", "count": n_sc, "amount": sc_pay * 10})
    total = s["spin_t"] + sc_pay
    emit({"type": "setWin", "amount": min(total, C.WINCAP_T) * 10})
    bonus = None
    if n_sc >= 3:
        bonus = "rally" if n_sc == 3 else "final"
        cfg = P["BONUS"][bonus]
        free = proto_reels("free")
        total_spins = cfg["spins"]
        emit({"type": "protoBonusStart", "bonus": bonus, "spins": total_spins, "positions": pos})
        done, bt, ss_used = 0, 0, False
        while done < total_spins:
            done += 1
            emit({"type": "spinStart", "spin": done, "total": total_spins})
            f = play_spin(draw, free, emit, "freegame")
            bt += f["spin_t"]
            if f["rp"] is not None and cfg["second_serve"] and not ss_used and f["rp"]["length"] <= cfg["second_serve_max_len"]:
                ss_used = True
                total_spins += 1
                emit({"type": "secondServe", "added": 1, "total": total_spins})
            emit({"type": "setTotalWin", "amount": min(total + bt, C.WINCAP_T) * 10})
        total += bt
        emit({"type": "protoBonusEnd", "bonus": bonus, "amount": min(total, C.WINCAP_T) * 10, "spins": done})
    total = min(total, C.WINCAP_T)
    emit({"type": "finalWin", "amount": total * 10})
    return {"total_t": total, "events": ev, "bonus": bonus, "length": s["rp"]["length"] if s["rp"] else 0, "cs": s["cs"]}
