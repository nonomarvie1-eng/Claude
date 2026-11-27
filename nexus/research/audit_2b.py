"""Audit approfondi des résultats du lot 2B-01 (NEXUS A et référence SBA, BTC/USDT spot).

    python -m nexus.research.audit_2b

Ré-exécute, à titre DIAGNOSTIQUE (essais comptés, famille AUDIT), les configurations
de base sur la période de développement :
- contrôle de reproductibilité (coûts ×1 doivent redonner l'espérance enregistrée) ;
- espérance sans aucun frottement (coûts ×0), avant commissions, nette, IC95 ;
- courbe de sensibilité aux coûts ;
- part expliquée par la hausse de BTC : entrées aléatoires à exposition comparable,
  alpha/bêta quotidiens, détention passive dans la même fenêtre horaire ;
- résultats par année et par régime (causal) ;
- biais de l'arrêt à 10 % : capital avec et sans arrêt, date de déclenchement.
"""
from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pandas as pd

from ..config import INITIAL_CAPITAL_EUR, PERIODS, RESULTS_DIR, RISK_PROFILES
from ..engine.backtest import run_backtest
from ..engine.execution import ExecFrame
from ..features.core import resample, signal_frame
from ..features.regime import daily_regimes, regime_at
from ..instruments import SPECS
from ..stats.inference import block_bootstrap_mean, week_groups
from ..stats.metrics import exposure_stats, market_attribution, summarize
from ..strategies.random_baseline import exposure_matched_random
from ..strategies.session import SessionContext, _range, _window
from ..timeutils import SESSION_HYPOTHESES
from .lab import data_hash
from .registry import Registry
from .runner import STAT_PROFILE, load_inputs, make_signals

TARGETS = [("REF-SBA-01", {"ema_buffer_atr": 0.1, "min_stop_atr": 0.5, "target_r": 2.0}),
           ("NXA-01", {"target_r": 2.0}), ("NXA-01", {"target_r": "none"}),
           ("NXA-03", {"compression_filter": True, "target_r": 2.0})]
SESSIONS = ["paris", "london", "utc"]
COSTS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]


def main(n_random: int = 200):
    symbol, period = "BTCUSDT", "dev"
    p0, p1 = PERIODS[period]
    reg = Registry()
    reg.set_budget("AUDIT", 12, "Audit diagnostique des 4 configurations × 3 sessions du lot 2B-01 ; "
                   "aucune sélection, aucun nouveau paramètre.")
    reg.register_hypothesis({
        "key": "AUDIT-2B-01", "family": "AUDIT",
        "statement": "Ré-analyse diagnostique de REF-SBA-01, NXA-01 (2 variantes) et NXA-03 sur BTC/USDT dev.",
        "rationale": "Décomposer espérance brute / nette, exposition au marché, régimes et biais de l'arrêt à 10 %.",
        "params": {"targets": [f"{k} {json.dumps(v, sort_keys=True)}" for k, v in TARGETS], "sessions": SESSIONS,
                   "costs": COSTS},
        "data": {"period": period, "symbols": [symbol]}, "metrics": ["voir module"],
        "rejection": {"text": "Diagnostic : pas de critère de sélection."},
    })
    prev = {(r["hypothesis"], r["session"], r["variant"]): r for r in
            json.loads((RESULTS_DIR / "batch_2b_01" / "summary_BTCUSDT.json").read_text())}
    sp = SPECS[symbol]
    m1, fx = load_inputs(symbol, period)
    dh = data_hash([symbol, "EURUSDT_1h"], range(p0.year, p1.year + 1))
    sig = signal_frame(m1)
    frames = {c: ExecFrame.from_m1(m1, sp.stressed(c)) for c in COSTS}
    low_fee = replace(sp, commission_rate_side=0.00075)
    frames["bnb"] = ExecFrame.from_m1(m1, low_fee)
    regimes = daily_regimes(sig)
    d1 = resample(sig, 1440).set_index("ts")["c"]
    out = {"bh": {"start_price": float(d1.iloc[0]), "end_price": float(d1.iloc[-1])}, "rows": []}
    for sess in SESSIONS:
        ctx = SessionContext.build(sig, SESSION_HYPOTHESES[sess])
        # Détention passive dans la même fenêtre horaire (tous les jours éligibles)
        win_ret = []
        for day in ctx.days:
            rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
            if _range(ctx, i0, i1, rs, re_) is None:
                continue
            a = frames[1.0].index_at_or_after(re_.value); b = frames[1.0].index_at_or_after(xt.value)
            if b < len(frames[1.0].ts) and b > a:
                ex = frames[1.0]
                win_ret.append((ex.bid_o[b] * (1 - sp.slippage_market_frac)) / (ex.ask_o[a] * (1 + sp.slippage_market_frac))
                               - 1 - 2 * sp.commission_rate_side)
        for key, variant in TARGETS:
            vkey = json.dumps(variant, sort_keys=True)
            tid = reg.start_trial("AUDIT-2B-01", {"target": key, **variant, "session": sess}, symbol, period, 1.0,
                                  data_hash=dh, seed=7, purpose="diagnostic")
            signals = make_signals(key, variant, ctx, sp.allow_short)
            res = {c: run_backtest(signals, frames[c], sp.stressed(c), STAT_PROFILE, fx, strategy=key) for c in COSTS}
            res["bnb"] = run_backtest(signals, frames["bnb"], low_fee, STAT_PROFILE, fx, strategy=key)
            tr = res[1.0].trades
            g = week_groups(tr["exit_time"])
            m, lo, hi, p = block_bootstrap_mean(tr["r_net"].to_numpy(), g)
            t0 = res[0.0].trades
            m0, lo0, hi0, p0v = block_bootstrap_mean(t0["r_net"].to_numpy(), week_groups(t0["exit_time"]))
            mb, lob, hib, _ = block_bootstrap_mean(tr["r_gross"].to_numpy(), g)
            rnd = exposure_matched_random(tr, frames[1.0], sp, p0, p1, n_rep=n_random, seed=tid)
            regs = [regime_at(regimes, int(t.value)) for t in tr["entry_time"]]
            tr = tr.assign(reg_trend=[x["trend"] for x in regs], reg_vol=[x["vol"] for x in regs])
            ret_pct = tr["side"] * (tr["exit"] - tr["entry"]) / tr["entry"]
            profiles = {}
            for pname, pr in RISK_PROFILES.items():
                for halt in (True, False):
                    rr = run_backtest(signals, frames[1.0], sp, pr if halt else replace(pr, max_drawdown_halt=1.0), fx, strategy=key)
                    sm = summarize(rr.trades, rr.equity_daily, INITIAL_CAPITAL_EUR, periods_per_year=365)
                    profiles[f"{pname}{'' if halt else '_sans_arret'}"] = {
                        "n_trades": sm["n_trades"], "final_eur": sm["final_capital_eur"], "net_return_pct": sm.get("net_return_pct"),
                        "max_dd_pct": 100 * sm.get("max_dd_pct", 0), "halted": rr.halted,
                        "halt_time": str(rr.halt_time) if rr.halt_time is not None else None,
                        "fees_eur": sm.get("total_fees_eur"), "annual_pnl_eur": sm.get("annual_pnl_eur"),
                        "sharpe": sm.get("sharpe")}
            stored = prev.get((key, sess, vkey), {})
            row = {
                "trial_id": tid, "hypothesis": key, "variant": vkey, "session": sess, "n_trades": int(len(tr)),
                "repro_stored_mean_r": stored.get("mean_r"), "repro_now_mean_r": m,
                "mean_r_frictionless": m0, "ci_frictionless": [lo0, hi0], "n_trades_frictionless": int(len(t0)),
                "mean_r_before_commission": mb, "ci_before_commission": [lob, hib],
                "mean_r_net": m, "ci_net": [lo, hi], "p_net": p,
                "cost_curve": {str(c): float(res[c].trades["r_net"].mean()) for c in COSTS},
                "cost_curve_n": {str(c): int(len(res[c].trades)) for c in COSTS},
                "mean_r_bnb_fee": float(res["bnb"].trades["r_net"].mean()),
                "mean_cost_r": float((tr["r_gross"] - tr["r_net"]).mean()),
                "expo_random_mean_r": float(np.nanmean(rnd["r_means"])),
                "expo_random_p95_r": float(np.nanpercentile(rnd["r_means"], 95)),
                "p_vs_expo_random": float((np.sum(rnd["r_means"] >= m) + 1) / (np.sum(np.isfinite(rnd["r_means"])) + 1)),
                "strategy_mean_ret_pct": float(ret_pct.mean() * 100),
                "expo_random_mean_ret_pct": float(np.nanmean(rnd["ret_means"]) * 100),
                "window_hold_mean_ret_pct": float(np.mean(win_ret) * 100), "window_hold_days": len(win_ret),
                "attribution": market_attribution(res[1.0].equity_daily, d1),
                "exposure": exposure_stats(tr, p0, p1),
                "annual_mean_r": {str(k.year): float(v) for k, v in tr.set_index("exit_time")["r_net"].resample("YS").mean().items()},
                "by_trend_regime": {k: {"n": int(len(x)), "mean_r": float(x["r_net"].mean())} for k, x in tr.groupby("reg_trend")},
                "by_vol_regime": {k: {"n": int(len(x)), "mean_r": float(x["r_net"].mean())} for k, x in tr.groupby("reg_vol")},
                "profiles": profiles,
            }
            reg.finish_trial(tid, status="done", n_trades=len(tr), mean_r=m, p_value=p)
            out["rows"].append(row)
            print(f"{sess:7s} {key:10s} {vkey:50s} n={len(tr)} stored={stored.get('mean_r', float('nan')):+.4f} now={m:+.4f} "
                  f"R0={m0:+.3f} Rbc={mb:+.3f} expoRnd={row['expo_random_mean_r']:+.3f}", flush=True)
    d = RESULTS_DIR / "audit_2b_01"
    d.mkdir(parents=True, exist_ok=True)
    (d / "audit.json").write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
