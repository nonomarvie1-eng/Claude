// GOLDEN SERVE prototypes — port of math/rally_math/golden_serve.py.
// A = CROSS-COURT (hit cells become the drawn target symbol),
// B = COURT SWITCH (hit cells exchange places across the net).
// Parity with Python: goldenServe.test.ts against shared/golden-serve-proto.json.
// The engine fixes board, shot, trajectory, changes and wins BEFORE any animation.
import raw from '$shared/golden-serve-proto.json';
import { SC_PAY, evaluateWays, positionsOf, windowOf, winList } from './engine';
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import type { Board, BonusLevel, BookEvent, Position, SymbolName } from './types';

export type Concept = 'A' | 'B';
export type Phase = 'base' | BonusLevel;
export type ShotKind = 'serve' | 'smash' | 'double';

interface GsData {
  rules: {
    G_ON_REEL1: Record<'base' | 'free', number>;
    TARGET_SYMS: SymbolName[];
    TARGET_W: Record<Phase, number[]>;
    P_SMASH: Record<Phase, number>;
    P_DOUBLE: Record<Phase, number>;
    BONUS: Record<BonusLevel, { spins: number }>;
  };
  serveDraw: number[];
  strips: { base: SymbolName[][]; free: SymbolName[][] };
  stats: Record<Concept, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  scenarios: Record<string, { label: string; draws: number[][]; totalX: Record<Concept, number> }>;
  fixtures: { concept: Concept; draws: number[][]; events: BookEvent[] }[];
}
export const GS = raw as unknown as GsData;
const P = GS.rules;
const ROWS = RULES.rows;
const NR = RULES.reels;
const WINCAP_T = WINCAP / 10;

export function targetOf(phase: Phase, roll: number): SymbolName {
  let acc = 0;
  for (let i = 0; i < P.TARGET_SYMS.length; i++) {
    acc += P.TARGET_W[phase][i];
    if (roll < acc) return P.TARGET_SYMS[i];
  }
  throw new RangeError('target roll outside table');
}

export function shotOf(phase: Phase, roll: number): ShotKind {
  const ps = P.P_SMASH[phase];
  const pd = P.P_DOUBLE[phase];
  return roll < ps ? 'smash' : roll < ps + pd ? 'double' : 'serve';
}

export const pathRows = (r0: number, rt: number) => Array.from({ length: NR }, (_, i) => Math.floor(r0 + ((rt - r0) * i) / 5 + 0.5));

export function trajectories(r0: number, shot: ShotKind, rt: number, rt2: number): [number, number][][] {
  const t1 = pathRows(r0, rt).map((r, i) => [i, r] as [number, number]);
  const out = [t1];
  if (shot === 'smash') out.push([[0, r0], ...t1.slice(1).map(([i, r]) => [i, r < ROWS - 1 ? r + 1 : r - 1] as [number, number])]);
  else if (shot === 'double') out.push(pathRows(r0, rt2).map((r, i) => [i, r] as [number, number]));
  return out;
}

export interface Change { reel: number; row: number; from: SymbolName; to: SymbolName }
export interface Swap { a: Position & { sym: SymbolName }; b: Position & { sym: SymbolName } }

export function applyShot(board: Board, concept: Concept, phase: Phase, serve: number[]): { board: Board; ev: Record<string, unknown> | null } {
  const starts: number[] = [];
  for (let r = 0; r < ROWS; r++) if (board[0][r] === 'G') starts.push(r);
  if (!starts.length) return { board, ev: null };
  const [rt, symRoll, spRoll, rt2] = serve;
  const r0 = starts[0];
  const shot = shotOf(phase, spRoll);
  const trajs = trajectories(r0, shot, rt, rt2);
  const b = board.map((c) => [...c]);
  const paths = trajs.map((t) => t.map(([reel, row]) => ({ reel, row })));
  if (concept === 'A') {
    const T = targetOf(phase, symRoll);
    const seen = new Set<string>();
    const cells: [number, number][] = [];
    for (const t of trajs) for (const c of t) if (!seen.has(c.join())) { seen.add(c.join()); cells.push(c); }
    cells.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
    const changes: Change[] = [];
    for (const [i, r] of cells) {
      const fr = b[i][r];
      if (fr === 'W' || fr === 'S' || fr === T) continue;
      b[i][r] = T;
      changes.push({ reel: i, row: r, from: fr, to: T });
    }
    return { board: b, ev: { concept: 'A', shot, origin: { reel: 0, row: r0 }, target: T, paths, changes } };
  }
  const swaps: Swap[] = [];
  for (const t of trajs) {
    const row = new Map(t);
    for (const [a, c] of [[1, 4], [2, 5]]) {
      const ra = row.get(a)!, rc = row.get(c)!;
      const sa = b[a][ra], sc = b[c][rc];
      b[a][ra] = sc;
      b[c][rc] = sa;
      swaps.push({ a: { reel: a, row: ra, sym: sa }, b: { reel: c, row: rc, sym: sc } });
    }
  }
  const net = b[3][new Map(trajs[0]).get(3)!];
  b[0][r0] = net;
  return { board: b, ev: { concept: 'B', shot, origin: { reel: 0, row: r0 }, paths, swaps, changes: [{ reel: 0, row: r0, from: 'G', to: net }] } };
}

type Emit = (e: Record<string, unknown>) => void;

function playSpin(draw: StopDrawer, concept: Concept, phase: Phase, emit: Emit, gameType: 'basegame' | 'freegame') {
  const strips = phase === 'base' ? GS.strips.base : GS.strips.free;
  const stops = draw(strips.map((s) => s.length));
  const serve = draw(GS.serveDraw);
  const board = windowOf(strips, stops);
  emit({ type: 'reveal', gameType, board, stops: [...stops], anticipation: new Array(NR).fill(0) });
  const { board: nb, ev } = applyShot(board, concept, phase, serve);
  if (ev) emit({ type: 'goldenServe', ...ev, board: nb });
  const wins = evaluateWays(nb);
  const t = wins.reduce((a, w) => a + w.payPerWay * w.ways, 0);
  if (t) emit({ type: 'winInfo', gameType, multiplier: 1, totalWin: t * 10, wins: winList(wins, nb, 1) });
  return { t, orig: board, shot: ev ? (ev.shot as ShotKind) : null };
}

/** One complete paid round (port of golden_serve.play_round). */
export function playGsRound(draw: StopDrawer, concept: Concept, id = 0) {
  const events: BookEvent[] = [];
  const emit: Emit = (e) => events.push({ index: events.length, ...e } as BookEvent);
  const s = playSpin(draw, concept, 'base', emit, 'basegame');
  const pos = positionsOf(s.orig, 'S');
  const nSc = pos.length;
  const scPay = SC_PAY[nSc] ?? 0;
  if (scPay) emit({ type: 'scatterPay', count: nSc, amount: scPay * 10, positions: pos });
  let total = s.t + scPay;
  emit({ type: 'setWin', amount: Math.min(total, WINCAP_T) * 10 });
  let bonus: BonusLevel | null = null;
  if (nSc >= 3) {
    bonus = nSc === 3 ? 'rally' : 'final';
    const n = P.BONUS[bonus].spins;
    emit({ type: 'gsBonusStart', bonus, spins: n, positions: pos });
    let bt = 0;
    for (let k = 1; k <= n; k++) {
      emit({ type: 'spinStart', spin: k, total: n });
      const f = playSpin(draw, concept, bonus, emit, 'freegame');
      bt += f.t;
      emit({ type: 'setTotalWin', amount: Math.min(total + bt, WINCAP_T) * 10 });
    }
    total += bt;
    emit({ type: 'gsBonusEnd', bonus, amount: Math.min(total, WINCAP_T) * 10, bonusWin: Math.min(bt, WINCAP_T) * 10 });
  }
  total = Math.min(total, WINCAP_T);
  emit({ type: 'finalWin', amount: total * 10 });
  return { book: { id, payoutMultiplier: total * 10, events }, bonus };
}
