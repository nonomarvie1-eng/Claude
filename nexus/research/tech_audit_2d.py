"""Répétitions TECHNIQUES (famille TECH, non comptées comme hypothèses) : mesure de l'effet
des deux défauts corrigés en phase 2D sur les candidats « prometteurs » du lot 2C :
 (1) courbe de capital limitée à [premier signal, dernière sortie] au lieu de la période entière ;
 (2) Buy & Hold démarrant à la clôture du premier jour ;
 (3) valorisation quotidienne convertie au taux d'entrée au lieu du taux du jour.
Les résultats enregistrés ne sont pas modifiés ; cette analyse les complète.

    python -m nexus.research.tech_audit_2d
"""
from __future__ import annotations

import json

from ..config import INITIAL_CAPITAL_EUR, PERIODS, RESULTS_DIR, RISK_PROFILES
from ..data.store import load_bars
from ..engine.backtest import run_backtest
from ..engine.execution import ExecFrame
from ..features.core import resample, signal_frame
from ..instruments import SPECS
from ..stats.metrics import daily_sharpe_ci, market_attribution, passive_benchmarks, summarize
from ..strategies import trend
from .lab_runner import STRATS
from .registry import Registry
from .runner import STAT_PROFILE, load_inputs

CANDIDATES = [("NXF-01", "F_TSMOM", {"lookback": 20, "tf": "D1"}, "batch_2c_01"),
              ("NXF-01", "F_TSMOM", {"lookback": 60, "tf": "D1"}, "batch_2c_01"),
              ("NXF-02H4", "F_DONCHIAN", {"n": 120, "tf": "H4"}, "batch_2c_01"),
              ("NXF-03", "F_TSMOM", {"lookback": 20, "tf": "D1", "vol_filter": True}, "batch_2c_01"),
              ("REF-SMA-01", "REF_SMA", {"n": 50, "tf": "D1"}, "batch_2c_01"),
              ("NXD-02", "D", {"require_compression": False, "tf": "H4"}, "batch_2c_02")]


def main():
    sym, period = "BTCUSDT", "dev"
    p0, p1 = PERIODS[period]
    reg = Registry()
    if reg.con.execute("SELECT 1 FROM budgets WHERE family='TECH'").fetchone() is None:
        reg.set_budget("TECH", 20, "Répétitions techniques d'audit du moteur (aucune hypothèse nouvelle, hors correction statistique).")
    reg.register_hypothesis({"key": "TECH-2D-01", "family": "TECH",
                             "statement": "Recalcul des métriques des 6 candidats 2C après correction des défauts (1)(2)(3).",
                             "rationale": "Audit technique : mesurer l'effet des défauts de traitement.",
                             "params": {"candidates": [f"{k} {json.dumps(v, sort_keys=True)}" for k, _, v, _ in CANDIDATES]},
                             "data": {"period": period, "symbols": [sym]}, "metrics": ["sharpe", "cagr", "alpha", "bh"],
                             "rejection": {"text": "aucun (répétition technique)"}})
    sp = SPECS[sym]
    m1, fx = load_inputs(sym, period)
    sig = signal_frame(m1)
    ex = ExecFrame.from_m1(m1, sp)
    d1f = resample(sig, 1440).set_index("ts")
    eurusdt = load_bars("EURUSDT_1h", p0 - __import__("pandas").Timedelta(days=5), p1).set_index("ts")["c"].resample("1D").last()
    ctxs, out = {}, {"rows": []}
    bh_old = passive_benchmarks(d1f["c"], eurusdt, INITIAL_CAPITAL_EUR, sp.commission_rate_side, 1.0)["buy_hold"]
    bh_new = passive_benchmarks(d1f["c"], eurusdt, INITIAL_CAPITAL_EUR, sp.commission_rate_side, 1.0,
                                start_price=float(d1f["o"].iloc[0]))["buy_hold"]
    out["buy_hold"] = {"avant": bh_old, "apres": bh_new}
    for key, strat, v, batch in CANDIDATES:
        old = next(r for r in json.loads((RESULTS_DIR / batch / "summary.json").read_text())
                   if r["hypothesis"] == key and json.loads(r["variant"]) == v)
        tid = reg.start_trial("TECH-2D-01", {"target": key, **v}, sym, period, 1.0, purpose="technique")
        vv = dict(v); tf = vv.pop("tf")
        ctxs.setdefault(tf, trend.TFContext.build(sig, tf))
        signals = STRATS[strat](ctxs[tf], **vv)
        stat = run_backtest(signals, ex, sp, STAT_PROFILE, fx, period=(p0, p1))
        eq = run_backtest(signals, ex, sp, RISK_PROFILES["equilibre"], fx, period=(p0, p1))
        sm = summarize(eq.trades, eq.equity_daily, INITIAL_CAPITAL_EUR, periods_per_year=365)
        row = {"hypothesis": key, "variant": v,
               "mean_r_avant": old["mean_r"], "mean_r_apres": float(stat.trades["r_net"].mean()),
               "sharpe_quot_avant": old["daily_sharpe"], "sharpe_quot_apres": daily_sharpe_ci(stat.equity_daily),
               "alpha_avant": old["attribution"], "alpha_apres": market_attribution(stat.equity_daily, d1f["c"]),
               "equilibre_avant": {k: old["profiles"]["equilibre"].get(k) for k in ("net_return_pct", "cagr_pct", "max_dd_pct", "sharpe", "calmar")},
               "equilibre_apres": {k: sm.get(k) for k in ("net_return_pct", "cagr_pct", "max_dd_pct", "sharpe", "calmar")},
               "jours_courbe_avant": None, "jours_courbe_apres": int(len(stat.equity_daily))}
        reg.finish_trial(tid, status="done", n_trades=len(stat.trades), mean_r=row["mean_r_apres"])
        out["rows"].append(row)
        print(key, v, "R", round(row["mean_r_avant"], 4), "->", round(row["mean_r_apres"], 4),
              "| Sharpe", round(old["daily_sharpe"]["sharpe"], 2), "->", round(row["sharpe_quot_apres"]["sharpe"], 2),
              row["sharpe_quot_apres"]["sharpe_ci95"],
              "| alpha", round(old["attribution"]["alpha_ann_pct"], 2), "->", round(row["alpha_apres"]["alpha_ann_pct"], 2),
              [round(x, 2) for x in row["alpha_apres"]["alpha_ci95_ann_pct"]],
              "| CAGR eq", round(old["profiles"]["equilibre"]["cagr_pct"], 2), "->", round(sm["cagr_pct"], 2), flush=True)
    print("B&H", round(bh_old["net_return_pct"], 1), "->", round(bh_new["net_return_pct"], 1))
    d = RESULTS_DIR / "tech_audit_2d"; d.mkdir(exist_ok=True)
    (d / "tech_audit.json").write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
