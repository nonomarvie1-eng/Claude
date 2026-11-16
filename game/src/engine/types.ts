// Book / event types.  A "book" is the complete, pre-determined result of one
// paid round (same structure as the Stake Engine books produced by
// math/rally_math/engine.py).  Amounts are payoutMultiplier units
// (bet multiple x 100).

export type SymbolName = 'W' | 'S' | 'H1' | 'H2' | 'H3' | 'H4' | 'H5' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5';
export type GameType = 'basegame' | 'freegame';
export type Board = SymbolName[][]; // board[reel][row]

export interface Position {
  reel: number;
  row: number;
}

export interface WinLine {
  kind: 'ways' | 'scatter';
  symbol: SymbolName;
  count: number; // reels
  ways: number;
  basePay: number;
  multiplier: number;
  win: number;
  positions: Position[];
}

export type BookEvent =
  | { index: number; type: 'reveal'; gameType: GameType; board: Board; stops: number[]; paddingAbove: SymbolName[]; paddingBelow: SymbolName[]; anticipation: number[] }
  | { index: number; type: 'winInfo'; gameType: GameType; multiplier: number; totalWin: number; wins: WinLine[] }
  | { index: number; type: 'setWin'; amount: number; winLevel: string }
  | { index: number; type: 'freeSpinTrigger'; totalFs: number; positions: Position[]; level: BonusLevel; startMultiplier: number; bought?: boolean }
  | { index: number; type: 'updateFreeSpin'; amount: number; total: number }
  | { index: number; type: 'rallyUp'; added: number; collected: number; multiplier: number; previousMultiplier: number; positions: Position[] }
  | { index: number; type: 'freeSpinRetrigger'; totalFs: number; added: number; positions: Position[] }
  | { index: number; type: 'setTotalWin'; amount: number }
  | { index: number; type: 'wincap'; amount: number }
  | { index: number; type: 'freeSpinEnd'; amount: number; winLevel: string }
  | { index: number; type: 'finalWin'; amount: number };

export interface Book {
  id: number;
  payoutMultiplier: number;
  events: BookEvent[];
}

export type BonusLevel = 'tiebreak' | 'super';
export type ModeName = 'base' | 'bonus_chance' | 'buy_tiebreak' | 'buy_super';
export const MODE_NAMES: ModeName[] = ['base', 'bonus_chance', 'buy_tiebreak', 'buy_super'];

/** Validated statistics of one bet mode, exported by the Python maths. */
export interface ModeInfo {
  cost: number;
  kind: 'spin' | 'buy';
  scatters: number | null;
  level: BonusLevel | null;
  spins: number | null;
  rtp: number | null;
  bonusOneIn: number | null;
  tiebreakOneIn: number | null;
  superOneIn: number | null;
  hitFrequency: number | null;
  stdDevX: number | null;
  meanX: number | null;
}

export interface GameConfig {
  gameId: string;
  name: string;
  mathVersion: string;
  reels: number;
  rows: number;
  symbols: SymbolName[];
  symbolInfo: Record<SymbolName, { label: string; fr: string; role: string }>;
  paytable: Record<string, Record<string, number>>;
  scatterPay: Record<string, number>;
  fsAward: Record<string, number>;
  fsRetrigger: number;
  fsMaxRemaining: number;
  rallyLadder: number[];
  wincapX: number;
  minKind: number;
  bonusLevels: Record<BonusLevel, { start_index: number; startMultiplier: number; fr: string; en: string }>;
  modes: Record<ModeName, ModeInfo>;
  payModel: string;
  winLevels: { name: string; min: number }[];
  reelStrips: { base: SymbolName[][]; free: SymbolName[][]; bonusChance: SymbolName[][] };
  stats?: { rtp: number; hitFrequency: number; bonusOneIn: number; stdDev: number; method: string };
}
