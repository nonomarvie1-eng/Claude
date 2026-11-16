import { describe, expect, it } from 'vitest';
import { GS, playGsRound } from './goldenServe';
import { listDrawer } from './rng';

describe('Golden Serve prototypes: TS parity with the Python reference', () => {
  it('has fixtures for both concepts, with bonus rounds', () => {
    for (const c of ['A', 'B'] as const) expect(GS.fixtures.filter((f) => f.concept === c).length).toBeGreaterThanOrEqual(44);
  });
  it('reproduces every fixture exactly (board, shot, trajectory, changes, wins)', () => {
    for (const f of GS.fixtures) expect(playGsRound(listDrawer(f.draws), f.concept).book.events).toEqual(f.events);
  });
  it('scenarios replay to their recorded totals for both concepts', () => {
    for (const s of Object.values(GS.scenarios))
      for (const c of ['A', 'B'] as const) expect(playGsRound(listDrawer(s.draws), c).book.payoutMultiplier / 100).toBeCloseTo(s.totalX[c], 6);
  });
  it('the smash scenario is a smash and shows a racket shot event', () => {
    const ev = playGsRound(listDrawer(GS.scenarios.smash.draws), 'A').book.events;
    const g = ev.find((e) => e.type === 'goldenServe') as { shot: string; paths: unknown[] } | undefined;
    expect(g?.shot).toBe('smash');
    expect(g?.paths.length).toBe(2);
  });
});
