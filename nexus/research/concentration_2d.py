"""Concentration des profits des candidats 2C comparée à la distribution attendue sous des
entrées aléatoires à exposition comparable (mêmes durées, mêmes stops). Analyse des trades
déjà enregistrés : répétition technique (famille TECH), aucune hypothèse nouvelle.

    python -m nexus.research.concentration_2d
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from ..config import PERIODS, RESULTS_DIR
from ..engine.execution import ExecFrame
from ..instruments import SPECS
from ..strategies.random_baseline import exposure_matched_random
from .lab_runner import _top5
from .registry import Registry
from .runner import load_inputs

CANDS = [("batch_2c_01", "NXF-01", {"lookback": 20, "tf": "D1"}), ("batch_2c_01", "NXF-01", {"lookback": 60, "tf": "D1"}),
         ("batch_2c_01", "NXF-02H4", {"n": 120, "tf": "H4"}), ("batch_2c_01", "NXF-03", {"lookback": 20, "tf": "D1", "vol_filter": True}),
         ("batch_2c_01", "REF-SMA-01", {"n": 50, "tf": "D1"}), ("batch_2c_02", "NXD-02", {"require_compression": False, "tf": "H4"})]


def main():
    p0, p1 = PERIODS["dev"]
    reg = Registry()
    reg.register_hypothesis({"key": "TECH-2D-02", "family": "TECH", "statement": "Concentration des profits des 6 candidats 2C vs entrées aléatoires.",
                             "rationale": "Les stratégies de tendance sont naturellement concentrées : comparer à la distribution attendue.",
                             "params": {"candidates": [f"{k} {json.dumps(v, sort_keys=True)}" for _, k, v in CANDS]},
                             "data": {"period": "dev", "symbols": ["BTCUSDT"]}, "metrics": ["top5_share"], "rejection": {"text": "aucun"}})
    sp = SPECS["BTCUSDT"]
    m1, _ = load_inputs("BTCUSDT", "dev")
    ex = ExecFrame.from_m1(m1, sp)
    out = []
    for batch, key, v in CANDS:
        row = next(r for r in json.loads((RESULTS_DIR / batch / "summary.json").read_text())
                   if r["hypothesis"] == key and json.loads(r["variant"]) == v)
        tr = pd.read_parquet(RESULTS_DIR / batch / f"trades_{row['trial_id']}.parquet")
        tid = reg.start_trial("TECH-2D-02", {"target": key, **v}, "BTCUSDT", "dev", 1.0, purpose="technique", seed=11)
        rnd = exposure_matched_random(tr, ex, sp, p0, p1, n_rep=300, seed=11)
        s = _top5(tr["side"] * (tr["exit"] - tr["entry"]) / tr["entry"])
        t5 = rnd["top5_share"][np.isfinite(rnd["top5_share"])]
        res = {"hypothesis": key, "variant": v, "n": len(tr), "strategy_top5_pct": s,
               "random_top5_median_pct": float(np.median(t5)), "random_top5_p5_p95": [float(np.percentile(t5, 5)), float(np.percentile(t5, 95))],
               "share_random_more_concentrated": float((t5 >= s).mean())}
        reg.finish_trial(tid, status="done", n_trades=len(tr))
        out.append(res)
        print(res, flush=True)
    d = RESULTS_DIR / "tech_audit_2d"; d.mkdir(exist_ok=True)
    (d / "concentration.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
