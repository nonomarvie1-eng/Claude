"""Reference game engine (Python).

This module is the authoritative implementation of the rules.  It is used by
  * the Monte-Carlo simulator (`simulate.py`),
  * the Stake Engine book exporter (`export_stake.py`),
  * the parity fixtures consumed by the TypeScript demo engine tests.

Outcome determination is a pure function of the reel stops drawn by the RNG.
Nothing here depends on previous rounds, balance or player behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import config as C

N_SYM = len(C.SYMBOLS)
PAY_BASES = np.array([N_SYM ** (C.NUM_REELS - 1 - r) for r in range(C.NUM_REELS)], dtype=np.int64)


def _line_eval(seq: tuple[int, ...]) -> tuple[int, int, int]:
    """Return (pay_t, paying_symbol, count) for a 5-symbol line, left to right.

    Rules: wild substitutes for every symbol except the scatter.  A line pays
    the highest of (a) the pure-wild run and (b) the run of the first
    non-wild symbol extended by wilds.  Scatters never pay on lines.
    """
    W, S = C.WILD, C.SCATTER
    # pure wild run
    wr = 0
    while wr < C.NUM_REELS and seq[wr] == W:
        wr += 1
    wild_pay = C.PAYTABLE["W"].get(wr, 0) if wr >= 3 else 0
    best = (wild_pay, W, wr) if wild_pay > 0 else (0, -1, 0)
    if wr < C.NUM_REELS:
        s = seq[wr]
        if s != S:
            n = wr
            while n < C.NUM_REELS and seq[n] in (s, W):
                n += 1
            p = C.PAYTABLE[C.SYMBOLS[s]].get(n, 0)
            if p > best[0]:
                best = (p, s, n)
    return best


def _build_line_table() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    size = N_SYM ** C.NUM_REELS
    pay = np.zeros(size, dtype=np.int32)
    sym = np.full(size, -1, dtype=np.int8)
    cnt = np.zeros(size, dtype=np.int8)
    for idx in range(size):
        seq = []
        x = idx
        for r in range(C.NUM_REELS):
            seq.append(x // int(PAY_BASES[r]))
            x %= int(PAY_BASES[r])
        p, s, n = _line_eval(tuple(seq))
        pay[idx], sym[idx], cnt[idx] = p, s, n
    return pay, sym, cnt


LINE_PAY, LINE_SYM, LINE_CNT = _build_line_table()


# --------------------------------------------------------------------------
# board helpers
# --------------------------------------------------------------------------

def window(strips: list[list[int]], stops: list[int]) -> list[list[int]]:
    """Visible board: board[reel][row], row 0 = top.  stop = index of top row."""
    out = []
    for r, strip in enumerate(strips):
        n = len(strip)
        out.append([strip[(stops[r] + k) % n] for k in range(C.NUM_ROWS)])
    return out


def padding(strips: list[list[int]], stops: list[int]) -> tuple[list[int], list[int]]:
    """Symbols directly above and below the visible window (cosmetic, real strip)."""
    above, below = [], []
    for r, strip in enumerate(strips):
        n = len(strip)
        above.append(strip[(stops[r] - 1) % n])
        below.append(strip[(stops[r] + C.NUM_ROWS) % n])
    return above, below


@dataclass
class LineWin:
    line: int
    symbol: int
    count: int
    base_pay: int  # t-units before multiplier


def evaluate_lines(board: list[list[int]]) -> list[LineWin]:
    wins = []
    for li, line in enumerate(C.PAYLINES):
        idx = 0
        for r in range(C.NUM_REELS):
            idx += board[r][line[r]] * int(PAY_BASES[r])
        p = int(LINE_PAY[idx])
        if p > 0:
            wins.append(LineWin(li, int(LINE_SYM[idx]), int(LINE_CNT[idx]), p))
    return wins


def positions_of(board: list[list[int]], symbol: int) -> list[dict]:
    return [
        {"reel": r, "row": row}
        for r in range(C.NUM_REELS)
        for row in range(C.NUM_ROWS)
        if board[r][row] == symbol
    ]


def anticipation(board: list[list[int]]) -> list[int]:
    """Reels that may still complete a scatter trigger (>=2 scatters already
    visible on reels to the left).  Purely presentational, derived from the
    already-determined board."""
    out, seen = [], 0
    for r in range(C.NUM_REELS):
        out.append(1 if seen >= 2 else 0)
        seen += sum(1 for s in board[r] if s == C.SCATTER)
    return out


# --------------------------------------------------------------------------
# round generation
# --------------------------------------------------------------------------

StopDrawer = Callable[[list[int]], list[int]]


def numpy_drawer(rng: np.random.Generator) -> StopDrawer:
    def draw(lengths: list[int]) -> list[int]:
        return [int(rng.integers(0, n)) for n in lengths]

    return draw


def list_drawer(stops_seq: list[list[int]]) -> StopDrawer:
    """Replays a recorded sequence of stops (used for parity fixtures/replay)."""
    it = iter(stops_seq)

    def draw(lengths: list[int]) -> list[int]:
        return list(next(it))

    return draw


def _names(board: list[list[int]]) -> list[list[str]]:
    return [[C.SYMBOLS[s] for s in reel] for reel in board]


@dataclass
class RoundResult:
    total_t: int  # capped total win in t-units
    base_t: int
    free_t: int
    triggered: bool
    fs_spins: int
    retriggers: int
    final_multiplier: int
    capped: bool
    base_hit: bool
    events: list[dict] | None
    stops: list[list[int]]


def play_round(
    draw: StopDrawer,
    base: C.ReelSet,
    free: C.ReelSet,
    record_events: bool = True,
    forced_base_stops: list[int] | None = None,
) -> RoundResult:
    """Play one complete paid round (base spin + any free spins).

    The whole round, including the bonus, is resolved here, in a single bet,
    before anything is shown to the player.
    """
    ev: list[dict] | None = [] if record_events else None
    all_stops: list[list[int]] = []

    def emit(e: dict) -> None:
        if ev is not None:
            e = {"index": len(ev), **e}
            ev.append(e)

    # ---------------- base spin ----------------
    stops = forced_base_stops if forced_base_stops is not None else draw(base.lengths)
    all_stops.append(list(stops))
    board = window(base.strips, stops)
    if ev is not None:
        above, below = padding(base.strips, stops)
        emit({
            "type": "reveal",
            "gameType": "basegame",
            "board": _names(board),
            "stops": list(stops),
            "paddingAbove": [C.SYMBOLS[s] for s in above],
            "paddingBelow": [C.SYMBOLS[s] for s in below],
            "anticipation": anticipation(board),
        })
    lw = evaluate_lines(board)
    sc_pos = positions_of(board, C.SCATTER)
    n_sc = len(sc_pos)
    sc_pay = C.SCATTER_PAY.get(n_sc, 0)
    base_t = sum(w.base_pay for w in lw) + sc_pay
    if ev is not None and base_t > 0:
        emit({
            "type": "winInfo",
            "gameType": "basegame",
            "multiplier": 1,
            "totalWin": base_t * 10,
            "wins": _win_list(lw, board, 1) + _scatter_win(sc_pos, sc_pay),
        })
        emit({"type": "setWin", "amount": base_t * 10, "winLevel": C.win_level(base_t / 10)})

    total = min(base_t, C.WINCAP_T)
    capped = base_t >= C.WINCAP_T
    triggered = n_sc >= 3 and not capped
    free_t = 0
    fs_spins = 0
    retrig = 0
    collected = 0
    mult = 1

    if triggered:
        remaining = C.FS_AWARD[n_sc]
        awarded_total = remaining
        emit({"type": "freeSpinTrigger", "totalFs": remaining, "positions": sc_pos})
        while remaining > 0:
            remaining -= 1
            fs_spins += 1
            emit({"type": "updateFreeSpin", "amount": fs_spins, "total": awarded_total})
            stops = draw(free.lengths)
            all_stops.append(list(stops))
            board = window(free.strips, stops)
            if ev is not None:
                above, below = padding(free.strips, stops)
                emit({
                    "type": "reveal",
                    "gameType": "freegame",
                    "board": _names(board),
                    "stops": list(stops),
                    "paddingAbove": [C.SYMBOLS[s] for s in above],
                    "paddingBelow": [C.SYMBOLS[s] for s in below],
                    "anticipation": [0] * C.NUM_REELS,
                })
            w_pos = positions_of(board, C.WILD)
            if w_pos:
                collected += len(w_pos)
                new_mult = C.MAINSPRING_LADDER[min(collected, len(C.MAINSPRING_LADDER) - 1)]
                emit({
                    "type": "mainspringWind",
                    "added": len(w_pos),
                    "collected": collected,
                    "multiplier": new_mult,
                    "previousMultiplier": mult,
                    "positions": w_pos,
                })
                mult = new_mult
            lw = evaluate_lines(board)
            sc_pos = positions_of(board, C.SCATTER)
            n_sc = len(sc_pos)
            sc_pay = C.SCATTER_PAY.get(n_sc, 0)
            spin_t = sum(w.base_pay for w in lw) * mult + sc_pay
            if spin_t > 0:
                free_t += spin_t
                if ev is not None:
                    emit({
                        "type": "winInfo",
                        "gameType": "freegame",
                        "multiplier": mult,
                        "totalWin": spin_t * 10,
                        "wins": _win_list(lw, board, mult) + _scatter_win(sc_pos, sc_pay),
                    })
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
                    awarded_total += add
                    retrig += 1
                    emit({"type": "freeSpinRetrigger", "totalFs": awarded_total, "added": add, "positions": sc_pos})
        total = min(base_t + free_t, C.WINCAP_T)
        emit({"type": "freeSpinEnd", "amount": total * 10, "winLevel": C.win_level(total / 10)})

    emit({"type": "finalWin", "amount": total * 10})
    return RoundResult(
        total_t=total,
        base_t=base_t,
        free_t=free_t,
        triggered=triggered,
        fs_spins=fs_spins,
        retriggers=retrig,
        final_multiplier=mult,
        capped=capped,
        base_hit=base_t > 0,
        events=ev,
        stops=all_stops,
    )


def _win_list(lw: list[LineWin], board: list[list[int]], mult: int) -> list[dict]:
    out = []
    for w in lw:
        line = C.PAYLINES[w.line]
        out.append({
            "kind": "line",
            "line": w.line,
            "symbol": C.SYMBOLS[w.symbol],
            "count": w.count,
            "basePay": w.base_pay * 10,
            "multiplier": mult,
            "win": w.base_pay * mult * 10,
            "positions": [{"reel": r, "row": line[r]} for r in range(w.count)],
        })
    return out


def _scatter_win(sc_pos: list[dict], sc_pay: int) -> list[dict]:
    if sc_pay <= 0:
        return []
    return [{
        "kind": "scatter",
        "line": None,
        "symbol": "S",
        "count": len(sc_pos),
        "basePay": sc_pay * 10,
        "multiplier": 1,
        "win": sc_pay * 10,
        "positions": sc_pos,
    }]


def make_book(book_id: int, res: RoundResult) -> dict:
    assert res.events is not None
    return {"id": book_id, "payoutMultiplier": res.total_t * 10, "events": res.events}
