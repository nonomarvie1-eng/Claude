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

    def emit(e):
        if ev is not None:
            ev.append({"index": len(ev), **e})

    stops = forced_base_stops if forced_base_stops is not None else draw(base.lengths)
    all_stops.append(list(stops))
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
    free_t = fs_spins = retrig = collected = 0
    level = C.bonus_level(n_sc) if triggered else None
    start = C.BONUS_LEVELS[level]["start_index"] if level else 0
    top = len(C.RALLY_LADDER) - 1
    mult = C.RALLY_LADDER[start]
    if triggered:
        remaining = C.FS_AWARD[n_sc]
        awarded = remaining
        emit({"type": "freeSpinTrigger", "totalFs": remaining, "positions": sc_pos, "level": level,
              "startMultiplier": mult, **({"bought": True} if bought else {})})
        while remaining > 0:
            remaining -= 1
            fs_spins += 1
            emit({"type": "updateFreeSpin", "amount": fs_spins, "total": awarded})
            stops = draw(free.lengths)
            all_stops.append(list(stops))
            board = window(free.strips, stops)
            if ev is not None:
                a, b = padding(free.strips, stops)
                emit({"type": "reveal", "gameType": "freegame", "board": _names(board), "stops": list(stops),
                      "paddingAbove": [C.SYMBOLS[s] for s in a], "paddingBelow": [C.SYMBOLS[s] for s in b],
                      "anticipation": [0] * R})
            w_pos = positions_of(board, C.WILD)
            if w_pos:
                collected += len(w_pos)
                new_mult = C.RALLY_LADDER[min(start + collected, top)]
                emit({"type": "rallyUp", "added": len(w_pos), "collected": collected, "multiplier": new_mult,
                      "previousMultiplier": mult, "positions": w_pos})
                mult = new_mult
            wins = evaluate_ways(board)
            sc_pos = positions_of(board, C.SCATTER)
            n_sc = len(sc_pos)
            sc_pay = C.SCATTER_PAY.get(n_sc, 0)
            spin_t = sum(w.base_pay for w in wins) * mult + sc_pay
            if spin_t > 0:
                free_t += spin_t
                if ev is not None:
                    emit({"type": "winInfo", "gameType": "freegame", "multiplier": mult, "totalWin": spin_t * 10,
                          "wins": _win_list(wins, board, mult) + _scatter_win(sc_pos, sc_pay)})
                    emit({"type": "setWin", "amount": spin_t * 10, "winLevel": C.win_level(spin_t / 10)})
            running = base_t + free_t
            emit({"type": "setTotalWin", "amount": min(running, C.WINCAP_T) * 10})
            if running >= C.WINCAP_T:
                capped = True
                emit({"type": "wincap", "amount": C.WINCAP_T * 10})
                break
            if n_sc >= 3:
                add = min(C.FS_RETRIGGER, C.FS_MAX_REMAINING - remaining)
                if add > 0:
                    remaining += add
                    awarded += add
                    retrig += 1
                    emit({"type": "freeSpinRetrigger", "totalFs": awarded, "added": add, "positions": sc_pos})
        total = min(base_t + free_t, C.WINCAP_T)
        emit({"type": "freeSpinEnd", "amount": total * 10, "winLevel": C.win_level(total / 10)})
    emit({"type": "finalWin", "amount": total * 10})
    return RoundResult(total, base_t, free_t, triggered, level, fs_spins, retrig, mult, capped, ev, all_stops)


def make_book(book_id: int, res: RoundResult) -> dict:
    assert res.events is not None
    return {"id": book_id, "payoutMultiplier": res.total_t * 10, "events": res.events}
