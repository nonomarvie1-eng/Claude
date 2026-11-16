// GOLDEN SERVE — RETURN SPINS: port of math/rally_math/return_spins.py.
// Parity: returnSpins.test.ts against shared/return-spins.json fixtures.
// The engine fixes every stop, strike, zone, respin and win before any animation.
import raw from '$shared/return-spins.json';
import { SC_PAY, evaluateWays, positionsOf, winList } from './engine';
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import type { Board, BonusLevel, BookEvent, SymbolName } from './types';

export type RsPhase = 'base' | BonusLevel;
interface RsData {
  rules: { G_PER_REEL: Record<'base' | 'free', number[]>; P_SMASH: Record<RsPhase, number>; MAX_RETURNS: Record<RsPhase, number>; BONUS: Record<BonusLevel, { spins: number }> };
  zones: Record<'left' | 'center' | 'right', number[]>;
  strips: { base: SymbolName[][]; free: SymbolName[][] };
  stats: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  scenarios: Record<string, { label: string; draws: number[][]; totalX: number; stagesX: number[] | null }>;
  fixtures: { draws: number[][]; events: BookEvent[] }[];
}
export const RS = raw as unknown as RsData;
const P = RS.rules;
const NR = RULES.reels;
const ROWS = RULES.rows;
const ORDER = ['left', 'center', 'right'] as const;
const WINCAP_T = WINCAP / 10;

const windowOf = (strips: SymbolName[][], stops: number[]): Board =>
  strips.map((st, r) => Array.from({ length: ROWS }, (_, k) => st[(stops[r] + k) % st.length]));

export function strike(phase: RsPhase, prev: string | null, zoneRoll: number, smashRoll: number): { zone: string; reels: number[]; smash: boolean } {
  const covered = new Set(prev ? prev.split('+') : []);
  const cand = ORDER.filter((z) => !covered.has(z));
  const z = cand[Math.floor((zoneRoll * cand.length) / 1000)];
  if (smashRoll < P.P_SMASH[phase]) {
    const z2 = z === 'left' ? 'left+center' : z === 'right' ? 'center+right' : zoneRoll % 2 === 0 ? 'left+center' : 'center+right';
    const reels = z2.split('+').flatMap((p) => RS.zones[p as keyof RsData['zones']]).sort((a, b) => a - b);
    return { zone: z2, reels, smash: true };
  }
  return { zone: z, reels: RS.zones[z], smash: false };
}

type Emit = (e: Record<string, unknown>) => void;

function playSpin(draw: StopDrawer, phase: RsPhase, emit: Emit, gameType: 'basegame' | 'freegame', totalBefore: number) {
  const strips = phase === 'base' ? RS.strips.base : RS.strips.free;
  const stops = [...draw(strips.map((s) => s.length))];
  let board = windowOf(strips, stops);
  const first = board;
  emit({ type: 'reveal', gameType, board, stops: [...stops], anticipation: new Array(NR).fill(0) });
  let spinT = 0;
  let stage = 0;
  const evaluate = () => {
    const wins = evaluateWays(board);
    const t = wins.reduce((a, w) => a + w.payPerWay * w.ways, 0);
    spinT += t;
    emit({ type: 'stageWin', gameType, stage, stageWin: t * 10, spinTotal: spinT * 10, runningTotal: (totalBefore + spinT) * 10, wins: t ? winList(wins, board, 1) : [] });
  };
  evaluate();
  const gpos: [number, number][] = [];
  for (let r = 0; r < NR; r++) for (let row = 0; row < ROWS; row++) if (board[r][row] === 'G') gpos.push([r, row]);
  let returns = 0;
  let prev: string | null = null;
  let origin: [number, number] | null = gpos.length ? gpos[0] : null;
  let kind = 'serve';
  while (origin) {
    const [zr, sr] = draw([1000, 1000]);
    const { zone, reels, smash } = strike(phase, prev, zr, sr);
    emit({ type: 'serve', kind, smash, origin: { reel: origin[0], row: origin[1] }, zone, reels, returnIndex: returns, maxReturns: P.MAX_RETURNS[phase] });
    const nw = draw(reels.map((r) => strips[r].length));
    reels.forEach((r, i) => (stops[r] = nw[i]));
    board = windowOf(strips, stops);
    stage++;
    emit({ type: 'respin', gameType, stage, reels, stops: [...stops], board });
    evaluate();
    prev = zone;
    const newg: [number, number][] = [];
    for (const r of reels) for (let row = 0; row < ROWS; row++) if (board[r][row] === 'G') newg.push([r, row]);
    if (newg.length && returns < P.MAX_RETURNS[phase]) {
      returns++;
      origin = newg[0];
      kind = 'return';
    } else origin = null;
  }
  return { t: spinT, first };
}

/** One complete paid round (port of return_spins.play_round). */
export function playRsRound(draw: StopDrawer, id = 0) {
  const events: BookEvent[] = [];
  const emit: Emit = (e) => events.push({ index: events.length, ...e } as BookEvent);
  const s = playSpin(draw, 'base', emit, 'basegame', 0);
  const pos = positionsOf(s.first, 'S');
  const sc = SC_PAY[pos.length] ?? 0;
  if (sc) emit({ type: 'scatterPay', count: pos.length, amount: sc * 10, positions: pos });
  let total = s.t + sc;
  emit({ type: 'setWin', amount: Math.min(total, WINCAP_T) * 10 });
  let bonus: BonusLevel | null = null;
  if (pos.length >= 3) {
    bonus = pos.length === 3 ? 'rally' : 'final';
    const n = P.BONUS[bonus].spins;
    emit({ type: 'rsBonusStart', bonus, spins: n, positions: pos });
    let bt = 0;
    for (let k = 1; k <= n; k++) {
      emit({ type: 'spinStart', spin: k, total: n });
      bt += playSpin(draw, bonus, emit, 'freegame', total + bt).t;
      emit({ type: 'setTotalWin', amount: Math.min(total + bt, WINCAP_T) * 10 });
    }
    total += bt;
    emit({ type: 'rsBonusEnd', bonus, bonusWin: Math.min(bt, WINCAP_T) * 10, amount: Math.min(total, WINCAP_T) * 10 });
  }
  total = Math.min(total, WINCAP_T);
  emit({ type: 'finalWin', amount: total * 10 });
  return { book: { id, payoutMultiplier: total * 10, events }, bonus };
}
