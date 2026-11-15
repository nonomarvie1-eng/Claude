import { describe, expect, it } from 'vitest';
import fixtures from '$shared/parity-fixtures.json';
import { playRound, evaluateWays, drawBaseStopsWithScatters, positionsOf, windowOf, STRIPS } from './engine';
import { cryptoDrawer, cryptoInt, listDrawer } from './rng';
import { RULES } from './rules';
import type { Book } from './types';

type Fixture = { stops: number[][]; book: Book; bought?: boolean };

describe('TS engine parity with the Python reference engine', () => {
  const fx = fixtures as unknown as Fixture[];
  it('has fixtures including bonus rounds', () => {
    expect(fx.length).toBeGreaterThanOrEqual(100);
    expect(fx.filter((f) => f.book.events.some((e) => e.type === 'freeSpinTrigger')).length).toBeGreaterThan(40);
  });
  it('reproduces every fixture book exactly (events, payouts)', () => {
    for (const f of fx) {
      const out = playRound(listDrawer(f.stops), f.book.id, undefined, !!f.bought);
      expect(out.book).toEqual(f.book);
    }
  });
});

describe('ways evaluation', () => {
  it('multiplies matches per reel and substitutes wilds', () => {
    const b = [
      ['H2', 'H2', 'L1', 'L1', 'L1'],
      ['W', 'L2', 'L2', 'L2', 'L2'],
      ['H2', 'H2', 'H2', 'L3', 'L3'],
      ['H2', 'L4', 'L4', 'L4', 'L4'],
      ['L5', 'L5', 'L5', 'L5', 'L5'],
      ['H2', 'H2', 'H2', 'H2', 'H2'],
    ] as const;
    const w = evaluateWays(b.map((c) => [...c])).find((x) => x.symbol === 'H2')!;
    expect(w.reels).toBe(4);
    expect(w.ways).toBe(6);
    expect(w.payPerWay).toBe(RULES.paytable.H2['4'] / 10);
  });
});

describe('round invariants (random rounds)', () => {
  it('book totals are consistent and capped', () => {
    for (let i = 0; i < 3000; i++) {
      const { book } = playRound(cryptoDrawer, i);
      expect(book.payoutMultiplier % 10).toBe(0);
      expect(book.payoutMultiplier).toBeLessThanOrEqual(RULES.wincapX * 100);
      const fin = book.events.filter((e) => e.type === 'finalWin');
      expect(fin).toHaveLength(1);
      const sum = book.events.reduce((a, e) => a + (e.type === 'winInfo' ? e.totalWin : 0), 0);
      expect(Math.min(sum, RULES.wincapX * 100)).toBe(book.payoutMultiplier);
    }
  });
});

describe('demo bonus tester', () => {
  it('draws base stops with exactly k scatters', () => {
    for (const k of [3, 4, 5]) {
      for (let i = 0; i < 50; i++) {
        const stops = drawBaseStopsWithScatters(k, cryptoInt);
        expect(positionsOf(windowOf(STRIPS.base, stops), 'S')).toHaveLength(k);
      }
    }
  });
});

describe('RNG', () => {
  it('cryptoInt is uniform (chi-square, 7 bins, 70k draws)', () => {
    const n = 7, N = 70_000;
    const c = new Array(n).fill(0);
    for (let i = 0; i < N; i++) c[cryptoInt(n)]++;
    const chi = c.reduce((a, o) => a + (o - N / n) ** 2 / (N / n), 0);
    expect(chi).toBeLessThan(22.46); // p = 0.001, 6 dof
  });
  it('rejects invalid ranges', () => {
    expect(() => cryptoInt(0)).toThrow();
  });
});
