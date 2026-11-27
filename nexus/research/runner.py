"""Exécution d'un lot d'expériences pré-enregistré.

    python -m nexus.research.runner experiments/preregistration/batch_2b_01.toml --symbols BTCUSDT

Étapes par essai (hypothèse × variante × session × actif) :
 1. génération causale des signaux ;
 2. backtest « statistique » (risque 0,5 %, sans disjoncteur) à coûts x1 / x1,5 / x2 → R nets ;
 3. bootstrap par blocs hebdomadaires, entrées aléatoires appariées ;
 4. simulation des trois profils de risque avec limites actives + Monte-Carlo de drawdown ;
 5. journalisation dans le registre ; verdict après correction BH sur tout le lot.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
import tomllib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import INITIAL_CAPITAL_EUR, PERIODS, RESULTS_DIR, RISK_PROFILES, RiskProfile
from ..data.store import load_bars
from ..engine.backtest import FxConverter, run_backtest
from ..engine.execution import ExecFrame
from ..features.core import signal_frame
from ..instruments import SPECS
from ..stats.inference import (CATEGORIES, autocorr_sum, benjamini_hochberg, block_bootstrap_mean,
                               verdict, week_groups)
from ..stats.metrics import summarize
from ..strategies.random_baseline import matched_random_r
from ..strategies.session import SessionContext, _range, _window, nexus_a, nexus_b, sba_reference
from ..timeutils import SESSION_HYPOTHESES
from .registry import Registry, code_version

STAT_PROFILE = RiskProfile("statistique", 0.005, daily_loss_limit=1.0, max_drawdown_halt=1.0)


def expand_variants(params: dict):
    keys = sorted(params)
    for combo in itertools.product(*(params[k] for k in keys)):
        yield dict(zip(keys, combo))


def make_signals(key: str, variant: dict, ctx: SessionContext, allow_short: bool):
    v = dict(variant)
    if "target_r" in v and v["target_r"] == "none":
        v["target_r"] = None
    if key.startswith("REF-SBA"):
        return sba_reference(ctx, allow_short=allow_short, **v)
    if key.startswith("NXA"):
        return nexus_a(ctx, allow_short=allow_short, **v)
    if key.startswith("NXB"):
        return nexus_b(ctx, allow_short=allow_short, **v)
    raise KeyError(key)


def mc_drawdown(r: np.ndarray, groups: np.ndarray, risk: float, n_paths: int = 2000, seed: int = 0) -> dict:
    """Monte-Carlo par blocs hebdomadaires des R nets ; capital composé à risque fixe.
    Ignore l'arrondi des tailles et les disjoncteurs (borne indicative)."""
    rng = np.random.default_rng(seed)
    uniq, inv = np.unique(groups, return_inverse=True)
    blocks = [r[inv == i] for i in range(len(uniq))]
    n_target = len(r)
    mdd, final = np.empty(n_paths), np.empty(n_paths)
    for p in range(n_paths):
        seq = []
        while len(seq) < n_target:
            seq.extend(blocks[rng.integers(len(blocks))])
        eq = np.cumprod(1 + risk * np.asarray(seq[:n_target]))
        peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
        mdd[p] = np.max(1 - eq / peak)
        final[p] = eq[-1]
    return {"p_dd_ge_10pct": float((mdd >= 0.10).mean()), "p_dd_ge_20pct": float((mdd >= 0.20).mean()),
            "median_max_dd_pct": float(np.median(mdd) * 100), "p95_max_dd_pct": float(np.percentile(mdd, 95) * 100),
            "median_final_multiple": float(np.median(final)), "p_final_below_initial": float((final < 1).mean())}


def diff_bootstrap(a: pd.DataFrame, b: pd.DataFrame, n_boot: int = 3000, seed: int = 0):
    """Différence de moyenne de R (a - b), bootstrap par semaines communes."""
    ga, gb = week_groups(a["exit_time"]), week_groups(b["exit_time"])
    weeks = np.union1d(ga, gb)
    sa = pd.Series(a["r_net"].to_numpy()).groupby(ga).agg(["sum", "count"]).reindex(weeks, fill_value=0)
    sb = pd.Series(b["r_net"].to_numpy()).groupby(gb).agg(["sum", "count"]).reindex(weeks, fill_value=0)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(weeks), (n_boot, len(weeks)))
    ma = sa["sum"].to_numpy()[idx].sum(1) / np.maximum(sa["count"].to_numpy()[idx].sum(1), 1)
    mb = sb["sum"].to_numpy()[idx].sum(1) / np.maximum(sb["count"].to_numpy()[idx].sum(1), 1)
    d = ma - mb
    return float(a["r_net"].mean() - b["r_net"].mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def load_inputs(symbol: str, period: str):
    s, e = PERIODS[period]
    m1 = load_bars(symbol, s, e)
    if symbol == "EURUSD":
        fx = FxConverter.build(eurusd_m1=m1)
    else:
        h1 = load_bars("EURUSDT_1h", s - pd.Timedelta(days=5), e)
        fx = FxConverter.build(eurusdt_h1=h1)
    return m1, fx


def fold_means(trades: pd.DataFrame, period: str) -> dict:
    s, e = PERIODS[period]
    edges = pd.date_range(s, e, freq="6MS")
    out = {}
    for a, b in zip(edges[:-1], edges[1:]):
        sub = trades[(trades["exit_time"] >= a) & (trades["exit_time"] < b)]
        out[f"{a.date()}..{b.date()}"] = {"n": int(len(sub)), "mean_r": float(sub["r_net"].mean()) if len(sub) else None}
    return out


def run_batch(toml_path: str, symbols: list[str] | None = None, sessions: list[str] | None = None,
              n_random: int | None = None, out_dir: Path | None = None) -> pd.DataFrame:
    spec = tomllib.loads(Path(toml_path).read_text())
    common = spec["common"]
    period = common["period"]
    if period != "dev":
        raise PermissionError("Ce lanceur n'exécute que la période de développement.")
    symbols = symbols or common["symbols"]
    sessions = sessions or common["sessions"]
    n_random = n_random or common["random_baseline_reps"]
    reg = Registry()
    batch = Path(toml_path).stem
    out_dir = out_dir or (RESULTS_DIR / batch)
    out_dir.mkdir(parents=True, exist_ok=True)
    for h in spec["hypothesis"]:
        reg.register_hypothesis({
            "key": h["key"], "family": h["family"], "statement": h["statement"], "rationale": h["rationale"],
            "params": h["params"], "data": {"period": period, "symbols": common["symbols"], "sessions": common["sessions"]},
            "metrics": common["metrics"], "rejection": {"text": common["rejection"]},
        })
    rows = []
    for symbol in symbols:
        base_spec = SPECS[symbol]
        t0 = time.time()
        m1, fx = load_inputs(symbol, period)
        sig = signal_frame(m1)
        frames = {c: ExecFrame.from_m1(m1, base_spec.stressed(c)) for c in common["cost_stress"]}
        print(f"[{symbol}] {len(m1):,} minutes chargées ({time.time() - t0:.0f} s)", flush=True)
        for sess in sessions:
            hyp = SESSION_HYPOTHESES[sess]
            ctx = SessionContext.build(sig, hyp)
            windows = {}
            for day in ctx.days:
                rs, re_, ee, xt, i0, i1, j1 = _window(ctx, day)
                if _range(ctx, i0, i1, rs, re_) is not None:   # jours éligibles uniquement
                    windows[str(day.date())] = (re_, ee, xt)
            base_trades = {}
            for h in spec["hypothesis"]:
                for variant in expand_variants(h["params"]):
                    tid = reg.start_trial(h["key"], {**variant, "session": sess}, symbol, period, 1.0)
                    t1 = time.time()
                    try:
                        signals = make_signals(h["key"], variant, ctx, base_spec.allow_short)
                        res = {c: run_backtest(signals, frames[c], base_spec.stressed(c), STAT_PROFILE, fx,
                                               strategy=h["key"], max_cost_frac=common.get("max_cost_frac", 0.33))
                               for c in common["cost_stress"]}
                        tr = res[1.0].trades
                        row = {"trial_id": tid, "hypothesis": h["key"], "family": h["family"], "symbol": symbol,
                               "session": sess, "variant": json.dumps(variant, sort_keys=True),
                               "n_signals": len(signals), "n_trades": len(tr),
                               "rejections": res[1.0].rejections["reason"].value_counts().to_dict() if len(res[1.0].rejections) else {}}
                        if len(tr) < 20:
                            row.update({"mean_r": np.nan, "p_zero": np.nan, "p_random": np.nan})
                            reg.finish_trial(tid, status="too_few_trades", n_trades=len(tr))
                            rows.append(row); continue
                        g = week_groups(tr["exit_time"])
                        m, lo, hi, p = block_bootstrap_mean(tr["r_net"].to_numpy(), g)
                        sig_by_day = {s_.tags["day"]: s_ for s_ in signals}
                        tgt_r = []
                        for _, t_ in tr.iterrows():
                            s_ = sig_by_day[t_["day"]]
                            tgt_r.append(s_.target_r if s_.target is None else abs(s_.target - t_["entry"]) / abs(t_["entry"] - t_["stop"]))
                        rnd = matched_random_r(tr, tgt_r, frames[1.0], base_spec, windows, n_rep=n_random, seed=tid)
                        p_rand = float((np.sum(rnd >= m) + 1) / (np.sum(np.isfinite(rnd)) + 1))
                        prof = {}
                        for pname, pr in ({} if common.get("diagnostic_only") else RISK_PROFILES).items():
                            rr = run_backtest(signals, frames[1.0], base_spec, pr, fx, strategy=h["key"])
                            summ = summarize(rr.trades, rr.equity_daily, INITIAL_CAPITAL_EUR,
                                             periods_per_year=365 if symbol == "BTCUSDT" else 260)
                            summ["halted"] = rr.halted; summ["halt_reason"] = rr.halt_reason
                            summ["n_rejected"] = int(len(rr.rejections))
                            summ["mc"] = mc_drawdown(tr["r_net"].to_numpy(), g, pr.risk_per_trade)
                            prof[pname] = summ
                        row.update({
                            "mean_r": m, "ci_lo": lo, "ci_hi": hi, "p_zero": p,
                            "mean_r_gross": float(tr["r_gross"].mean()),
                            "mean_r_x1.5": float(res[1.5].trades["r_net"].mean()) if len(res[1.5].trades) else np.nan,
                            "mean_r_x2": float(res[2.0].trades["r_net"].mean()) if len(res[2.0].trades) else np.nan,
                            "n_trades_x2": int(len(res[2.0].trades)),
                            "random_mean": float(np.nanmean(rnd)), "random_p95": float(np.nanpercentile(rnd, 95)),
                            "p_random": p_rand, "win_rate": float((tr["r_net"] > 0).mean()),
                            "r_std": float(tr["r_net"].std()), "rho_sum": autocorr_sum(tr["r_net"].to_numpy()),
                            "folds": fold_means(tr, period), "profiles": prof,
                            "exit_reasons": tr["exit_reason"].value_counts().to_dict(),
                            "ambiguous_pct": float(tr["ambiguous_bar"].mean() * 100),
                            "median_cost_frac_est": float(tr["cost_frac_est"].median()),
                        })
                        if h["key"] in ("NXA-01", "NXB-01"):
                            base_trades[(h["key"], json.dumps(variant, sort_keys=True))] = tr
                        else:
                            ref_key = ("NXA-01", json.dumps({"target_r": 2.0})) if h["family"] == "A" else \
                                      ("NXB-01", json.dumps({"target": "mid"})) if h["family"] == "B" else None
                            if ref_key and ref_key in base_trades:
                                row["ablation_vs_base"] = diff_bootstrap(tr, base_trades[ref_key])
                        tr.to_parquet(out_dir / f"trades_{tid}.parquet", index=False)
                        reg.finish_trial(tid, status="done", n_trades=len(tr), mean_r=m, p_value=p,
                                         result={k: v for k, v in row.items() if k != "profiles"})
                    except Exception as exc:  # l'échec est journalisé, jamais masqué
                        reg.finish_trial(tid, status=f"error: {exc!r}")
                        raise
                    rows.append(row)
                    print(f"  {symbol} {sess:7s} {h['key']:10s} {json.dumps(variant):45s} n={row['n_trades']:4d} "
                          f"R={row.get('mean_r', float('nan')):+.3f} p0={row.get('p_zero', float('nan')):.3f} "
                          f"pR={row.get('p_random', float('nan')):.3f} ({time.time() - t1:.0f} s)", flush=True)
    df = pd.DataFrame(rows)
    ok = df["p_zero"].notna()
    df.loc[ok, "p_zero_bh"] = benjamini_hochberg(df.loc[ok, "p_zero"])
    df.loc[ok, "p_random_bh"] = benjamini_hochberg(df.loc[ok, "p_random"])
    df["verdict"] = [
        verdict(r.mean_r, r.ci_lo, r.ci_hi, r.p_zero_bh, mean_r_2x_costs=r["mean_r_x2"], p_random_adj=r.p_random_bh, phase="dev")
        if ok.iat[i] else "Données insuffisantes (< 20 trades)"
        for i, (_, r) in enumerate(df.iterrows())
    ]
    df["code_version"] = code_version()
    df["registry_trials_total"] = reg.n_trials()
    df.to_json(out_dir / f"summary_{'_'.join(symbols)}.json", orient="records", indent=2, default_handler=str, force_ascii=False)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("toml")
    ap.add_argument("--symbols", nargs="*")
    ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--n-random", type=int)
    a = ap.parse_args()
    df = run_batch(a.toml, a.symbols, a.sessions, a.n_random)
    cols = ["symbol", "session", "hypothesis", "variant", "n_trades", "mean_r", "ci_lo", "ci_hi", "mean_r_x2",
            "p_zero_bh", "p_random_bh", "verdict"]
    print(df[[c for c in cols if c in df]].to_string())


if __name__ == "__main__":
    main()
