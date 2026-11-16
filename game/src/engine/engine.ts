// TypeScript port of math/rally_math/engine.py (6x5 ways), used ONLY by the
// local demo simulator.  Parity with the Python reference engine is enforced
// by engine.test.ts against shared/parity-fixtures.json.
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import { playBonus } from './bonus';
import type { Board, BonusLevel, Book, BookEvent, ModeName, Position, SymbolName, WinLine } from './types';

const R = RULES.reels;
const ROWS = RULES.rows;
const W: SymbolName = 'W';
const S: SymbolName = 'S';
const PAYING = RULES.symbols.filter((s) => s !== W && s !== S);

type Strips = SymbolName[][];
const BASE: Strips = RULES.reelStrips.base;
const FREE: Strips = RULES.reelStrips.free;
const BONUS_CHANCE: Strips = RULES.reelStrips.bonusChance;
/** Reel set of the base spin of each mode (buys use the normal reels). */
export const baseStripsOf = (mode: ModeName): Strips => (mode === 'bonus_chance' ? BONUS_CHANCE : BASE);
const lengths = (s: Strips) => s.map((x) => x.length);

// pays in t-units (tenths of bet), like the Python engine; events are x10
export const PAY: Record<string, Record<number, number>> = {};
for (const [sym, p] of Object.entries(RULES.paytable)) {
  PAY[sym] = {};
  for (const [k, v] of Object.entries(p)) PAY[sym][+k] = v / 10;
}
export const SC_PAY: Record<number, number> = {};
for (const [k, v] of Object.entries(RULES.scatterPay)) SC_PAY[+k] = v / 10;
const FS_AWARD: Record<number, number> = {};
for (const [k, v] of Object.entries(RULES.fsAward)) FS_AWARD[+k] = v;
const WINCAP_T = WINCAP / 10;

const mod = (a: number, n: number) => ((a % n) + n) % n;

export function windowOf(strips: Strips, stops: number[]): Board {
  return strips.map((strip, r) => Array.from({ length: ROWS }, (_, k) => strip[(stops[r] + k) % strip.length]));
}

function padding(strips: Strips, stops: number[]) {
  return {
    above: strips.map((s, r) => s[mod(stops[r] - 1, s.length)]),
    below: strips.map((s, r) => s[(stops[r] + ROWS) % s.length]),
  };
}

export interface WaysWin {
  symbol: SymbolName;
  reels: number;
  ways: number;
  payPerWay: number; // t-units
}

export function evaluateWays(board: Board, pay: Record<string, Record<number, number>> = PAY): WaysWin[] {
  const out: WaysWin[] = [];
  for (const s of PAYING) {
    let ways = 1;
    let k = 0;
    for (let r = 0; r < R; r++) {
      const n = board[r].filter((x) => x === s || x === W).length;
      if (n === 0) break;
      ways *= n;
      k++;
    }
    if (k >= RULES.minKind) out.push({ symbol: s, reels: k, ways, payPerWay: pay[s][k] });
  }
  return out;
}

export function positionsOf(board: Board, sym: SymbolName): Position[] {
  const out: Position[] = [];
  for (let r = 0; r < R; r++) for (let row = 0; row < ROWS; row++) if (board[r][row] === sym) out.push({ reel: r, row });
  return out;
}

export function anticipation(board: Board): number[] {
  const out: number[] = [];
  let seen = 0;
  for (let r = 0; r < R; r++) {
    out.push(seen >= 2 ? 1 : 0);
    seen += board[r].filter((s) => s === S).length;
  }
  return out;
}

export function winLevel(x: number): string {
  if (x <= 0) return 'none';
  let name = 'none';
  for (const lv of RULES.winLevels) if (x >= lv.min) name = lv.name;
  return name;
}

export function winList(wins: WaysWin[], board: Board, mult: number): WinLine[] {
  return wins.map((w) => {
    const positions: Position[] = [];
    for (let r = 0; r < w.reels; r++) for (let row = 0; row < ROWS; row++) if (board[r][row] === w.symbol || board[r][row] === W) positions.push({ reel: r, row });
    return { kind: 'ways' as const, symbol: w.symbol, count: w.reels, ways: w.ways, basePay: w.payPerWay * 10, multiplier: mult, win: w.payPerWay * w.ways * mult * 10, positions };
  });
}

function scatterWin(pos: Position[], pay: number): WinLine[] {
  if (pay <= 0) return [];
  return [{ kind: 'scatter', symbol: 'S', count: pos.length, ways: 1, basePay: pay * 10, multiplier: 1, win: pay * 10, positions: pos }];
}

const sumPay = (w: WaysWin[]) => w.reduce((a, x) => a + x.payPerWay * x.ways, 0);

export interface RoundOutcome {
  book: Book;
  stops: number[][];
  triggered: boolean;
}

export function bonusLevel(nScatters: number): BonusLevel | null {
  if (nScatters < 3) return null;
  return nScatters === 3 ? 'rally' : 'final';
}

/** Plays one complete round (base spin + whole bonus) and returns its book.
 *  mode buy_rally / buy_final: forcedBaseStops must show exactly 3 / 4 scatters. */
export function playRound(rawDraw: StopDrawer, id = 0, forcedBaseStops?: number[], mode: ModeName = 'base'): RoundOutcome {
  const BASE = baseStripsOf(mode);
  const buyK = RULES.modes[mode]?.kind === 'buy' ? RULES.modes[mode].scatters : null;
  const events: BookEvent[] = [];
  const allStops: number[][] = [];
  // every draw is recorded: the round can be replayed exactly from allStops
  const draw: StopDrawer = (l) => {
    const v = rawDraw(l);
    allStops.push([...v]);
    return v;
  };
  const emit = (e: Record<string, unknown>) => {
    events.push({ index: events.length, ...e } as BookEvent);
  };
  let stops: number[];
  if (forcedBaseStops) {
    stops = [...forcedBaseStops];
    allStops.push([...stops]);
  } else stops = draw(lengths(BASE));
  let board = windowOf(BASE, stops);
  let pad = padding(BASE, stops);
  emit({ type: 'reveal', gameType: 'basegame', board, stops: [...stops], paddingAbove: pad.above, paddingBelow: pad.below, anticipation: anticipation(board) });
  let wins = evaluateWays(board);
  let scPos = positionsOf(board, S);
  let nSc = scPos.length;
  let scPay = SC_PAY[nSc] ?? 0;
  const baseT = sumPay(wins) + scPay;
  if (baseT > 0) {
    emit({ type: 'winInfo', gameType: 'basegame', multiplier: 1, totalWin: baseT * 10, wins: [...winList(wins, board, 1), ...scatterWin(scPos, scPay)] });
    emit({ type: 'setWin', amount: Math.min(baseT, WINCAP_T) * 10, winLevel: winLevel(baseT / 10) });
  }
  const capped0 = baseT >= WINCAP_T;
  let total = Math.min(baseT, WINCAP_T);
  const triggered = nSc >= 3 && !capped0;
  let freeT = 0;
  if (buyK !== null && nSc !== buyK) throw new Error('bought round must show exactly the bought scatter count');
  const level = triggered ? bonusLevel(nSc) : null;
  if (triggered && level) {
    const exchanges = FS_AWARD[nSc];
    emit({ type: 'bonusStart', bonus: level, exchanges, positions: scPos, ...(buyK !== null ? { bought: true } : {}) });
    const r = playBonus(draw, FREE, level, exchanges, baseT, emit, windowOf, padding, WINCAP_T);
    freeT = r.winT;
    total = Math.min(baseT + freeT, WINCAP_T);
    const bx = freeT / 10;
    const ceremony = bx >= RULES.ceremonyX.grand ? 'grand' : bx >= RULES.ceremonyX.trophy ? 'trophy' : 'none';
    emit({ type: 'bonusEnd', bonus: level, amount: total * 10, bonusWin: freeT * 10, exchanges: r.exchanges, points: r.points, ceremony, winLevel: winLevel(total / 10) });
  }
  emit({ type: 'finalWin', amount: total * 10 });
  return { book: { id, payoutMultiplier: total * 10, events }, stops: allStops, triggered };
}

/** Base-game stops showing exactly k scatters, drawn with the exact
 *  conditional law (demo "test the bonus" feature only). */
export function drawBaseStopsWithScatters(k: number, rand: (n: number) => number): number[] {
  const withS: number[][] = [];
  const withoutS: number[][] = [];
  BASE.forEach((strip) => {
    const a: number[] = [];
    const b: number[] = [];
    for (let s = 0; s < strip.length; s++) {
      const has = Array.from({ length: ROWS }, (_, d) => strip[(s + d) % strip.length]).includes(S);
      (has ? a : b).push(s);
    }
    withS.push(a);
    withoutS.push(b);
  });
  const pats: { bits: number[]; p: number }[] = [];
  for (let m = 0; m < 1 << R; m++) {
    const bits = Array.from({ length: R }, (_, r) => (m >> r) & 1);
    if (bits.reduce((x, y) => x + y, 0) !== k) continue;
    let p = 1;
    bits.forEach((b, r) => (p *= (b ? withS[r].length : withoutS[r].length) / BASE[r].length));
    if (p > 0) pats.push({ bits, p });
  }
  const total = pats.reduce((a, x) => a + x.p, 0);
  let u = (rand(2 ** 32) / 2 ** 32) * total;
  let chosen = pats[pats.length - 1];
  for (const pt of pats) {
    if (u < pt.p) {
      chosen = pt;
      break;
    }
    u -= pt.p;
  }
  return chosen.bits.map((b, r) => {
    const arr = b ? withS[r] : withoutS[r];
    return arr[rand(arr.length)];
  });
}

export const STRIPS = { base: BASE, free: FREE, bonusChance: BONUS_CHANCE };
