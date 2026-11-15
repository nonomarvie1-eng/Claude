// TypeScript port of math/rally_math/engine.py, used ONLY by the local demo
// simulator.  Parity with the Python reference is enforced by
// engine.test.ts against shared/parity-fixtures.json (identical books for
// identical stops).
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import type { Board, Book, BookEvent, Position, SymbolName, WinLine } from './types';

const R = RULES.reels;
const ROWS = RULES.rows;
const W: SymbolName = 'W';
const S: SymbolName = 'S';

type Strips = SymbolName[][];
const BASE: Strips = RULES.reelStrips.base;
const FREE: Strips = RULES.reelStrips.free;
const lengths = (s: Strips) => s.map((x) => x.length);

// paytable in t-units (tenths of bet) like the Python engine; events are x10
const PAY: Record<string, Record<number, number>> = {};
for (const [sym, p] of Object.entries(RULES.paytable)) {
  PAY[sym] = {};
  for (const [k, v] of Object.entries(p)) PAY[sym][+k] = v / 10;
}
const SC_PAY: Record<number, number> = {};
for (const [k, v] of Object.entries(RULES.scatterPay)) SC_PAY[+k] = v / 10;
const FS_AWARD: Record<number, number> = {};
for (const [k, v] of Object.entries(RULES.fsAward)) FS_AWARD[+k] = v;
const WINCAP_T = WINCAP / 10;
const LADDER = RULES.rallyLadder;

export function lineEval(seq: SymbolName[]): { pay: number; symbol: SymbolName | null; count: number } {
  let wr = 0;
  while (wr < R && seq[wr] === W) wr++;
  const wildPay = wr >= 3 ? PAY.W[wr] ?? 0 : 0;
  let best = wildPay > 0 ? { pay: wildPay, symbol: W as SymbolName | null, count: wr } : { pay: 0, symbol: null, count: 0 };
  if (wr < R) {
    const s = seq[wr];
    if (s !== S) {
      let n = wr;
      while (n < R && (seq[n] === s || seq[n] === W)) n++;
      const p = PAY[s]?.[n] ?? 0;
      if (p > best.pay) best = { pay: p, symbol: s, count: n };
    }
  }
  return best;
}

export function windowOf(strips: Strips, stops: number[]): Board {
  return strips.map((strip, r) => Array.from({ length: ROWS }, (_, k) => strip[(stops[r] + k) % strip.length]));
}

function mod(a: number, n: number) {
  return ((a % n) + n) % n;
}

function padding(strips: Strips, stops: number[]) {
  return {
    above: strips.map((s, r) => s[mod(stops[r] - 1, s.length)]),
    below: strips.map((s, r) => s[(stops[r] + ROWS) % s.length]),
  };
}

interface LW {
  line: number;
  symbol: SymbolName;
  count: number;
  basePay: number;
}

export function evaluateLines(board: Board): LW[] {
  const out: LW[] = [];
  RULES.paylines.forEach((line, li) => {
    const seq = line.map((row, r) => board[r][row]);
    const e = lineEval(seq);
    if (e.pay > 0 && e.symbol) out.push({ line: li, symbol: e.symbol, count: e.count, basePay: e.pay });
  });
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

function winList(lw: LW[], mult: number): WinLine[] {
  return lw.map((w) => ({
    kind: 'line' as const,
    line: w.line,
    symbol: w.symbol,
    count: w.count,
    basePay: w.basePay * 10,
    multiplier: mult,
    win: w.basePay * mult * 10,
    positions: Array.from({ length: w.count }, (_, r) => ({ reel: r, row: RULES.paylines[w.line][r] })),
  }));
}

function scatterWin(pos: Position[], pay: number): WinLine[] {
  if (pay <= 0) return [];
  return [{ kind: 'scatter', line: null, symbol: 'S', count: pos.length, basePay: pay * 10, multiplier: 1, win: pay * 10, positions: pos }];
}

export interface RoundOutcome {
  book: Book;
  stops: number[][];
  triggered: boolean;
}

/** Plays one complete round (base spin + whole bonus) and returns its book. */
export function playRound(draw: StopDrawer, id = 0, forcedBaseStops?: number[]): RoundOutcome {
  const events: BookEvent[] = [];
  const allStops: number[][] = [];
  const emit = (e: Record<string, unknown>) => {
    events.push({ index: events.length, ...e } as BookEvent);
  };

  let stops = forcedBaseStops ? [...forcedBaseStops] : draw(lengths(BASE));
  allStops.push([...stops]);
  let board = windowOf(BASE, stops);
  let pad = padding(BASE, stops);
  emit({ type: 'reveal', gameType: 'basegame', board, stops: [...stops], paddingAbove: pad.above, paddingBelow: pad.below, anticipation: anticipation(board) });
  let lw = evaluateLines(board);
  let scPos = positionsOf(board, S);
  let nSc = scPos.length;
  let scPay = SC_PAY[nSc] ?? 0;
  const baseT = lw.reduce((a, w) => a + w.basePay, 0) + scPay;
  if (baseT > 0) {
    emit({ type: 'winInfo', gameType: 'basegame', multiplier: 1, totalWin: baseT * 10, wins: [...winList(lw, 1), ...scatterWin(scPos, scPay)] });
    emit({ type: 'setWin', amount: baseT * 10, winLevel: winLevel(baseT / 10) });
  }
  let total = Math.min(baseT, WINCAP_T);
  const capped0 = baseT >= WINCAP_T;
  const triggered = nSc >= 3 && !capped0;
  let freeT = 0;
  let fsSpins = 0;
  let collected = 0;
  let mult = 1;

  if (triggered) {
    let remaining = FS_AWARD[nSc];
    let awardedTotal = remaining;
    emit({ type: 'freeSpinTrigger', totalFs: remaining, positions: scPos });
    while (remaining > 0) {
      remaining -= 1;
      fsSpins += 1;
      emit({ type: 'updateFreeSpin', amount: fsSpins, total: awardedTotal });
      stops = draw(lengths(FREE));
      allStops.push([...stops]);
      board = windowOf(FREE, stops);
      pad = padding(FREE, stops);
      emit({ type: 'reveal', gameType: 'freegame', board, stops: [...stops], paddingAbove: pad.above, paddingBelow: pad.below, anticipation: [0, 0, 0, 0, 0] });
      const wPos = positionsOf(board, W);
      if (wPos.length) {
        collected += wPos.length;
        const newMult = LADDER[Math.min(collected, LADDER.length - 1)];
        emit({ type: 'rallyUp', added: wPos.length, collected, multiplier: newMult, previousMultiplier: mult, positions: wPos });
        mult = newMult;
      }
      lw = evaluateLines(board);
      scPos = positionsOf(board, S);
      nSc = scPos.length;
      scPay = SC_PAY[nSc] ?? 0;
      const spinT = lw.reduce((a, w) => a + w.basePay, 0) * mult + scPay;
      if (spinT > 0) {
        freeT += spinT;
        emit({ type: 'winInfo', gameType: 'freegame', multiplier: mult, totalWin: spinT * 10, wins: [...winList(lw, mult), ...scatterWin(scPos, scPay)] });
        emit({ type: 'setWin', amount: spinT * 10, winLevel: winLevel(spinT / 10) });
      }
      const running = baseT + freeT;
      emit({ type: 'setTotalWin', amount: Math.min(running, WINCAP_T) * 10 });
      if (running >= WINCAP_T) {
        emit({ type: 'wincap', amount: WINCAP_T * 10 });
        break;
      }
      if (nSc >= 3) {
        const add = Math.min(RULES.fsRetrigger, RULES.fsMaxRemaining - remaining);
        if (add > 0) {
          remaining += add;
          awardedTotal += add;
          emit({ type: 'freeSpinRetrigger', totalFs: awardedTotal, added: add, positions: scPos });
        }
      }
    }
    total = Math.min(baseT + freeT, WINCAP_T);
    emit({ type: 'freeSpinEnd', amount: total * 10, winLevel: winLevel(total / 10) });
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
      const has = [0, 1, 2].some((d) => strip[(s + d) % strip.length] === S);
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
  // continuous pick using a 2^32 integer draw
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

export const STRIPS = { base: BASE, free: FREE };
