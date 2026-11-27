"""Lanceur des familles à horizon long (H1, H4, D1) : NEXUS C, F, D et références.

    python -m nexus.research.lab_runner experiments/preregistration/batch_2c_01.toml

Pour chaque essai, trois niveaux de lecture strictement séparés :
 1. qualité intrinsèque des signaux, en R (profil statistique 0,5 %, sans arrêt) ;
 2. simulation du capital avec les règles de risque mais SANS arrêt à 10 % (analytique) ;
 3. simulation avec arrêt automatique (règle du futur bot), et date de l'arrêt.
Les diagnostics sans arrêt ne modifient en rien les règles de sécurité du bot.
"""
from __future__ import annotations

import argparse
import json
import time
import tomllib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import INITIAL_CAPITAL_EUR, PERIODS, RESULTS_DIR, RISK_PROFILES
from ..engine.backtest import run_backtest
from ..engine.execution import ExecFrame
from ..features.core import resample, signal_frame
from ..features.regime import daily_regimes, regime_at
from ..instruments import SPECS
from ..stats.inference import benjamini_hochberg, block_bootstrap_mean
from ..stats.metrics import (daily_sharpe_ci, exposure_stats, market_attribution, passive_benchmarks,
                             summarize)
from ..strategies import trend
from ..strategies.random_baseline import exposure_matched_random
from .lab import data_hash, overfit_flags, walk_forward_selection
from .registry import Registry, code_version
from .runner import STAT_PROFILE, expand_variants, fold_means, load_inputs, mc_drawdown

STRATS = {
    "C": trend.nexus_c, "F_TSMOM": trend.nexus_f_tsmom, "F_DONCHIAN": trend.nexus_f_donchian,
    "REF_SMA": trend.ref_sma, "D": trend.nexus_d,
}

CATS = ("Avantage statistique démontré", "Résultats prometteurs mais preuves insuffisantes",
        "Absence d'avantage démontré", "Résultats incompatibles avec une exploitation rentable")


def verdict_v2(r: dict) -> str:
    """Règles pré-enregistrées pour la phase 2C (docs/phase2c/01_protocole_et_budget.md §4)."""
    if r["n_trades"] < 20:
        return "Données insuffisantes (< 20 trades)"
    if r["ci_hi"] < 0:
        return CATS[3]
    beats_expo = r["p_random_bh"] < 0.25 and r["mean_r"] > r["random_mean"]
    if r["mean_r"] > 0 and r["p_zero_bh"] < 0.25 and r["mean_r_x2"] > 0 and beats_expo:
        return CATS[1]   # « démontré » est impossible sans validation + test final
    if r["mean_r"] <= 0 and r["ci_hi"] < 0.05 and r["mean_r_x2"] < 0:
        return CATS[3]
    return CATS[2]


def run(toml_path: str, n_random: int | None = None) -> pd.DataFrame:
    spec = tomllib.loads(Path(toml_path).read_text())
    common = spec["common"]
    if common["period"] != "dev":
        raise PermissionError("Seule la période de développement est accessible dans cette phase.")
    period = "dev"
    p0, p1 = PERIODS[period]
    reg = Registry()
    for fam, b in spec.get("budget", {}).items():
        # Le fichier ne crée un budget que s'il n'existe pas : toute modification ultérieure
        # passe par Registry.set_budget explicite, journalisé dans budget_changes.
        if reg.con.execute("SELECT 1 FROM budgets WHERE family=?", (fam,)).fetchone() is None:
            reg.set_budget(fam, int(b["max_trials"]), b["justification"])
    for h in spec["hypothesis"]:
        reg.register_hypothesis({
            "key": h["key"], "family": h["family"], "statement": h["statement"], "rationale": h["rationale"],
            "params": h["params"], "data": {"period": period, "symbols": common["symbols"], "strategy": h["strategy"]},
            "metrics": common["metrics"], "rejection": {"text": common["rejection"]},
        })
    batch = Path(toml_path).stem
    out_dir = RESULTS_DIR / batch
    out_dir.mkdir(parents=True, exist_ok=True)
    n_random = n_random or common["random_baseline_reps"]
    rows = []
    for symbol in common["symbols"]:
        sp = SPECS[symbol]
        m1, fx = load_inputs(symbol, period)
        dh = data_hash([symbol, "EURUSDT_1h"], range(p0.year, p1.year + 1))
        sig = signal_frame(m1)
        frames = {c: ExecFrame.from_m1(m1, sp.stressed(c)) for c in (0.0, 1.0, 1.5, 2.0)}
        low_fee = replace(sp, commission_rate_side=0.00075)  # sensibilité : remise BNB 25 % (non retenue)
        frames["bnb"] = ExecFrame.from_m1(m1, low_fee)
        regimes = daily_regimes(sig)
        d1 = resample(sig, 1440).set_index("ts")["c"]
        eurusdt = load_bars("EURUSDT_1h", p0 - pd.Timedelta(days=5), p1).set_index("ts")["c"].resample("1D").last()
        contexts = {}
        for h in spec["hypothesis"]:
            for variant in expand_variants(h["params"]):
                v = dict(variant)
                tf = v.pop("tf")
                if tf not in contexts:
                    contexts[tf] = trend.TFContext.build(sig, tf)
                ctx = contexts[tf]
                if v.pop("regime_filter", False):
                    v["regime"], v["regime_filter"] = regimes, True
                # Reprise : un essai déjà terminé (même hypothèse, variante, actif, période) n'est pas relancé
                done = reg.con.execute(
                    "SELECT id FROM trials WHERE hypothesis_key=? AND variant_json=? AND symbol=? AND period=? "
                    "AND status IN ('done','too_few_trades') ORDER BY id DESC",
                    (h["key"], json.dumps(variant, sort_keys=True), symbol, period)).fetchone()
                if done and (out_dir / f"row_{done[0]}.json").exists():
                    rows.append(json.loads((out_dir / f"row_{done[0]}.json").read_text()))
                    print(f"  reprise : essai {done[0]} {h['key']} {json.dumps(variant, sort_keys=True)}", flush=True)
                    continue
                if done:
                    # Essai terminé dont le résumé a été perdu (interruption) : recalcul déterministe
                    # sous le MÊME identifiant et la MÊME graine — ce n'est pas un nouvel essai.
                    tid, seed = done[0], reg.con.execute("SELECT seed FROM trials WHERE id=?", (done[0],)).fetchone()[0]
                    print(f"  recalcul du résumé de l'essai {tid} (graine {seed})", flush=True)
                else:
                    seed = 1000 + reg.n_trials()
                    tid = reg.start_trial(h["key"], {**variant}, symbol, period, 1.0, data_hash=dh, seed=seed,
                                          purpose=h.get("purpose", "selection"))
                t1 = time.time()
                try:
                    signals = STRATS[h["strategy"]](ctx, **v)
                    res = {c: run_backtest(signals, frames[c], sp.stressed(c), STAT_PROFILE, fx, strategy=h["key"])
                           for c in (0.0, 1.0, 1.5, 2.0)}
                    res["bnb"] = run_backtest(signals, frames["bnb"], low_fee, STAT_PROFILE, fx, strategy=h["key"])
                    tr = res[1.0].trades
                    row = {"trial_id": tid, "hypothesis": h["key"], "family": h["family"], "strategy": h["strategy"],
                           "symbol": symbol, "variant": json.dumps(variant, sort_keys=True), "tf": tf,
                           "n_signals": len(signals), "n_trades": int(len(tr)),
                           "rejections": res[1.0].rejections["reason"].value_counts().to_dict() if len(res[1.0].rejections) else {}}
                    if len(tr) < 5:
                        row["verdict"] = "Données insuffisantes (< 20 trades)"
                        reg.finish_trial(tid, status="too_few_trades", n_trades=len(tr))
                        (out_dir / f"row_{tid}.json").write_text(json.dumps(row, default=str, ensure_ascii=False))
                        rows.append(row); continue
                    block = (tr["exit_time"].dt.year * 100 + tr["exit_time"].dt.month).to_numpy() if tf != "H1" else \
                        (tr["exit_time"].dt.isocalendar().year * 100 + tr["exit_time"].dt.isocalendar().week).to_numpy()
                    m, lo, hi, p = block_bootstrap_mean(tr["r_net"].to_numpy(), block)
                    t0 = res[0.0].trades
                    b0 = (t0["exit_time"].dt.year * 100 + t0["exit_time"].dt.month).to_numpy()
                    mg, glo, ghi, gp = block_bootstrap_mean(t0["r_net"].to_numpy(), b0)
                    rnd = exposure_matched_random(tr, frames[1.0], sp, p0, p1, n_rep=n_random, seed=seed)
                    rm = rnd["r_means"]
                    p_rand = float((np.sum(rm >= m) + 1) / (np.sum(np.isfinite(rm)) + 1))
                    eq = res[1.0].equity_daily
                    attr = market_attribution(eq, d1)
                    expo = exposure_stats(tr, p0, p1)
                    tr_reg = [regime_at(regimes, int(t.value)) for t in tr["entry_time"]]
                    tr = tr.assign(reg_trend=[x["trend"] for x in tr_reg], reg_vol=[x["vol"] for x in tr_reg])
                    by_reg = {f"{k}": {"n": int(len(g)), "mean_r": float(g["r_net"].mean())}
                              for k, g in tr.groupby("reg_trend")}
                    by_vol = {f"{k}": {"n": int(len(g)), "mean_r": float(g["r_net"].mean())} for k, g in tr.groupby("reg_vol")}
                    profiles = {}
                    for pname, pr in RISK_PROFILES.items():
                        for halt in (True, False):
                            prof = pr if halt else replace(pr, max_drawdown_halt=1.0)
                            rr = run_backtest(signals, frames[1.0], sp, prof, fx, strategy=h["key"])
                            sm = summarize(rr.trades, rr.equity_daily, INITIAL_CAPITAL_EUR, periods_per_year=365)
                            sm.update(exposure_stats(rr.trades, p0, p1) if len(rr.trades) else {})
                            sm["halted"], sm["halt_reason"] = rr.halted, rr.halt_reason
                            sm["halt_time"] = str(rr.halt_time) if rr.halt_time is not None else None
                            sm["n_rejected"] = int(len(rr.rejections))
                            if halt:
                                g = (tr["exit_time"].dt.year * 100 + tr["exit_time"].dt.month).to_numpy()
                                sm["mc"] = mc_drawdown(tr["r_net"].to_numpy(), g, pr.risk_per_trade)
                            for k in ("monthly_pnl_eur",):
                                sm.pop(k, None)
                            profiles[f"{pname}{'' if halt else '_sans_arret'}"] = sm
                    wins = tr["pnl_eur"][tr["pnl_eur"] > 0]
                    row.update({
                        "mean_r": m, "ci_lo": lo, "ci_hi": hi, "p_zero": p,
                        "mean_r_frictionless": mg, "ci_frictionless": [glo, ghi], "p_zero_frictionless": gp,
                        "mean_r_before_commission": float(tr["r_gross"].mean()),
                        "mean_r_x1.5": float(res[1.5].trades["r_net"].mean()),
                        "mean_r_x2": float(res[2.0].trades["r_net"].mean()),
                        "mean_r_bnb_fee_sensitivity": float(res["bnb"].trades["r_net"].mean()),
                        "random_mean": float(np.nanmean(rm)), "random_p95": float(np.nanpercentile(rm, 95)),
                        "p_random": p_rand, "random_ret_mean_pct": float(np.nanmean(rnd["ret_means"]) * 100),
                        "strategy_ret_mean_pct": float((tr["side"] * (tr["exit"] - tr["entry"]) / tr["entry"]).mean() * 100),
                        "win_rate": float((tr["r_net"] > 0).mean()), "r_std": float(tr["r_net"].std()),
                        "top5_share": float(np.sort(wins.to_numpy())[-5:].sum() / wins.sum() * 100) if wins.sum() > 0 else None,
                        "folds": fold_means(tr, period), "by_trend_regime": by_reg, "by_vol_regime": by_vol,
                        "annual_mean_r": {str(k): float(v) for k, v in tr.set_index("exit_time")["r_net"].resample("YS").mean().items()},
                        "attribution": attr, "beta": attr.get("beta"),
                        "alpha_lo": (attr.get("alpha_ci95_ann_pct") or [None])[0],
                        "daily_sharpe": daily_sharpe_ci(eq), "exposure": expo,
                        "passive": passive_benchmarks(d1, eurusdt, INITIAL_CAPITAL_EUR, sp.commission_rate_side,
                                                      expo["avg_exposure_pct"] / 100),
                        "profiles": profiles,
                        "exit_reasons": tr["exit_reason"].value_counts().to_dict(),
                        "ambiguous_pct": float(tr["ambiguous_bar"].mean() * 100),
                    })
                    row["overfit_flags"] = overfit_flags(row)
                    tr.to_parquet(out_dir / f"trades_{tid}.parquet", index=False)
                    (out_dir / f"row_{tid}.json").write_text(json.dumps(row, default=str, ensure_ascii=False))
                    reg.finish_trial(tid, status="done", n_trades=len(tr), mean_r=m, p_value=p,
                                     result={k: row[k] for k in ("mean_r", "ci_lo", "ci_hi", "mean_r_frictionless", "p_random")})
                except Exception as exc:
                    reg.finish_trial(tid, status=f"error: {exc!r}")
                    raise
                rows.append(row)
                print(f"  {symbol} {h['key']:9s} {row['variant']:60s} n={row['n_trades']:4d} "
                      f"R={row.get('mean_r', np.nan):+.3f} R0={row.get('mean_r_frictionless', np.nan):+.3f} "
                      f"alea={row.get('random_mean', np.nan):+.3f} pR={row.get('p_random', np.nan):.3f} "
                      f"({time.time() - t1:.0f} s)", flush=True)
    df = pd.DataFrame(rows)
    ok = df["mean_r"].notna() if "mean_r" in df else pd.Series(False, index=df.index)
    for fam, g in df[ok].groupby("family"):
        df.loc[g.index, "p_zero_bh"] = benjamini_hochberg(g["p_zero"])
        df.loc[g.index, "p_random_bh"] = benjamini_hochberg(g["p_random"])
    df["verdict"] = [verdict_v2(r) if ok.iat[i] else r.get("verdict", "Données insuffisantes (< 20 trades)")
                     for i, (_, r) in enumerate(df.iterrows())]
    for _, r in df.iterrows():
        status = {CATS[1]: "candidate", CATS[2]: "rejected", CATS[3]: "rejected"}.get(r["verdict"], "insufficient")
        reg.set_status(r["hypothesis"], json.loads(r["variant"]), r["symbol"], status, r["verdict"],
                       "; ".join(r.get("overfit_flags") or []) if isinstance(r.get("overfit_flags"), list) else "", int(r["trial_id"]))
    # Walk-forward du processus de sélection, par famille
    wf = {}
    for fam, g in df[ok].groupby("family"):
        tbv = {f"{r.hypothesis} {r.variant}": pd.read_parquet(out_dir / f"trades_{int(r.trial_id)}.parquet") for r in g.itertuples()}
        wf[fam] = walk_forward_selection(tbv, p0, p1)
    df["code_version"] = code_version()
    df["registry_trials_total"] = reg.n_trials()
    df.to_json(out_dir / "summary.json", orient="records", indent=2, default_handler=str, force_ascii=False)
    (out_dir / "walk_forward.json").write_text(json.dumps(wf, indent=2, default=str, ensure_ascii=False))
    return df


from ..data.store import load_bars  # noqa: E402  (import tardif pour éviter un cycle)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("toml")
    ap.add_argument("--n-random", type=int)
    a = ap.parse_args()
    df = run(a.toml, a.n_random)
    cols = ["hypothesis", "variant", "n_trades", "mean_r", "ci_lo", "ci_hi", "mean_r_frictionless", "mean_r_x2",
            "random_mean", "p_zero_bh", "p_random_bh", "verdict"]
    print(df[[c for c in cols if c in df]].to_string())


if __name__ == "__main__":
    main()
