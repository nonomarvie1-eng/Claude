"""Simulateur de portefeuille reproduisant la sémantique des règles Cubrik (docs/phase4/01 §3).

- Signaux calculés à la clôture des bougies D1 UTC ; « price » = clôture.
- highest/lowest(N) = extrême des N bougies PRÉCÉDENTES (bougie courante exclue).
- Exécution au marché à l'ouverture de la bougie D1 suivante (1re bougie H1 du jour).
- Stop en % fixe depuis le prix d'exécution, vérifié bougie H1 par bougie H1 ;
  exécution au stop, ou à l'ouverture si le prix ouvre au-delà (gap).
- Une position par actif ; plusieurs actifs = plusieurs agents sur un capital commun.
- Taille : risque = `risk` × capital (à la clôture précédente) ; quantité = risque / (prix × stop).
  Somme des positions <= capital (aucun levier, y compris sur perpétuels).
- Comptant : achat seulement. Perpétuels : achat et vente, financement réel à chaque échéance.
- Mode « règles » : perte maximale de 2 % par jour (fermeture de toutes les positions) et arrêt
  définitif à 10 % de drawdown, évalués sur la valeur liquidative horaire.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Costs:
    fee: float
    slip: float
    perp: bool = False

    def scaled(self, k: float) -> "Costs":
        return Costs(self.fee * k, self.slip * k, self.perp)


SPOT = Costs(0.0010, 0.0005, False)
PERP = Costs(0.0005, 0.0005, True)


# --------------------------------------------------------------------------- indicateurs
def sma(c: pd.Series, n: int) -> pd.Series:
    return c.rolling(n, min_periods=n).mean()


def rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(dn != 0, 100.0)


def atr_pct(d1: pd.DataFrame, n: int = 14) -> pd.Series:
    pc = d1["c"].shift(1)
    tr = pd.concat([d1["h"] - d1["l"], (d1["h"] - pc).abs(), (d1["l"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / d1["c"]


def adx(d: pd.DataFrame, n: int = 14) -> pd.Series:
    """ADX de Wilder (lissage alpha = 1/n)."""
    h, l, c = d["h"], d["l"], d["c"]
    up, dn = h.diff(), -l.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    atr_ = tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    pdi = 100 * pdm.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / atr_
    mdi = 100 * mdm.ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / atr_
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def bollinger(c: pd.Series, n: int = 20, k: float = 2.0) -> tuple[pd.Series, pd.Series]:
    m = c.rolling(n, min_periods=n).mean()
    sd = c.rolling(n, min_periods=n).std(ddof=0)
    return m - k * sd, m + k * sd


def cross_above(a: pd.Series, b) -> pd.Series:
    b = b if isinstance(b, pd.Series) else pd.Series(float(b), index=a.index)
    ok = a.notna() & b.notna() & a.shift(1).notna() & b.shift(1).notna()
    return ok & (a > b) & (a.shift(1) <= b.shift(1))


def cross_below(a: pd.Series, b) -> pd.Series:
    b = b if isinstance(b, pd.Series) else pd.Series(float(b), index=a.index)
    ok = a.notna() & b.notna() & a.shift(1).notna() & b.shift(1).notna()
    return ok & (a < b) & (a.shift(1) >= b.shift(1))


def signals(d1: pd.DataFrame, rule: dict) -> pd.DataFrame:
    """Drapeaux évalués à la clôture de chaque bougie D1 (index = début du jour UTC).
    Aucun drapeau n'utilise de donnée postérieure à la clôture du jour."""
    c = d1["c"]
    f = pd.DataFrame(False, index=d1.index, columns=["long_entry", "long_exit", "short_entry", "short_exit"])
    kind = rule["kind"]
    if kind == "donch":
        hh = d1["h"].rolling(rule["entry_n"], min_periods=rule["entry_n"]).max().shift(1)
        ll = d1["l"].rolling(rule["exit_n"], min_periods=rule["exit_n"]).min().shift(1)
        f["long_entry"] = cross_above(c, hh)
        f["long_exit"] = cross_below(c, ll)
    elif kind == "sma":
        s = sma(c, rule["sma_n"])
        f["long_entry"] = cross_above(c, s)
        f["long_exit"] = cross_below(c, s)
    elif kind == "tsmom":
        roc = c / c.shift(rule["roc_n"]) - 1
        f["long_entry"] = cross_above(roc, 0.0)
        f["short_entry"] = cross_below(roc, 0.0)
        f["long_exit"] = f["short_entry"]
        f["short_exit"] = f["long_entry"]
    elif kind == "bbmr":
        lo, hi = bollinger(c, rule["bb_n"], rule["bb_k"])
        f["long_entry"] = (c < lo) & (rsi(c, rule["rsi_n"]) > rule["rsi_th"]) & (adx(d1, rule["adx_n"]) > rule["adx_th"])
        f["long_exit"] = c > hi
    elif kind == "rsi2":
        r = rsi(c, rule["rsi_n"])
        trend = sma(c, rule["trend_sma"])
        f["long_entry"] = (r < rule["rsi_th"]) & (c > trend) & r.notna() & trend.notna()
        f["long_exit"] = cross_above(c, sma(c, rule["exit_sma"]))
    else:
        raise ValueError(kind)
    return f


# --------------------------------------------------------------------------- simulation
@dataclass
class AssetData:
    h1: pd.DataFrame                     # ts, o, h, l, c
    d1: pd.DataFrame                     # index = jour UTC ; o, h, l, c
    funding: pd.Series | None = None     # index = horodatage d'échéance ; taux


@dataclass
class Result:
    equity: pd.Series                    # USDT, clôture de chaque jour
    exposure: pd.Series                  # somme |notionnels| / capital, clôture de chaque jour
    trades: pd.DataFrame
    info: dict = field(default_factory=dict)


def simulate(assets: dict[str, AssetData], rule: dict, stops: dict[str, float], *, start, end,
             risk: float = 0.005, costs: Costs = SPOT, cost_mult: float = 1.0, initial: float = 1000.0,
             rules_mode: bool = False, daily_loss: float = 0.02, dd_halt: float = 0.10,
             stop_mult: float = 1.0, tiers: list[tuple[float, float]] | None = None, bar_hours: int = 24,
             delay_bars: int = 0) -> Result:
    """`tiers` : paliers Cubrik « lock » en % du prix (phase 5) : dès que le prix atteint entrée × (1 + at)
    (plus haut pour un achat), le stop remonte à entrée × (1 + lock), effectif à partir de la bougie H1
    suivante (aucune hypothèse favorable sur l'ordre intrabougie)."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    cst = costs.scaled(cost_mult)
    allow_short = costs.perp
    grid = pd.date_range(start, end, freq="1h", inclusive="left")
    # bougies de signal : D1 par défaut (phase 4) ; H4 en phase 7 (`a.d1` contient alors les bougies H4)
    days = pd.date_range(start, end, freq=f"{bar_hours}h", inclusive="left")
    names = list(assets)
    A = {}
    for s in names:
        a = assets[s]
        h = a.h1.set_index("ts")[["o", "h", "l", "c"]].reindex(grid)
        sig = signals(a.d1, rule).reindex(days).fillna(False)
        fund = None
        if a.funding is not None and costs.perp:
            fund = a.funding.reindex(grid).to_numpy()
        A[s] = {"o": h["o"].to_numpy(), "h": h["h"].to_numpy(), "l": h["l"].to_numpy(),
                "c": h["c"].to_numpy(), "cff": h["c"].ffill().to_numpy(), "sig": sig, "fund": fund,
                "stop": stops[s] * stop_mult}
    cash = initial
    pos: dict[str, dict] = {}
    trades, eq_days, expo_days = [], [], []
    pending: dict[str, str] = {}
    due: dict[str, int] = {}                     # bougie à partir de laquelle l'ordre est exécuté (retard)
    e_prev = initial
    peak = initial
    halted = False
    n_skipped = 0
    stats = {"daily_loss_events": 0, "halt_time": None}

    def mtm(k: int) -> float:
        v = cash
        for s, p in pos.items():
            px = A[s]["cff"][k]
            if np.isnan(px):
                px = p["entry"]
            v += p["qty"] * px if not cst.perp else p["dir"] * p["qty"] * (px - p["entry"])
        return v

    def close(s: str, px: float, ts, reason: str):
        nonlocal cash
        p = pos.pop(s)
        fill = px * (1 - cst.slip) if p["dir"] > 0 else px * (1 + cst.slip)
        fee = abs(p["qty"] * fill) * cst.fee
        if cst.perp:
            pnl_gross = p["dir"] * p["qty"] * (fill - p["entry"])
            cash += pnl_gross - fee
        else:
            pnl_gross = p["qty"] * (fill - p["entry"])
            cash += p["qty"] * fill - fee
        pnl = pnl_gross - p["fee_in"] - fee - p["funding"]
        trades.append({"symbol": s, "side": "long" if p["dir"] > 0 else "short", "entry_ts": p["ts"], "exit_ts": ts,
                       "entry": p["entry"], "exit": fill, "qty": p["qty"], "risk_amt": p["risk_amt"],
                       "fees": p["fee_in"] + fee, "funding": p["funding"], "pnl": pnl, "R": pnl / p["risk_amt"],
                       "R_ex_funding": (pnl + p["funding"]) / p["risk_amt"], "bars": p["bars"], "reason": reason})

    def open_(s: str, d: int, k: int, px: float, ts):
        nonlocal cash, n_skipped
        stop = A[s]["stop"]
        fill = px * (1 + cst.slip) if d > 0 else px * (1 - cst.slip)
        risk_amt = risk * e_prev
        qty = risk_amt / (fill * stop)
        notional = qty * fill
        used = sum(p["qty"] * A[x]["cff"][k] if not np.isnan(A[x]["cff"][k]) else p["qty"] * p["entry"]
                   for x, p in pos.items())
        if used + notional > mtm(k) + 1e-9:
            n_skipped += 1
            return
        fee = notional * cst.fee
        if cst.perp:
            cash -= fee
        else:
            cash -= notional + fee
        pos[s] = {"dir": d, "qty": qty, "entry": fill, "ts": ts, "risk_amt": risk_amt, "fee_in": fee,
                  "funding": 0.0, "bars": 0, "stop_px": fill * (1 - stop) if d > 0 else fill * (1 + stop)}

    for di, day in enumerate(days):
        k0 = di * bar_hours
        # ---- ouverture : ordres issus de la clôture précédente
        if not halted:
            for s, act in list(pending.items()):
                if due.get(s, di) > di:
                    continue                                     # retard d'exécution simulé
                a = A[s]
                kk = next((k for k in range(k0, min(k0 + bar_hours, len(grid))) if not np.isnan(a["o"][k])), None)
                if kk is None:
                    continue                                     # pas de cotation ce jour : ordre reporté
                px = a["o"][kk]
                if act in ("exit", "reverse_long", "reverse_short") and s in pos:
                    close(s, px, grid[kk], "signal")
                if act in ("long", "reverse_long") and s not in pos:
                    open_(s, +1, kk, px, grid[kk])
                if act in ("short", "reverse_short") and s not in pos and allow_short:
                    open_(s, -1, kk, px, grid[kk])
                del pending[s]
        # ---- heures du jour : stops, financement, règles de risque
        for k in range(k0, min(k0 + bar_hours, len(grid))):
            for s in list(pos):
                a, p = A[s], pos[s]
                if a["fund"] is not None and not np.isnan(a["fund"][k]):
                    px = a["o"][k] if not np.isnan(a["o"][k]) else a["cff"][k]
                    pay = p["dir"] * p["qty"] * px * a["fund"][k]
                    p["funding"] += pay
                    cash -= pay
                o, h, l = a["o"][k], a["h"][k], a["l"][k]
                if np.isnan(o) or grid[k] < p["ts"]:
                    continue
                if p["dir"] > 0 and l <= p["stop_px"]:
                    close(s, min(o, p["stop_px"]), grid[k], "stop")
                elif p["dir"] < 0 and h >= p["stop_px"]:
                    close(s, max(o, p["stop_px"]), grid[k], "stop")
                if tiers and s in pos:
                    for at, lock in tiers:
                        if p["dir"] > 0 and h >= p["entry"] * (1 + at):
                            p["stop_px"] = max(p["stop_px"], p["entry"] * (1 + lock))
                        elif p["dir"] < 0 and l <= p["entry"] * (1 - at):
                            p["stop_px"] = min(p["stop_px"], p["entry"] * (1 - lock))
            if rules_mode and pos and not halted:
                e = mtm(k)
                peak = max(peak, e)
                if e <= (1 - dd_halt) * peak:
                    for s in list(pos):
                        close(s, A[s]["cff"][k], grid[k], "halt_drawdown")
                    halted, stats["halt_time"] = True, str(grid[k])
                    pending.clear()
                elif e <= (1 - daily_loss) * e_prev:
                    for s in list(pos):
                        close(s, A[s]["cff"][k], grid[k], "daily_loss")
                    stats["daily_loss_events"] += 1
        # ---- clôture : valeur, exposition, nouveaux ordres
        klast = min(k0 + bar_hours - 1, len(grid) - 1)
        e_close = mtm(klast)
        peak = max(peak, e_close)
        expo = sum(p["qty"] * (A[s]["cff"][klast] if not np.isnan(A[s]["cff"][klast]) else p["entry"]) for s, p in pos.items())
        eq_days.append(e_close)
        expo_days.append(expo / e_close if e_close > 0 else 0.0)
        e_prev = e_close
        if halted:
            continue
        for s in names:
            if delay_bars and s in pending:
                continue                                         # un ordre déjà en attente n'est pas remplacé
            f = A[s]["sig"].iloc[di]
            due[s] = di + 1 + delay_bars
            if s in pos:
                p = pos[s]
                p["bars"] += 1
                if p["dir"] > 0:
                    if allow_short and f["short_entry"]:
                        pending[s] = "reverse_short"
                    elif f["long_exit"] or (rule.get("max_bars") and p["bars"] >= rule["max_bars"]):
                        pending[s] = "exit"
                else:
                    if f["long_entry"]:
                        pending[s] = "reverse_long"
                    elif f["short_exit"]:
                        pending[s] = "exit"
            else:
                if f["long_entry"]:
                    pending[s] = "long"
                elif allow_short and f["short_entry"]:
                    pending[s] = "short"
    for s in list(pos):
        close(s, A[s]["cff"][len(grid) - 1], grid[-1], "end")
    eq = pd.Series(eq_days, index=days)
    eq.iloc[-1] = cash                      # après fermeture finale, frais de sortie inclus
    info = {"n_skipped_capacity": n_skipped, **stats}
    return Result(eq, pd.Series(expo_days, index=days), pd.DataFrame(trades), info)


# --------------------------------------------------------------------------- base aléatoire
def random_trades_R(a: AssetData, start, end, durations, sides, stop: float, costs: Costs, n_reps: int,
                    seed: int = 0) -> np.ndarray:
    """R moyen (hors financement) de trades placés à des jours tirés au hasard, de même nombre, même
    durée (en jours) et même sens que les trades réels, avec la même règle de stop. Renvoie n_reps moyennes."""
    rng = np.random.default_rng(seed)
    days = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="1D", inclusive="left")
    h = a.h1.set_index("ts")[["o", "h", "l", "c"]].reindex(pd.date_range(days[0], days[-1] + pd.Timedelta(days=1), freq="1h", inclusive="left"))
    o, hi, lo, c = (h[x].to_numpy() for x in "ohlc")
    cff = pd.Series(c).ffill().to_numpy()
    nd = len(days)
    out = np.empty(n_reps)
    durations = np.asarray(durations, int)
    for r in range(n_reps):
        acc = []
        for dur, side in zip(durations, sides):
            dur = max(int(dur), 1)
            if dur >= nd:
                continue
            d0 = rng.integers(0, nd - dur)
            a0, b0 = d0 * 24, (d0 + dur) * 24
            seg_o = o[a0:b0]
            ok = ~np.isnan(seg_o)
            if not ok.any():
                continue
            i0 = a0 + int(np.argmax(ok))
            px = o[i0]
            sgn = 1 if side == "long" else -1
            fill = px * (1 + sgn * costs.slip)
            stop_px = fill * (1 - sgn * stop)
            seg_l, seg_h = lo[i0:b0], hi[i0:b0]
            hit = (seg_l <= stop_px) if sgn > 0 else (seg_h >= stop_px)
            if hit.any():
                j = i0 + int(np.argmax(hit))
                xo = o[j]
                xp = min(xo, stop_px) if sgn > 0 else max(xo, stop_px)
            else:
                j = b0 if b0 < len(o) and not np.isnan(o[b0]) else b0 - 1
                xp = o[j] if not np.isnan(o[j]) else cff[j]
            xf = xp * (1 - sgn * costs.slip)
            ret = sgn * (xf - fill) / fill - costs.fee * (1 + xf / fill)
            acc.append(ret / stop)
        out[r] = np.mean(acc) if acc else np.nan
    return out
