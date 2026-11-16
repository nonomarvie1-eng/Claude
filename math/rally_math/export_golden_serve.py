"""Export Golden Serve prototypes (A Cross-Court / B Court Switch) for the game:
shared/golden-serve-proto.json = rules, strips, simulated stats, reproducible
scenarios (recorded draws, valid for both concepts) and TS parity fixtures."""

from __future__ import annotations

import json
import os

import numpy as np

from . import config as C
from . import golden_serve as GS
from .engine import list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))


def _rec(rng):
    rec = []

    def draw(lengths):
        v = [int(rng.integers(0, n)) for n in lengths]
        rec.append(v)
        return v

    return draw, rec


def _shots(r, kind):
    return [e for e in r["events"] if e["type"] == "goldenServe" and e["shot"] == kind]


SCEN = [
    ("serve", "Golden Serve (jeu de base)", lambda r: r["bonus"] is None and len(_shots(r, "serve")) == 1 and 4 <= r["total_t"] / 10 <= 40),
    ("smash", "Golden Smash (jeu de base)", lambda r: r["bonus"] is None and len(_shots(r, "smash")) == 1 and r["total_t"] / 10 >= 15),
    ("rally", "3 scatters → Rally Challenge", lambda r: r["bonus"] == "rally" and len(r["shots"]) >= 3 and 20 <= r["total_t"] / 10 <= 120),
    ("final", "4 scatters → The Grand Final (Smash + Double Serve)", lambda r: r["bonus"] == "final" and "smash" in r["shots"] and "double" in r["shots"]),
]


def export():
    sim = json.load(open(os.path.join(os.path.dirname(C.HERE), "reports", "golden_serve_sim.json")))
    scen = {}
    for i, (k, label, pred) in enumerate(SCEN):
        rng = np.random.Generator(np.random.PCG64(500 + i))
        for _ in range(5_000_000):
            draw, rec = _rec(rng)
            r = GS.play_round(draw, "A")
            if pred(r):
                break
        else:
            raise RuntimeError(k)
        scen[k] = {"label": label, "draws": rec, "totalX": {c: GS.play_round(list_drawer(rec), c)["total_t"] / 10 for c in "AB"}}
    fx = []
    rng = np.random.Generator(np.random.PCG64(4040))
    for c in "AB":
        nb = 0
        while sum(1 for f in fx if f["concept"] == c) < 40 or nb < 4:
            draw, rec = _rec(rng)
            r = GS.play_round(draw, c)
            if sum(1 for f in fx if f["concept"] == c) < 40 or r["bonus"]:
                fx.append({"concept": c, "draws": rec, "events": r["events"]})
                nb += bool(r["bonus"])
        for s in scen.values():
            fx.append({"concept": c, "draws": s["draws"], "events": GS.play_round(list_drawer(s["draws"]), c)["events"]})
    P = C.GOLDEN_SERVE_PROTO
    out = {
        "experimental": True,
        "rules": {k: P[k] for k in ("G_ON_REEL1", "TARGET_SYMS", "TARGET_W", "P_SMASH", "P_DOUBLE", "BONUS")},
        "serveDraw": GS.SERVE_DRAW,
        "strips": {k: [[GS.NAMES[x] for x in s] for s in GS.strips_of(k)] for k in ("base", "free")},
        "stats": {c: {"game": sim[c]["game"], "bonus_rally": sim[c]["bonus_rally"], "bonus_final": sim[c]["bonus_final"],
                      "base": sim[c]["base_components"], "seed": sim[c]["seed"], "n": sim[c]["n"], "n_bonus": sim[c]["n_bonus"]} for c in "AB"},
        "scenarios": scen,
        "fixtures": fx,
    }
    with open(os.path.join(ROOT, "shared", "golden-serve-proto.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


if __name__ == "__main__":
    o = export()
    for k, s in o["scenarios"].items():
        print(k, len(s["draws"]), s["totalX"])
    print(len(o["fixtures"]), "fixtures")
