import { RULES } from '../engine/rules';
import { describe, expect, it, vi } from 'vitest';
import { DemoRgs, memoryStorage, DEMO_START_BALANCE } from './demoRgs';
import { StakeRgs } from './stakeRgs';
import { RgsError, validateRound } from './types';
import { createRgs } from './index';
import { playRound } from '../engine/engine';
import { cryptoDrawer } from '../engine/rng';

import { FINAL_SET_BUILD, GOLDEN_SERVE_BUILD, RALLY_PATH_BUILD } from '../engine/gameplay';
// v6 FINAL SET gameplay tests: run with `npm run test:finalset` (disabled in the Rally Path test build)
const itOld = FINAL_SET_BUILD ? it : it.skip;

describe.runIf(GOLDEN_SERVE_BUILD)('DemoRgs — Golden Serve test build GOLDEN-SERVE-02', () => {
  const OLD = ['bonusStart', 'hawkEye', 'shot', 'exchangeStart', 'rallyPath', 'protoBonusStart'];
  it('old buys and Bonus Chance are refused without debit', async () => {
    const r = new DemoRgs(memoryStorage());
    for (const m of ['buy_rally', 'buy_final', 'bonus_chance']) await expect(r.play(1_000_000, m)).rejects.toThrow();
    expect((await r.balance()).amount).toBe(DEMO_START_BALANCE);
  });
  it('TEST SERVE: a Golden Serve whose wins are paid on the transformed grid, credited once', async () => {
    for (const concept of ['A', 'B'] as const) {
      const r = new DemoRgs(memoryStorage());
      r.concept = concept;
      r.forceNext = 'gs_serve';
      const { round } = await r.play(1_000_000, 'base');
      const g = round.state.find((e) => e.type === 'goldenServe');
      expect(g && g.type === 'goldenServe' && g.concept === concept).toBe(true);
      expect(round.concept).toBe(concept);
      const end = await r.endRound();
      expect(end.balance.amount).toBe(DEMO_START_BALANCE - 1_000_000 + round.payout);
    }
  });
  it('random rounds of both prototypes never contain older gameplay events', async () => {
    for (const concept of ['A', 'B'] as const) {
      const r = new DemoRgs(memoryStorage());
      r.concept = concept;
      for (let i = 0; i < 300; i++) {
        const { round } = await r.play(1_000_000, 'base');
        expect(round.state.some((e) => OLD.includes(e.type))).toBe(false);
        await r.endRound();
        if ((await r.balance()).amount < 2_000_000) r.reset();
      }
    }
  });
});

describe.runIf(RALLY_PATH_BUILD)('DemoRgs — Rally Path test build RALLY-PATH-01', () => {
  it('old buys and Bonus Chance are refused without debit', async () => {
    const r = new DemoRgs(memoryStorage());
    for (const m of ['buy_rally', 'buy_final', 'bonus_chance']) await expect(r.play(1_000_000, m)).rejects.toThrow();
    expect((await r.balance()).amount).toBe(DEMO_START_BALANCE);
  });
  it('test button scenario: full 6-shot rally, Championship Shot, credited exactly once, no Final Set event', async () => {
    const r = new DemoRgs(memoryStorage());
    r.forceNext = 'game_full6';
    const { round } = await r.play(1_000_000, 'base');
    const rp = round.state.find((e) => e.type === 'rallyPath');
    expect(rp && rp.type === 'rallyPath' && rp.length === 6 && rp.championshipShot).toBe(true);
    expect(round.state.some((e) => ['bonusStart', 'hawkEye', 'shot', 'exchangeStart'].includes(e.type))).toBe(false);
    const end = await r.endRound();
    expect(end.balance.amount).toBe(DEMO_START_BALANCE - 1_000_000 + round.payout);
  });
  it('random rounds only produce Rally Path events', async () => {
    const r = new DemoRgs(memoryStorage());
    for (let i = 0; i < 300; i++) {
      const { round } = await r.play(1_000_000, 'base');
      expect(round.state.some((e) => ['bonusStart', 'hawkEye', 'shot', 'exchangeStart'].includes(e.type))).toBe(false);
      await r.endRound();
      if ((await r.balance()).amount < 2_000_000) r.reset();
    }
  });
});

describe('DemoRgs (play money)', () => {
  it('debits on play, credits payout on endRound', async () => {
    const rgs = new DemoRgs(memoryStorage());
    const a = await rgs.authenticate();
    expect(a.balance.amount).toBe(DEMO_START_BALANCE);
    expect(a.balance.currency).toBe('DEMO');
    for (let i = 0; i < 200; i++) {
      const before = (await rgs.balance()).amount;
      const { balance, round } = await rgs.play(1_000_000, 'base');
      expect(balance.amount).toBe(before - 1_000_000);
      expect(round.payout).toBe((1_000_000 * round.payoutMultiplier) / 100);
      const end = await rgs.endRound();
      expect(end.balance.amount).toBe(before - 1_000_000 + round.payout);
    }
  });

  it('refuses invalid bets, insufficient funds and concurrent rounds', async () => {
    const rgs = new DemoRgs(memoryStorage());
    await expect(rgs.play(123, 'base')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await expect(rgs.play(1_000_000, 'TURBO')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await rgs.play(1_000_000, 'base');
    await expect(rgs.play(1_000_000, 'base')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await rgs.endRound();
    const poor = new DemoRgs({ get: () => JSON.stringify({ balance: 100_000, active: null, nextId: 1 }), set: () => {} });
    await expect(poor.play(1_000_000, 'base')).rejects.toMatchObject({ code: 'ERR_IPB' });
  });

  it('persists an unfinished round and resumes it after reload', async () => {
    const store = memoryStorage();
    const a = new DemoRgs(store);
    const { round } = await a.play(2_000_000, 'base');
    const b = new DemoRgs(store); // "page reload"
    const auth = await b.authenticate();
    expect(auth.round?.betID).toBe(round.betID);
    expect(auth.round?.state).toEqual(round.state);
    const end = await b.endRound();
    expect(end.balance.amount).toBe(DEMO_START_BALANCE - 2_000_000 + round.payout);
    expect((await b.authenticate()).round).toBeNull();
    // endRound is idempotent
    expect((await b.endRound()).balance.amount).toBe(end.balance.amount);
  });

  it('recovers from corrupted storage', async () => {
    const rgs = new DemoRgs({ get: () => '{not json', set: () => {} });
    expect((await rgs.authenticate()).balance.amount).toBe(DEMO_START_BALANCE);
  });

  itOld.each([
    ['buy_rally', 'rally', 3],
    ['buy_final', 'final', 4],
  ] as const)('%s debits bet x cost and always gives exactly its bonus', async (mode, level, k) => {
    const cost = RULES.modes[mode].cost;
    for (let i = 0; i < 25; i++) {
      const rgs = new DemoRgs(memoryStorage());
      const { balance, round } = await rgs.play(1_000_000, mode);
      expect(balance.amount).toBe(DEMO_START_BALANCE - Math.round(cost * 1_000_000));
      expect(round.cost).toBe(cost);
      const reveal = round.state[0] as { board: string[][] };
      expect(reveal.board.flat().filter((x) => x === 'S').length).toBe(k);
      const trig = round.state.find((e) => e.type === 'bonusStart') as { bought?: boolean; bonus: string; exchanges: number };
      expect(trig.bought).toBe(true);
      expect(trig.bonus).toBe(level);
      expect(trig.exchanges).toBe(RULES.fsAward[String(k)]);
      // the bonus really plays its own mechanics: Hawk-Eye / championship point only in the Grand Final
      const hasCp = round.state.some((e) => e.type === 'exchangeStart' && (e as { championshipPoint: boolean }).championshipPoint);
      expect(hasCp).toBe(level === 'final');
      const end = await rgs.endRound();
      expect(end.balance.amount).toBe(DEMO_START_BALANCE - Math.round(cost * 1_000_000) + round.payout);
    }
    const poor = new DemoRgs({ get: () => JSON.stringify({ balance: Math.round((cost - 1) * 1_000_000), active: null, nextId: 1 }), set: () => {} });
    await expect(poor.play(1_000_000, mode)).rejects.toMatchObject({ code: 'ERR_IPB' });
  });

  itOld('a second play while a bought round is active is refused (no double debit)', async () => {
    const rgs = new DemoRgs(memoryStorage());
    await rgs.play(1_000_000, 'buy_rally');
    await expect(rgs.play(1_000_000, 'buy_rally')).rejects.toMatchObject({ code: 'ERR_VAL' });
    expect((await rgs.balance()).amount).toBe(DEMO_START_BALANCE - Math.round(RULES.modes.buy_rally.cost * 1_000_000));
  });

  itOld('bonus_chance debits 1.4x and uses the bonus-chance reels; unknown modes are refused', async () => {
    const rgs = new DemoRgs(memoryStorage());
    const { balance, round } = await rgs.play(1_000_000, 'bonus_chance');
    expect(balance.amount).toBe(DEMO_START_BALANCE - Math.round(RULES.modes.bonus_chance.cost * 1_000_000));
    const rv = round.state[0] as { stops: number[]; board: string[][] };
    const strips = RULES.reelStrips.bonusChance;
    rv.board.forEach((col, r) => col.forEach((sym, row) => expect(sym).toBe(strips[r][(rv.stops[r] + row) % strips[r].length])));
    await rgs.endRound();
    await expect(rgs.play(1_000_000, 'BONUS')).rejects.toMatchObject({ code: 'ERR_VAL' });
  });

  it('bonus_chance really triggers more bonuses (statistical, same engine as the maths)', () => {
    const count = (mode: 'base' | 'bonus_chance', n: number) => {
      let b = 0;
      for (let i = 0; i < n; i++) if (playRound(cryptoDrawer, i, undefined, mode).triggered) b++;
      return b / n;
    };
    const n = 40_000;
    const pb = count('base', n);
    const pc = count('bonus_chance', n);
    // exact values: 1/175 and 1/74 -> means 229 vs 538 bonuses; 6 sigma apart at this n
    expect(pc).toBeGreaterThan(pb * 1.6);
    expect(Math.abs(pc - 1 / RULES.modes.bonus_chance.bonusOneIn!)).toBeLessThan(6 * Math.sqrt(pc / n));
  });

  itOld('forced bonus scenario triggers free spins (demo QA only)', async () => {
    const rgs = new DemoRgs(memoryStorage());
    for (const f of ['bonus3', 'bonus4', 'bonus5'] as const) {
      rgs.forceNext = f;
      const { round } = await rgs.play(1_000_000, 'base');
      const trig = round.state.find((e) => e.type === 'bonusStart');
      expect(trig).toBeTruthy();
      expect(round.forced).toBe(f);
      await rgs.endRound();
    }
  });
});

describe('StakeRgs client (mocked network, no real credentials)', () => {
  const book = playRound(cryptoDrawer, 1).book;
  const mk = (handler: (url: string, body: Record<string, unknown>) => [number, unknown]) =>
    vi.fn(async (url: string, init: RequestInit) => {
      const [status, data] = handler(url, JSON.parse(String(init.body)));
      return new Response(JSON.stringify(data), { status });
    }) as unknown as typeof fetch;

  it('calls the documented endpoints with sessionID and amount', async () => {
    const calls: string[] = [];
    const f = mk((url, body) => {
      calls.push(url);
      expect(body.sessionID).toBe('test-session');
      if (url.endsWith('/wallet/authenticate')) return [200, { balance: { amount: 5, currency: 'USD' }, config: { betLevels: [] }, round: null }];
      if (url.endsWith('/wallet/play')) {
        expect(body).toMatchObject({ amount: 1_000_000, mode: 'base' });
        return [200, { balance: { amount: 4, currency: 'USD' }, round: { betID: 1, amount: 1_000_000, payout: 0, payoutMultiplier: book.payoutMultiplier, active: true, mode: 'base', state: book.events } }];
      }
      return [200, { balance: { amount: 4, currency: 'USD' } }];
    });
    const rgs = new StakeRgs('rgs.example.invalid', 'test-session', f);
    await rgs.authenticate();
    const p = await rgs.play(1_000_000, 'base');
    expect(p.round.state).toEqual(book.events);
    await rgs.endRound();
    expect(calls).toEqual([
      'https://rgs.example.invalid/wallet/authenticate',
      'https://rgs.example.invalid/wallet/play',
      'https://rgs.example.invalid/wallet/end-round',
    ]);
  });

  it('maps RGS error codes and network failures', async () => {
    const rgs = new StakeRgs('https://x.invalid', 's', mk(() => [400, { code: 'ERR_IPB', message: 'no funds' }]));
    await expect(rgs.play(1, 'base')).rejects.toMatchObject({ code: 'ERR_IPB' });
    const down = new StakeRgs('https://x.invalid', 's', (async () => {
      throw new TypeError('network down');
    }) as unknown as typeof fetch);
    await expect(down.balance()).rejects.toMatchObject({ code: 'ERR_NETWORK', retryable: true });
  });

  it('rejects malformed books before display', () => {
    expect(() => validateRound({ state: [], payoutMultiplier: 0 })).toThrow(RgsError);
    expect(() => validateRound({ state: [{ type: 'finalWin', amount: 10 }], payoutMultiplier: 20 })).toThrow(/finalWin/);
    const bad = structuredClone(book.events);
    (bad[0] as { board: unknown }).board = [['H1']];
    expect(() => validateRound({ state: bad, payoutMultiplier: book.payoutMultiplier })).toThrow(/board/);
  });
});

describe('server selection', () => {
  it('uses the demo unless the RGS build flag is set', () => {
    expect(createRgs('?sessionID=abc&rgs_url=rgs.invalid').kind).toBe('demo');
    expect(createRgs('').kind).toBe('demo');
  });
});
