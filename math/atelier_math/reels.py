"""Deterministic reel-strip generator.

Strips are built from per-reel symbol counts, shuffled with a fixed seed and
repaired so that:
  * two scatters are always at least 3 positions apart (circularly), so a reel
    window of 3 rows shows at most one scatter;
  * a wild never sits directly next to a scatter or another wild.
The resulting strips are written to math/reels/*.csv and are the ONLY input
used by the exact calculator, the simulator, the book exporter and the TS
demo engine (through shared/game-config.json).
"""

from __future__ import annotations

import csv
import os

import numpy as np

from .config import NUM_REELS, REELS_DIR, SYMBOLS

# symbol counts per reel  (reel 1 .. reel 5)
BASE_COUNTS: dict[str, list[int]] = {
    "W": [0, 3, 3, 3, 0],
    "S": [2, 1, 1, 1, 2],
    "H1": [2, 2, 2, 2, 2],
    "H2": [3, 3, 3, 3, 3],
    "H3": [4, 4, 4, 4, 4],
    "H4": [5, 5, 5, 5, 5],
    "L1": [6, 6, 6, 6, 6],
    "L2": [7, 7, 7, 7, 7],
    "L3": [7, 7, 7, 7, 7],
    "L4": [7, 7, 7, 7, 7],
}

FREE_COUNTS: dict[str, list[int]] = {
    "W": [0, 2, 2, 2, 0],
    "S": [1, 1, 1, 1, 1],
    "H1": [3, 3, 3, 3, 3],
    "H2": [3, 3, 3, 3, 3],
    "H3": [4, 4, 4, 4, 4],
    "H4": [4, 4, 4, 4, 4],
    "L1": [3, 3, 3, 3, 3],
    "L2": [4, 4, 4, 4, 4],
    "L3": [3, 4, 4, 4, 3],
    "L4": [3, 4, 4, 4, 3],
}


def _valid(strip: list[str]) -> bool:
    n = len(strip)
    for i, s in enumerate(strip):
        if s == "S":
            for d in (1, 2):
                if strip[(i + d) % n] == "S":
                    return False
        if s == "W":
            if strip[(i + 1) % n] in ("W", "S") or strip[(i - 1) % n] == "S":
                return False
    return True


def build_strip(counts: dict[str, int], rng: np.random.Generator, max_tries: int = 200_000) -> list[str]:
    pool = [s for s, c in counts.items() for _ in range(c)]
    for _ in range(max_tries):
        perm = list(rng.permutation(pool))
        if _valid(perm):
            return [str(x) for x in perm]
    raise RuntimeError("could not build a valid strip with these counts")


def build_reelset(counts: dict[str, list[int]], seed: int) -> list[list[str]]:
    rng = np.random.default_rng(seed)
    strips = []
    for r in range(NUM_REELS):
        c = {s: counts[s][r] for s in SYMBOLS if counts.get(s, [0] * NUM_REELS)[r] > 0}
        strips.append(build_strip(c, rng))
    return strips


def write_reelset(name: str, strips: list[list[str]]) -> str:
    os.makedirs(REELS_DIR, exist_ok=True)
    path = os.path.join(REELS_DIR, f"{name}.csv")
    rows = max(len(s) for s in strips)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for i in range(rows):
            w.writerow([s[i] if i < len(s) else "" for s in strips])
    return path


def main() -> None:
    write_reelset("BASE", build_reelset(BASE_COUNTS, seed=20261115))
    write_reelset("FREE", build_reelset(FREE_COUNTS, seed=20261116))
    print("reel strips written to", REELS_DIR)


if __name__ == "__main__":
    main()
