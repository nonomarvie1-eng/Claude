// Common contract between the game and any Remote Game Server.
// Shapes follow the Stake Engine RGS documentation (math-sdk/docs/rgs_docs/RGS.md,
// commit 141b4e8): money is an integer with 6 decimals (1_000_000 = 1.00).
import type { Book } from '../engine/types';
import { RULES } from '../engine/rules';

export const MONEY_SCALE = 1_000_000;

export interface Balance {
  amount: number;
  currency: string;
}

export interface Jurisdiction {
  socialCasino?: boolean;
  disabledFullscreen?: boolean;
  disabledTurbo?: boolean;
  disabledSlamstop?: boolean;
  disabledSpacebar?: boolean;
  disabledAutoplay?: boolean;   // name to confirm with Stake (assumption)
  disabledBuyBonus?: boolean;   // name to confirm with Stake (assumption)
  disabledBonusChance?: boolean; // assumption: operator/jurisdiction switch for the bonus_chance mode
  displayRTP?: boolean;
  minimumRoundDuration?: number; // ms
  [k: string]: unknown;
}

export interface RgsConfig {
  minBet: number;
  maxBet: number;
  stepBet: number;
  defaultBetLevel: number;
  betLevels: number[];
  jurisdiction: Jurisdiction;
}

export interface Round {
  betID: string | number;
  amount: number;
  payout: number;
  payoutMultiplier: number;
  active: boolean;
  mode: string;
  /** Book events.  Stake Engine returns the selected book inside the round
   *  (field name to be confirmed on the Stake sandbox: `state` or `events`). */
  state: Book['events'];
  bookId?: number;
  cost?: number; // bet-mode cost multiplier from index.json (1 = base)
  debit?: number; // amount actually debited = amount x cost (money units)
  forced?: string; // demo-only: forced scenario label
}

export interface AuthResult {
  balance: Balance;
  config: RgsConfig;
  round: Round | null;
}

export interface RgsClient {
  readonly kind: 'demo' | 'stake';
  authenticate(): Promise<AuthResult>;
  balance(): Promise<Balance>;
  play(amount: number, mode: string): Promise<{ balance: Balance; round: Round }>;
  endRound(): Promise<{ balance: Balance }>;
  event(event: string): Promise<void>;
}

export type RgsErrorCode =
  | 'ERR_VAL' | 'ERR_IPB' | 'ERR_IS' | 'ERR_ATE' | 'ERR_GLE' | 'ERR_LOC'
  | 'ERR_GEN' | 'ERR_MAINTENANCE' | 'ERR_NETWORK' | 'ERR_TIMEOUT' | 'ERR_DATA';

export class RgsError extends Error {
  constructor(public code: RgsErrorCode, message?: string, public retryable = false) {
    super(message ?? code);
  }
}

/** Validates a book coming from any server before it is displayed. */
export function validateRound(r: unknown): Round {
  const x = r as Round;
  if (!x || typeof x !== 'object') throw new RgsError('ERR_DATA', 'round missing');
  if (!Array.isArray(x.state) || x.state.length === 0) throw new RgsError('ERR_DATA', 'round events missing');
  if (!Number.isInteger(x.payoutMultiplier) || x.payoutMultiplier < 0) throw new RgsError('ERR_DATA', 'bad payoutMultiplier');
  const last = x.state[x.state.length - 1];
  if (last.type !== 'finalWin' || last.amount !== x.payoutMultiplier) throw new RgsError('ERR_DATA', 'finalWin does not match payout');
  for (const e of x.state) {
    if (e.type === 'reveal') {
      if (!Array.isArray(e.board) || e.board.length !== RULES.reels || e.board.some((c) => !Array.isArray(c) || c.length !== RULES.rows)) {
        throw new RgsError('ERR_DATA', 'bad board');
      }
    }
  }
  return x;
}
