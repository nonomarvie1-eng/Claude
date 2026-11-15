import { describe, expect, it, vi } from 'vitest';
import { DemoRgs, memoryStorage, DEMO_START_BALANCE } from './demoRgs';
import { StakeRgs } from './stakeRgs';
import { RgsError, validateRound } from './types';
import { createRgs } from './index';
import { playRound } from '../engine/engine';
import { cryptoDrawer } from '../engine/rng';

describe('DemoRgs (play money)', () => {
  it('debits on play, credits payout on endRound', async () => {
    const rgs = new DemoRgs(memoryStorage());
    const a = await rgs.authenticate();
    expect(a.balance.amount).toBe(DEMO_START_BALANCE);
    expect(a.balance.currency).toBe('DEMO');
    for (let i = 0; i < 200; i++) {
      const before = (await rgs.balance()).amount;
      const { balance, round } = await rgs.play(1_000_000, 'BASE');
      expect(balance.amount).toBe(before - 1_000_000);
      expect(round.payout).toBe((1_000_000 * round.payoutMultiplier) / 100);
      const end = await rgs.endRound();
      expect(end.balance.amount).toBe(before - 1_000_000 + round.payout);
    }
  });

  it('refuses invalid bets, insufficient funds and concurrent rounds', async () => {
    const rgs = new DemoRgs(memoryStorage());
    await expect(rgs.play(123, 'BASE')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await expect(rgs.play(1_000_000, 'TURBO')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await rgs.play(1_000_000, 'BASE');
    await expect(rgs.play(1_000_000, 'BASE')).rejects.toMatchObject({ code: 'ERR_VAL' });
    await rgs.endRound();
    const poor = new DemoRgs({ get: () => JSON.stringify({ balance: 100_000, active: null, nextId: 1 }), set: () => {} });
    await expect(poor.play(1_000_000, 'BASE')).rejects.toMatchObject({ code: 'ERR_IPB' });
  });

  it('persists an unfinished round and resumes it after reload', async () => {
    const store = memoryStorage();
    const a = new DemoRgs(store);
    const { round } = await a.play(2_000_000, 'BASE');
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

  it('bonus buy debits bet x cost and plays a bought Tie-Break', async () => {
    const rgs = new DemoRgs(memoryStorage());
    const { balance, round } = await rgs.play(1_000_000, 'BONUS');
    expect(balance.amount).toBe(DEMO_START_BALANCE - 100 * 1_000_000);
    expect(round.cost).toBe(100);
    const trig = round.state.find((e) => e.type === 'freeSpinTrigger') as { bought?: boolean; totalFs: number };
    expect(trig.bought).toBe(true);
    expect([9, 12]).toContain(trig.totalFs);
    const end = await rgs.endRound();
    expect(end.balance.amount).toBe(DEMO_START_BALANCE - 100 * 1_000_000 + round.payout);
    const poor = new DemoRgs({ get: () => JSON.stringify({ balance: 80 * 1_000_000, active: null, nextId: 1 }), set: () => {} });
    await expect(poor.play(1_000_000, 'BONUS')).rejects.toMatchObject({ code: 'ERR_IPB' });
  });

  it('forced bonus scenario triggers free spins (demo QA only)', async () => {
    const rgs = new DemoRgs(memoryStorage());
    for (const f of ['bonus3', 'bonus4', 'bonus5'] as const) {
      rgs.forceNext = f;
      const { round } = await rgs.play(1_000_000, 'BASE');
      const trig = round.state.find((e) => e.type === 'freeSpinTrigger');
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
        expect(body).toMatchObject({ amount: 1_000_000, mode: 'BASE' });
        return [200, { balance: { amount: 4, currency: 'USD' }, round: { betID: 1, amount: 1_000_000, payout: 0, payoutMultiplier: book.payoutMultiplier, active: true, mode: 'BASE', state: book.events } }];
      }
      return [200, { balance: { amount: 4, currency: 'USD' } }];
    });
    const rgs = new StakeRgs('rgs.example.invalid', 'test-session', f);
    await rgs.authenticate();
    const p = await rgs.play(1_000_000, 'BASE');
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
    await expect(rgs.play(1, 'BASE')).rejects.toMatchObject({ code: 'ERR_IPB' });
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
