"""Lot 6-01 : confirmation des signaux figés et étude du dimensionnement (période de développement).

    python -m nexus.research.p6_runner diag     # D0-D6
    python -m nexus.research.p6_runner sizing   # profils de risque et expositions fixes, Monte Carlo, Pareto
"""
from __future__ import annotations

import json
import sys
import tomllib

import numpy as np
import pandas as pd

from ..config import RESULTS_DIR, ROOT
from ..phase5 import data as p5d
from ..phase5 import ecb
from ..phase5.montecarlo import path_stats
from ..phase5.mr import random_entries, simulate
from ..stats.inference import block_bootstrap_mean
from .registry import Registry

TOML = ROOT / "experiments" / "preregistration" / "batch_6_01_confirmation.toml"
OUT = RESULTS_DIR / "batch_6_01_confirmation"
P5 = RESULTS_DIR / "batch_5_01_indices"
COST = 0.0003
JP = {"rule": {"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200, "exit_sma": 5}, "stop": 0.11,
      "window": ("1991-07-01", "2023-07-01"), "market": "Japan", "p5": "H5-04-RSI2-INTL_Japan"}
US = {"rule": {"kind": "rsi3050", "rsi_n": 5, "entry_th": 30, "exit_th": 50, "trend_sma": 200}, "stop": 0.06,
      "window": ("2010-01-01", "2023-07-01"), "market": "US", "p5": "H5-02-RSI3050_US"}


def T(x):
    x = pd.Timestamp(x)
    return x if x.tzinfo else x.tz_localize("UTC")


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def registry() -> Registry:
    reg, s = Registry(), tomllib.loads(TOML.read_text())
    for fam, b in s["budget"].items():
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for d in s["diagnostic"]:
        reg.register_hypothesis({"key": d["key"], "family": "P6-DIAG", "statement": d["statement"], "rationale": "Diagnostic du lot 6-01 (aucune règle modifiée).",
                                 "params": {}, "data": s["data"], "metrics": ["voir pré-enregistrement"], "rejection": {"text": d.get("decision", "diagnostic")}})
    for k in ("P6-SIZE-JAPAN", "P6-SIZE-US"):
        reg.register_hypothesis({"key": k, "family": "P6-SIZE", "statement": f"Étude de dimensionnement de la stratégie figée ({k[-5:].strip('-')}).",
                                 "rationale": "Le dimensionnement est distinct de la qualité du signal ; aucun profil n'est sélectionné par le rendement.",
                                 "params": s["sizing"], "data": {"period": "dev"}, "metrics": s["sizing"]["metrics"], "rejection": {"text": s["sizing"]["rule"]}})
    return reg


def run(df, cfg, start=None, end=None, fraction=None, **kw):
    a, b = cfg["window"]
    return simulate(df, cfg["rule"], T(start or a), T(end or b), stop=cfg["stop"], fraction=fraction if fraction is not None else 0.005 / cfg["stop"],
                    cost_side=COST, **kw)


def tstats(r: np.ndarray, dates) -> dict:
    months = pd.to_datetime(pd.Series(dates)).dt.strftime("%Y-%m").to_numpy()
    m, lo, hi, p = block_bootstrap_mean(np.asarray(r, float), months)
    return {"n": int(len(r)), "mean_pct": m * 100, "ci95_pct": [lo * 100, hi * 100], "p_le_0": p}


def random_test(df, cfg, t, start, end, n=10_000, stop=None, fin=0.025):
    if t.empty:
        return None
    dur = np.array([df.index.get_loc(x) - df.index.get_loc(y) for x, y in zip(t.exit_date, t.entry_date)])
    dist = random_entries(df, cfg["rule"], T(start), T(end), np.maximum(dur, 1), n, stop=stop if stop is not None else cfg["stop"],
                          cost_side=COST, fin_spread=fin, seed=7)
    act = float(t.ret_net.mean())
    return {"actual_pct": act * 100, "random_mean_pct": float(dist.mean() * 100), "p": float((np.sum(dist >= act) + 1) / (len(dist) + 1))}


# --------------------------------------------------------------------------- diagnostics
def cmd_diag():
    reg = registry()
    jp, us = p5d.load("Japan"), p5d.load("US")
    out = {}
    done = {k: json.loads(v) for k, v in reg.con.execute(
        "SELECT hypothesis_key, result_json FROM trials WHERE hypothesis_key LIKE 'P6-D%' AND status='done'").fetchall()}
    # D0 reproduction
    tid = None if "P6-D0-REPRO" in done else reg.start_trial("P6-D0-REPRO", {}, "Japan+US", "dev", 1.0, purpose="diagnostic")
    d0 = {}
    for name, df, cfg in (("Japan", jp, JP), ("US", us, US)):
        t_new = run(df, cfg).trades
        t_old = pd.read_csv(P5 / f"trades_{cfg['p5']}.csv")
        same = len(t_new) == len(t_old) and np.allclose(t_new.ret_net.to_numpy(), t_old.ret_net.to_numpy())
        d0[name] = {"n_trades": len(t_new), "identical_to_phase5": bool(same), "mean_ret_pct": float(t_new.ret_net.mean() * 100)}
    out["D0"] = d0
    if tid:
        reg.finish_trial(tid, status="done", result=d0)
    # D1 décomposition change / marché local (trades depuis 1999)
    uj = ecb.usdjpy()
    tid = None if "P6-D1-FX-DECOMP" in done else reg.start_trial("P6-D1-FX-DECOMP", {}, "Japan", "1999-2023H1", 1.0, purpose="diagnostic")
    t = run(jp, JP).trades
    t = t[pd.to_datetime(t.entry_date) >= uj.index.min()].copy()
    ujd = uj.reindex(uj.index.union(pd.to_datetime(t.entry_date)).union(pd.to_datetime(t.exit_date))).ffill()
    e, x = ujd.reindex(pd.to_datetime(t.entry_date)).to_numpy(), ujd.reindex(pd.to_datetime(t.exit_date)).to_numpy()
    fx = e / x - 1                                         # valeur du yen en USD
    local = (1 + t.ret_gross.to_numpy()) / (1 + fx) - 1
    d1 = {"n_trades_since_1999": int(len(t)), "usd_gross": tstats(t.ret_gross.to_numpy(), t.entry_date),
          "fx_component": tstats(fx, t.entry_date), "local_component": tstats(local, t.entry_date),
          "usd_net": tstats(t.ret_net.to_numpy(), t.entry_date)}
    d1["fx_share_of_mean_usd_gross"] = float(np.mean(fx) / np.mean(t.ret_gross)) if np.mean(t.ret_gross) != 0 else None
    loc, fxc = d1["local_component"], d1["fx_component"]
    d1["decision"] = ("avantage attribuable au marché japonais (composante locale > 0, change non significatif)"
                      if loc["ci95_pct"][0] > 0 and fxc["ci95_pct"][0] <= 0 else "non attribuable au seul marché local")
    out["D1"] = d1
    if tid:
        reg.finish_trial(tid, status="done", result=d1)
    # D2 indice reconstruit en JPY
    tid = reg.start_trial("P6-D2-JPY-INDEX", {}, "Japan-JPY", "1999-2023H1", 1.0, purpose="diagnostic")
    j = jp[jp.index >= uj.index.min()].copy()
    ujj = uj.reindex(uj.index.union(j.index)).ffill().reindex(j.index)
    fxd = ujj.shift(1) / ujj - 1
    loc_ret = ((1 + j["ret"]) / (1 + fxd) - 1).fillna(j["ret"])
    jl = pd.DataFrame({"ret": loc_ret, "rf": 0.0}, index=j.index)
    jl["close"] = 100 * np.cumprod(1 + jl["ret"].to_numpy())
    start2 = j.index[0] + pd.Timedelta(days=300)
    d2 = {}
    for lab, df in (("JPY (reconstruit)", jl), ("USD (French)", jp)):
        r = simulate(df, JP["rule"], start2, T("2023-07-01"), stop=JP["stop"], fraction=0.005 / JP["stop"], cost_side=COST)
        d2[lab] = {**tstats(r.trades.ret_net.to_numpy(), r.trades.entry_date), "win_rate": float((r.trades.ret_net > 0).mean()),
                   "random": random_test(df, JP, r.trades, start2, "2023-07-01")}
    # recouvrement des signaux
    rj = simulate(jl, JP["rule"], start2, T("2023-07-01"), stop=JP["stop"], fraction=0.05, cost_side=COST).trades
    ru = simulate(jp, JP["rule"], start2, T("2023-07-01"), stop=JP["stop"], fraction=0.05, cost_side=COST).trades
    d2["entries_in_common"] = int(len(set(pd.to_datetime(rj.entry_date)) & set(pd.to_datetime(ru.entry_date))))
    d2["start"] = str(start2.date())
    out["D2"] = d2
    reg.finish_trial(tid, status="done", result={k: v for k, v in d2.items() if isinstance(v, dict)})
    # D3 change seul
    tid = reg.start_trial("P6-D3-FX-ALONE", {}, "JPYUSD", "1999-2023H1", 1.0, purpose="diagnostic")
    fxdf = pd.DataFrame({"close": (1 / uj).to_numpy(), "rf": 0.0}, index=uj.index)
    r = simulate(fxdf, JP["rule"], fxdf.index[0] + pd.Timedelta(days=300), T("2023-07-01"), stop=JP["stop"], fraction=0.05, cost_side=0.0001, fin_spread=0.0)
    out["D3"] = {**tstats(r.trades.ret_net.to_numpy(), r.trades.entry_date), "win_rate": float((r.trades.ret_net > 0).mean()),
                 "note": "achat du yen contre dollar ; coût 0,01 %/côté, financement ignoré (différentiel de taux non modélisé)"}
    reg.finish_trial(tid, status="done", result=out["D3"])
    # D4 audit du stop
    tid = reg.start_trial("P6-D4-STOP-AUDIT", {}, "Japan+US", "dev", 1.0, purpose="diagnostic")
    d4 = {}
    for name, df, cfg in (("Japan", jp, JP), ("US", us, US)):
        tt = run(df, cfg).trades
        c = df["close"]
        mae = [float(c.loc[a:b].min() / c.loc[a] - 1) for a, b in zip(pd.to_datetime(tt.entry_date), pd.to_datetime(tt.exit_date))]
        st = tt[tt.reason == "stop"]
        d4[name] = {"stop_pct": cfg["stop"] * 100, "n_trades": len(tt), "n_stop_exits": len(st),
                    "stop_exit_returns_pct": [float(x * 100) for x in st.ret_gross],
                    "overshoot_beyond_stop_pct": [float((x + cfg["stop"]) * 100) for x in st.ret_gross],
                    "mae_close_pct_quantiles": {q: float(np.quantile(mae, q) * 100) for q in (0.5, 0.9, 0.95, 0.99)},
                    "trades_with_close_mae_beyond_half_stop": int(sum(m <= -cfg["stop"] / 2 for m in mae)),
                    "worst_close_mae_pct": float(min(mae) * 100)}
    out["D4"] = d4
    reg.finish_trial(tid, status="done", result=d4)
    # D5 stabilité US
    tid = reg.start_trial("P6-D5-US-STABILITY", {}, "US", "1930-2023H1", 1.0, purpose="diagnostic")
    d5 = {}
    for a, b in [(f"{y}-01-01", f"{y+10}-01-01") for y in range(1930, 2020, 10)] + [("2020-01-01", "2023-07-01"), ("1928-01-01", "1993-01-01"),
                                                                                   ("1993-01-01", "2010-01-01"), ("2010-01-01", "2023-07-01")]:
        tt = run(us, US, a, b).trades
        d5[f"{a[:4]}-{b[:4]}"] = {**tstats(tt.ret_net.to_numpy(), tt.entry_date), "win_rate": float((tt.ret_net > 0).mean()),
                                   "random": random_test(us, US, tt, a, b, n=2000)}
    out["D5"] = d5
    reg.finish_trial(tid, status="done", result={k: v["mean_pct"] for k, v in d5.items()})
    # D6 utilisation du capital et combinaison
    tid = reg.start_trial("P6-D6-COMBINED", {}, "Japan+US", "1991-2023H1", 1.0, purpose="diagnostic")
    a, b = "1991-07-01", "2023-07-01"
    rj, ru = run(jp, JP, a, b), run(us, US, a, b)
    idx = rj.equity.index.intersection(ru.equity.index)
    inj, inu = (rj.exposure.reindex(idx) > 0), (ru.exposure.reindex(idx) > 0)
    dj, du = rj.equity.reindex(idx).pct_change(), ru.equity.reindex(idx).pct_change()
    mj = rj.trades.assign(m=pd.to_datetime(rj.trades.exit_date).dt.to_period("M")).groupby("m").pnl.sum()
    mu = ru.trades.assign(m=pd.to_datetime(ru.trades.exit_date).dt.to_period("M")).groupby("m").pnl.sum()
    mm = pd.concat([mj, mu], axis=1, keys=["j", "u"]).fillna(0)
    up_j = (jp["close"] > jp["close"].rolling(200).mean()).reindex(idx)
    up_u = (us["close"] > us["close"].rolling(200).mean()).reindex(idx)
    d6 = {"days_invested_japan_pct": float(inj.mean() * 100), "days_invested_us_pct": float(inu.mean() * 100),
          "days_invested_either_pct": float((inj | inu).mean() * 100), "days_both_pct": float((inj & inu).mean() * 100),
          "days_above_sma200_japan_pct": float(up_j.mean() * 100), "days_above_sma200_us_pct": float(up_u.mean() * 100),
          "trades_per_year_japan": len(rj.trades) / 32, "trades_per_year_us": len(ru.trades) / 32,
          "corr_daily_strategy_returns": float(dj.corr(du)), "corr_monthly_pnl": float(mm.j.corr(mm.u)),
          "corr_monthly_pnl_when_either_loses": float(mm[(mm.j < 0) | (mm.u < 0)].corr().iloc[0, 1]),
          "corr_daily_index_returns": float(jp["ret"].reindex(idx).corr(us["ret"].reindex(idx))),
          "combined_nexus": {"final_eur": float(1000 + (rj.equity.iloc[-1] - 1000) + (ru.equity.iloc[-1] - 1000)),
                             "note": "somme des P&L à 0,5 % de risque chacun (approximation : expositions faibles, capital non partagé)"}}
    out["D6"] = d6
    reg.finish_trial(tid, status="done", result=d6)
    save("diagnostics.json", out)
    print(json.dumps(out, indent=1, default=str)[:6000])


# --------------------------------------------------------------------------- dimensionnement
def mc_dd(r, months, f, years, n=10_000, seed=3):
    rng = np.random.default_rng(seed)
    uniq, inv = np.unique(months, return_inverse=True)
    groups = [r[inv == g] for g in range(len(uniq))]
    tot, dd = np.empty(n), np.empty(n)
    for k in range(n):
        pick = rng.integers(0, len(groups), len(groups))
        tot[k], dd[k] = path_stats(np.concatenate([groups[g] for g in pick]), f)
    ann = (1 + tot) ** (1 / years) - 1
    return {"median_cagr_pct": float(np.median(ann) * 100), "p05_cagr_pct": float(np.percentile(ann, 5) * 100),
            "p95_dd_pct": float(np.percentile(dd, 95) * 100), **{f"p_dd_gt_{x}": float((dd > x / 100).mean()) for x in (10, 15, 20, 25)}}


def cmd_sizing():
    reg = registry()
    s = tomllib.loads(TOML.read_text())["sizing"]
    out = {}
    for name, df, cfg in (("Japan", p5d.load("Japan"), JP), ("US", p5d.load("US"), US)):
        tid = reg.start_trial(f"P6-SIZE-{name.upper()}", s, name, "dev", 1.0, purpose="sizing")
        a, b = cfg["window"]
        years = (T(b) - T(a)).days / 365.25
        prof = [(f"risque {x*100:g} %", min(x / cfg["stop"], 1.0)) for x in s["profiles_risk"]] + \
               [(f"exposition fixe {x*100:g} %", x) for x in s["diagnostic_fixed_exposure"]]
        rows = []
        for lab, f in prof:
            r = run(df, cfg, fraction=f)
            eq, t = r.equity, r.trades
            dr = eq.pct_change().dropna()
            dd = float((1 - eq / eq.cummax()).max() * 100)
            cagr = float(((eq.iloc[-1] / 1000) ** (1 / years) - 1) * 100)
            months = pd.to_datetime(t.entry_date).dt.strftime("%Y-%m").to_numpy()
            rows.append({"profil": lab, "fraction_notionnelle": f, "final_eur": float(eq.iloc[-1]), "cagr_pct": cagr, "max_dd_pct": dd,
                         "sharpe": float(dr.mean() / dr.std() * np.sqrt(252)), "calmar": cagr / dd if dd > 0 else None,
                         "expo_moy_pct": float(r.exposure.mean() * 100), "expo_max_pct": float(r.exposure.max() * 100),
                         "pire_trade_pct_capital": float(t.ret_net.min() * f * 100), "pire_jour_pct_capital": float(dr.min() * 100),
                         "frais_eur": float(t.fees.sum()), "financement_eur": float(t.financing.sum()),
                         "mc": mc_dd(t.ret_net.to_numpy(), months, f, years)})
        # frontière de Pareto : maximiser la médiane du CAGR simulé, minimiser le 95e percentile du DD
        for x in rows:
            x["pareto"] = not any((y["mc"]["median_cagr_pct"] >= x["mc"]["median_cagr_pct"] and y["mc"]["p95_dd_pct"] <= x["mc"]["p95_dd_pct"]
                                   and (y["mc"]["median_cagr_pct"] > x["mc"]["median_cagr_pct"] or y["mc"]["p95_dd_pct"] < x["mc"]["p95_dd_pct"])) for y in rows)
        out[name] = {"window": cfg["window"], "stop_pct": cfg["stop"] * 100, "rows": rows}
        reg.finish_trial(tid, status="done", result={x["profil"]: [x["cagr_pct"], x["max_dd_pct"]] for x in rows})
        for x in rows:
            print(name, x["profil"], round(x["cagr_pct"], 2), round(x["max_dd_pct"], 1), x["mc"], flush=True)
    save("sizing.json", out)


if __name__ == "__main__":
    {"diag": cmd_diag, "sizing": cmd_sizing}[sys.argv[1]]()
