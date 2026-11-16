import { describe, expect, it } from 'vitest';
import { GAME_FIXTURES, GAME_SCENARIOS, PROTO, playGameRound, playProtoRound, rally } from './rallyPath';
import { listDrawer } from './rng';
import type { Board } from './types';

describe('Rally Path prototype: TS parity with the Python reference', () => {
  it('has fixtures for the three prototype modes and every scenario', () => {
    expect(PROTO.fixtures.length).toBeGreaterThanOrEqual(28);
    expect(Object.keys(PROTO.scenarios)).toHaveLength(8);
  });
  it('reproduces every fixture exactly', () => {
    for (const f of PROTO.fixtures) expect(playProtoRound(listDrawer(f.draws), f.mode).events).toEqual(f.events);
  });
  it('scenarios replay to their recorded totals', () => {
    for (const s of Object.values(PROTO.scenarios)) {
      const r = playProtoRound(listDrawer(s.draws), s.mode);
      expect(r.totalT / 10).toBeCloseTo(s.totalX, 6);
    }
  });
  it('path rule: same row or one row, never two', () => {
    const col = (s: string) => [...s].map((c) => (c === 'G' ? 'G' : c === 'R' ? 'H4' : 'L5'));
    const b = ['G....', '..R..', 'RRRRR', 'RRRRR', 'RRRRR', 'RRRRR'].map(col) as Board;
    expect(rally(b)!.length).toBe(1);
    const d = ['G....', '.R...', '..R..', '...R.', '....R', '...R.'].map(col) as Board;
    expect(rally(d)!.length).toBe(6);
  });
});

describe('Rally Path game round (test build RALLY-PATH-01)', () => {
  it('reproduces every Python game-round fixture exactly, bonus rounds included', () => {
    expect(GAME_FIXTURES.filter((f) => f.bonus).length).toBeGreaterThanOrEqual(6);
    for (const f of GAME_FIXTURES) expect(playGameRound(listDrawer(f.draws)).book.events).toEqual(f.events);
  });
  it('the 6-shot test scenario is a Championship Shot and never emits old Final Set events', () => {
    const r = playGameRound(listDrawer(GAME_SCENARIOS.game_full6.draws));
    const rp = r.book.events.find((e) => e.type === 'rallyPath');
    expect(rp && rp.type === 'rallyPath' && rp.length === 6 && rp.championshipShot).toBe(true);
    for (const s of Object.values(GAME_SCENARIOS)) {
      const ev = playGameRound(listDrawer(s.draws)).book.events;
      expect(ev.some((e) => ['bonusStart', 'hawkEye', 'shot', 'exchangeStart'].includes(e.type))).toBe(false);
    }
  });
});
