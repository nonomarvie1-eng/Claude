"""Lanceur NEXUS G (allocation dynamique BTC / liquidités).

    python -m nexus.research.g_runner experiments/preregistration/batch_2d_01.toml
"""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import INITIAL_CAPITAL_EUR, PERIODS, RESULTS_DIR
from ..data.store import load_bars
from ..features.core import signal_frame
from ..portfolio.allocation import Costs, daily_frame, diff_test, episode_returns, metrics, simulate, weights
from ..stats.inference import benjamini_hochberg
from ..stats.metrics import market_attribution
from .lab import data_hash
from .registry import Registry, code_version
from .runner import expand_variants

EVAL_START = pd.Timestamp("2020-05-01", tz="UTC")
EPISODES = {"mars_2020_covid": ("2020-03-01", "2020-03-31"), "mai_2021": ("2021-05-08", "2021-05-31"),
            "juin_2022_luna_celsius": ("2022-05-01", "2022-06-30"), "nov_2022_ftx": ("2022-11-01", "2022-11-30"),
            "bear_2022": ("2021-11-10", "2022-11-21")}


def g_verdict(r: dict) -> str:
    t, t2 = r["vs_passive_same_expo"], r["vs_passive_same_expo_x2"]
    if t["ci95_ann_pct"][1] < 0:
        return "Résultats incompatibles avec une exploitation rentable"
    if (t["diff_ann_pct"] > 0 and r["p_bh"] < 0.25 and t2["diff_ann_pct"] > 0
            and r["net"]["max_dd_pct"] <= r["ref"]["passive_same_expo"]["max_dd_pct"]
            and r["net"]["sharpe"] >= r["ref"]["passive_same_expo"]["sharpe"]):
        return "Résultats prometteurs mais preuves insuffisantes"
    return "Absence d'avantage démontré"


def run(toml_path: str) -> list[dict]:
    spec = tomllib.loads(Path(toml_path).read_text())
    common = spec["common"]
    assert common["period"] == "dev"
    p0, p1 = PERIODS["dev"]
    reg = Registry()
    for fam, b in spec.get("budget", {}).items():
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for h in spec["hypothesis"]:
        reg.register_hypothesis({"key": h["key"], "family": h["family"], "statement": h["statement"], "rationale": h["rationale"],
                                 "params": h["params"], "data": {"period": "dev", "symbols": common["symbols"], "strategy": h["strategy"]},
                                 "metrics": common["metrics"], "rejection": {"text": common["rejection"]}})
    m1 = load_bars("BTCUSDT", p0, p1)
    h1 = load_bars("EURUSDT_1h", p0 - pd.Timedelta(days=5), p1)
    d = daily_frame(signal_frame(m1), h1)
    dh = data_hash(["BTCUSDT", "EURUSDT_1h"], range(p0.year, p1.year + 1))
    costs = Costs()
    ref_cache = {}

    def ref(w, rebalance="monthly", c=costs):
        key = (round(w, 6), rebalance, c.btc_fee)
        if key not in ref_cache:
            ref_cache[key] = simulate(d, weights(d, "CONST", w), EVAL_START, p1, costs=c, rebalance=rebalance)
        return ref_cache[key]

    btc_close = d["close"]
    bh = ref(1.0, "never")
    out_rows = []
    out_dir = RESULTS_DIR / Path(toml_path).stem
    out_dir.mkdir(parents=True, exist_ok=True)
    for h in spec["hypothesis"]:
        if not h["strategy"].startswith("G_"):
            continue
        for variant in expand_variants(h["params"]):
            w_max = variant["w_max"]
            tid = reg.start_trial(h["key"], variant, "BTCUSDT", "dev", 1.0, data_hash=dh, seed=0)
            tgt = weights(d, h["strategy"], w_max)
            net = simulate(d, tgt, EVAL_START, p1, costs=costs, w_max=w_max)
            gross = simulate(d, tgt, EVAL_START, p1, costs=costs.scaled(0.0), w_max=w_max)
            x2 = simulate(d, tgt, EVAL_START, p1, costs=costs.scaled(2.0), w_max=w_max)
            halt = simulate(d, tgt, EVAL_START, p1, costs=costs, w_max=w_max, global_halt=0.10)
            mn = metrics(net)
            avg_w = mn["avg_exposure_pct"] / 100
            bh_vol = metrics(bh)["ann_vol_pct"]
            w_vol = min(1.0, mn["ann_vol_pct"] / bh_vol) if bh_vol > 0 else avg_w
            refs = {"cash": {"final_eur": INITIAL_CAPITAL_EUR, "net_return_pct": 0.0, "max_dd_pct": 0.0, "sharpe": None},
                    "buy_hold": metrics(bh), "fixed_10pct": metrics(ref(0.10)), "fixed_25pct": metrics(ref(0.25)),
                    "passive_same_expo": metrics(ref(avg_w)), "passive_same_vol": metrics(ref(w_vol))}
            pse = ref(avg_w)
            pse_x2 = simulate(d, weights(d, "CONST", avg_w), EVAL_START, p1, costs=costs.scaled(2.0), rebalance="monthly")
            row = {"trial_id": tid, "hypothesis": h["key"], "strategy": h["strategy"], "variant": json.dumps(variant),
                   "w_max": w_max, "net": mn, "gross": metrics(gross), "cost_x2": metrics(x2), "with_global_halt": metrics(halt),
                   "ref": refs, "passive_same_expo_weight": avg_w, "passive_same_vol_weight": w_vol,
                   "vs_passive_same_expo": diff_test(net.values, pse.values, seed=tid),
                   "vs_passive_same_expo_x2": diff_test(x2.values, pse_x2.values, seed=tid),
                   "vs_passive_same_vol": diff_test(net.values, ref(w_vol).values, seed=tid),
                   "vs_fixed_same_cap": diff_test(net.values, ref(w_max).values, seed=tid),
                   "decomposition_pct": {
                       "exposition_btc (passif même expo)": refs["passive_same_expo"]["net_return_pct"],
                       "timing+dimensionnement (stratégie − passif même expo)": mn["net_return_pct"] - refs["passive_same_expo"]["net_return_pct"],
                       "frais (brut − net)": metrics(gross)["net_return_pct"] - mn["net_return_pct"],
                       "reduction_mecanique_dd (B&H − passif même expo, points de DD)": refs["buy_hold"]["max_dd_pct"] - refs["passive_same_expo"]["max_dd_pct"],
                   },
                   "attribution": market_attribution(net.values, btc_close),
                   "episodes_pct": episode_returns(net, EPISODES),
                   "episodes_passive_same_expo_pct": episode_returns(pse, EPISODES),
                   "annual_return_pct": {str(y): float((g.iloc[-1] / g.iloc[0] - 1) * 100) for y, g in net.values.groupby(net.values.index.year)},
                   }
            reg.finish_trial(tid, status="done", n_trades=net.n_trades, mean_r=row["vs_passive_same_expo"]["diff_ann_pct"],
                             p_value=row["vs_passive_same_expo"]["p"])
            out_rows.append(row)
            t = row["vs_passive_same_expo"]
            print(f"{h['key']} w_max={w_max:.2f} net {mn['net_return_pct']:+.1f}% DD {mn['max_dd_pct']:.1f}% Sh {mn['sharpe']:.2f} "
                  f"| passif même expo ({avg_w:.1%}) {refs['passive_same_expo']['net_return_pct']:+.1f}% DD {refs['passive_same_expo']['max_dd_pct']:.1f}% "
                  f"Sh {refs['passive_same_expo']['sharpe']:.2f} | Δ {t['diff_ann_pct']:+.2f}%/an {t['ci95_ann_pct']} p={t['p']:.3f}", flush=True)
    padj = benjamini_hochberg([r["vs_passive_same_expo"]["p"] for r in out_rows])
    for r, p in zip(out_rows, padj):
        r["p_bh"] = float(p)
        r["verdict"] = g_verdict(r)
        status = {"Résultats prometteurs mais preuves insuffisantes": "candidate"}.get(r["verdict"], "rejected")
        reg.set_status(r["hypothesis"], json.loads(r["variant"]), "BTCUSDT", status, r["verdict"], "", r["trial_id"])
    summary = {"code_version": code_version(), "registry_trials_total": reg.n_trials(), "eval_window": [str(EVAL_START), str(p1)],
               "buy_hold": metrics(bh), "rows": out_rows}
    (out_dir / "g_summary.json").write_text(json.dumps(summary, indent=2, default=str, ensure_ascii=False))
    for r in out_rows:
        print(r["hypothesis"], r["variant"], r["verdict"], "p_bh", round(r["p_bh"], 3))
    return out_rows


if __name__ == "__main__":
    run(sys.argv[1])
