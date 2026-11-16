"""Export CHAMPIONSHIP DUEL for the game: rules, exact report, reproducible
single-point scenarios, full-round scenarios and TS parity fixtures
-> shared/championship-duel.json"""

from __future__ import annotations

import json
import os

import numpy as np

from . import championship_duel as CD
from . import config as C
from .engine import list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))

POINT_SCEN = [
    # key, level, label, predicate on the point
    ("double_fault", "tiebreak", "Double faute", lambda p: p["outcome"] == "DOUBLE_FAULT"),
    ("ace", "tiebreak", "Ace (premier service)", lambda p: p["outcome"] == "ACE" and p["firstServe"] == "ACE"),
    ("winner", "tiebreak", "Coup gagnant", lambda p: p["outcome"] == "WINNER" and p["secondServe"] is None and p["shots"] == 3),
    ("rally_lost", "tiebreak", "Échange perdu", lambda p: p["outcome"] == "LOST" and p["shots"] >= 3),
    ("second_ace", "tiebreak", "Faute puis ace en second service", lambda p: p["outcome"] == "ACE" and p["firstServe"] == "FAULT"),
    ("golden_smash", "final", "Golden Smash (Grand Final)", lambda p: p["outcome"] == "GOLDEN" and not p["goldenMatchPoint"]),
    ("golden_match_point", "final", "Golden Match Point gagné", lambda p: p["goldenMatchPoint"] and p["won"]),
]


def export():
    rep = json.load(open(os.path.join(os.path.dirname(C.HERE), "reports", "championship_duel_exact.json")))
    scen = {}
    for i, (k, lv, label, pred) in enumerate(POINT_SCEN):
        rng = np.random.Generator(np.random.PCG64(900 + i))
        for _ in range(2_000_000):
            d = [int(x) for x in rng.integers(0, 1000, 6)]
            p = CD.play_point(lv, d, 0)
            if pred(p):
                break
        else:
            raise RuntimeError(k)
        scen[k] = {"level": lv, "label": label, "draws": d, "prizeX": p["prize"], "outcome": p["outcome"]}
    rounds = {}
    for k, want in (("tiebreak", "tiebreak"), ("final", "final")):
        rng = np.random.Generator(np.random.PCG64(950 + len(k)))
        while True:
            rec = []

            def draw(lengths, rec=rec):
                v = [int(rng.integers(0, n)) for n in lengths]
                rec.append(v)
                return v

            r = CD.play_round(draw)
            if r["level"] == want:
                rounds[k] = {"label": "3 scatters → TIE-BREAK DUEL" if want == "tiebreak" else "4 scatters → THE GRAND FINAL", "draws": rec, "totalX": r["total_t"] / 10}
                break
    fx = []
    rng = np.random.Generator(np.random.PCG64(4141))
    nb = 0
    while len(fx) < 60 or nb < 6:
        rec = []

        def draw(lengths, rec=rec):
            v = [int(rng.integers(0, n)) for n in lengths]
            rec.append(v)
            return v

        r = CD.play_round(draw)
        if len(fx) < 60 or r["level"]:
            fx.append({"kind": "round", "draws": rec, "events": r["events"]})
            nb += bool(r["level"])
    for s in rounds.values():
        fx.append({"kind": "round", "draws": s["draws"], "events": CD.play_round(list_drawer(s["draws"]))["events"]})
    for lv in ("tiebreak", "final"):
        for _ in range(150):
            d = [int(x) for x in rng.integers(0, 1000, 6)]
            fx.append({"kind": "point", "level": lv, "draws": d, "events": CD.play_single_point(lv, d)["events"]})
    out = {
        "experimental": True,
        "rules": C.CHAMPIONSHIP_DUEL,
        "exact": {"rtp": rep["rtp"], "p_tiebreak": rep["p_tiebreak"], "p_final": rep["p_final"],
                  "tiebreak": rep["tiebreak"], "final": rep["final"]},
        "pointScenarios": scen,
        "roundScenarios": rounds,
        "fixtures": fx,
    }
    with open(os.path.join(ROOT, "shared", "championship-duel.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


if __name__ == "__main__":
    o = export()
    for k, s in o["pointScenarios"].items():
        print(k, s["draws"], s["outcome"], s["prizeX"])
    print({k: v["totalX"] for k, v in o["roundScenarios"].items()}, len(o["fixtures"]))
