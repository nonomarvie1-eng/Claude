"""Export the Rally Path PROTOTYPE for the demo lab: strips, rules, exact stats,
reproducible scenarios (recorded draws) and TS parity fixtures.

Writes shared/rally-path-proto.json.  Nothing here touches the Stake export or
the normal game: the prototype only runs in the demo lab, without credits."""

from __future__ import annotations

import json
import os

import numpy as np

from . import config as C
from . import rally_path as R
from .engine import list_drawer

ROOT = os.path.dirname(os.path.dirname(C.HERE))


def _recording(rng):
    rec: list[list[int]] = []

    def draw(lengths):
        v = [int(rng.integers(0, n)) for n in lengths]
        rec.append(v)
        return v

    return draw, rec


def _search(mode, pred, seed, tries=400_000):
    rng = np.random.Generator(np.random.PCG64(seed))
    for _ in range(tries):
        draw, rec = _recording(rng)
        r = R.play_proto_round(draw, mode)
        if pred(r):
            return rec, r
    raise RuntimeError(f"scenario not found: {mode}")


def _rp(r):
    return [e for e in r["events"] if e["type"] == "rallyPath"]


SCENARIOS = [
    # key, mode, label, predicate
    ("no_return", "base", "Balle d'or sans retour", lambda r: r["length"] == 1),
    ("short", "base", "Échange court (2 coups)", lambda r: r["length"] == 2),
    ("three", "base", "Échange de 3 coups", lambda r: r["length"] == 3),
    ("five", "base", "Échange de 5 coups", lambda r: r["length"] == 5),
    ("full", "base", "Échange complet — Championship Shot", lambda r: r["length"] == 6),
    ("rally_plain", "rally", "Rally Challenge sans événement exceptionnel",
     lambda r: r["cs"] == 0 and r["rp"] >= 3 and max(r["lengths"] or [0]) <= 4 and 15 <= r["total_t"] / 10 <= 60),
    ("final_ss", "final", "Grand Final avec Second Serve",
     lambda r: r["second_serve"] == 1 and r["cs"] == 0 and any(L >= 3 for L in r["lengths"])),
    ("final_cs", "final", "Grand Final avec Championship Shot", lambda r: r["cs"] >= 1),
]


GAME_SCENARIOS = [
    ("game_full6", "Test : Rally Path complet 6 coups → Championship Shot", lambda r: r["length"] == 6 and r["bonus"] is None),
    ("game_rally", "Test : 3 scatters → Rally Challenge", lambda r: r["bonus"] == "rally" and 15 <= r["total_t"] / 10 <= 80),
    ("game_final", "Test : 4 scatters → The Grand Final", lambda r: r["bonus"] == "final" and any(e["type"] == "secondServe" for e in r["events"])),
]


def _search_game(pred, seed, tries=3_000_000):
    rng = np.random.Generator(np.random.PCG64(seed))
    strips = R.proto_reels("base")
    for _ in range(tries):
        draw, rec = _recording(rng)
        r = R.play_game_round(draw)
        if pred(r):
            return rec, r
    raise RuntimeError("game scenario not found")


def export() -> dict:
    rep = R.exact_report()
    scen = {}
    for i, (key, mode, label, pred) in enumerate(SCENARIOS):
        rec, r = _search(mode, pred, 100 + i)
        assert R.play_proto_round(list_drawer(rec), mode)["events"] == r["events"]
        scen[key] = {"mode": mode, "label": label, "draws": rec, "totalX": r["total_t"] / 10}
    game_scen = {}
    for i, (key, label, pred) in enumerate(GAME_SCENARIOS):
        rec, r = _search_game(pred, 300 + i)
        game_scen[key] = {"label": label, "draws": rec, "totalX": r["total_t"] / 10}
    # parity fixtures: random rounds of each mode with their Python events
    rng = np.random.Generator(np.random.PCG64(4242))
    fixtures = []
    for mode in ("base", "rally", "final"):
        for _ in range(12 if mode == "base" else 4):
            draw, rec = _recording(rng)
            r = R.play_proto_round(draw, mode)
            fixtures.append({"mode": mode, "draws": rec, "events": r["events"]})
    for key, s in scen.items():
        r = R.play_proto_round(list_drawer(s["draws"]), s["mode"])
        fixtures.append({"mode": s["mode"], "draws": s["draws"], "events": r["events"]})
    game_fx = []
    rng = np.random.Generator(np.random.PCG64(777))
    while len(game_fx) < 40 or sum(1 for f in game_fx if f["bonus"]) < 6:
        draw, rec = _recording(rng)
        r = R.play_game_round(draw)
        if len(game_fx) < 40 or r["bonus"]:
            game_fx.append({"draws": rec, "events": r["events"], "bonus": r["bonus"]})
    for s2 in game_scen.values():
        r = R.play_game_round(list_drawer(s2["draws"]))
        game_fx.append({"draws": s2["draws"], "events": r["events"], "bonus": r["bonus"]})
    P = C.RALLY_PATH_PROTO
    out = {
        "experimental": True,
        "note": "PROTOTYPE — demo lab only, no credits; not part of the Stake modes.",
        "rules": {
            "racket": P["RACKET"], "maxShots": P["MAX_SHOTS"], "reward": P["REWARD"], "csRoll": P["CS_ROLL"],
            "csTable": P["CS_TABLE"], "racketWaysPay": P["RACKET_WAYS_PAY"], "bonus": P["BONUS"],
        },
        "symbols": R.NAMES,
        "strips": {k: [[R.NAMES[x] for x in s] for s in R.proto_reels(k)] for k in ("base", "free")},
        "stats": {
            "base": {k: rep["base"][k] for k in ("p_golden_ball", "length_dist_given_ball", "p_full_rally", "championship_shot_1_in_spins", "E_rally_path_x", "E_ways_x")},
            "free": {k: rep["free"][k] for k in ("p_golden_ball", "length_dist_given_ball", "p_full_rally", "championship_shot_1_in_spins", "E_rally_path_x", "E_ways_x")},
            "bonus_rally": rep["bonus_rally"], "bonus_final": rep["bonus_final"],
            "prototype_rtp": rep["prototype_rtp"], "cs_mean_x": rep["cs_mean_x"],
        },
        "scenarios": scen,
        "fixtures": fixtures,
        "gameScenarios": game_scen,
        "gameFixtures": game_fx,
    }
    path = os.path.join(ROOT, "shared", "rally-path-proto.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    return out


if __name__ == "__main__":
    o = export()
    for k, s in o["scenarios"].items():
        print(k, s["mode"], len(s["draws"]), "draws", s["totalX"], "x")
