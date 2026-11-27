"""Lot 5-01 : retour à la moyenne sur indices (données French) et gestion de l'exposition (P4-01 + lock).

    python -m nexus.research.p5_runner diag     # stops, reproduction des chiffres annoncés
    python -m nexus.research.p5_runner run      # 7 essais principaux (H5-01a … H5-04)
    python -m nexus.research.p5_runner sens     # grilles de perturbation (P5-SENS)
    python -m nexus.research.p5_runner exp      # H5-EXP (+ sensibilité)
    python -m nexus.research.p5_runner mc       # Monte Carlo (diagnostic)
"""
from __future__ import annotations

import itertools
import json
import sys
import tomllib

import numpy as np
import pandas as pd

from ..config import RESULTS_DIR, ROOT
from ..phase5 import data as p5d
from ..phase5 import montecarlo as mc
from ..phase5.mr import random_entries, random_same_exit, simulate
from ..portfolio.allocation import diff_test
from ..stats.inference import benjamini_hochberg, block_bootstrap_mean
from .registry import Registry

TOML = ROOT / "experiments" / "preregistration" / "batch_5_01_indices.toml"
OUT = RESULTS_DIR / "batch_5_01_indices"
RISK = 0.005
COST = 0.0003
N_RANDOM = 10_000
INTL = ["Europe", "Japan", "AsiaPacExJapan"]
INTL_SUB = [["1991-07-01", "2003-01-01"], ["2003-01-01", "2013-01-01"], ["2013-01-01", "2023-07-01"]]


def spec():
    return tomllib.loads(TOML.read_text())


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def load(name):
    return json.loads((OUT / name).read_text())


def registry() -> Registry:
    reg, s = Registry(), spec()
    for fam, b in s["budget"].items():
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for h in s["hypothesis"]:
        reg.register_hypothesis({k: h[k] for k in ("key", "family", "statement", "rationale", "params", "data", "metrics", "rejection")})
        reg.register_hypothesis({"key": h["key"] + "-SENS", "family": "P5-SENS", "statement": f"Grille de perturbation pré-déclarée de {h['key']}.",
                                 "rationale": "Robustesse ; jamais utilisée pour choisir.", "params": {"grid": h["grid"]},
                                 "data": h["data"], "metrics": ["part des configurations à rendement net moyen > 0"], "rejection": {"text": "C4"}})
    for key, st in (("P5-DIAG-STOPS", "Stops catastrophe : 3 × écart-type 5 séances avant 2010."),
                    ("P5-DIAG-REPRO", "Reproduction des chiffres annoncés (RSI 2, 1993-2009)."),
                    ("P5-DIAG-MC", "Procédure Monte Carlo du protocole 5-01 §6.")):
        reg.register_hypothesis({"key": key, "family": "P5-DIAG", "statement": st, "rationale": "Diagnostic du lot 5-01.", "params": {},
                                 "data": {"source": "French"}, "metrics": ["voir module"], "rejection": {"text": "diagnostic"}})
    return reg


def W(a, b):
    return pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")


def rule_of(h: dict, **over) -> dict:
    p = {**h["params"], **over}
    k = h["key"]
    if "RSI2" in k:
        return {"kind": "rsi2", "rsi_n": p["rsi_n"], "rsi_th": p["rsi_th"], "trend_sma": p["trend_sma"], "exit_sma": 5}
    if "RSI3050" in k:
        return {"kind": "rsi3050", "rsi_n": p["rsi_n"], "entry_th": p["entry_th"], "exit_th": p["exit_th"], "trend_sma": p["trend_sma"]}
    if "DOUBLE5" in k:
        return {"kind": "double", "n": p["n"], "trend_sma": p["trend_sma"]}
    raise ValueError(k)


def uses_stop(h):
    return h["params"].get("stop") != "none"


# --------------------------------------------------------------------------- diagnostics
def cmd_diag():
    reg = registry()
    tid = reg.start_trial("P5-DIAG-STOPS", spec()["stops"], "US+intl", "pre-2010", 1.0, purpose="diagnostic")
    stops = {}
    for m in ["US"] + INTL:
        df = p5d.load(m)
        a = "1950-01-01" if m == "US" else "1990-07-01"
        c = df["close"][(df.index >= pd.Timestamp(a, tz="UTC")) & (df.index < pd.Timestamp("2010-01-01", tz="UTC"))]
        r5 = np.log(c.iloc[::5]).diff().dropna()
        sd = float(r5.std())
        stops[m] = {"sd_5d_pct": sd * 100, "stop_pct": int(np.clip(round(3 * sd * 100), 5, 15))}
    save("stops.json", stops)
    reg.finish_trial(tid, status="done", result=stops)
    print(stops)
    # reproduction : RSI 2 d'origine, 1993-2009, notionnel 100 %, coûts 0,03 %/côté et 0
    tid = reg.start_trial("P5-DIAG-REPRO", {"window": spec()["windows"]["us_repro"]}, "US", "pre-dev", 1.0, purpose="diagnostic")
    df = p5d.load("US")
    a, b = W(*spec()["windows"]["us_repro"])
    out = {}
    for label, cost, fin in (("coûts NEXUS", COST, 0.025), ("sans coûts", 0.0, 0.0)):
        r = simulate(df, {"kind": "rsi2", "rsi_n": 2, "rsi_th": 10, "trend_sma": 200, "exit_sma": 5}, a, b, stop=None,
                     fraction=1.0, cost_side=cost, fin_spread=fin)
        t = r.trades
        gp, gl = t.loc[t.ret_net > 0, "ret_net"].sum(), -t.loc[t.ret_net < 0, "ret_net"].sum()
        out[label] = {"n_trades": len(t), "win_rate": float((t.ret_net > 0).mean()), "mean_ret_pct": float(t.ret_net.mean() * 100),
                      "profit_factor": float(gp / gl), "exposure_pct": float((r.exposure > 0).mean() * 100),
                      "growth_multiple": float(r.equity.iloc[-1] / 1000)}
    out["annonce_doc2"] = {"win_rate": 0.766, "mean_ret_pct": 0.63, "profit_factor": 2.98, "exposure_pct": 10.6,
                           "note": "SPY 1993 → fin des données de l'auteur (≈ 2026) ; notre fenêtre s'arrête à 2009 (période principale séparée)"}
    save("reproduction.json", out)
    reg.finish_trial(tid, status="done", result=out)
    print(json.dumps(out, indent=1))


# --------------------------------------------------------------------------- évaluation
def trade_stats(t: pd.DataFrame) -> dict:
    if t.empty:
        return {"n": 0}
    r = t["ret_net"].to_numpy()
    months = pd.to_datetime(t["entry_date"]).dt.strftime("%Y-%m").to_numpy()
    m, lo, hi, p = block_bootstrap_mean(r, months)
    gp, gl = r[r > 0].sum(), -r[r < 0].sum()
    return {"n": int(len(r)), "mean_ret_pct": m * 100, "ci95_pct": [lo * 100, hi * 100], "p_mean_le_0": p,
            "win_rate": float((r > 0).mean()), "avg_win_pct": float(r[r > 0].mean() * 100) if (r > 0).any() else None,
            "avg_loss_pct": float(r[r < 0].mean() * 100) if (r < 0).any() else None, "profit_factor": float(gp / gl) if gl > 0 else None,
            "worst_trade_pct": float(r.min() * 100), "best_trade_pct": float(r.max() * 100),
            "median_days": float((pd.to_datetime(t.exit_date) - pd.to_datetime(t.entry_date)).dt.days.median()),
            "by_reason": t["reason"].value_counts().to_dict()}


def equity_stats(eq: pd.Series, t: pd.DataFrame, initial=1000.0) -> dict:
    r = eq.pct_change().dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    return {"initial_eur": initial, "final_eur": float(eq.iloc[-1]), "pnl_eur": float(eq.iloc[-1] - initial),
            "total_return_pct": float((eq.iloc[-1] / initial - 1) * 100), "cagr_pct": float(((eq.iloc[-1] / initial) ** (1 / yrs) - 1) * 100),
            "max_dd_pct": float((1 - eq / eq.cummax()).max() * 100), "sharpe": float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else None,
            "fees_eur": float(t["fees"].sum()) if len(t) else 0.0, "financing_eur": float(t["financing"].sum()) if len(t) else 0.0}


def passive(df, a, b, expo):
    c = df["close"][(df.index >= a) & (df.index < b)]
    r = c.pct_change().fillna(0)
    return (1 + expo * r).cumprod() * 1000.0, float(c.iloc[-1] / c.iloc[0] - 1)


def evaluate(h: dict, market: str, df: pd.DataFrame, stops: dict, window, subwindows, hist=None, rule=None) -> dict:
    rule = rule or rule_of(h)
    s = stops[market]["stop_pct"] / 100
    stop = s if uses_stop(h) else None
    a, b = W(*window)
    f_nexus = RISK / s
    res = simulate(df, rule, a, b, stop=stop, fraction=f_nexus, cost_side=COST)
    t = res.trades
    ev = {"market": market, "window": window, "stop_pct": s * 100, "fraction_nexus": f_nexus, "rule": rule,
          "trades": trade_stats(t), "eur_nexus": equity_stats(res.equity, t),
          "exposure_time_pct": float((res.exposure > 0).mean() * 100), "avg_exposure": float(res.exposure.mean())}
    full = simulate(df, rule, a, b, stop=stop, fraction=1.0, cost_side=COST)
    ev["eur_full_notional"] = equity_stats(full.equity, full.trades)
    ev["eur_prudent"] = equity_stats(simulate(df, rule, a, b, stop=stop, fraction=0.0025 / s, cost_side=COST).equity, t)
    # références
    pas, bh = passive(df, a, b, ev["avg_exposure"])
    ev["alpha_vs_passive_same_exposure"] = diff_test(res.equity, pas)
    ev["buy_hold_return_pct"] = bh * 100
    trend = simulate(df, {"kind": "trend_only", "trend_sma": rule.get("trend_sma", 200)}, a, b, stop=None, fraction=1.0, cost_side=COST)
    ev["filter_only_sma_full"] = equity_stats(trend.equity, trend.trades)
    # entrées aléatoires (même régime, mêmes durées)
    if len(t):
        dur_idx = np.array([df.index.get_loc(x) - df.index.get_loc(y) for x, y in zip(t.exit_date, t.entry_date)])
        dist = random_entries(df, rule, a, b, np.maximum(dur_idx, 1), N_RANDOM, stop=stop, cost_side=COST, seed=7)
        act = float(t["ret_net"].mean())
        ev["random_entries"] = {"actual_mean_pct": act * 100, "random_mean_pct": float(dist.mean() * 100),
                                "random_p95_pct": float(np.percentile(dist, 95) * 100), "p": float((np.sum(dist >= act) + 1) / (len(dist) + 1))}
        same = random_same_exit(df, rule, a, b, len(t), 2000, stop=stop, cost_side=COST)
        ev["random_same_exit"] = {"win_rate": same["win_rate"], "mean_ret_pct": same["mean_ret"] * 100}
    # C3 : coûts x2, 0,20 %/côté, exécution à t+1
    ev["stress"] = {}
    for lab, kw in (("couts_x2", dict(cost_side=2 * COST, fin_spread=0.05)), ("cout_0.20pct", dict(cost_side=0.002)),
                    ("delai_t+1", dict(delay=1, cost_side=COST))):
        r2 = simulate(df, rule, a, b, stop=stop, fraction=f_nexus, **kw)
        ev["stress"][lab] = {"n": len(r2.trades), "mean_ret_pct": float(r2.trades.ret_net.mean() * 100) if len(r2.trades) else None}
    # C5 : sous-périodes et période historique
    ev["subperiods"] = {}
    for sa, sb in subwindows:
        r3 = simulate(df, rule, *W(sa, sb), stop=stop, fraction=f_nexus, cost_side=COST)
        ev["subperiods"][f"{sa[:4]}-{sb[:4]}"] = {"n": len(r3.trades), "mean_ret_pct": float(r3.trades.ret_net.mean() * 100) if len(r3.trades) else None}
    if hist:
        r4 = simulate(df, rule, *W(*hist), stop=stop, fraction=f_nexus, cost_side=COST)
        ev["hist"] = {"window": hist, **trade_stats(r4.trades)}
    ev["_trades"] = t
    return ev


def cmd_run():
    s, reg = spec(), registry()
    stops = load("stops.json")
    us = p5d.load("US")
    win = s["windows"]
    out, pvals = {}, {}
    for h in s["hypothesis"]:
        if h["key"] == "H5-EXP-DONCH-LOCK":
            continue
        markets = INTL if h["key"] == "H5-04-RSI2-INTL" else ["US"]
        for m in markets:
            tid = reg.start_trial(h["key"], {"market": m, **h["params"]}, m, "dev", 1.0, purpose="selection")
            if m == "US":
                ev = evaluate(h, m, us, stops, win["us_primary"], win["us_primary_subperiods"], hist=win["us_hist"])
                ev["repro_window"] = {"window": win["us_repro"], **trade_stats(simulate(us, rule_of(h), *W(*win["us_repro"]),
                                      stop=stops["US"]["stop_pct"] / 100 if uses_stop(h) else None, fraction=1.0, cost_side=COST).trades)}
            else:
                ev = evaluate(h, m, p5d.load(m), stops, win["intl"], INTL_SUB)
            t = ev.pop("_trades")
            name = f"{h['key']}_{m}"
            t.to_csv(OUT / f"trades_{name}.csv", index=False)
            pvals[name] = ev.get("random_entries", {}).get("p", 1.0)
            reg.finish_trial(tid, status="done", n_trades=len(t), mean_r=ev["trades"].get("mean_ret_pct"),
                             p_value=pvals[name], result={k: ev[k] for k in ("trades", "eur_nexus", "random_entries") if k in ev})
            out[name] = ev
            print(name, json.dumps({"trades": ev["trades"], "rand": ev.get("random_entries")}, default=str)[:600], flush=True)
    keys = list(pvals)
    for k, pa in zip(keys, benjamini_hochberg([pvals[k] for k in keys])):
        out[k]["p_bh"] = float(pa)
    out["_registry_trials_total"] = reg.n_trials()
    save("results.json", out)


# --------------------------------------------------------------------------- sensibilité
def cmd_sens():
    s, reg = spec(), registry()
    stops = load("stops.json")
    res = load("results.json")
    for h in s["hypothesis"]:
        if h["key"] == "H5-EXP-DONCH-LOCK":
            continue
        markets = INTL if h["key"] == "H5-04-RSI2-INTL" else ["US"]
        tid = reg.start_trial(h["key"] + "-SENS", {"grid": h["grid"]}, "+".join(markets), "dev", 1.0, purpose="sensitivity")
        keys, vals = zip(*h["grid"].items())
        rows = []
        for m in markets:
            df = p5d.load(m)
            w = s["windows"]["us_primary"] if m == "US" else s["windows"]["intl"]
            sp = stops[m]["stop_pct"] / 100
            for combo in itertools.product(*vals):
                over = dict(zip(keys, combo))
                r = simulate(df, rule_of(h, **over), *W(*w), stop=sp if uses_stop(h) else None, fraction=RISK / sp, cost_side=COST)
                rows.append({"market": m, **over, "n": len(r.trades), "mean_ret_pct": float(r.trades.ret_net.mean() * 100) if len(r.trades) else None})
        share = float(np.mean([(x["mean_ret_pct"] or -1) > 0 for x in rows]))
        reg.finish_trial(tid, status="done", result={"share_positive": share})
        for m in markets:
            res[f"{h['key']}_{m}"]["grid"] = {"rows": [x for x in rows if x["market"] == m],
                                               "share_positive": float(np.mean([(x["mean_ret_pct"] or -1) > 0 for x in rows if x["market"] == m]))}
        print(h["key"], share, flush=True)
    for k, ev in res.items():
        if k.startswith("_"):
            continue
        ev["criteria"] = criteria(k, ev)
        ev["verdict"] = verdict(ev)
    save("results.json", res)


def criteria(k: str, ev: dict) -> dict:
    tr = ev["trades"]
    st = ev["stress"]
    sub = [v["mean_ret_pct"] for v in ev["subperiods"].values()]
    c5 = sum((x or -1) > 0 for x in sub) >= 2
    if "hist" in ev:
        c5 = c5 and (ev["hist"].get("mean_ret_pct") or -1) > 0
    return {"C1": ev.get("p_bh", 1) < 0.05,
            "C2": tr.get("n", 0) > 0 and tr["mean_ret_pct"] > 0 and tr["ci95_pct"][0] > 0,
            "C3": all((st[x]["mean_ret_pct"] or -1) > 0 for x in ("couts_x2", "delai_t+1")),
            "C4": ev.get("grid", {}).get("share_positive", 0) >= 0.70,
            "C5": bool(c5), "C6": ev["eur_nexus"]["max_dd_pct"] < 10}


def verdict(ev: dict) -> str:
    c = ev["criteria"]
    if all(c.values()):
        return "candidate (Monte Carlo à confirmer)"
    if c["C2"] and c["C3"] and ev.get("p_bh", 1) < 0.20:
        return "prometteur"
    return "rejeté"


# --------------------------------------------------------------------------- Monte Carlo
def cmd_mc():
    reg = registry()
    res = load("results.json")
    stops = load("stops.json")
    tid = reg.start_trial("P5-DIAG-MC", {"n": 10_000}, "tous", "dev", 1.0, purpose="diagnostic", seed=0)
    out = {}
    for k, ev in res.items():
        if k.startswith("_"):
            continue
        t = pd.read_csv(OUT / f"trades_{k}.csv", parse_dates=["entry_date", "exit_date"])
        if len(t) < 5:
            continue
        r = t["ret_net"].to_numpy()
        months = t["entry_date"].dt.strftime("%Y-%m").to_numpy()
        o = {}
        for lab, f in (("nexus_0.5pct", ev["fraction_nexus"]), ("notionnel_100pct", 1.0)):
            o[lab] = {"shuffle": mc.shuffle(r, f), "block_bootstrap": mc.block_bootstrap(r, months, f),
                      "removal": {str(x): mc.removal(r, f, x) for x in (0.05, 0.10, 0.20)},
                      "concentration": mc.concentration(t, f)}
        # bruit ±0,1 % sur les clôtures servant aux signaux (200 tirages)
        h = next(x for x in spec()["hypothesis"] if k.startswith(x["key"]))
        m = ev["market"]
        df = p5d.load(m)
        a, b = W(*ev["window"])
        sp = stops[m]["stop_pct"] / 100
        rng = np.random.default_rng(11)
        noisy = []
        for _ in range(200):
            sc = df["close"] * (1 + rng.uniform(-0.001, 0.001, len(df)))
            rr = simulate(df, rule_of(h), a, b, stop=sp if uses_stop(h) else None, fraction=ev["fraction_nexus"], cost_side=COST, signal_close=sc)
            noisy.append(rr.trades.ret_net.mean() if len(rr.trades) else np.nan)
        noisy = np.array(noisy)
        o["noise_0.1pct"] = {"median_mean_ret_pct": float(np.nanmedian(noisy) * 100), "p05_mean_ret_pct": float(np.nanpercentile(noisy, 5) * 100),
                             "share_positive": float(np.nanmean(noisy > 0))}
        # régimes : tercile de volatilité réalisée 20 j à l'entrée ; décennie
        vol = np.log(df["close"]).diff().rolling(20).std()
        t["vol"] = vol.reindex(t["entry_date"]).to_numpy()
        q = pd.qcut(t["vol"], 3, labels=["basse", "moyenne", "haute"])
        o["regimes_vol"] = {str(g): {"n": int(len(x)), "mean_ret_pct": float(x.ret_net.mean() * 100)} for g, x in t.groupby(q, observed=True)}
        o["regimes_year"] = {str(g): {"n": int(len(x)), "mean_ret_pct": float(x.ret_net.mean() * 100)} for g, x in t.groupby(t.entry_date.dt.year)}
        out[k] = o
        c = o["nexus_0.5pct"]
        mc_ok = (c["block_bootstrap"]["p05_return_pct"] > 0 and c["removal"]["0.2"]["median_return_pct"] > 0
                 and c["concentration"]["without_best_trade_pct"] > 0 and c["concentration"]["without_best_year_pct"] > 0)
        ev["montecarlo_pass"] = bool(mc_ok)
        if ev.get("verdict", "").startswith("candidate"):
            ev["verdict"] = "candidate" if mc_ok else ("prometteur (échec Monte Carlo)" if ev["criteria"]["C2"] else "rejeté")
        print(k, json.dumps(c["block_bootstrap"]), flush=True)
    reg.finish_trial(tid, status="done", result={k: v["nexus_0.5pct"]["block_bootstrap"] for k, v in out.items()})
    save("montecarlo.json", out)
    save("results.json", res)


# --------------------------------------------------------------------------- H5-EXP (crypto)
def cmd_exp():
    from . import p4_runner as p4
    from ..config import DEV
    from ..phase4.sim import SPOT
    from ..phase4.sim import simulate as sim4
    s, reg = spec(), registry()
    h = next(x for x in s["hypothesis"] if x["key"] == "H5-EXP-DONCH-LOCK")
    stops4 = p4.load("stops.json")
    a = p4.assets()
    st = {k: stops4[k]["stop_pct"] / 100 for k in a}
    bask = p4.basket(a, *DEV, SPOT)
    rule = {"kind": "donch", "entry_n": 55, "exit_n": 20}

    def tiers(frac):
        return [(x, x * frac) for x in h["params"]["tiers_at"]]

    def run(tr=None, cost_mult=1.0):
        return sim4(a, rule, st, start=DEV[0], end=DEV[1], risk=0.005, costs=SPOT, cost_mult=cost_mult, initial=1000.0, tiers=tr)

    base = run()                                                   # reproduction technique de P4-01 (non journalisée : budget P4 épuisé)
    tid = reg.start_trial(h["key"], h["params"], "univers P4", "dev", 1.0, purpose="selection")
    lock = run(tiers(h["params"]["lock_fraction"]))
    out = {}
    for lab, r in (("P4-01 original", base), ("P4-01 + lock 1/2", lock)):
        ev = p4.evaluate(r, bask, vs_cash=False)
        t = r.trades
        pnl = t["pnl"]
        yr = pd.to_datetime(t["entry_ts"]).dt.year
        ev["concentration"] = {"best_trade_pnl": float(pnl.max()), "total_pnl": float(pnl.sum()),
                               "best_trade_share": float(pnl.max() / pnl.sum()) if pnl.sum() > 0 else None,
                               "pnl_without_best_trade": float(pnl.sum() - pnl.max()),
                               "pnl_by_entry_year": {int(y): float(g.sum()) for y, g in pnl.groupby(yr)},
                               "pnl_without_2021": float(pnl[yr != 2021].sum()),
                               "pnl_without_MATIC": float(pnl[t.symbol != "MATICUSDT"].sum())}
        ev["equity_peak"] = float(r.equity.max())
        ev["equity_peak_date"] = str(r.equity.idxmax().date())
        ev["giveback_from_peak_pct"] = float((1 - r.equity.iloc[-1] / r.equity.max()) * 100)
        out[lab] = ev
    reg.finish_trial(tid, status="done", n_trades=len(lock.trades), mean_r=out["P4-01 + lock 1/2"]["trade_R"]["mean"],
                     p_value=out["P4-01 + lock 1/2"]["primary"]["p"], result={"primary": out["P4-01 + lock 1/2"]["primary"]})
    # sensibilité (1 essai P5-SENS) : fractions 1/3, 2/3 et coûts x2
    tid2 = reg.start_trial(h["key"] + "-SENS", {"lock_fraction": [0.33, 0.67], "cost_x2": True}, "univers P4", "dev", 2.0, purpose="sensitivity")
    sens = {}
    for lab, r in (("lock 1/3", run(tiers(0.33))), ("lock 2/3", run(tiers(0.67))), ("lock 1/2 coûts x2", run(tiers(0.5), 2.0))):
        e = p4.evaluate(r, bask, vs_cash=False)
        sens[lab] = {"primary": e["primary"], "trade_R": e.get("trade_R"), "perf_usdt": e["perf_usdt"]}
    reg.finish_trial(tid2, status="done", result={k: v["primary"] for k, v in sens.items()})
    ev = out["P4-01 + lock 1/2"]
    ev["sensitivity"] = sens
    c = {"C1": ev["primary"]["p"] < 0.05 and ev["primary"]["diff_ann_pct"] > 0,
         "C2": ev["trade_R"]["ci95"][0] > 0, "C3": sens["lock 1/2 coûts x2"]["trade_R"]["mean"] > 0,
         "C4": all(v["primary"]["diff_ann_pct"] > 0 for k, v in sens.items() if k.startswith("lock 1/3") or k.startswith("lock 2/3")),
         "C5": sum(v > 0 for v in ev["subperiods"].values()) >= 3, "C6": ev["perf_usdt"]["max_dd_pct"] < 10}
    ev["criteria"] = c
    ev["verdict"] = "candidate" if all(c.values()) else ("prometteur" if c["C2"] and c["C3"] and ev["primary"]["p"] < 0.20 else "rejeté")
    lock.trades.to_csv(OUT / "trades_H5-EXP.csv", index=False)
    pd.DataFrame({"original": base.equity, "lock": lock.equity, "expo_original": base.exposure, "expo_lock": lock.exposure}).to_csv(OUT / "equity_H5-EXP.csv")
    out["_registry_trials_total"] = reg.n_trials()
    save("h5_exp.json", out)
    print(json.dumps({k: {"perf": v["perf_usdt"], "primary": v["primary"], "conc": v["concentration"]} for k, v in out.items() if not k.startswith("_")}, default=str, indent=1))


if __name__ == "__main__":
    {"diag": cmd_diag, "run": cmd_run, "sens": cmd_sens, "mc": cmd_mc, "exp": cmd_exp}[sys.argv[1]]()
