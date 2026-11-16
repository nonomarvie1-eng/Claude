// RALLY PATH — EXPERIMENTAL PROTOTYPE (demo lab only, never credited).
// TypeScript port of math/rally_math/rally_path.py; parity enforced by
// rallyPath.test.ts against the fixtures of shared/rally-path-proto.json.
// The presentation never decides anything: the path, its length and its
// reward are computed here, before any animation, from the drawn stops.
import raw from '$shared/rally-path-proto.json';
import { PAY, SC_PAY, evaluateWays, positionsOf, windowOf, winList } from './engine';
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import type { Board, BonusLevel, BookEvent, Position, SymbolName } from './types';

export interface ProtoData {
  experimental: true;
  rules: {
    racket: SymbolName;
    maxShots: number;
    reward: Record<string, number>;
    csRoll: number;
    csTable: [number, number][];
    racketWaysPay: Record<string, number>;
    bonus: Record<BonusLevel, { spins: number; second_serve: boolean; second_serve_max_len?: number }>;
  };
  strips: { base: SymbolName[][]; free: SymbolName[][] };
  stats: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  scenarios: Record<string, { mode: ProtoMode; label: string; draws: number[][]; totalX: number }>;
  fixtures: { mode: ProtoMode; draws: number[][]; events: BookEvent[] }[];
}
export type ProtoMode = 'base' | BonusLevel;

export const PROTO = raw as unknown as ProtoData;
const P = PROTO.rules;
const ROWS = RULES.rows;
const NR = RULES.reels;
const G: SymbolName = 'G';
const WINCAP_T = WINCAP / 10;

const PROTO_PAY: Record<string, Record<number, number>> = { ...PAY, [P.racket]: {} };
for (const [k, v] of Object.entries(P.racketWaysPay)) PROTO_PAY[P.racket][+k] = v;

export interface Rally {
  length: number;
  path: Position[];
  serve: Position;
}

/** Longest Rally Path (deterministic tie-break, see the Python reference). */
export function rally(board: Board): Rally | null {
  const starts: number[] = [];
  for (let r = 0; r < ROWS; r++) if (board[0][r] === G) starts.push(r);
  if (!starts.length) return null;
  const best = Array.from({ length: NR }, () => new Array(ROWS).fill(0));
  const nxt: (number | null)[][] = Array.from({ length: NR }, () => new Array(ROWS).fill(null));
  for (let r = 0; r < ROWS; r++) best[NR - 1][r] = 1;
  for (let i = NR - 2; i >= 0; i--)
    for (let r = 0; r < ROWS; r++) {
      let b = 1;
      let choice: number | null = null;
      for (const r2 of [r, r - 1, r + 1])
        if (r2 >= 0 && r2 < ROWS && board[i + 1][r2] === P.racket && 1 + best[i + 1][r2] > b) {
          b = 1 + best[i + 1][r2];
          choice = r2;
        }
      best[i][r] = b;
      nxt[i][r] = choice;
    }
  let s = starts[0];
  for (const r of starts) if (best[0][r] > best[0][s]) s = r; // ties -> topmost (first)
  const path: Position[] = [{ reel: 0, row: s }];
  let r = s;
  let i = 0;
  while (nxt[i][r] !== null) {
    r = nxt[i][r] as number;
    i++;
    path.push({ reel: i, row: r });
  }
  return { length: path.length, path, serve: { reel: 0, row: s } };
}

export function csPick(roll: number): number {
  let acc = 0;
  for (const [prize, w] of P.csTable) {
    acc += w;
    if (roll < acc) return prize;
  }
  throw new RangeError('roll outside CS table');
}

export function rewardT(length: number, csRoll: number): { t: number; cs: boolean } {
  if (length >= P.maxShots) return { t: csPick(csRoll), cs: true };
  return { t: P.reward[String(length)] ?? 0, cs: false };
}

type Emit = (e: Record<string, unknown>) => void;

function playSpin(draw: StopDrawer, strips: SymbolName[][], emit: Emit, gameType: 'basegame' | 'freegame') {
  const stops = draw(strips.map((s) => s.length));
  const csRoll = draw([P.csRoll])[0];
  const board = windowOf(strips, stops);
  emit({ type: 'reveal', gameType, board, stops: [...stops], anticipation: new Array(NR).fill(0) });
  const wins = evaluateWays(board, PROTO_PAY);
  const waysT = wins.reduce((a, w) => a + w.payPerWay * w.ways, 0);
  if (waysT) emit({ type: 'winInfo', gameType, multiplier: 1, totalWin: waysT * 10, wins: winList(wins, board, 1) });
  const rp = rally(board);
  let rpT = 0;
  let cs = false;
  if (rp) {
    ({ t: rpT, cs } = rewardT(rp.length, csRoll));
    emit({ type: 'rallyPath', length: rp.length, path: rp.path, reward: rpT * 10, championshipShot: cs });
  }
  return { board, stops, rp, rpT, cs, spinT: waysT + rpT };
}

export interface ProtoRound {
  totalT: number;
  events: BookEvent[];
}

/** One prototype round: a base spin, or a whole prototype bonus. */
export function playProtoRound(draw: StopDrawer, mode: ProtoMode): ProtoRound {
  const events: BookEvent[] = [];
  const emit: Emit = (e) => events.push({ index: events.length, ...e } as BookEvent);
  let total = 0;
  if (mode === 'base') {
    const s = playSpin(draw, PROTO.strips.base, emit, 'basegame');
    const nSc = positionsOf(s.board, 'S').length;
    const scPay = SC_PAY[nSc] ?? 0;
    total = s.spinT + scPay;
    if (scPay) emit({ type: 'scatterPay', count: nSc, amount: scPay * 10 });
  } else {
    const cfg = P.bonus[mode];
    let totalSpins = cfg.spins;
    emit({ type: 'protoBonusStart', bonus: mode, spins: totalSpins });
    let done = 0;
    let ssUsed = false;
    while (done < totalSpins) {
      done++;
      emit({ type: 'spinStart', spin: done, total: totalSpins });
      const s = playSpin(draw, PROTO.strips.free, emit, 'freegame');
      total += s.spinT;
      if (s.rp && cfg.second_serve && !ssUsed && s.rp.length <= (cfg.second_serve_max_len ?? 0)) {
        ssUsed = true;
        totalSpins++;
        emit({ type: 'secondServe', added: 1, total: totalSpins });
      }
      emit({ type: 'setTotalWin', amount: total * 10 });
    }
    emit({ type: 'protoBonusEnd', bonus: mode, amount: total * 10, spins: done });
  }
  total = Math.min(total, WINCAP_T);
  emit({ type: 'finalWin', amount: total * 10 });
  return { totalT: total, events };
}
