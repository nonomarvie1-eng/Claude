import { describe, expect, it } from 'vitest';
import { DUEL, playDuelRound, playSinglePoint } from './duel';
import { listDrawer } from './rng';

describe('Championship Duel: TS parity with the Python reference', () => {
  it('reproduces every fixture exactly (rounds with bonuses and single points)', () => {
    expect(DUEL.fixtures.filter((f) => f.kind === 'round').length).toBeGreaterThanOrEqual(60);
    for (const f of DUEL.fixtures) {
      if (f.kind === 'round') expect(playDuelRound(listDrawer(f.draws)).book.events).toEqual(f.events);
      else expect(playSinglePoint(f.level, f.draws).events).toEqual(f.events);
    }
  });
  it('point scenarios give their documented outcome', () => {
    for (const s of Object.values(DUEL.pointScenarios)) {
      const p = playSinglePoint(s.level, s.draws).point;
      expect(p.outcome).toBe(s.outcome);
      expect(p.prize).toBe(s.prizeX);
    }
    expect(DUEL.pointScenarios.double_fault.outcome).toBe('DOUBLE_FAULT');
    expect(DUEL.pointScenarios.ace.outcome).toBe('ACE');
    expect(DUEL.pointScenarios.winner.outcome).toBe('WINNER');
  });
  it('round scenarios trigger the right level', () => {
    expect(playDuelRound(listDrawer(DUEL.roundScenarios.tiebreak.draws)).level).toBe('tiebreak');
    expect(playDuelRound(listDrawer(DUEL.roundScenarios.final.draws)).level).toBe('final');
  });
});
