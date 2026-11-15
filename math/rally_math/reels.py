"""Deterministic reel-strip generator (6 reels, windows of 5 rows).

Constraints repaired by rejection sampling:
  * scatters at least NUM_ROWS positions apart (at most one per reel window);
  * wilds at least 2 positions apart and never adjacent to a scatter.
"""

from __future__ import annotations

import csv
import os

import numpy as np

from .config import NUM_REELS, NUM_ROWS, REELS_DIR, SYMBOLS

BASE_COUNTS: dict[str, list[int]] = {
    "W":  [0, 1, 1, 1, 1, 1],
    "S":  [1, 2, 1, 2, 1, 2],
    "H1": [7, 7, 7, 7, 7, 7],
    "H2": [8, 8, 8, 8, 8, 8],
    "H3": [9, 9, 9, 9, 9, 9],
    "H4": [10, 10, 10, 10, 10, 10],
    "H5": [10, 10, 10, 10, 10, 10],
    "L1": [11, 11, 11, 11, 11, 11],
    "L2": [11, 11, 11, 11, 11, 11],
    "L3": [12, 12, 12, 12, 12, 12],
    "L4": [12, 12, 12, 12, 12, 12],
    "L5": [13, 13, 13, 13, 13, 13],
}

FREE_COUNTS: dict[str, list[int]] = {
    "W":  [0, 3, 3, 3, 3, 3],
    "S":  [1, 1, 1, 1, 1, 1],
    "H1": [7, 7, 7, 7, 7, 7],
    "H2": [8, 8, 8, 8, 8, 8],
    "H3": [9, 9, 9, 9, 9, 9],
    "H4": [10, 10, 10, 10, 10, 10],
    "H5": [10, 10, 10, 10, 10, 10],
    "L1": [11, 11, 11, 11, 11, 11],
    "L2": [11, 11, 11, 11, 11, 11],
    "L3": [12, 12, 12, 12, 12, 12],
    "L4": [12, 12, 12, 12, 12, 12],
    "L5": [13, 13, 13, 13, 13, 13],
}


def _valid(strip: list[str]) -> bool:
    n = len(strip)
    for i, s in enumerate(strip):
        if s == "S":
            for d in range(1, NUM_ROWS):
                if strip[(i + d) % n] == "S":
                    return False
        if s == "W":
            if strip[(i + 1) % n] in ("W", "S") or strip[(i - 1) % n] == "S":
                return False
    return True


def build_strip(counts: dict[str, int], rng: np.random.Generator, max_tries: int = 500_000) -> list[str]:
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
    write_reelset("BASE", build_reelset(BASE_COUNTS, seed=1))
    write_reelset("FREE", build_reelset(FREE_COUNTS, seed=2))
    print("reel strips written to", REELS_DIR)


if __name__ == "__main__":
    main()
