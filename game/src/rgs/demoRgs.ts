// LOCAL DEMO SIMULATOR — play money only.
// * Credits have no monetary value and cannot be withdrawn or converted.
// * Outcomes come from the same rules as the production math (TS port with
//   proven parity), drawn with the browser CSPRNG.
// * Nothing here talks to a network or an operator.
import { drawBaseStopsWithScatters, playRound } from '../engine/engine';
import { MODE_NAMES, type ModeName } from '../engine/types';
import { RULES } from '../engine/rules';
import { cryptoDrawer, cryptoInt } from '../engine/rng';
import { MONEY_SCALE, RgsError, type AuthResult, type Balance, type RgsClient, type RgsConfig, type Round } from './types';

const KEY = 'golden-rally-demo-v1';
export const DEMO_START_BALANCE = 1_000 * MONEY_SCALE;

export interface DemoStorage {
  get(): string | null;
  set(v: string): void;
}

export const browserStorage: DemoStorage = {
  get() {
    try {
      return localStorage.getItem(KEY);
    } catch {
      return null;
    }
  },
  set(v) {
    try {
      localStorage.setItem(KEY, v);
    } catch {
      /* private mode: demo still works, without persistence */
    }
  },
};

export const memoryStorage = (): DemoStorage => {
  let v: string | null = null;
  return { get: () => v, set: (x) => (v = x) };
};

interface Persisted {
  balance: number;
  active: Round | null;
  nextId: number;
}

export type ForcedScenario = null | 'bonus3' | 'bonus4' | 'bonus5';

export class DemoRgs implements RgsClient {
  readonly kind = 'demo' as const;
  private s: Persisted;
  /** demo-only: next round forced to trigger the bonus (clearly labelled in UI). */
  forceNext: ForcedScenario = null;
  failNext: string | null = null; // QA: simulate a server error on next call

  readonly config: RgsConfig = {
    minBet: 100_000,
    maxBet: 100 * MONEY_SCALE,
    stepBet: 10_000,
    defaultBetLevel: 1 * MONEY_SCALE,
    betLevels: [0.2, 0.4, 0.6, 1, 2, 4, 6, 10, 20, 50, 100].map((x) => Math.round(x * MONEY_SCALE)),
    jurisdiction: { socialCasino: false, disabledTurbo: false, disabledSlamstop: true, displayRTP: true },
  };

  constructor(private storage: DemoStorage = browserStorage) {
    this.s = this.load();
  }

  private load(): Persisted {
    const raw = this.storage.get();
    if (raw) {
      try {
        const p = JSON.parse(raw) as Persisted;
        if (Number.isSafeInteger(p.balance) && p.balance >= 0) return p;
      } catch {
        /* corrupted: reset */
      }
    }
    return { balance: DEMO_START_BALANCE, active: null, nextId: 1 };
  }

  private save() {
    this.storage.set(JSON.stringify(this.s));
  }

  private bal(): Balance {
    return { amount: this.s.balance, currency: 'DEMO' };
  }

  private maybeFail(op: string) {
    if (this.failNext === op) {
      this.failNext = null;
      throw new RgsError('ERR_GEN', 'simulated server error', true);
    }
  }

  async authenticate(): Promise<AuthResult> {
    this.maybeFail('authenticate');
    return { balance: this.bal(), config: this.config, round: this.s.active };
  }

  async balance(): Promise<Balance> {
    return this.bal();
  }

  async play(amount: number, mode: string): Promise<{ balance: Balance; round: Round }> {
    this.maybeFail('play');
    if (this.s.active) throw new RgsError('ERR_VAL', 'a round is already active');
    if (!MODE_NAMES.includes(mode as ModeName)) throw new RgsError('ERR_VAL', 'unknown mode');
    const m = mode as ModeName;
    if (!this.config.betLevels.includes(amount)) throw new RgsError('ERR_VAL', 'invalid bet');
    const info = RULES.modes[m];
    if (info.kind === 'buy' && this.config.jurisdiction.disabledBuyBonus) throw new RgsError('ERR_VAL', 'bonus buy disabled');
    if (m === 'bonus_chance' && this.config.jurisdiction.disabledBonusChance) throw new RgsError('ERR_VAL', 'bonus chance disabled');
    const cost = info.cost;
    const debit = Math.round(amount * cost); // Stake RGS: debit = base bet x mode cost multiplier
    if (debit > this.s.balance) throw new RgsError('ERR_IPB', 'insufficient balance');
    const forced = m === 'base' ? this.forceNext : null;
    this.forceNext = null;
    // buys: exact conditional law of the normal reels given exactly 3 / 4 scatters
    const k = info.kind === 'buy' ? (info.scatters as number) : forced ? +forced.slice(-1) : 0;
    const out = playRound(cryptoDrawer, this.s.nextId, k ? drawBaseStopsWithScatters(k, cryptoInt) : undefined, m);
    const pm = out.book.payoutMultiplier;
    const round: Round = {
      betID: this.s.nextId,
      bookId: out.book.id,
      amount,
      cost,
      payoutMultiplier: pm,
      payout: Math.round((amount * pm) / 100),
      active: true,
      mode,
      state: out.book.events,
      ...(forced ? { forced } : {}),
    };
    this.s.nextId += 1;
    this.s.balance -= debit;
    round.debit = debit;
    this.s.active = round;
    this.save();
    return { balance: this.bal(), round };
  }

  async endRound(): Promise<{ balance: Balance }> {
    this.maybeFail('endRound');
    const r = this.s.active;
    if (r) {
      this.s.balance += r.payout;
      this.s.active = null;
      this.save();
    }
    return { balance: this.bal() };
  }

  async event(_e: string): Promise<void> {}

  /** Demo only: refill play credits (no monetary value). */
  reset() {
    this.s = { balance: DEMO_START_BALANCE, active: null, nextId: this.s.nextId };
    this.save();
  }
}
