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

# Paying symbols are stacked in blocks of 1, 2 or 3 (probabilities below):
# fewer, bigger and more readable wins (hit rate ~28% instead of ~67%).
STACK = (0.3, 0.4, 0.3)

# v3 balance (derived with tune.py, exact maths): see docs/MATH_REPORT.md
_H = {"H1": 8, "H2": 9, "H3": 10, "H4": 11}
_L = {"L1": 12, "L2": 12, "L3": 13, "L4": 13}

BASE_COUNTS: dict[str, list[int]] = {
    "W": [0, 0, 1, 1, 1, 1],
    "S": [1, 2, 1, 2, 1, 2],
    **{k: [v] * NUM_REELS for k, v in _H.items()},
    **{k: [v] * NUM_REELS for k, v in _L.items()},
    "L5": [15, 15, 15, 16, 16, 16],
}

# Bonus Chance mode: BASE plus extra scatters (chosen in tune.py)
BC_COUNTS: dict[str, list[int]] = {**BASE_COUNTS, "S": [2, 2, 2, 2, 2, 2]}

FREE_COUNTS: dict[str, list[int]] = {
    "W": [0, 1, 1, 1, 1, 1],
    "S": [1, 1, 1, 1, 1, 1],
    **{k: [v] * NUM_REELS for k, v in _H.items()},
    **{k: [v] * NUM_REELS for k, v in _L.items()},
    "L5": [14] * NUM_REELS,
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


def build_strip_stacked(counts: dict[str, int], rng: np.random.Generator, stack: tuple[float, ...],
                        max_tries: int = 500_000) -> list[str]:
    """Paying symbols are cut into blocks of 1..len(stack) identical symbols
    (block size drawn with probabilities `stack`); Wild and Scatter stay single.
    Symbol counts are preserved exactly."""
    sizes = np.arange(1, len(stack) + 1)
    for _ in range(max_tries):
        blocks = []
        for s, c in counts.items():
            left = c
            while left > 0:
                b = 1 if s in ("W", "S") else int(min(left, rng.choice(sizes, p=stack)))
                blocks.append([s] * b)
                left -= b
        order = rng.permutation(len(blocks))
        strip = [x for i in order for x in blocks[i]]
        if _valid(strip):
            return [str(x) for x in strip]
    raise RuntimeError("could not build a valid stacked strip")


def build_reelset(counts: dict[str, list[int]], seed: int, stack: tuple[float, ...] | None = None) -> list[list[str]]:
    rng = np.random.default_rng(seed)
    strips = []
    for r in range(NUM_REELS):
        c = {s: counts[s][r] for s in SYMBOLS if counts.get(s, [0] * NUM_REELS)[r] > 0}
        strips.append(build_strip_stacked(c, rng, stack) if stack else build_strip(c, rng))
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
    write_reelset("BASE", build_reelset(BASE_COUNTS, seed=55, stack=STACK))
    write_reelset("FREE", build_reelset(FREE_COUNTS, seed=6, stack=STACK))
    write_reelset("BASE_BC", build_reelset(BC_COUNTS, seed=57, stack=STACK))
    print("reel strips written to", REELS_DIR)


if __name__ == "__main__":
    main()
