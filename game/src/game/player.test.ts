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
  const shots: unknown[] = [];
  const ends: unknown[] = [];
  let shownWin = 0;
  let fs = [0, 0];
  let mult = 1;
  const view: View = {
    setMode: (m) => log.push('mode:' + m),
    spinTo: async (b) => void boards.push(b),
    showWins: async () => void log.push('wins'),
    clearWins: () => {},
    scatterCelebrate: async () => {},
    bonusIntro: async (e) => void log.push('intro:' + e.bonus),
    exchangeStart: async (e) => void log.push('ex:' + e.exchange + (e.championshipPoint ? ':cp' : '')),
    showCourt: async () => {},
    hawkEye: async (e) => void log.push('hawk:' + e.call),
    shot: async (e) => void shots.push(e),
    grandSlam: async () => void log.push('slam'),
    marksExpire: async () => {},
    extraExchange: async (e) => void log.push('extra:' + e.added),
    exchangeEnd: async (e) => void ends.push(e),
    bonusOutro: async (e) => void log.push('outro:' + e.ceremony),
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
  return { view, hud, boards, log, shots, ends, get win() { return shownWin; }, get fs() { return fs; }, get mult() { return mult; } };
}

describe('display / result consistency', () => {
  it('every displayed board and the final displayed win come from the book', async () => {
    const bet = 2_000_000;
    for (let i = 0; i < 400; i++) {
      const forced = i % 4 === 0 ? drawBaseStopsWithScatters(3 + (i % 8 === 0 ? 1 : 0), cryptoInt) : undefined;
      const { book } = playRound(cryptoDrawer, i, forced);
      const rec = recorder();
      const { total } = await playBook(book.events, rec.view, rec.hud, { bet });
      const reveals = book.events.filter((e) => e.type === 'reveal').map((e) => (e as { board: Board }).board);
      expect(rec.boards).toEqual(reveals);
      expect(total).toBe(winAmount(bet, book.payoutMultiplier));
      expect(rec.win).toBe(total);
      const trig = book.events.find((e) => e.type === 'bonusStart') as { bonus: string } | undefined;
      if (trig) {
        expect(rec.log).toContain('intro:' + trig.bonus);
        const end = book.events.find((e) => e.type === 'bonusEnd') as { ceremony: string };
        expect(rec.log).toContain('outro:' + end.ceremony);
        // every shot / exchange end shown is exactly the one of the book, in order
        expect(rec.shots).toEqual(book.events.filter((e) => e.type === 'shot'));
        expect(rec.ends).toEqual(book.events.filter((e) => e.type === 'exchangeEnd'));
        const hawk = book.events.filter((e) => e.type === 'hawkEye').map((e) => 'hawk:' + (e as { call: string }).call);
        expect(rec.log.filter((l) => l.startsWith('hawk:'))).toEqual(hawk);
        const lastEx = book.events.filter((e) => e.type === 'exchangeStart').pop() as { exchange: number };
        expect(rec.fs[0]).toBe(lastEx.exchange);
        // the bonus total equals the sum of the shot wins shown
        const shotSum = (book.events.filter((e) => e.type === 'shot') as { win: number }[]).reduce((a, x) => a + x.win, 0);
        expect(shotSum).toBe((book.events.find((e) => e.type === 'bonusEnd') as { bonusWin: number }).bonusWin);
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
