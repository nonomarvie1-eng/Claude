"""Reference game engine (Python) — 6x5 "ways" version.

Authoritative implementation of the rules, used by the simulator, the Stake
Engine book exporter and the parity fixtures for the TypeScript demo engine.
An outcome is a pure function of the reel stops drawn for that round.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import config as C

R, ROWS = C.NUM_REELS, C.NUM_ROWS
PAY_IDX = [C.SYM[s] for s in C.PAYING]


def window(strips: list[list[int]], stops: list[int]) -> list[list[int]]:
    """board[reel][row], row 0 = top; stop = index of the top row."""
    return [[strip[(stops[r] + k) % len(strip)] for k in range(ROWS)] for r, strip in enumerate(strips)]


def padding(strips, stops):
    above = [strip[(stops[r] - 1) % len(strip)] for r, strip in enumerate(strips)]
    below = [strip[(stops[r] + ROWS) % len(strip)] for r, strip in enumerate(strips)]
    return above, below


@dataclass
class WaysWin:
    symbol: int
    reels: int
    ways: int
    pay_per_way: int  # t-units

    @property
    def base_pay(self) -> int:
        return self.pay_per_way * self.ways


def evaluate_ways(board: list[list[int]]) -> list[WaysWin]:
    wins = []
    for s in PAY_IDX:
        ways = 1
        k = 0
        for r in range(R):
            n = sum(1 for x in board[r] if x == s or x == C.WILD)
            if n == 0:
                break
            ways *= n
            k += 1
        if k >= C.MIN_KIND:
            p = C.PAYTABLE[C.SYMBOLS[s]][k]
            wins.append(WaysWin(s, k, ways, p))
    return wins


def positions_of(board, symbol: int) -> list[dict]:
    return [{"reel": r, "row": row} for r in range(R) for row in range(ROWS) if board[r][row] == symbol]


def anticipation(board) -> list[int]:
    out, seen = [], 0
    for r in range(R):
        out.append(1 if seen >= 2 else 0)
        seen += sum(1 for s in board[r] if s == C.SCATTER)
    return out


# ------------------------------------------------------------------ vectorised helpers (simulation)

def count_tables(strips: list[list[int]]) -> list[np.ndarray]:
    """cnt[r][stop, symbol] = occurrences of symbol in the window at that stop."""
    out = []
    n_sym = len(C.SYMBOLS)
    for strip in strips:
        a = np.array(strip)
        L = len(a)
        t = np.zeros((L, n_sym), dtype=np.int64)
        for k in range(ROWS):
            np.add.at(t, (np.arange(L), np.roll(a, -k)), 1)
        out.append(t)
    return out


def ways_win_vec(cnt: list[np.ndarray], stops: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorised over N boards: (line/ways win t-units at mult 1, wild count, scatter count)."""
    N = stops.shape[0]
    per_reel = [cnt[r][stops[:, r]] for r in range(R)]  # each (N, nsym)
    total = np.zeros(N, dtype=np.int64)
    for s in PAY_IDX:
        ways = np.ones(N, dtype=np.int64)
        alive = np.ones(N, dtype=bool)
        k = np.zeros(N, dtype=np.int64)
        for r in range(R):
            n = per_reel[r][:, s] + per_reel[r][:, C.WILD]
            alive &= n > 0
            ways = np.where(alive, ways * n, ways)
            k += alive
        pay = np.zeros(N, dtype=np.int64)
        for kk in range(C.MIN_KIND, R + 1):
            pay = np.where(k == kk, C.PAYTABLE[C.SYMBOLS[s]][kk], pay)
        total += pay * ways
    wilds = sum(per_reel[r][:, C.WILD] for r in range(R))
    scat = sum(per_reel[r][:, C.SCATTER] for r in range(R))
    return total, wilds, scat


# ------------------------------------------------------------------ round generation

StopDrawer = Callable[[list[int]], list[int]]


def numpy_drawer(rng: np.random.Generator) -> StopDrawer:
    def draw(lengths):
        return [int(rng.integers(0, n)) for n in lengths]

    return draw


def list_drawer(stops_seq):
    it = iter(stops_seq)

    def draw(lengths):
        return list(next(it))

    return draw


def _names(board):
    return [[C.SYMBOLS[s] for s in reel] for reel in board]


@dataclass
class RoundResult:
    total_t: int
    base_t: int
    free_t: int
    triggered: bool
    level: str | None
    fs_spins: int
    retriggers: int
    final_multiplier: int
    capped: bool
    events: list[dict] | None
    stops: list[list[int]]
    bonus_stats: dict | None = None


def _win_list(wins: list[WaysWin], board, mult: int) -> list[dict]:
    out = []
    for w in wins:
        pos = [{"reel": r, "row": row} for r in range(w.reels) for row in range(ROWS) if board[r][row] in (w.symbol, C.WILD)]
        out.append({
            "kind": "ways",
            "symbol": C.SYMBOLS[w.symbol],
            "count": w.reels,
            "ways": w.ways,
            "basePay": w.pay_per_way * 10,
            "multiplier": mult,
            "win": w.base_pay * mult * 10,
            "positions": pos,
        })
    return out


def _scatter_win(sc_pos, sc_pay):
    if sc_pay <= 0:
        return []
    return [{"kind": "scatter", "symbol": "S", "count": len(sc_pos), "ways": 1, "basePay": sc_pay * 10,
             "multiplier": 1, "win": sc_pay * 10, "positions": sc_pos}]


def play_round(draw: StopDrawer, base: C.ReelSet, free: C.ReelSet, record_events: bool = True,
               forced_base_stops: list[int] | None = None, mode: str = "base") -> RoundResult:
    """One complete round (base spin + whole bonus), stateless.

    mode "base" / "bonus_chance": `base` is the reel set of that mode.
    mode "buy_tiebreak" / "buy_super": forced_base_stops must show exactly
    BUY_SCATTERS[mode] scatters (3 -> Tie-Break, 4 -> Super Tie-Break); the
    bonus then follows the normal rules."""
    ev: list[dict] | None = [] if record_events else None
    all_stops = []
    if draw is not None:
        inner = draw

        def draw(lengths):  # noqa: F811 - records every draw for exact replay
            v = inner(lengths)
            all_stops.append(list(v))
            return v

    def emit(e):
        if ev is not None:
            ev.append({"index": len(ev), **e})

    if forced_base_stops is not None:
        stops = forced_base_stops
        all_stops.append(list(stops))
    else:
        stops = draw(base.lengths)
    board = window(base.strips, stops)
    if ev is not None:
        a, b = padding(base.strips, stops)
        emit({"type": "reveal", "gameType": "basegame", "board": _names(board), "stops": list(stops),
              "paddingAbove": [C.SYMBOLS[s] for s in a], "paddingBelow": [C.SYMBOLS[s] for s in b],
              "anticipation": anticipation(board)})
    wins = evaluate_ways(board)
    sc_pos = positions_of(board, C.SCATTER)
    n_sc = len(sc_pos)
    sc_pay = C.SCATTER_PAY.get(n_sc, 0)
    base_t = sum(w.base_pay for w in wins) + sc_pay
    if ev is not None and base_t > 0:
        emit({"type": "winInfo", "gameType": "basegame", "multiplier": 1, "totalWin": base_t * 10,
              "wins": _win_list(wins, board, 1) + _scatter_win(sc_pos, sc_pay)})
        emit({"type": "setWin", "amount": min(base_t, C.WINCAP_T) * 10, "winLevel": C.win_level(base_t / 10)})

    capped = base_t >= C.WINCAP_T
    total = min(base_t, C.WINCAP_T)
    triggered = n_sc >= 3 and not capped
    bought = mode in C.BUY_SCATTERS
    if bought:
        assert n_sc == C.BUY_SCATTERS[mode], "bought round must show exactly the bought scatter count"
    level = C.bonus_level(n_sc) if triggered else None
    free_t = 0
    bstats: dict = {}
    if triggered:
        from .bonus import play_bonus

        exchanges = C.FS_AWARD[n_sc]
        emit({"type": "bonusStart", "bonus": level, "exchanges": exchanges, "positions": sc_pos,
              **({"bought": True} if bought else {})})
        bstats = play_bonus(draw, free, level, exchanges, base_t, emit, window, _names, padding)
        free_t = bstats["win_t"]
        capped = capped or bstats["capped"]
        total = min(base_t + free_t, C.WINCAP_T)
        bx = free_t / 10
        ceremony = "grand" if bx >= C.CEREMONY_X["grand"] else "trophy" if bx >= C.CEREMONY_X["trophy"] else "none"
        emit({"type": "bonusEnd", "bonus": level, "amount": total * 10, "bonusWin": free_t * 10,
              "exchanges": bstats["exchanges"], "points": bstats["points"], "ceremony": ceremony,
              "winLevel": C.win_level(total / 10)})
    emit({"type": "finalWin", "amount": total * 10})
    return RoundResult(total, base_t, free_t, triggered, level, bstats.get("exchanges", 0), bstats.get("extensions", 0), 0, capped, ev, all_stops, bstats)


def make_book(book_id: int, res: RoundResult) -> dict:
    assert res.events is not None
    return {"id": book_id, "payoutMultiplier": res.total_t * 10, "events": res.events}
