// CHAMPIONSHIP DUEL — port of math/rally_math/championship_duel.py.
// Parity: duel.test.ts against shared/championship-duel.json fixtures.
// Every outcome and prize is decided here before any animation.
import raw from '$shared/championship-duel.json';
import { SC_PAY, evaluateWays, positionsOf, windowOf, winList, STRIPS } from './engine';
import { RULES, WINCAP } from './rules';
import type { StopDrawer } from './rng';
import type { BookEvent } from './types';

export type DuelLevel = 'tiebreak' | 'final';
export type Outcome = 'DOUBLE_FAULT' | 'ACE' | 'LOST' | 'RALLY_WON' | 'WINNER' | 'GOLDEN';
type Table = [number, number][];
interface LevelRules {
  POINTS: number;
  RALLY_SHOTS: [number, number];
  P_GMP?: number;
  SERVE1: Record<'ACE' | 'FAULT' | 'IN', number>;
  SERVE2: Record<'ACE' | 'DOUBLE_FAULT' | 'IN', number>;
  RALLY: Record<'LOST' | 'RALLY_WON' | 'WINNER' | 'GOLDEN', number>;
  PRIZES: Record<'ACE' | 'RALLY_WON' | 'WINNER' | 'GOLDEN', Table>;
}
interface DuelData {
  rules: { LEVELS: Record<DuelLevel, LevelRules>; GMP_TABLE: Table };
  exact: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  pointScenarios: Record<string, { level: DuelLevel; label: string; draws: number[]; prizeX: number; outcome: Outcome }>;
  roundScenarios: Record<string, { label: string; draws: number[][]; totalX: number }>;
  fixtures: ({ kind: 'round'; draws: number[][]; events: BookEvent[] } | { kind: 'point'; level: DuelLevel; draws: number[]; events: BookEvent[] })[];
}
export const DUEL = raw as unknown as DuelData;
const R = DUEL.rules;
const WON = new Set<Outcome>(['ACE', 'RALLY_WON', 'WINNER', 'GOLDEN']);
const WINCAP_T = WINCAP / 10;

function pick(t: Table, roll: number) {
  let acc = 0;
  for (const [v, w] of t) {
    acc += w;
    if (roll < acc) return v;
  }
  throw new RangeError('roll outside table');
}
function pick3<K extends string>(probs: Record<K, number>, roll: number): K {
  let acc = 0;
  for (const [k, w] of Object.entries(probs) as [K, number][]) {
    acc += w;
    if (roll < acc) return k;
  }
  throw new RangeError('roll outside table');
}

export interface DuelPoint {
  point: number;
  goldenMatchPoint: boolean;
  firstServe: 'ACE' | 'FAULT' | 'IN';
  secondServe: 'ACE' | 'DOUBLE_FAULT' | 'IN' | null;
  outcome: Outcome;
  won: boolean;
  prize: number; // x bet
  side: 'deuce' | 'ad';
  target: 'T' | 'wide' | 'body';
  shots: number;
  finish: 'cross' | 'line' | 'inside-out';
}

export function playPoint(level: DuelLevel, draws: number[], pointIndex: number): DuelPoint {
  const L = R.LEVELS[level];
  const [gmpR, s1, s2, rr, pr, pres] = draws;
  const gmp = (L.P_GMP ?? 0) > gmpR;
  const first = pick3(L.SERVE1, s1);
  let second: DuelPoint['secondServe'] = null;
  let outcome: Outcome | null = null;
  if (first === 'ACE') outcome = 'ACE';
  else if (first === 'FAULT') {
    second = pick3(L.SERVE2, s2);
    outcome = second === 'ACE' ? 'ACE' : second === 'DOUBLE_FAULT' ? 'DOUBLE_FAULT' : null;
  }
  if (outcome === null) outcome = pick3(L.RALLY, rr);
  const won = WON.has(outcome);
  const prize = won ? pick(gmp ? R.GMP_TABLE : L.PRIZES[outcome as keyof LevelRules['PRIZES']], pr) : 0;
  const [lo, hi] = L.RALLY_SHOTS;
  const shots = outcome === 'ACE' || outcome === 'DOUBLE_FAULT' ? 1 : lo + (Math.floor(pres / 3) % (hi - lo + 1));
  return {
    point: pointIndex + 1, goldenMatchPoint: gmp, firstServe: first, secondServe: second, outcome, won, prize,
    side: pointIndex % 2 === 0 ? 'deuce' : 'ad',
    target: (['T', 'wide', 'body'] as const)[pres % 3],
    shots,
    finish: (['cross', 'line', 'inside-out'] as const)[Math.floor(pres / 20) % 3],
  };
}

type Emit = (e: Record<string, unknown>) => void;

/** One complete paid round: v6 base spin; 3 scatters -> TIE-BREAK DUEL, 4+ -> THE GRAND FINAL. */
export function playDuelRound(draw: StopDrawer, id = 0) {
  const events: BookEvent[] = [];
  const emit: Emit = (e) => events.push({ index: events.length, ...e } as BookEvent);
  const strips = STRIPS.base;
  const stops = draw(strips.map((s) => s.length));
  const board = windowOf(strips, stops);
  emit({ type: 'reveal', gameType: 'basegame', board, stops: [...stops], anticipation: new Array(RULES.reels).fill(0) });
  const wins = evaluateWays(board);
  const t = wins.reduce((a, w) => a + w.payPerWay * w.ways, 0);
  const pos = positionsOf(board, 'S');
  const sc = SC_PAY[pos.length] ?? 0;
  if (t) emit({ type: 'winInfo', gameType: 'basegame', multiplier: 1, totalWin: t * 10, wins: winList(wins, board, 1) });
  if (sc) emit({ type: 'scatterPay', count: pos.length, amount: sc * 10, positions: pos });
  let total = t + sc;
  emit({ type: 'setWin', amount: Math.min(total, WINCAP_T) * 10 });
  let level: DuelLevel | null = null;
  if (pos.length >= 3) {
    level = pos.length === 3 ? 'tiebreak' : 'final';
    const n = R.LEVELS[level].POINTS;
    emit({ type: 'duelStart', level, points: n, positions: pos });
    let bt = 0;
    for (let i = 0; i < n; i++) {
      const p = playPoint(level, draw(new Array(6).fill(1000)), i);
      bt += p.prize * 10;
      emit({ type: 'duelPoint', ...p, prize: p.prize * 100, bonusTotal: Math.min(bt, WINCAP_T) * 10 });
    }
    total += bt;
    emit({ type: 'duelEnd', level, bonusWin: Math.min(bt, WINCAP_T) * 10, amount: Math.min(total, WINCAP_T) * 10 });
  }
  total = Math.min(total, WINCAP_T);
  emit({ type: 'finalWin', amount: total * 10 });
  return { book: { id, payoutMultiplier: total * 10, events }, level };
}

/** Demo lab: one point as a book of its own (never credited). */
export function playSinglePoint(level: DuelLevel, draws: number[]) {
  const p = playPoint(level, draws, 0);
  const v = p.prize * 100;
  const events = [
    { index: 0, type: 'duelStart', level, points: 1, positions: [], single: true },
    { index: 1, type: 'duelPoint', ...p, prize: v, bonusTotal: v },
    { index: 2, type: 'duelEnd', level, bonusWin: v, amount: v },
    { index: 3, type: 'finalWin', amount: v },
  ] as unknown as BookEvent[];
  return { point: p, events };
}

/** Demo lab: a short sequence of single points (recorded or random draws),
 *  shown on the court but never debited nor credited. */
export function playLabPoints(list: { level: DuelLevel; draws: number[] }[]) {
  const level = list[0].level;
  const events: Record<string, unknown>[] = [{ index: 0, type: 'duelStart', level, points: list.length, positions: [], single: true }];
  let tot = 0;
  list.forEach((it, i) => {
    const p = playPoint(it.level, it.draws, i);
    tot += p.prize * 100;
    events.push({ index: events.length, type: 'duelPoint', ...p, prize: p.prize * 100, bonusTotal: tot });
  });
  events.push({ index: events.length, type: 'duelEnd', level, bonusWin: tot, amount: tot });
  events.push({ index: events.length, type: 'finalWin', amount: tot });
  return events as unknown as BookEvent[];
}
