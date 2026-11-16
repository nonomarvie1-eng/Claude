import { describe, expect, it } from 'vitest';
import { RS, playRsRound } from './returnSpins';
import { listDrawer } from './rng';

describe('Return Spins: TS parity with the Python reference', () => {
  it('reproduces every fixture exactly (stops, strikes, respins, stage wins, bonuses)', () => {
    expect(RS.fixtures.length).toBeGreaterThanOrEqual(90);
    for (const f of RS.fixtures) expect(playRsRound(listDrawer(f.draws)).book.events).toEqual(f.events);
  });
  it('development scenarios replay to their recorded totals and stage wins', () => {
    for (const s of Object.values(RS.scenarios)) {
      const r = playRsRound(listDrawer(s.draws));
      expect(r.book.payoutMultiplier / 100).toBeCloseTo(s.totalX, 6);
      if (s.stagesX) expect(r.book.events.filter((e) => e.type === 'stageWin').map((e) => (e as { stageWin: number }).stageWin / 100)).toEqual(s.stagesX);
    }
  });
  it('scenario contents', () => {
    const ev = (k: string) => playRsRound(listDrawer(RS.scenarios[k].draws)).book.events;
    expect(ev('plain').some((e) => e.type === 'serve')).toBe(false);
    const c = ev('center').filter((e) => e.type === 'serve') as { zone: string; reels: number[] }[];
    expect(c[0].zone).toBe('center');
    expect(c[0].reels).toEqual([2, 3]);
    expect(ev('returns').filter((e) => e.type === 'serve' && (e as { kind: string }).kind === 'return').length).toBe(2);
    const sm = ev('smash').find((e) => e.type === 'serve' && (e as { smash: boolean }).smash) as { reels: number[] };
    expect(sm.reels.length).toBe(4);
  });
});
