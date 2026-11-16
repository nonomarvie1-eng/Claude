"""THE FINAL SET — bonus engine (Court Control + Power Shots + Hawk-Eye).

Rules (all numbers in config.FINAL_SET):

* During a bonus the 6x5 grid is the opponent's half of a court, seen from the
  server: rows 0-2 are DEEP (baseline side), rows 3-4 are SHORT (net side);
  reels 1-2 / 3-4 / 5-6 are LEFT / CENTRE / RIGHT.  Six zones:
      0 DL  1 DC  2 DR   (deep, 6 cells each)
      3 SL  4 SC  5 SR   (short, 4 cells each)
* Each EXCHANGE: the reels show a new board (bonus reel set), then exactly one
  shot is played.  The shot type and its landing zones are drawn from the
  published shot table of the bonus.
* A hit on a zone COLLECTS the court value of the symbols inside it
  (COURT_VALUE per symbol).  Every Scatter inside a collected zone adds one
  exchange (two for a Drop Shot).  If the zone carries a MARK, the mark pays
  MARK_PRIZE and is consumed.
* Shots:
    RALLY    1 zone, uniform over the 6 zones.
    ACE      1 deep zone; pays ACE_PRIZE; leaves a mark (ACE_MARK exchanges).
    SMASH    1 zone + its neighbours (left/right, and the other depth).
    PASSING  a diagonal path through 3 zones (4 possible paths).
    DROP     1 short zone; its Scatters count double; leaves a mark (DROP_MARK).
    GOLDEN   a "Golden Rally": GR_MIN to GR_MAX rally shots in the same exchange;
             every zone it hits is marked (GOLDEN_MARK).
* GRAND SLAM: when, after the marks of an exchange are placed, all six zones
  are marked, the exchange pays SLAM_PRIZE and every mark is cleared.
* Marks last N exchanges after the one that set them, then expire.
* GRAND FINAL only:
    - HAWK-EYE: a single-landing shot (RALLY/ACE/DROP) can land on a line
      (P_LINE); the call is IN (P_IN) or OUT.  IN: the hit counts, pays
      HAWK_PRIZE and marks the zone (HAWK_MARK).  OUT: nothing is collected
      but the point is replayed (+1 exchange).
    - CHAMPIONSHIP POINT: an exchange that starts with 1 exchange left uses
      the CP table (power shots only).  If an extension is won the match goes on.
* The win cap ends the round immediately.

Random numbers: every exchange makes exactly two draw() calls -- the 6 reel
stops, then an AUX vector of fixed length (see AUX).  The scalar engine
(events, books) and the vectorised engine (simulation) therefore consume the
same numbers in the same order: a round can be replayed exactly from its log.
"""

from __future__ import annotations

import numpy as np

from . import config as C

F = C.FINAL_SET
ROWS = C.NUM_ROWS
NZ = 6
ZONE_NAMES = ["DL", "DC", "DR", "SL", "SC", "SR"]
DEEP_ROWS = (0, 1, 2)
SHORT_ROWS = (3, 4)
SHOTS = ["RALLY", "ACE", "SMASH", "PASSING", "DROP", "GOLDEN"]
SHOT_ID = {s: i for i, s in enumerate(SHOTS)}
PASS_PATHS = [[0, 1, 5], [2, 1, 3], [3, 4, 2], [5, 4, 0]]

# AUX vector: index -> range
AUX = [
    ("shot", F["SHOT_ROLL"]),   # 0 shot type (weighted)
    ("zone6", 6),               # 1 RALLY / SMASH zone
    ("deep3", 3),               # 2 ACE zone
    ("short3", 3),              # 3 DROP zone
    ("path4", 4),               # 4 PASSING path
    ("gr_n", F["GR_MAX"] - F["GR_MIN"] + 1),  # 5 GOLDEN: GR_MIN + value shots
    *[(f"gr{i + 1}", 6) for i in range(F["GR_MAX"])],  # 6.. GOLDEN zones
    ("line", 1000),             # Hawk-Eye: on the line if < P_LINE
    ("call", 1000),             # Hawk-Eye: IN if < P_IN
]
I_LINE = 6 + F["GR_MAX"]
I_CALL = I_LINE + 1
AUX_LEN = [n for _, n in AUX]


def zone_cells(z: int) -> list[tuple[int, int]]:
    c, depth = z % 3, z // 3
    rows = DEEP_ROWS if depth == 0 else SHORT_ROWS
    return [(r, row) for r in (2 * c, 2 * c + 1) for row in rows]


def neighbours(z: int) -> list[int]:
    c, depth = z % 3, z // 3
    out = [depth * 3 + cc for cc in (c - 1, c + 1) if 0 <= cc < 3]
    out.append((1 - depth) * 3 + c)
    return out


def shot_table(level: str, championship_point: bool) -> list[int]:
    key = "CP_TABLE" if championship_point else ("FINAL_TABLE" if level == "final" else "RALLY_TABLE")
    return [F[key][s] for s in SHOTS]


def pick(weights: list[int], roll: int) -> int:
    acc = 0
    for i, w in enumerate(weights):
        acc += w
        if roll < acc:
            return i
    raise ValueError("roll outside table")


def shot_zones(shot: int, aux: list[int]) -> list[int]:
    s = SHOTS[shot]
    if s == "RALLY":
        return [aux[1]]
    if s == "ACE":
        return [aux[2]]
    if s == "SMASH":
        return [aux[1]] + neighbours(aux[1])
    if s == "PASSING":
        return list(PASS_PATHS[aux[4]])
    if s == "DROP":
        return [3 + aux[3]]
    n = F["GR_MIN"] + aux[5]
    return [aux[6 + i] for i in range(n)]


def court_values(board) -> tuple[list[int], list[int]]:
    """(value in t-units, scatter count) of each of the 6 zones for a board[reel][row]."""
    vals, scs = [], []
    for z in range(NZ):
        v = s = 0
        for r, row in zone_cells(z):
            sym = C.SYMBOLS[board[r][row]]
            v += F["COURT_VALUE"][sym]
            s += sym == "S"
        vals.append(v)
        scs.append(s)
    return vals, scs


def check_tables():
    for k in ("RALLY_TABLE", "FINAL_TABLE", "CP_TABLE"):
        assert sum(F[k].values()) == F["SHOT_ROLL"], k
        assert set(F[k]) == set(SHOTS), k


check_tables()


# ------------------------------------------------------------------ scalar reference (events)

def play_bonus(draw, free: "C.ReelSet", level: str, exchanges: int, base_t: int, emit, window, names, padding) -> dict:
    """Plays one complete bonus.  Returns {'win_t', 'capped', stats...}.  `emit`
    receives the events; `window`/`names`/`padding` come from engine.py."""
    marks = [0] * NZ
    remaining = exchanges
    awarded = exchanges
    played = points = 0
    win_t = 0
    capped = False
    stats = {s: 0 for s in SHOTS}
    stats.update(hawk=0, hawk_in=0, marks_set=0, mark_hits=0, mark_expired=0, cp=0, extensions=0, slam=0)
    cap_room = C.WINCAP_T - base_t
    while remaining > 0:
        cp = level == "final" and remaining == 1
        remaining -= 1
        played += 1
        stops = draw(free.lengths)
        aux = draw(AUX_LEN)
        board = window(free.strips, stops)
        vals, scs = court_values(board)
        a, b = padding(free.strips, stops)
        emit({"type": "exchangeStart", "exchange": played, "total": awarded, "remaining": remaining,
              "championshipPoint": cp, "marks": list(marks)})
        emit({"type": "reveal", "gameType": "freegame", "board": names(board), "stops": list(stops),
              "paddingAbove": [C.SYMBOLS[s] for s in a], "paddingBelow": [C.SYMBOLS[s] for s in b],
              "anticipation": [0] * C.NUM_REELS, "courtValues": [v * 10 for v in vals], "courtScatters": list(scs)})
        if cp:
            stats["cp"] += 1
        shot = pick(shot_table(level, cp), aux[0])
        name = SHOTS[shot]
        stats[name] += 1
        zones = shot_zones(shot, aux)
        hawk = None
        replay = 0
        if level == "final" and name in ("RALLY", "ACE", "DROP") and aux[I_LINE] < F["P_LINE"]:
            hawk = "in" if aux[I_CALL] < F["P_IN"] else "out"
            stats["hawk"] += 1
            if hawk == "in":
                stats["hawk_in"] += 1
            else:
                zones = []
                replay = 1
        hits = []
        ext = replay
        spin_t = 0
        for z in zones:
            pay = vals[z]
            mark_prize = 0
            if marks[z] > 0:
                mark_prize = F["MARK_PRIZE"]
                marks[z] = 0
                stats["mark_hits"] += 1
            extra = scs[z] * (2 if name == "DROP" else 1)
            ext += extra
            spin_t += pay + mark_prize
            hits.append({"zone": z, "zoneName": ZONE_NAMES[z], "value": pay * 10, "markPrize": mark_prize * 10,
                         "scatters": scs[z], "extraExchanges": extra, "cells": [{"reel": r, "row": row} for r, row in zone_cells(z)]})
            points += pay + mark_prize > 0
        prize = 0
        new_marks = []
        if name == "ACE" and zones:  # an ACE called OUT is a fault: no prize, no mark
            prize += F["ACE_PRIZE"]
            new_marks.append((zones[0], F["ACE_MARK"]))
        if name == "DROP" and zones:
            new_marks.append((zones[0], F["DROP_MARK"]))
        if hawk == "in":
            prize += F["HAWK_PRIZE"]
            new_marks.append((zones[0], F["HAWK_MARK"]))
        if name == "GOLDEN":
            for z in dict.fromkeys(zones):
                new_marks.append((z, F["GOLDEN_MARK"]))
        if hawk is not None:
            emit({"type": "hawkEye", "zone": shot_zones(shot, aux)[0], "call": hawk, "prize": (F["HAWK_PRIZE"] if hawk == "in" else 0) * 10,
                  "replay": hawk == "out"})
        set_now = set()
        for z, d in new_marks:
            marks[z] = max(marks[z], d)
            set_now.add(z)
            stats["marks_set"] += 1
        # GRAND SLAM: the whole court is marked -> big prize, court reset
        slam = all(m > 0 for m in marks)
        if slam:
            prize += F["SLAM_PRIZE"]
            stats["slam"] += 1
        spin_t += prize
        emit({"type": "shot", "shot": name, "zones": [h["zone"] for h in hits] if hits else zones, "path": shot_zones(shot, aux),
              "hits": hits, "prize": prize * 10, "win": spin_t * 10, "marksSet": [{"zone": z, "duration": d} for z, d in new_marks],
              "grandSlam": slam,
              "hawkEye": hawk})
        if slam:
            emit({"type": "grandSlam", "prize": F["SLAM_PRIZE"] * 10})
            marks = [0] * NZ
            set_now = set()
        expired = []
        for z in range(NZ):
            if marks[z] > 0 and z not in set_now:
                marks[z] -= 1
                if marks[z] == 0:
                    expired.append(z)
                    stats["mark_expired"] += 1
        if expired:
            emit({"type": "markExpire", "zones": expired})
        win_t += spin_t
        add = min(ext, F["MAX_REMAINING"] - remaining)
        if add > 0:
            remaining += add
            awarded += add
            stats["extensions"] += add
            emit({"type": "extraExchange", "added": add, "total": awarded, "reason": "replay" if replay and add == 1 and ext == 1 else "scatter"})
        running = min(win_t, cap_room)
        emit({"type": "exchangeEnd", "exchange": played, "win": spin_t * 10, "points": points,
              "bonusWin": running * 10, "marks": list(marks)})
        emit({"type": "setTotalWin", "amount": min(base_t + win_t, C.WINCAP_T) * 10})
        if base_t + win_t >= C.WINCAP_T:
            capped = True
            emit({"type": "wincap", "amount": C.WINCAP_T * 10})
            break
    return {"win_t": min(win_t, cap_room), "capped": capped, "exchanges": played, "points": points, **stats}


# ------------------------------------------------------------------ vectorised (simulation / pilots)

def _free_tables(free_strips):
    """Per reel and stop: deep/short value and scatter count."""
    val = np.array([F["COURT_VALUE"][s] for s in C.SYMBOLS], dtype=np.int64)
    isS = np.array([s == "S" for s in C.SYMBOLS], dtype=np.int64)
    out = []
    for strip in free_strips:
        a = np.array(strip)
        L = len(a)
        rows = np.stack([np.roll(a, -k) for k in range(ROWS)], axis=1)  # (L, 5)
        out.append({
            "dv": val[rows[:, :3]].sum(1), "sv": val[rows[:, 3:]].sum(1),
            "ds": isS[rows[:, :3]].sum(1), "ss": isS[rows[:, 3:]].sum(1),
        })
    return out


def play_bonus_vec(rng, level: np.ndarray, exchanges: np.ndarray, base_t: np.ndarray, free, log: list | None = None,
                   ids: np.ndarray | None = None) -> dict:
    """Vectorised bonuses.  level: 0 rally / 1 final per round.  If `log` is a
    list, appends (ids, stops, aux) for every iteration (exact replay)."""
    n = len(level)
    T = _free_tables(free.strips)
    flen = free.lengths
    ids = np.arange(n) if ids is None else ids
    tabs = {k: np.cumsum([F[k][s] for s in SHOTS]) for k in ("RALLY_TABLE", "FINAL_TABLE", "CP_TABLE")}
    marks = np.zeros((n, NZ), dtype=np.int64)
    remaining = exchanges.astype(np.int64).copy()
    win = np.zeros(n, dtype=np.int64)
    active = remaining > 0
    cap_room = C.WINCAP_T - base_t
    capped = np.zeros(n, dtype=bool)
    st = {k: np.zeros(n, dtype=np.int64) for k in SHOTS + ["hawk", "hawk_in", "marks_set", "mark_hits", "mark_expired", "cp", "extensions", "played", "slam"]}
    nb = np.array([neighbours(z) + [-1] * (3 - len(neighbours(z))) for z in range(NZ)])  # (6,3)
    paths = np.array(PASS_PATHS)
    while active.any():
        a = np.nonzero(active)[0]
        m = len(a)
        lv = level[a]
        cp = (lv == 1) & (remaining[a] == 1)
        remaining[a] -= 1
        st["played"][a] += 1
        stops = np.stack([rng.integers(0, L, m) for L in flen], axis=1)
        aux = np.stack([rng.integers(0, L, m) for L in AUX_LEN], axis=1)
        if log is not None:
            log.append((ids[a], stops, aux))
        # zone values / scatters (m, 6)
        zv = np.zeros((m, NZ), dtype=np.int64)
        zs = np.zeros((m, NZ), dtype=np.int64)
        for z in range(NZ):
            c, depth = z % 3, z // 3
            k1, k2 = ("dv", "ds") if depth == 0 else ("sv", "ss")
            for r in (2 * c, 2 * c + 1):
                zv[:, z] += T[r][k1][stops[:, r]]
                zs[:, z] += T[r][k2][stops[:, r]]
        cum = np.where(cp[:, None], tabs["CP_TABLE"][None, :], np.where((lv == 1)[:, None], tabs["FINAL_TABLE"][None, :], tabs["RALLY_TABLE"][None, :]))
        shot = (aux[:, 0:1] >= cum).sum(1)
        # hits (m, 5), -1 = none
        H = max(4, F["GR_MAX"])
        hits = np.full((m, H), -1, dtype=np.int64)
        s_r, s_a, s_s, s_p, s_d, s_g = (shot == i for i in range(6))
        hits[s_r, 0] = aux[s_r, 1]
        hits[s_a, 0] = aux[s_a, 2]
        hits[s_s, 0] = aux[s_s, 1]
        hits[s_s, 1:4] = nb[aux[s_s, 1]]
        hits[s_p, 0:3] = paths[aux[s_p, 4]]
        hits[s_d, 0] = 3 + aux[s_d, 3]
        gn = F["GR_MIN"] + aux[:, 5]
        for i in range(F["GR_MAX"]):
            sel = s_g & (gn > i)
            hits[sel, i] = aux[sel, 6 + i]
        first = hits[:, 0].copy()
        single = s_r | s_a | s_d
        hawk = (lv == 1) & single & (aux[:, I_LINE] < F["P_LINE"])
        hin = hawk & (aux[:, I_CALL] < F["P_IN"])
        hout = hawk & ~hin
        hits[hout, :] = -1
        rows = np.arange(m)
        mk = marks[a]
        spin = np.zeros(m, dtype=np.int64)
        ext = hout.astype(np.int64)
        for i in range(H):
            z = hits[:, i]
            ok = z >= 0
            zz = np.where(ok, z, 0)
            pay = np.where(ok, zv[rows, zz], 0)
            marked = ok & (mk[rows, zz] > 0)
            spin += pay + np.where(marked, F["MARK_PRIZE"], 0)
            st["mark_hits"][a] += marked
            mk[rows[marked], zz[marked]] = 0
            ext += np.where(ok, zs[rows, zz] * np.where(s_d, 2, 1), 0)
        spin += np.where(s_a & ~hout, F["ACE_PRIZE"], 0) + np.where(hin, F["HAWK_PRIZE"], 0)
        # new marks (same order as the scalar engine)
        set_now = np.zeros((m, NZ), dtype=bool)
        for sel, dur in ((s_a & ~hout, F["ACE_MARK"]), (s_d & ~hout, F["DROP_MARK"]), (hin, F["HAWK_MARK"])):
            idx = np.nonzero(sel)[0]
            if len(idx):
                zz = first[idx]
                mk[idx, zz] = np.maximum(mk[idx, zz], dur)
                set_now[idx, zz] = True
                st["marks_set"][a[idx]] += 1
        gi = np.nonzero(s_g)[0]
        if len(gi):
            gz = np.zeros((len(gi), NZ), dtype=bool)
            for i in range(F["GR_MAX"]):
                z = hits[gi, i]
                ok = z >= 0
                gz[np.nonzero(ok)[0], z[ok]] = True
            st["marks_set"][a[gi]] += gz.sum(1)
            sub = mk[gi]
            sub[gz] = np.maximum(sub[gz], F["GOLDEN_MARK"])
            mk[gi] = sub
            sn = set_now[gi]
            sn |= gz
            set_now[gi] = sn
        slam = (mk > 0).all(1)
        spin += np.where(slam, F["SLAM_PRIZE"], 0)
        st["slam"][a] += slam
        mk[slam] = 0
        set_now[slam] = False
        dec = (mk > 0) & ~set_now
        mk[dec] -= 1
        st["mark_expired"][a] += (dec & (mk == 0)).sum(1)
        marks[a] = mk
        for i, sname in enumerate(SHOTS):
            st[sname][a] += shot == i
        st["hawk"][a] += hawk
        st["hawk_in"][a] += hin
        st["cp"][a] += cp
        win[a] += spin
        add = np.minimum(ext, F["MAX_REMAINING"] - remaining[a])
        add = np.maximum(add, 0)
        hit_cap = base_t[a] + win[a] >= C.WINCAP_T
        capped[a] |= hit_cap
        add = np.where(hit_cap, 0, add)
        remaining[a] += add
        st["extensions"][a] += add
        active[a] = (remaining[a] > 0) & ~hit_cap
    return {"win_t": np.minimum(win, cap_room), "capped": capped, **st}
