// BookPlayer: turns an already-determined book into a presentation.
// It never computes or alters an outcome: every board, win, multiplier and
// total shown comes verbatim from the book returned by the RGS.
import type { Board, BonusLevel, BookEvent, GameType, ModeName, Position, WinLine } from '../engine/types';
import { winAmount } from './format';

export type WinTier = 'none' | 'ldw' | 'small' | 'big' | 'mega' | 'epic';

export interface View {
  setMode(mode: GameType, level?: BonusLevel | null): void;
  spinTo(board: Board, stops: number[], gameType: GameType, anticipation: number[], quick: boolean, betMode?: ModeName): Promise<void>;
  showWins(wins: WinLine[], multiplier: number, tier: WinTier): Promise<void>;
  clearWins(): void;
  scatterCelebrate(positions: Position[]): Promise<void>;
  bonusIntro(spins: number, level: BonusLevel, startMultiplier: number, bought: boolean): Promise<void>;
  wind(positions: Position[], collected: number, multiplier: number, previous: number): Promise<void>;
  retrigger(added: number, total: number): Promise<void>;
  bonusOutro(amount: number): Promise<void>;
  bigWin(amount: number, tier: WinTier): Promise<void>;
  wincap(): Promise<void>;
  pause(ms: number): Promise<void>;
}

export interface Hud {
  setWin(amount: number): void;
  setFreeSpins(current: number, total: number): void;
  setMultiplier(m: number): void;
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
      case 'freeSpinTrigger': {
        const level = e.level ?? 'tiebreak';
        const start = e.startMultiplier ?? 1;
        hud.setBonusLevel?.(level);
        hud.setInBonus(true);
        hud.setFreeSpins(0, e.totalFs);
        hud.setMultiplier(start);
        view.setMode('freegame', level);
        await view.bonusIntro(e.totalFs, level, start, !!e.bought);
        break;
      }
      case 'updateFreeSpin':
        hud.setFreeSpins(e.amount, e.total);
        break;
      case 'rallyUp':
        await view.wind(e.positions, e.collected, e.multiplier, e.previousMultiplier);
        hud.setMultiplier(e.multiplier);
        break;
      case 'freeSpinRetrigger':
        await view.retrigger(e.added, e.totalFs);
        break;
      case 'setTotalWin':
        hud.setWin(winAmount(bet, e.amount));
        break;
      case 'wincap':
        await view.wincap();
        break;
      case 'freeSpinEnd': {
        const amt = winAmount(bet, e.amount);
        await view.bonusOutro(amt);
        view.setMode('basegame');
        hud.setInBonus(false);
        hud.setBonusLevel?.(null);
        break;
      }
      case 'finalWin': {
        total = winAmount(bet, e.amount);
        hud.setWin(total);
        const tier = tierFor(total, debit);
        if (!opts.quick && (tier === 'big' || tier === 'mega' || tier === 'epic')) await view.bigWin(total, tier);
        break;
      }
    }
  }
  return { total };
}
