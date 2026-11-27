"""Lot 8-01 : day trading H1 sur perpétuels (pré-enregistrement batch_8_01_intraday.toml).

    python -m nexus.research.p8_runner all
"""
from __future__ import annotations

import json
import zlib
import sys
import tomllib

import numpy as np
import pandas as pd

from ..config import DEV, RESULTS_DIR, ROOT
from ..phase4 import data as p4d
from ..phase4.sim import atr_pct
from ..phase8 import data as p8d
from ..phase8.sim import random_R, simulate
from ..stats.inference import block_bootstrap_mean, deflated_sharpe, week_groups
from .registry import Registry

TOML = ROOT / "experiments" / "preregistration" / "batch_8_01_intraday.toml"
OUT = RESULTS_DIR / "batch_8_01_intraday"
S = tomllib.loads(TOML.read_text())
UNIV = S["universe"]["decision"] + S["universe"]["replication"]
START, END = (pd.Timestamp(x, tz="UTC") for x in S["periods"]["eval"])
HYP = {"H8-3-BB-RANGE-MR": {"kind": "bb_range"}, "H8-4-TREND-PULLBACK": {"kind": "pullback"},
       "H8-1-BREAKOUT24": {"kind": "breakout"}, "H8-2-VWAP-TREND": {"kind": "vwap_trend"}}
SENS = {"H8-3-BB-RANGE-MR": [({"adx_th": 15}, 1), ({"adx_th": 25}, 1), ({"bb_k": 1.5}, 1), ({"bb_k": 2.5}, 1)],
        "H8-4-TREND-PULLBACK": [({"rsi_low": 25, "rsi_high": 75}, 1), ({"rsi_low": 35, "rsi_high": 65}, 1), ({}, 0.75), ({}, 1.5)],
        "H8-1-BREAKOUT24": [({"n_entry": 18, "n_exit": 9}, 1), ({"n_entry": 36, "n_exit": 18}, 1), ({}, 0.75), ({}, 1.5)],
        "H8-2-VWAP-TREND": [({"ema_fast": 34}, 1), ({"ema_fast": 89}, 1), ({}, 0.75), ({}, 1.5)]}
# stop_mult 0,75 et 1,5 appliqués à k = 2 donnent k = 1,5 et k = 3,0 (pré-enregistré)


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def registry():
    reg = Registry()
    for fam, n in (("P8", 4), ("P8-SENS", 16), ("P8-DIAG", 4)):
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, n, "Budget autorisé par l'utilisateur (lot 8-01).")
    for k, h in S["hypothesis"].items():
        spec = {"key": k, "family": "P8", "statement": f"long : {h['long']} ; short : {h['short']} ; sorties : {h['exit_long']} / {h['exit_short']}",
                "rationale": "Pré-enregistrement batch_8_01_intraday.toml", "params": {"rule": HYP[k], "conventions": S["conventions"]},
                "data": S["data"], "metrics": ["R moyen net du portefeuille", "voir [tests]"], "rejection": S["criteria"]}
        reg.register_hypothesis(spec)
        reg.register_hypothesis({**spec, "key": k + "-SENS", "family": "P8-SENS", "statement": "Voisins pré-déclarés : " + "; ".join(h["sensitivity"])})
    for k, st in (("P8-DIAG-STOPS", "Calibration des stops (S2 2019) et disponibilité des perpétuels."),
                  ("P8-DIAG-RANDOM", "Entrées aléatoires appariées (1 000 tirages)."),
                  ("P8-DIAG-STRESS", "Coûts x2, retard d'une bougie, signaux manqués."),
                  ("P8-DIAG-MC", "Monte Carlo (ou levier si une hypothèse est candidate).")):
        reg.register_hypothesis({"key": k, "family": "P8-DIAG", "statement": st, "rationale": "Diagnostic du lot 8-01.", "params": {},
                                 "data": S["data"], "metrics": ["voir module"], "rejection": {"text": "diagnostic"}})
    return reg


def load_all():
    bars = {s: p8d.load(s) for s in UNIV}
    fund = {}
    for s in UNIV:
        f = p4d.read_funding(s, "2019-09", p4d.LAST_MONTH)
        fund[s] = f.set_index("ts")["rate"]
    return bars, fund


def calib_stops(reg):
    tid = reg.start_trial("P8-DIAG-STOPS", {"k": 2}, "univers", "2019H2", 1.0, purpose="diagnostic")
    out = {}
    for s in UNIV:
        h1 = p4d.load_h1(s, "2019-07-01", "2020-01-01")
        d = h1.set_index("ts")[["o", "h", "l", "c"]]
        m = float(atr_pct(d).median())
        out[s] = {"atr_h1_median_pct": m * 100, "stop_pct": float(np.clip(round(2 * m * 100, 2), 0.5, 10.0))}
    reg.finish_trial(tid, status="done", result=out)
    return out


# --------------------------------------------------------------------------- mesures
def longest_loss_streak(pnl):
    m = c = 0
    for x in pnl:
        c = c + 1 if x < 0 else 0
        m = max(m, c)
    return m


def metrics(res, initial=1000.0):
    eq = res.equity
    t = res.trades.sort_values("exit_ts") if len(res.trades) else res.trades
    daily = eq.resample("1D").last()
    dr = daily.pct_change().fillna(daily.iloc[0] / initial - 1)
    wk = daily.resample("W").last().pct_change().dropna()
    mo = daily.resample("ME").last().pct_change().dropna()
    n_days = len(daily)
    out = {"capital_final": float(eq.iloc[-1]), "gain_net": float(eq.iloc[-1] - initial),
           "ret_daily_mean_pct": float(dr.mean() * 100), "ret_daily_median_pct": float(dr.median() * 100),
           "ret_weekly_mean_pct": float(wk.mean() * 100), "ret_monthly_mean_pct": float(mo.mean() * 100),
           "cagr_pct": float(((eq.iloc[-1] / initial) ** (365.25 / n_days) - 1) * 100),
           "trades": int(len(t)), "trades_per_day": float(len(t) / n_days),
           "days_positive_pct": float((dr > 0).mean() * 100), "days_negative_pct": float((dr < 0).mean() * 100),
           "days_plus5_pct": float((dr >= 0.05).mean() * 100),
           "sharpe": float(dr.mean() / dr.std() * np.sqrt(365)) if dr.std() > 0 else None,
           "max_dd_pct": float((1 - eq / eq.cummax()).max() * 100),
           "worst_day_pct": float(dr.min() * 100), "worst_week_pct": float(wk.min() * 100) if len(wk) else None,
           "info": res.info}
    if len(t):
        R = t["R"].to_numpy()
        m, lo, hi, p = block_bootstrap_mean(R, week_groups(pd.to_datetime(t["entry_ts"])))
        win, loss = t.pnl[t.pnl > 0], t.pnl[t.pnl < 0]
        out.update({"R_mean": m, "R_ci95": [lo, hi], "p_R_le_0": p, "win_rate": float((t.pnl > 0).mean()),
                    "avg_win_R": float(t.R[t.pnl > 0].mean()) if len(win) else None, "avg_loss_R": float(t.R[t.pnl < 0].mean()) if len(loss) else None,
                    "profit_factor": float(win.sum() / -loss.sum()) if len(loss) else None,
                    "longest_loss_streak": longest_loss_streak(t.pnl.to_numpy()),
                    "fees_total": float(t.fees.sum()), "funding_total": float(t.funding.sum()),
                    "cost_total": float(t.fees.sum() + t.funding.sum()),
                    "by_side": {sd: {"n": int((t.side == sd).sum()), "R": float(t.R[t.side == sd].mean())} for sd in ("long", "short")},
                    "by_reason": t.reason.value_counts().to_dict(),
                    "median_hours": float(t.hours.median())})
    out["_dr"] = dr
    return out


def dd_mc(dr: pd.Series, n=2000, seed=0):
    """Bootstrap par semaines des rendements quotidiens : drawdown et probabilités de ruine (scénarios)."""
    rng = np.random.default_rng(seed)
    wk = dr.groupby(dr.index.to_period("W"))
    blocks = [g.to_numpy() for _, g in wk]
    dds, tots = np.empty(n), np.empty(n)
    for k in range(n):
        path = np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))])
        eq = np.cumprod(1 + path)
        dds[k] = (1 - eq / np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]).max()
        tots[k] = eq[-1] - 1
    return {"dd_p95_pct": float(np.percentile(dds, 95) * 100), "p_dd_gt_10": float((dds > 0.10).mean()),
            "p_dd_gt_20": float((dds > 0.20).mean()), "p_ruin_50": float((dds > 0.50).mean()),
            "total_return_median_pct": float(np.median(tots) * 100), "total_return_p05_pct": float(np.percentile(tots, 5) * 100)}


def clean(m):
    return {k: v for k, v in m.items() if not k.startswith("_")}


# --------------------------------------------------------------------------- exécution
def cmd_all():
    reg = registry()
    bars, fund = load_all()
    stops = calib_stops(reg)
    st = {s: v["stop_pct"] / 100 for s, v in stops.items()}
    kw = dict(priority=UNIV, risk=0.005, max_positions=2, notional_cap=1.0, daily_block=0.02)
    out = {"stops": stops, "results": {}}
    sharpes = []
    for key, rule in HYP.items():
        tid = reg.start_trial(key, rule, "portefeuille 10", "dev", 1.0, purpose="selection")
        res = simulate(bars, fund, rule, st, START, END, **kw)
        m = metrics(res)
        dr = m.pop("_dr")
        sharpes.append(dr.mean() / dr.std() if dr.std() > 0 else 0.0)
        ev = {"portfolio": m, "mc": dd_mc(dr)}
        t = res.trades
        ev["subperiods"] = {}
        for a, b in S["periods"]["subperiods"]:
            x = t[(t.entry_ts >= pd.Timestamp(a, tz="UTC")) & (t.entry_ts < pd.Timestamp(b, tz="UTC"))]
            ev["subperiods"][f"{a[:4]}-{b[:4]}"] = {"n": int(len(x)), "R_mean": float(x.R.mean()) if len(x) else None}
        # mono-actif (C6)
        ev["single_asset"] = {}
        for s in UNIV:
            r1 = simulate({s: bars[s]}, {s: fund[s]}, rule, {s: st[s]}, START, END, **{**kw, "priority": [s], "max_positions": 1})
            ev["single_asset"][s] = {"n": int(len(r1.trades)), "R_mean": float(r1.trades.R.mean()) if len(r1.trades) else None,
                                     "final": float(r1.equity.iloc[-1])}
        # profils de risque (information, même essai)
        ev["profiles"] = {}
        for rk in (0.0025, 0.01, 0.02):
            rp = simulate(bars, fund, rule, st, START, END, **{**kw, "risk": rk})
            mp = metrics(rp)
            ev["profiles"][f"{rk*100:g} %"] = {**{k: mp.get(k) for k in ("capital_final", "cagr_pct", "max_dd_pct", "ret_daily_mean_pct", "days_plus5_pct", "worst_day_pct", "sharpe")},
                                               "mc": dd_mc(mp.pop("_dr"))}
        res.trades.to_csv(OUT / f"trades_{key}.csv", index=False)
        res.equity.resample("1D").last().to_csv(OUT / f"equity_daily_{key}.csv")
        reg.finish_trial(tid, status="done", n_trades=m["trades"], mean_r=m.get("R_mean"), p_value=m.get("p_R_le_0"),
                         result={k: m.get(k) for k in ("capital_final", "R_mean", "R_ci95", "max_dd_pct", "trades_per_day")})
        out["results"][key] = ev
        print(key, json.dumps({k: m.get(k) for k in ("capital_final", "trades_per_day", "R_mean", "R_ci95", "p_R_le_0", "max_dd_pct", "win_rate", "profit_factor")}, default=str), flush=True)
        save("results.json", out)
    # sensibilité
    for key, rule in HYP.items():
        out["results"][key]["sensitivity"] = []
        for over, sm in SENS[key]:
            tid = reg.start_trial(key + "-SENS", {**over, "stop_mult": sm}, "portefeuille 10", "dev", 1.0, purpose="sensitivity")
            r = simulate(bars, fund, {**rule, **over}, st, START, END, **kw, stop_mult=sm)
            m = metrics(r)
            dr = m.pop("_dr")
            sharpes.append(dr.mean() / dr.std() if dr.std() > 0 else 0.0)
            reg.finish_trial(tid, status="done", n_trades=m["trades"], mean_r=m.get("R_mean"), p_value=m.get("p_R_le_0"))
            out["results"][key]["sensitivity"].append({"variant": {**over, "stop_mult": sm}, "R_mean": m.get("R_mean"), "trades": m["trades"],
                                                       "capital_final": m["capital_final"], "max_dd_pct": m["max_dd_pct"]})
        print(key, "sens", [round(x["R_mean"] or 0, 3) for x in out["results"][key]["sensitivity"]], flush=True)
        save("results.json", out)
    # stress : coûts x2, retard, signaux manqués
    tid = reg.start_trial("P8-DIAG-STRESS", {"cost_mult": 2, "delay": 1, "missed": [0.05, 0.10, 0.20]}, "portefeuille 10", "dev", 2.0, purpose="diagnostic")
    for key, rule in HYP.items():
        ev = out["results"][key]
        rc = simulate(bars, fund, rule, st, START, END, **kw, cost_mult=2.0)
        rd = simulate(bars, fund, rule, st, START, END, **kw, delay=1)
        ev["stress"] = {"costs_x2_R": float(rc.trades.R.mean()) if len(rc.trades) else None, "costs_x2_final": float(rc.equity.iloc[-1]),
                        "delay1_R": float(rd.trades.R.mean()) if len(rd.trades) else None, "delay1_final": float(rd.equity.iloc[-1])}
        R = pd.read_csv(OUT / f"trades_{key}.csv")["R"].to_numpy()
        rng = np.random.default_rng(4)
        ev["missed_signals"] = {}
        for share in (0.05, 0.10, 0.20):
            means = [R[rng.random(len(R)) > share].mean() for _ in range(2000)]
            ev["missed_signals"][str(share)] = {"R_median": float(np.median(means)), "R_p05": float(np.percentile(means, 5))}
        print(key, "stress", ev["stress"], flush=True)
    reg.finish_trial(tid, status="done", result={k: v["stress"] for k, v in out["results"].items()})
    save("results.json", out)
    # bases aléatoires
    tid = reg.start_trial("P8-DIAG-RANDOM", {"reps": 1000}, "portefeuille 10", "dev", 1.0, purpose="diagnostic", seed=0)
    for key in HYP:
        t = pd.read_csv(OUT / f"trades_{key}.csv")
        if t.empty:
            continue
        dist, w = 0.0, 0
        for s, g in t.groupby("symbol"):
            d = random_R(bars[s], START, END, g.hours.to_numpy(), g.side.tolist(), st[s], 1000, seed=zlib.crc32(s.encode()) % 1000)
            dist = dist + d * len(g)
            w += len(g)
        dist = dist / w
        act = float((t.R + t.funding / t.risk_amt).mean())
        out["results"][key]["random"] = {"actual_R_ex_funding": act, "random_mean": float(np.nanmean(dist)),
                                         "random_p95": float(np.nanpercentile(dist, 95)), "percentile": float((dist < act).mean() * 100)}
    reg.finish_trial(tid, status="done", result={k: v.get("random") for k, v in out["results"].items()})
    # Holm, Sharpe déflaté, critères
    keys = list(HYP)
    ps = np.array([out["results"][k]["portfolio"].get("p_R_le_0", 1.0) for k in keys])
    order = np.argsort(ps)
    holm = np.empty(len(ps))
    run_max = 0.0
    for i, j in enumerate(order):
        run_max = max(run_max, min(1.0, (len(ps) - i) * ps[j]))
        holm[j] = run_max
    n_trials = reg.n_trials()
    var_sr = float(np.var(sharpes, ddof=1))
    for k, ph in zip(keys, holm):
        ev = out["results"][k]
        ev["p_holm"] = float(ph)
        dr = pd.read_csv(OUT / f"equity_daily_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0].pct_change().dropna()
        sr = dr.mean() / dr.std() if dr.std() > 0 else 0.0
        ev["dsr"] = deflated_sharpe(float(sr), len(dr), float(dr.skew()), float(dr.kurt() + 3), n_trials, var_sr)
        ev["dsr_inputs"] = {"sr_daily": float(sr), "n_trials_registry": n_trials, "var_sr_trials": var_sr}
        pm, sp, sa = ev["portfolio"], ev["subperiods"], ev["single_asset"]
        rep = [sa[s]["R_mean"] for s in S["universe"]["replication"]]
        c = {"C1": ph < 0.05,
             "C2": pm.get("R_ci95", [-1])[0] > 0,
             "C3": (ev["stress"]["costs_x2_R"] or -1) > 0 and (ev["stress"]["delay1_R"] or -1) > 0,
             "C4": sum((x["R_mean"] or -1) > 0 for x in ev["sensitivity"]) >= 3,
             "C5": all((v["R_mean"] or -1) > 0 for v in sp.values()),
             "C6": all((sa[s]["R_mean"] or -1) > 0 for s in S["universe"]["decision"]) and sum((x or -1) > 0 for x in rep) >= 6,
             "C7": pm["max_dd_pct"] < 10, "C8": ev["dsr"] > 0.95}
        ev["criteria"] = c
        ev["verdict"] = "candidate" if all(c.values()) else ("prometteur" if c["C2"] and c["C3"] and ph < 0.20 else "rejeté")
    out["registry_trials_total"] = reg.n_trials()
    # diagnostic 4 : Monte Carlo approfondi si candidate/prometteur, sinon constat
    tid = reg.start_trial("P8-DIAG-MC", {"n": 10000}, "portefeuille 10", "dev", 1.0, purpose="diagnostic", seed=1)
    mc = {}
    for k in keys:
        if out["results"][k]["verdict"] != "rejeté":
            dr = pd.read_csv(OUT / f"equity_daily_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0].pct_change().dropna()
            mc[k] = dd_mc(dr, n=10000, seed=9)
    out["montecarlo_10000"] = mc or "aucune hypothèse candidate ou prometteuse : Monte Carlo approfondi et analyse du levier non exécutés (pré-enregistré)"
    reg.finish_trial(tid, status="done", result={"ran": list(mc)})
    save("results.json", out)
    for k in keys:
        print(k, out["results"][k]["verdict"], out["results"][k]["criteria"], round(out["results"][k]["p_holm"], 4), round(out["results"][k]["dsr"], 3), flush=True)


if __name__ == "__main__":
    {"all": cmd_all}[sys.argv[1]]()
