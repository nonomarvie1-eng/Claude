// BookPlayer: turns an already-determined book into a presentation.
// It never computes or alters an outcome: every board, win, multiplier and
// total shown comes verbatim from the book returned by the RGS.
import type { Board, BonusLevel, BookEvent, GameType, ModeName, Position, WinLine } from '../engine/types';

type Ev<T extends BookEvent['type']> = Extract<BookEvent, { type: T }>;
import { winAmount } from './format';

export type WinTier = 'none' | 'ldw' | 'small' | 'big' | 'mega' | 'epic';

export interface View {
  setMode(mode: GameType, level?: BonusLevel | null): void;
  spinTo(board: Board, stops: number[], gameType: GameType, anticipation: number[], quick: boolean, betMode?: ModeName): Promise<void>;
  showWins(wins: WinLine[], multiplier: number, tier: WinTier): Promise<void>;
  clearWins(): void;
  scatterCelebrate(positions: Position[]): Promise<void>;
  // THE FINAL SET: one method per book event, all values come from the book
  bonusIntro(e: Ev<'bonusStart'>): Promise<void>;
  exchangeStart(e: Ev<'exchangeStart'>): Promise<void>;
  showCourt(courtValues: number[]): Promise<void>;
  hawkEye(e: Ev<'hawkEye'>): Promise<void>;
  shot(e: Ev<'shot'>): Promise<void>;
  grandSlam(e: Ev<'grandSlam'>): Promise<void>;
  marksExpire(e: Ev<'markExpire'>): Promise<void>;
  extraExchange(e: Ev<'extraExchange'>): Promise<void>;
  exchangeEnd(e: Ev<'exchangeEnd'>): Promise<void>;
  bonusOutro(e: Ev<'bonusEnd'>, amount: number, bonusWin: number): Promise<void>;
  bigWin(amount: number, tier: WinTier): Promise<void>;
  wincap(): Promise<void>;
  pause(ms: number): Promise<void>;
  // Rally Path prototype (demo lab only)
  rallyPath?(e: Ev<'rallyPath'>): Promise<void>;
  protoBonusStart?(e: Ev<'protoBonusStart'>): Promise<void>;
  protoSpinStart?(e: Ev<'spinStart'>): void;
  secondServe?(e: Ev<'secondServe'>): Promise<void>;
  protoBonusEnd?(e: Ev<'protoBonusEnd'>, amount: number): Promise<void>;
}

export interface Hud {
  setWin(amount: number): void;
  setFreeSpins(current: number, total: number): void; // exchanges played / awarded
  setMultiplier(m: number): void; // kept for compatibility (always 1 in v6)
  setPoints?(points: number, lastShot: string | null, exchangeWin: number): void;
  setInBonus(on: boolean): void;
  setBonusLevel?(level: BonusLevel | null): void;
}

/** Win tier relative to the bet.  Wins that do not exceed the bet are
 *  "ldw" (loss disguised as win) and are deliberately NOT celebrated. */
export function tierFor(amount: number, bet: number): WinTier {
  if (amount <= 0) return 'none';
  const x = amount / bet;
  if (x <= 1) return 'ldw';
  if (x < 10) return 'small';
  if (x < 50) return 'big';
  if (x < 200) return 'mega';
  return 'epic';
}

export interface PlayOptions {
  bet: number;
  cost?: number; // bet-mode cost multiplier: celebrations are relative to the amount actually debited
  quick?: boolean; // resume/replay of an interrupted round: shorter presentation
  mode?: ModeName; // bet mode of the round (selects the reel set used to animate the base spin)
}

export async function playBook(events: BookEvent[], view: View, hud: Hud, opts: PlayOptions): Promise<{ total: number }> {
  const bet = opts.bet;
  const debit = bet * (opts.cost ?? 1);
  let total = 0;
  let inBonus = false;
  let baseWin = 0;
  let hasBonus = false;
  let points = 0;
  let exchange = 0;
  let lastShot: string | null = null;
  view.clearWins();
  view.setMode('basegame');
  hud.setInBonus(false);
  hud.setMultiplier(1);
  for (const e of events) {
    switch (e.type) {
      case 'reveal': {
        view.clearWins();
        if (e.gameType === 'freegame' && !inBonus) {
          inBonus = true;
        }
        await view.spinTo(e.board, e.stops, e.gameType, e.anticipation, !!opts.quick, opts.mode ?? 'base');
        if (e.gameType === 'freegame' && e.courtValues) await view.showCourt(e.courtValues);
        break;
      }
      case 'winInfo': {
        const amt = winAmount(bet, e.totalWin);
        const tier = tierFor(amt, debit);
        const scatter = e.wins.find((w) => w.kind === 'scatter');
        if (scatter && e.gameType === 'basegame') await view.scatterCelebrate(scatter.positions);
        await view.showWins(e.wins, e.multiplier, tier);
        break;
      }
      case 'setWin': {
        if (!inBonus) {
          baseWin = winAmount(bet, e.amount);
          hud.setWin(baseWin);
        }
        break;
      }
      case 'bonusStart': {
        hasBonus = true;
        hud.setBonusLevel?.(e.bonus);
        hud.setInBonus(true);
        hud.setFreeSpins(0, e.exchanges);
        hud.setPoints?.(0, null, 0);
        view.setMode('freegame', e.bonus);
        await view.bonusIntro(e);
        break;
      }
      case 'exchangeStart':
        hud.setFreeSpins(e.exchange, e.total);
        await view.exchangeStart(e);
        break;
      case 'hawkEye':
        await view.hawkEye(e);
        break;
      case 'shot':
        lastShot = e.shot;
        await view.shot(e);
        hud.setPoints?.(points, lastShot, winAmount(bet, e.win));
        break;
      case 'grandSlam':
        await view.grandSlam(e);
        break;
      case 'markExpire':
        await view.marksExpire(e);
        break;
      case 'extraExchange':
        hud.setFreeSpins(exchange, e.total);
        await view.extraExchange(e);
        break;
      case 'exchangeEnd':
        exchange = e.exchange;
        points = e.points;
        hud.setPoints?.(points, lastShot, winAmount(bet, e.win));
        await view.exchangeEnd(e);
        break;
      case 'setTotalWin':
        hud.setWin(winAmount(bet, e.amount));
        break;
      case 'wincap':
        await view.wincap();
        break;
      case 'bonusEnd': {
        await view.bonusOutro(e, winAmount(bet, e.amount), winAmount(bet, e.bonusWin));
        view.setMode('basegame');
        hud.setInBonus(false);
        hud.setBonusLevel?.(null);
        break;
      }
      // ---- Rally Path prototype
      case 'rallyPath':
        await view.rallyPath?.(e);
        break;
      case 'protoBonusStart':
        hasBonus = true;
        hud.setBonusLevel?.(e.bonus);
        hud.setInBonus(true);
        hud.setFreeSpins(0, e.spins);
        view.setMode('freegame', e.bonus);
        await view.protoBonusStart?.(e);
        break;
      case 'spinStart':
        exchange = e.spin;
        hud.setFreeSpins(e.spin, e.total);
        view.protoSpinStart?.(e);
        break;
      case 'secondServe':
        hud.setFreeSpins(exchange, e.total);
        await view.secondServe?.(e);
        break;
      case 'protoBonusEnd':
        await view.protoBonusEnd?.(e, winAmount(bet, e.amount));
        view.setMode('basegame');
        hud.setInBonus(false);
        hud.setBonusLevel?.(null);
        break;
      case 'finalWin': {
        total = winAmount(bet, e.amount);
        hud.setWin(total);
        const tier = tierFor(total, debit);
        // bonus rounds end with their own (threshold-based) ceremony: no second celebration
        if (!opts.quick && !hasBonus && (tier === 'big' || tier === 'mega' || tier === 'epic')) await view.bigWin(total, tier);
        break;
      }
    }
  }
  return { total };
}
