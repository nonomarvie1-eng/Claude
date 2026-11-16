"""Export GOLDEN SERVE — RETURN SPINS for the game -> shared/return-spins.json:
rules, strips, simulated statistics, development scenarios (recorded draws)
and TS parity fixtures."""

from __future__ import annotations

import json
import os

import numpy as np

from . import config as C
from . import return_spins as RS
from .engine import list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))


def _serves(r):
    return [e for e in r["events"] if e["type"] == "serve"]


def _stages(r):
    return [e["stageWin"] for e in r["events"] if e["type"] == "stageWin"]


SCEN = [
    ("plain", "1 · Spin ordinaire sans Golden Serve", lambda r: r["bonus"] is None and not r["served"] and r["total_t"] > 0),
    ("center", "2 · Golden Serve → rouleaux centraux 3-4", lambda r: r["bonus"] is None and len(_serves(r)) == 1 and _serves(r)[0]["zone"] == "center" and _stages(r)[1] > 0),
    ("returns", "3 · Golden Serve + 2 Return Spins", lambda r: r["bonus"] is None and r["returns"] == 2),
    ("nowin", "4 · Événement sans gain après les relances", lambda r: r["bonus"] is None and r["served"] and sum(_stages(r)) == 0),
    ("win", "5 · Gain visible et cumulé sur deux arrêts", lambda r: r["bonus"] is None and len(_stages(r)) == 2 and _stages(r)[0] > 0 and _stages(r)[1] > _stages(r)[0] and _stages(r)[1] >= 200),
    ("smash", "6 · Golden Smash sur quatre rouleaux", lambda r: r["bonus"] is None and any(s["smash"] for s in _serves(r)) and sum(_stages(r)[1:]) > 0),
    ("rally", "3 scatters → Rally Challenge", lambda r: r["bonus"] == "rally" and 20 <= r["total_t"] / 10 <= 80),
    ("final", "4 scatters → Championship Night", lambda r: r["bonus"] == "final" and any(e["type"] == "serve" and e["smash"] for e in r["events"])),
]


def _rec(rng):
    rec = []

    def draw(lengths):
        v = [int(rng.integers(0, n)) for n in lengths]
        rec.append(v)
        return v

    return draw, rec


def export():
    sim = json.load(open(os.path.join(os.path.dirname(C.HERE), "reports", "return_spins_sim.json")))
    scen = {}
    for i, (k, label, pred) in enumerate(SCEN):
        rng = np.random.Generator(np.random.PCG64(700 + i))
        for _ in range(3_000_000):
            draw, rec = _rec(rng)
            r = RS.play_round(draw)
            if pred(r):
                break
        else:
            raise RuntimeError(k)
        scen[k] = {"label": label, "draws": rec, "totalX": r["total_t"] / 10, "stagesX": [x / 100 for x in _stages(r)] if r["bonus"] is None else None}
    fx = []
    rng = np.random.Generator(np.random.PCG64(4242))
    nb = ns = 0
    while len(fx) < 80 or nb < 4 or ns < 15:
        draw, rec = _rec(rng)
        r = RS.play_round(draw)
        if len(fx) < 80 or r["bonus"] or r["served"]:
            fx.append({"draws": rec, "events": r["events"]})
            nb += bool(r["bonus"])
            ns += r["served"]
    for s in scen.values():
        fx.append({"draws": s["draws"], "events": RS.play_round(list_drawer(s["draws"]))["events"]})
    out = {
        "experimental": True,
        "rules": {k: C.RETURN_SPINS[k] for k in ("G_PER_REEL", "P_SMASH", "MAX_RETURNS", "BONUS")},
        "zones": RS.ZONES,
        "strips": {k: [[RS.NAMES[x] for x in s] for s in RS.strips_of(k)] for k in ("base", "free")},
        "stats": {"game": sim["game"], "bonus_rally": sim["bonus_rally"], "bonus_final": sim["bonus_final"], "seed": sim["seed"], "n": sim["n"], "n_bonus": sim["n_bonus"]},
        "scenarios": scen,
        "fixtures": fx,
    }
    with open(os.path.join(ROOT, "shared", "return-spins.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


if __name__ == "__main__":
    o = export()
    for k, s in o["scenarios"].items():
        print(k, len(s["draws"]), s["totalX"], s["stagesX"])
    print(len(o["fixtures"]), "fixtures")
