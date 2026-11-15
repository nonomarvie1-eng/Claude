import { describe, expect, it } from 'vitest';
import { playBook, tierFor, type Hud, type View } from './player';
import { playRound } from '../engine/engine';
import { cryptoDrawer, cryptoInt } from '../engine/rng';
import { drawBaseStopsWithScatters } from '../engine/engine';
import type { Board } from '../engine/types';
import { winAmount } from './format';

function recorder() {
  const boards: Board[] = [];
  const log: string[] = [];
  let shownWin = 0;
  let fs = [0, 0];
  let mult = 1;
  const view: View = {
    setMode: (m) => log.push('mode:' + m),
    spinTo: async (b) => void boards.push(b),
    showWins: async () => void log.push('wins'),
    clearWins: () => {},
    scatterCelebrate: async () => {},
    bonusIntro: async () => void log.push('intro'),
    wind: async (_p, _c, m) => void log.push('wind:' + m),
    retrigger: async () => void log.push('retrigger'),
    bonusOutro: async () => void log.push('outro'),
    bigWin: async (_a, t) => void log.push('big:' + t),
    wincap: async () => void log.push('wincap'),
    pause: async () => {},
  };
  const hud: Hud = {
    setWin: (a) => (shownWin = a),
    setFreeSpins: (c, t) => (fs = [c, t]),
    setMultiplier: (m) => (mult = m),
    setInBonus: () => {},
  };
  return { view, hud, boards, log, get win() { return shownWin; }, get fs() { return fs; }, get mult() { return mult; } };
}

describe('display / result consistency', () => {
  it('every displayed board and the final displayed win come from the book', async () => {
    const bet = 2_000_000;
    for (let i = 0; i < 400; i++) {
      const forced = i % 4 === 0 ? drawBaseStopsWithScatters(3, cryptoInt) : undefined;
      const { book } = playRound(cryptoDrawer, i, forced);
      const rec = recorder();
      const { total } = await playBook(book.events, rec.view, rec.hud, { bet });
      const reveals = book.events.filter((e) => e.type === 'reveal').map((e) => (e as { board: Board }).board);
      expect(rec.boards).toEqual(reveals);
      expect(total).toBe(winAmount(bet, book.payoutMultiplier));
      expect(rec.win).toBe(total);
      const trig = book.events.find((e) => e.type === 'freeSpinTrigger');
      if (trig) {
        expect(rec.log).toContain('intro');
        expect(rec.log).toContain('outro');
        const lastFs = book.events.filter((e) => e.type === 'updateFreeSpin').pop() as { amount: number; total: number };
        expect(rec.fs).toEqual([lastFs.amount, lastFs.total]);
        const winds = book.events.filter((e) => e.type === 'rallyUp') as { multiplier: number }[];
        expect(rec.mult).toBe(winds.length ? winds[winds.length - 1].multiplier : 1);
      }
    }
  });

  it('never celebrates a win that does not exceed the bet (no LDW celebration)', () => {
    expect(tierFor(0, 100)).toBe('none');
    expect(tierFor(50, 100)).toBe('ldw');
    expect(tierFor(100, 100)).toBe('ldw');
    expect(tierFor(101, 100)).toBe('small');
    expect(tierFor(1000, 100)).toBe('big');
    expect(tierFor(5000, 100)).toBe('mega');
    expect(tierFor(20000, 100)).toBe('epic');
  });

  it('quick (resume) mode skips the big-win celebration but shows the same result', async () => {
    const { book } = playRound(cryptoDrawer, 1, drawBaseStopsWithScatters(5, cryptoInt));
    const rec = recorder();
    const { total } = await playBook(book.events, rec.view, rec.hud, { bet: 1_000_000, quick: true });
    expect(rec.log.some((l) => l.startsWith('big:'))).toBe(false);
    expect(total).toBe(winAmount(1_000_000, book.payoutMultiplier));
  });
});
