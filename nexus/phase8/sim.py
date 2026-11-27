"""Simulateur chronologique de PORTEFEUILLE H1 sur perpétuels (pré-enregistrement 8-01).

- Signaux sur bougies H1 clôturées ; ordres au marché à l'ouverture suivante (+ retard optionnel).
- Achat et vente ; une position par actif ; au plus `max_positions` positions ; notionnel total ≤ capital.
- Taille : risque = `risk` × valeur liquidative à la clôture du signal ; quantité = risque / (prix × stop).
- Stop % fixe par actif, vérifié sur le plus haut/plus bas de chaque bougie dès la bougie d'entrée ;
  exécution au stop ou à l'ouverture si le prix a ouvert au-delà.
- Financement réel à chaque échéance (prix d'ouverture de la bougie) ; frais taker + glissement par côté.
- Perte journalière : si la valeur liquidative à une clôture ≤ (1 − daily_block) × celle de la fin du jour
  UTC précédent, plus aucune entrée avant le jour suivant. Variante `dd_halt` : tout fermer et arrêter.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..phase4.sim import adx, bollinger, cross_above, cross_below, rsi, sma


def ema(c: pd.Series, n: int) -> pd.Series:
    return c.ewm(span=n, adjust=False, min_periods=n).mean()


def vwap_daily(d: pd.DataFrame) -> pd.Series:
    """VWAP ancré à 00:00 UTC sur les bougies clôturées du jour (bougie courante incluse, connue à sa clôture)."""
    tp = (d["h"] + d["l"] + d["c"]) / 3
    day = d.index.floor("D")
    pv = (tp * d["volume"]).groupby(day).cumsum()
    v = d["volume"].groupby(day).cumsum()
    return (pv / v.replace(0, np.nan))


def signals(d: pd.DataFrame, rule: dict) -> pd.DataFrame:
    c = d["c"]
    f = pd.DataFrame(False, index=d.index, columns=["long_entry", "short_entry", "long_exit", "short_exit"])
    k = rule["kind"]
    if k == "bb_range":
        lo, hi = bollinger(c, 20, rule.get("bb_k", 2.0))
        a = adx(d, 14)
        m = sma(c, 20)
        f["long_entry"] = (c < lo) & (a < rule.get("adx_th", 20))
        f["short_entry"] = (c > hi) & (a < rule.get("adx_th", 20))
        f["long_exit"] = cross_above(c, m)
        f["short_exit"] = cross_below(c, m)
    elif k == "pullback":
        up, dn = ema(c, 50) > ema(c, 200), ema(c, 50) < ema(c, 200)
        r = rsi(c, 14)
        f["long_entry"] = up & (r < rule.get("rsi_low", 30))
        f["short_entry"] = dn & (r > rule.get("rsi_high", 70))
        f["long_exit"] = cross_above(r, 50.0)
        f["short_exit"] = cross_below(r, 50.0)
    elif k == "breakout":
        n, x = rule.get("n_entry", 24), rule.get("n_exit", 12)
        hh = d["h"].rolling(n, min_periods=n).max().shift(1)
        ll = d["l"].rolling(n, min_periods=n).min().shift(1)
        hx = d["h"].rolling(x, min_periods=x).max().shift(1)
        lx = d["l"].rolling(x, min_periods=x).min().shift(1)
        f["long_entry"] = cross_above(c, hh)
        f["short_entry"] = cross_below(c, ll)
        f["long_exit"] = cross_below(c, lx)
        f["short_exit"] = cross_above(c, hx)
    elif k == "vwap_trend":
        v = vwap_daily(d)
        fast = rule.get("ema_fast", 50)
        up, dn = ema(c, fast) > ema(c, 200), ema(c, fast) < ema(c, 200)
        f["long_entry"] = cross_above(c, v) & up
        f["short_entry"] = cross_below(c, v) & dn
        f["long_exit"] = cross_below(c, v)
        f["short_exit"] = cross_above(c, v)
    else:
        raise ValueError(k)
    return f.fillna(False).astype(bool)


@dataclass
class Res:
    equity: pd.Series                     # horaire
    trades: pd.DataFrame
    info: dict = field(default_factory=dict)


def simulate(bars: dict[str, pd.DataFrame], funding: dict[str, pd.Series], rule: dict, stops: dict[str, float], start, end, *,
             risk=0.005, max_positions=2, notional_cap=1.0, fee=0.0005, slip=0.0005, cost_mult=1.0, delay=0,
             daily_block=0.02, dd_halt=None, initial=1000.0, priority=None, stop_mult=1.0) -> Res:
    grid = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="1h", inclusive="left")
    names = priority or list(bars)
    fee, slip = fee * cost_mult, slip * cost_mult
    A = {}
    for s in names:
        d = bars[s].set_index("ts") if "ts" in bars[s].columns else bars[s]
        sig = signals(d, rule).reindex(grid).fillna(False)
        g = d[["o", "h", "l", "c"]].reindex(grid)
        A[s] = {"o": g.o.to_numpy(), "h": g.h.to_numpy(), "l": g.l.to_numpy(), "c": g.c.to_numpy(),
                "cff": g.c.ffill().to_numpy(), "sig": sig.to_numpy(), "stop": stops[s] * stop_mult,
                "fund": funding[s].reindex(grid).to_numpy() if s in funding else np.full(len(grid), np.nan)}
    cash = initial
    pos, pend, trades, eq = {}, {}, [], np.empty(len(grid))
    blocked_day, halted, peak = None, False, initial
    prev_day_close = initial
    stats = {"skipped_capacity": 0, "skipped_daily_block": 0, "daily_block_days": 0, "halt_time": None}

    def mtm(t):
        return cash + sum(p["dir"] * p["qty"] * ((A[s]["cff"][t] if not np.isnan(A[s]["cff"][t]) else p["entry"]) - p["entry"])
                          for s, p in pos.items())

    def close(s, px, t, reason):
        nonlocal cash
        p = pos.pop(s)
        fill = px * (1 - slip) if p["dir"] > 0 else px * (1 + slip)
        f = p["qty"] * fill * fee
        gross = p["dir"] * p["qty"] * (fill - p["entry"])
        cash += gross - f
        pnl = gross - p["fee"] - f - p["fund"]
        trades.append({"symbol": s, "side": "long" if p["dir"] > 0 else "short", "entry_ts": grid[p["t"]], "exit_ts": grid[t],
                       "entry": p["entry"], "exit": fill, "qty": p["qty"], "risk_amt": p["risk"], "fees": p["fee"] + f,
                       "funding": p["fund"], "pnl": pnl, "R": pnl / p["risk"], "hours": t - p["t"], "reason": reason})

    def try_open(s, d, t, eq_signal):
        nonlocal cash
        if len(pos) >= max_positions:
            stats["skipped_capacity"] += 1
            return
        px = A[s]["o"][t]
        fill = px * (1 + slip) if d > 0 else px * (1 - slip)
        r_amt = risk * eq_signal
        qty = r_amt / (fill * A[s]["stop"])
        used = sum(p["qty"] * A[x]["cff"][t] for x, p in pos.items() if not np.isnan(A[x]["cff"][t]))
        if used + qty * fill > notional_cap * mtm(t) + 1e-9:
            stats["skipped_capacity"] += 1
            return
        f = qty * fill * fee
        cash -= f
        pos[s] = {"dir": d, "qty": qty, "entry": fill, "t": t, "risk": r_amt, "fee": f, "fund": 0.0,
                  "stop_px": fill * (1 - A[s]["stop"]) if d > 0 else fill * (1 + A[s]["stop"])}

    for t in range(len(grid)):
        day = grid[t].floor("D")
        if t > 0 and day != grid[t - 1].floor("D"):
            prev_day_close = eq[t - 1]
        # ---- ouverture : sorties d'abord, puis entrées par ordre de priorité
        if pend and not halted:
            due = [s for s in names if s in pend and pend[s][2] <= t and not np.isnan(A[s]["o"][t])]
            for s in due:
                act = pend[s][0]
                if act in ("exit", "rev_long", "rev_short") and s in pos:
                    close(s, A[s]["o"][t], t, "signal")
            for s in due:
                act, eqs, _ = pend.pop(s)
                d = +1 if act in ("long", "rev_long") else (-1 if act in ("short", "rev_short") else 0)
                if d and s not in pos:
                    if blocked_day == day:
                        stats["skipped_daily_block"] += 1
                    else:
                        try_open(s, d, t, eqs)
        # ---- financement et stops
        for s in list(pos):
            a, p = A[s], pos[s]
            if not np.isnan(a["fund"][t]):
                px = a["o"][t] if not np.isnan(a["o"][t]) else a["cff"][t]
                pay = p["dir"] * p["qty"] * px * a["fund"][t]
                p["fund"] += pay
                cash -= pay
            if np.isnan(a["o"][t]):
                continue
            if p["dir"] > 0 and a["l"][t] <= p["stop_px"]:
                close(s, min(a["o"][t], p["stop_px"]), t, "stop")
            elif p["dir"] < 0 and a["h"][t] >= p["stop_px"]:
                close(s, max(a["o"][t], p["stop_px"]), t, "stop")
        e = mtm(t)
        eq[t] = e
        peak = max(peak, e)
        if halted:
            continue
        if dd_halt and e <= (1 - dd_halt) * peak:
            for s in list(pos):
                close(s, A[s]["cff"][t], t, "halt_drawdown")
            eq[t] = cash
            halted, stats["halt_time"] = True, str(grid[t])
            pend.clear()
            continue
        if blocked_day != day and e <= (1 - daily_block) * prev_day_close:
            blocked_day = day
            stats["daily_block_days"] += 1
        # ---- signaux à la clôture
        for s in names:
            a = A[s]
            if np.isnan(a["c"][t]) or (s in pend):
                continue
            le, se, lx, sx = a["sig"][t]
            due_t = t + 1 + delay
            if s in pos:
                d = pos[s]["dir"]
                if d > 0 and se:
                    pend[s] = ("rev_short", e, due_t)
                elif d > 0 and lx:
                    pend[s] = ("exit", e, due_t)
                elif d < 0 and le:
                    pend[s] = ("rev_long", e, due_t)
                elif d < 0 and sx:
                    pend[s] = ("exit", e, due_t)
            else:
                if le:
                    pend[s] = ("long", e, due_t)
                elif se:
                    pend[s] = ("short", e, due_t)
    for s in list(pos):
        close(s, A[s]["cff"][-1], len(grid) - 1, "end")
    eq[-1] = cash
    return Res(pd.Series(eq, index=grid), pd.DataFrame(trades), stats)


def random_R(bars: pd.DataFrame, start, end, hours: np.ndarray, sides, stop: float, n_reps: int, *, fee=0.0005, slip=0.0005, seed=0) -> np.ndarray:
    """R moyen (hors financement) de trades aux heures d'entrée tirées au hasard (mêmes durées, sens, stop, coûts)."""
    d = bars.set_index("ts") if "ts" in bars.columns else bars
    grid = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="1h", inclusive="left")
    g = d[["o", "h", "l", "c"]].reindex(grid)
    o, h, l = (g[x].to_numpy() for x in "ohl")
    valid = np.flatnonzero(~np.isnan(o))
    rng = np.random.default_rng(seed)
    hours = np.maximum(np.asarray(hours, int), 1)
    sides = np.array([1 if x == "long" else -1 for x in sides])
    out = np.empty(n_reps)
    for r in range(n_reps):
        acc = []
        for k, sd in zip(hours, sides):
            t0 = valid[rng.integers(0, len(valid))]
            t1 = min(t0 + k, len(o) - 1)
            px = o[t0]
            if np.isnan(px):
                continue
            fill = px * (1 + sd * slip)
            sp = fill * (1 - sd * stop)
            seg = l[t0:t1] if sd > 0 else h[t0:t1]
            hit = (seg <= sp) if sd > 0 else (seg >= sp)
            hit = np.nan_to_num(hit, nan=False).astype(bool)
            if hit.any():
                j = t0 + int(np.argmax(hit))
                xp = min(o[j], sp) if sd > 0 else max(o[j], sp)
            else:
                xp = o[t1] if not np.isnan(o[t1]) else px
            xf = xp * (1 - sd * slip)
            ret = sd * (xf - fill) / fill - fee * (1 + xf / fill)
            acc.append(ret / stop)
        out[r] = np.mean(acc) if acc else np.nan
    return out
