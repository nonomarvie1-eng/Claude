"""Lot 4-01 : stratégies compatibles Cubrik (période de développement uniquement).

    python -m nexus.research.p4_runner universe   # classement T4 2019 -> univers figé
    python -m nexus.research.p4_runner data       # H1 2019-01 -> 2023-06 + financement
    python -m nexus.research.p4_runner stops      # stops % depuis l'ATR du S2 2019
    python -m nexus.research.p4_runner run        # 4 essais principaux + sensibilité + coûts x2
    python -m nexus.research.p4_runner random     # bases aléatoires (diagnostic)
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
from ..phase4.sim import PERP, SPOT, AssetData, atr_pct, random_trades_R, simulate
from ..portfolio.allocation import diff_test
from ..stats.inference import benjamini_hochberg, block_bootstrap_mean, week_groups
from .registry import Registry

TOML = ROOT / "experiments" / "preregistration" / "batch_4_01_cubrik.toml"
OUT = RESULTS_DIR / "batch_4_01_cubrik"
STABLE = {"USDCUSDT", "TUSDUSDT", "PAXUSDT", "BUSDUSDT", "USDSUSDT", "USDSBUSDT"}
RULES = {"P4-01-DONCH": "donch", "P4-02-SMA": "sma", "P4-03-TSMOM-LS": "tsmom", "P4-04-RSI2": "rsi2"}
SUBPERIODS = {"2020": ("2020-01-01", "2021-01-01"), "2021": ("2021-01-01", "2022-01-01"),
              "2022": ("2022-01-01", "2023-01-01"), "2023S1": ("2023-01-01", "2023-07-01")}


def spec():
    return tomllib.loads(TOML.read_text())


def registry() -> Registry:
    reg, s = Registry(), spec()
    for fam, b in s["budget"].items():
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for h in s["hypothesis"]:
        reg.register_hypothesis({k: h[k] for k in ("key", "family", "statement", "rationale", "params", "data", "metrics", "rejection")})
        reg.register_hypothesis({"key": h["key"] + "-SENS", "family": "P4-SENS",
                                 "statement": f"Voisins de sensibilité pré-déclarés et stress de coûts de {h['key']}.",
                                 "rationale": "Robustesse ; jamais utilisé pour choisir des paramètres.",
                                 "params": {"sensitivity": h["sensitivity"], "cost_multiplier": 2.0},
                                 "data": h["data"], "metrics": h["metrics"], "rejection": {"text": "critères C3, C4"}})
    for key, st in (("P4-DIAG-UNIVERSE", "Univers : 10 paires USDT au plus fort volume d'oct.–déc. 2019."),
                    ("P4-DIAG-STOPS", "Stops % par actif : 3 × médiane ATR14/clôture D1 du S2 2019."),
                    ("P4-DIAG-RANDOM", "Bases aléatoires : entrées tirées au hasard, même nombre, durée et sens.")):
        reg.register_hypothesis({"key": key, "family": "P4-DIAG", "statement": st, "rationale": "Diagnostic du lot 4-01.",
                                 "params": {}, "data": {"period": "2019 / dev"}, "metrics": ["voir module"],
                                 "rejection": {"text": "diagnostic"}})
    return reg


def save(name: str, obj) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def load(name: str):
    return json.loads((OUT / name).read_text())


# --------------------------------------------------------------------------- univers
def cmd_universe():
    s, reg = spec(), registry()
    u = s["universe"]
    tid = reg.start_trial("P4-DIAG-UNIVERSE", {"window": u["rank_window"]}, "candidats", "2019Q4", 1.0, purpose="diagnostic")
    rows = []
    for sym in u["candidates"]:
        if sym in STABLE:
            continue
        p4d.download_spot(sym, "2019-10", "2020-01", "1d")
        d = p4d.read_spot(sym, "1d", "2019-10", "2020-01")
        rows.append({"symbol": sym, "days": len(d), "quote_volume_usdt": float(d["quote_volume"].sum()) if len(d) else 0.0})
    df = pd.DataFrame(rows).sort_values("quote_volume_usdt", ascending=False).reset_index(drop=True)
    chosen = df[df["days"] >= 80]["symbol"].head(u["size"]).tolist()
    save("universe.json", {"ranking": df.to_dict("records"), "universe": chosen})
    reg.finish_trial(tid, status="done", n_trades=len(chosen), result={"universe": chosen})
    print(df.head(15).to_string(), "\nunivers :", chosen)


# --------------------------------------------------------------------------- données
def cmd_data():
    uni = load("universe.json")["universe"]
    rep = {}
    for sym in uni:
        r1 = p4d.download_spot(sym, "2019-01", p4d.LAST_MONTH, "1h")
        rf = p4d.download_funding(sym, "2019-09", p4d.LAST_MONTH)
        n = p4d.store_h1(sym)
        f = p4d.read_funding(sym, "2019-09", p4d.LAST_MONTH)
        rep[sym] = {"h1_months": r1["months"], "h1_missing": r1["missing"], "h1_rows": n,
                    "funding_first": str(f["ts"].min()) if len(f) else None, "funding_rows": len(f),
                    "funding_missing_months": rf["missing"]}
        print(sym, rep[sym], flush=True)
    save("data_report.json", rep)


def assets(with_funding=False) -> dict[str, AssetData]:
    out = {}
    for sym in load("universe.json")["universe"]:
        h1 = p4d.load_h1(sym)
        fund = None
        if with_funding:
            f = p4d.read_funding(sym, "2019-09", p4d.LAST_MONTH)
            fund = f.set_index("ts")["rate"] if len(f) else None
        out[sym] = AssetData(h1=h1, d1=p4d.daily_from_h1(h1), funding=fund)
    return out


def perp_assets(a: dict[str, AssetData]) -> dict[str, AssetData]:
    """Un actif n'est négociable en perpétuel qu'à partir de sa première échéance de financement."""
    out = {}
    for s, x in a.items():
        if x.funding is None or not len(x.funding):
            continue
        first = x.funding.index.min()
        out[s] = AssetData(h1=x.h1[x.h1["ts"] >= first].reset_index(drop=True), d1=x.d1, funding=x.funding)
    return out


# --------------------------------------------------------------------------- stops
def cmd_stops():
    s, reg = spec(), registry()
    st = s["stops"]
    tid = reg.start_trial("P4-DIAG-STOPS", st, "univers", "2019H2", 1.0, purpose="diagnostic")
    a0, a1 = (pd.Timestamp(x, tz="UTC") for x in st["window"])
    stops = {}
    for sym, a in assets().items():
        ap = atr_pct(a.d1)
        m = float(ap[(ap.index >= a0) & (ap.index < a1)].median())
        pct = int(np.clip(round(st["atr_mult"] * m * 100), st["floor_pct"], st["cap_pct"]))
        stops[sym] = {"median_atr_pct": m * 100, "stop_pct": pct}
    save("stops.json", stops)
    reg.finish_trial(tid, status="done", result=stops)
    print(pd.DataFrame(stops).T.to_string())


# --------------------------------------------------------------------------- évaluation
def basket(a: dict[str, AssetData], start, end, costs) -> pd.Series:
    """Panier équipondéré acheté au départ et conservé (coûts d'entrée et de sortie inclus)."""
    days = pd.date_range(start, end, freq="1D", inclusive="left")
    vals = []
    for s, x in a.items():
        c = x.d1["c"].reindex(days).ffill()
        o0 = x.d1["o"].reindex(days).bfill().iloc[0]
        vals.append(c / (o0 * (1 + costs.slip)) * (1 - costs.fee))
    v = pd.concat(vals, axis=1).mean(axis=1)
    v.iloc[-1] *= (1 - costs.fee) * (1 - costs.slip)
    return v


def eur_curve(eq_usdt: pd.Series, initial_eur: float = 1000.0, conv: float = 0.001) -> pd.Series:
    r = p4d.load_bars("EURUSDT_1h", eq_usdt.index[0] - pd.Timedelta(days=7), eq_usdt.index[-1] + pd.Timedelta(days=1))
    rate = r.set_index("ts")["c"].resample("1D").last().reindex(eq_usdt.index).ffill().bfill()
    usdt0 = initial_eur * rate.iloc[0] * (1 - conv)
    return eq_usdt / eq_usdt.iloc[0] * usdt0 / rate * (1 - conv)


def perf(eq: pd.Series, trades: pd.DataFrame) -> dict:
    r = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    dd = (eq / eq.cummax() - 1).min()
    gp = trades.loc[trades["pnl"] > 0, "pnl"].sum() if len(trades) else 0.0
    gl = -trades.loc[trades["pnl"] < 0, "pnl"].sum() if len(trades) else 0.0
    return {"final": float(eq.iloc[-1]), "total_return_pct": float((eq.iloc[-1] / eq.iloc[0] - 1) * 100),
            "cagr_pct": float(((eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1) * 100),
            "max_dd_pct": float(-dd * 100), "sharpe": float(r.mean() / r.std() * np.sqrt(365)) if r.std() > 0 else None,
            "profit_factor": float(gp / gl) if gl > 0 else None, "n_trades": int(len(trades)),
            "win_rate": float((trades["pnl"] > 0).mean()) if len(trades) else None}


def evaluate(res, bask: pd.Series, *, vs_cash: bool) -> dict:
    t = res.trades
    out = {"perf_usdt": perf(res.equity, t), "avg_exposure": float(res.exposure.mean()), "info": res.info}
    if len(t):
        m, lo, hi, p = block_bootstrap_mean(t["R"].to_numpy(), week_groups(pd.to_datetime(t["entry_ts"])))
        out["trade_R"] = {"mean": m, "ci95": [lo, hi], "p": p}
        out["by_side"] = {sd: {"n": int((t["side"] == sd).sum()), "mean_R": float(t.loc[t["side"] == sd, "R"].mean())}
                          for sd in t["side"].unique()}
        out["by_symbol"] = {s: {"n": int(len(g)), "mean_R": float(g["R"].mean()), "pnl": float(g["pnl"].sum())}
                            for s, g in t.groupby("symbol")}
        out["by_reason"] = t["reason"].value_counts().to_dict()
        out["funding_total"] = float(t["funding"].sum())
        out["fees_total"] = float(t["fees"].sum())
    br = bask.pct_change().fillna(0)
    e = out["avg_exposure"]
    passive = (1 + e * br).cumprod() * res.equity.iloc[0]
    ref = pd.Series(res.equity.iloc[0], index=res.equity.index) if vs_cash else passive
    out["primary"] = diff_test(res.equity, ref)
    out["primary"]["benchmark"] = "trésorerie (0)" if vs_cash else f"panier passif × exposition moyenne {e:.3f}"
    sr = res.equity.pct_change().dropna()
    bb = br.reindex(sr.index)
    out["beta_vs_basket"] = float(np.cov(sr, bb)[0, 1] / bb.var()) if bb.var() > 0 else None
    out["subperiods"] = {}
    for k, (a, b) in SUBPERIODS.items():
        m = (sr.index >= pd.Timestamp(a, tz="UTC")) & (sr.index < pd.Timestamp(b, tz="UTC"))
        refr = 0.0 if vs_cash else (e * bb[m])
        out["subperiods"][k] = float((sr[m] - refr).mean() * 365 * 100)
    return out


def run_one(reg, key, variant, a, stops, *, perp, cost_mult=1.0, purpose="selection", rules_mode=False, risk=0.005,
            stop_mult=1.0, log=True):
    start, end = DEV
    rule = {"kind": RULES[key.replace("-SENS", "")], **{k: v for k, v in variant.items() if k != "stop_mult"}}
    tid = reg.start_trial(key, variant, "univers", "dev", cost_mult, purpose=purpose) if log else None
    res = simulate(a, rule, {s: stops[s]["stop_pct"] / 100 for s in a}, start=start, end=end, risk=risk,
                   costs=PERP if perp else SPOT, cost_mult=cost_mult, initial=1000.0, rules_mode=rules_mode,
                   stop_mult=variant.get("stop_mult", stop_mult))
    return tid, res


def cmd_run():
    s, reg = spec(), registry()
    stops = load("stops.json")
    a_spot = assets(with_funding=True)
    a_perp = perp_assets(a_spot)
    start, end = DEV
    bask = basket(a_spot, start, end, SPOT)
    out = {"universe": list(a_spot), "perp_universe": list(a_perp), "stops": stops, "results": {}}
    pvals = {}
    for h in s["hypothesis"]:
        key, perp = h["key"], h["params"]["market"] == "perp"
        a = a_perp if perp else a_spot
        base = {k: v for k, v in h["params"].items() if k not in ("side", "market")}
        tid, res = run_one(reg, key, base, a, stops, perp=perp)
        ev = evaluate(res, bask, vs_cash=perp)
        eq_eur = eur_curve(res.equity)
        ev["perf_eur"] = perf(eq_eur, res.trades)
        # vue en euros avec les règles de risque (2 %/jour, arrêt 10 %) et au profil prudent : même essai
        _, rr = run_one(reg, key, base, a, stops, perp=perp, rules_mode=True, log=False)
        ev["perf_eur_rules"] = {**perf(eur_curve(rr.equity), rr.trades), "info": rr.info}
        _, rp = run_one(reg, key, base, a, stops, perp=perp, risk=0.0025, log=False)
        ev["perf_eur_prudent"] = perf(eur_curve(rp.equity), rp.trades)
        reg.finish_trial(tid, status="done", n_trades=len(res.trades), mean_r=ev.get("trade_R", {}).get("mean"),
                         p_value=ev["primary"]["p"], result={k: ev[k] for k in ("primary", "perf_usdt", "avg_exposure")})
        res.trades.to_csv(OUT / f"trades_{key}.csv", index=False)
        pd.DataFrame({"usdt": res.equity, "eur": eq_eur, "exposure": res.exposure}).to_csv(OUT / f"equity_{key}.csv")
        pvals[key] = ev["primary"]["p"]
        # ---- sensibilité et coûts x2 (famille P4-SENS)
        ev["sensitivity"] = []
        for v in h["sensitivity"]:
            var = {**base, **v}
            tid2, r2 = run_one(reg, key + "-SENS", var, a, stops, perp=perp, purpose="sensitivity")
            e2 = evaluate(r2, bask, vs_cash=perp)
            reg.finish_trial(tid2, status="done", n_trades=len(r2.trades), mean_r=e2.get("trade_R", {}).get("mean"),
                             p_value=e2["primary"]["p"], result={"primary": e2["primary"]})
            ev["sensitivity"].append({"variant": v, "primary": e2["primary"], "trade_R": e2.get("trade_R"),
                                      "perf_usdt": e2["perf_usdt"]})
        tid3, r3 = run_one(reg, key + "-SENS", base, a, stops, perp=perp, cost_mult=2.0, purpose="cost_stress")
        e3 = evaluate(r3, bask, vs_cash=perp)
        reg.finish_trial(tid3, status="done", n_trades=len(r3.trades), mean_r=e3.get("trade_R", {}).get("mean"),
                         p_value=e3["primary"]["p"], result={"primary": e3["primary"]})
        ev["cost_x2"] = {"trade_R": e3.get("trade_R"), "primary": e3["primary"], "perf_usdt": e3["perf_usdt"]}
        out["results"][key] = ev
        print(key, json.dumps({"primary": ev["primary"], "R": ev.get("trade_R"), "perf": ev["perf_usdt"]}, default=str), flush=True)
    keys = list(pvals)
    adj = benjamini_hochberg([pvals[k] for k in keys])
    for k, pa in zip(keys, adj):
        ev = out["results"][k]
        ev["p_bh"] = float(pa)
        ev["criteria"] = criteria(ev)
        ev["verdict"] = verdict(ev)
        reg.set_status(k, {}, "univers", {"candidate": "candidate", "prometteur": "insufficient", "rejeté": "rejected"}[ev["verdict"]],
                       ev["verdict"], json.dumps(ev["criteria"]))
    out["benchmark_basket"] = perf(bask * 1000, pd.DataFrame(columns=["pnl"]))
    out["benchmark_basket_eur"] = perf(eur_curve(bask * 1000), pd.DataFrame(columns=["pnl"]))
    out["registry_trials_total"] = reg.n_trials()
    save("results.json", out)


def criteria(ev: dict) -> dict:
    tr, sens = ev.get("trade_R") or {}, ev["sensitivity"]
    c = {"C1": ev["primary"]["diff_ann_pct"] > 0 and ev["p_bh"] < 0.05,
         "C2": bool(tr) and tr["mean"] > 0 and tr["ci95"][0] > 0,
         "C3": bool(ev["cost_x2"]["trade_R"]) and ev["cost_x2"]["trade_R"]["mean"] > 0,
         "C4": sum(x["primary"]["diff_ann_pct"] > 0 for x in sens) >= 3,
         "C5": sum(v > 0 for v in ev["subperiods"].values()) >= 3,
         "C6": ev["perf_usdt"]["max_dd_pct"] < 10}
    return c


def verdict(ev: dict) -> str:
    c = ev["criteria"]
    if all(c.values()):
        return "candidate"
    if c["C2"] and c["C3"] and ev["p_bh"] < 0.20:
        return "prometteur"
    return "rejeté"


def cmd_random():
    reg = registry()
    res = load("results.json")
    stops = load("stops.json")
    a_spot = assets(with_funding=True)
    start, end = DEV
    tid = reg.start_trial("P4-DIAG-RANDOM", {"reps": 200}, "univers", "dev", 1.0, purpose="diagnostic", seed=0)
    out = {}
    for key in RULES:
        t = pd.read_csv(OUT / f"trades_{key}.csv", parse_dates=["entry_ts", "exit_ts"])
        if t.empty:
            continue
        costs = PERP if key == "P4-03-TSMOM-LS" else SPOT
        means = []
        for sym, g in t.groupby("symbol"):
            dur = np.maximum(((g["exit_ts"] - g["entry_ts"]).dt.total_seconds() / 86400).round().astype(int), 1)
            m = random_trades_R(a_spot[sym], start, end, dur.to_numpy(), g["side"].tolist(), stops[sym]["stop_pct"] / 100,
                                costs, 200, seed=zlib.crc32(sym.encode()))
            means.append((m, len(g)))
        w = np.array([n for _, n in means], float)
        dist = sum(m * n for m, n in means) / w.sum()
        actual = float(t["R_ex_funding"].mean())
        out[key] = {"actual_mean_R_ex_funding": actual, "random_mean": float(np.nanmean(dist)),
                    "random_p95": float(np.nanpercentile(dist, 95)), "percentile_of_actual": float((dist < actual).mean() * 100)}
        print(key, out[key], flush=True)
    reg.finish_trial(tid, status="done", result=out)
    res["random_baseline"] = out
    save("results.json", res)


if __name__ == "__main__":
    {"universe": cmd_universe, "data": cmd_data, "stops": cmd_stops, "run": cmd_run, "random": cmd_random}[sys.argv[1]]()
