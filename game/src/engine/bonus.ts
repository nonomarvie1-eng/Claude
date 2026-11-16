// THE FINAL SET — TypeScript port of math/rally_math/bonus.py (scalar engine).
// Used ONLY by the local demo simulator.  Parity with the Python reference
// engine (same draws -> same events) is enforced by engine.test.ts.
import { RULES } from './rules';
import type { StopDrawer } from './rng';
import type { Board, SymbolName } from './types';

const F = RULES.finalSet;
const ROWS = RULES.rows;
export const ZONE_NAMES = ['DL', 'DC', 'DR', 'SL', 'SC', 'SR'] as const;
export const SHOTS = ['RALLY', 'ACE', 'SMASH', 'PASSING', 'DROP', 'GOLDEN'] as const;
export type ShotName = (typeof SHOTS)[number];
export const PASS_PATHS = [[0, 1, 5], [2, 1, 3], [3, 4, 2], [5, 4, 0]];
const NZ = 6;

/** AUX draw vector: [shot roll, zone6, deep3, short3, path4, gr_n, gr1..grMAX, line, call] */
export const AUX_LEN = [F.SHOT_ROLL, 6, 3, 3, 4, F.GR_MAX - F.GR_MIN + 1, ...Array(F.GR_MAX).fill(6), 1000, 1000];
const I_LINE = 6 + F.GR_MAX;
const I_CALL = I_LINE + 1;

export function zoneCells(z: number): [number, number][] {
  const c = z % 3;
  const rows = Math.floor(z / 3) === 0 ? [0, 1, 2] : [3, 4];
  const out: [number, number][] = [];
  for (const r of [2 * c, 2 * c + 1]) for (const row of rows) out.push([r, row]);
  return out;
}

export function neighbours(z: number): number[] {
  const c = z % 3;
  const d = Math.floor(z / 3);
  const out = [c - 1, c + 1].filter((x) => x >= 0 && x < 3).map((x) => d * 3 + x);
  out.push((1 - d) * 3 + c);
  return out;
}

function table(level: string, cp: boolean): number[] {
  const t = cp ? F.CP_TABLE : level === 'final' ? F.FINAL_TABLE : F.RALLY_TABLE;
  return SHOTS.map((s) => t[s]);
}

function pick(w: number[], roll: number): number {
  let acc = 0;
  for (let i = 0; i < w.length; i++) {
    acc += w[i];
    if (roll < acc) return i;
  }
  throw new Error('roll outside table');
}

export function shotZones(shot: number, aux: number[]): number[] {
  switch (SHOTS[shot]) {
    case 'RALLY':
      return [aux[1]];
    case 'ACE':
      return [aux[2]];
    case 'SMASH':
      return [aux[1], ...neighbours(aux[1])];
    case 'PASSING':
      return [...PASS_PATHS[aux[4]]];
    case 'DROP':
      return [3 + aux[3]];
    default: {
      const n = F.GR_MIN + aux[5];
      return Array.from({ length: n }, (_, i) => aux[6 + i]);
    }
  }
}

export function courtValues(board: Board): { vals: number[]; scs: number[] } {
  const vals: number[] = [];
  const scs: number[] = [];
  for (let z = 0; z < NZ; z++) {
    let v = 0;
    let s = 0;
    for (const [r, row] of zoneCells(z)) {
      const sym = board[r][row];
      v += F.COURT_VALUE[sym];
      if (sym === 'S') s++;
    }
    vals.push(v);
    scs.push(s);
  }
  return { vals, scs };
}

type Emit = (e: Record<string, unknown>) => void;

export function playBonus(
  draw: StopDrawer,
  freeStrips: SymbolName[][],
  level: 'rally' | 'final',
  exchanges: number,
  baseT: number,
  emit: Emit,
  windowOf: (s: SymbolName[][], st: number[]) => Board,
  padding: (s: SymbolName[][], st: number[]) => { above: SymbolName[]; below: SymbolName[] },
  wincapT: number,
): { winT: number; capped: boolean; exchanges: number; points: number } {
  let marks = new Array(NZ).fill(0);
  let remaining = exchanges;
  let awarded = exchanges;
  let played = 0;
  let points = 0;
  let winT = 0;
  let capped = false;
  const capRoom = wincapT - baseT;
  const lengths = freeStrips.map((s) => s.length);
  while (remaining > 0) {
    const cp = level === 'final' && remaining === 1;
    remaining -= 1;
    played += 1;
    const stops = draw(lengths);
    const aux = draw(AUX_LEN);
    const board = windowOf(freeStrips, stops);
    const { vals, scs } = courtValues(board);
    const pad = padding(freeStrips, stops);
    emit({ type: 'exchangeStart', exchange: played, total: awarded, remaining, championshipPoint: cp, marks: [...marks] });
    emit({ type: 'reveal', gameType: 'freegame', board, stops: [...stops], paddingAbove: pad.above, paddingBelow: pad.below, anticipation: new Array(RULES.reels).fill(0), courtValues: vals.map((v) => v * 10), courtScatters: [...scs] });
    const shot = pick(table(level, cp), aux[0]);
    const name = SHOTS[shot];
    const path = shotZones(shot, aux);
    let zones = [...path];
    let hawk: 'in' | 'out' | null = null;
    let replay = 0;
    if (level === 'final' && (name === 'RALLY' || name === 'ACE' || name === 'DROP') && aux[I_LINE] < F.P_LINE) {
      hawk = aux[I_CALL] < F.P_IN ? 'in' : 'out';
      if (hawk === 'out') {
        zones = [];
        replay = 1;
      }
    }
    const hits: Record<string, unknown>[] = [];
    let ext = replay;
    let spinT = 0;
    for (const z of zones) {
      const pay = vals[z];
      let markPrize = 0;
      if (marks[z] > 0) {
        markPrize = F.MARK_PRIZE;
        marks[z] = 0;
      }
      const extra = scs[z] * (name === 'DROP' ? 2 : 1);
      ext += extra;
      spinT += pay + markPrize;
      hits.push({ zone: z, zoneName: ZONE_NAMES[z], value: pay * 10, markPrize: markPrize * 10, scatters: scs[z], extraExchanges: extra, cells: zoneCells(z).map(([reel, row]) => ({ reel, row })) });
      if (pay + markPrize > 0) points += 1;
    }
    let prize = 0;
    const newMarks: [number, number][] = [];
    if (name === 'ACE' && zones.length) {
      prize += F.ACE_PRIZE;
      newMarks.push([zones[0], F.ACE_MARK]);
    }
    if (name === 'DROP' && zones.length) newMarks.push([zones[0], F.DROP_MARK]);
    if (hawk === 'in') {
      prize += F.HAWK_PRIZE;
      newMarks.push([zones[0], F.HAWK_MARK]);
    }
    if (name === 'GOLDEN') for (const z of [...new Set(zones)]) newMarks.push([z, F.GOLDEN_MARK]);
    let setNow = new Set<number>();
    for (const [z, d] of newMarks) {
      marks[z] = Math.max(marks[z], d);
      setNow.add(z);
    }
    const slam = marks.every((m) => m > 0);
    if (slam) prize += F.SLAM_PRIZE;
    spinT += prize;
    if (hawk !== null) emit({ type: 'hawkEye', zone: path[0], call: hawk, prize: (hawk === 'in' ? F.HAWK_PRIZE : 0) * 10, replay: hawk === 'out' });
    emit({
      type: 'shot', shot: name, zones: hits.length ? hits.map((h) => h.zone) : zones, path, hits, prize: prize * 10, win: spinT * 10,
      marksSet: newMarks.map(([zone, duration]) => ({ zone, duration })), grandSlam: slam, hawkEye: hawk,
    });
    if (slam) {
      emit({ type: 'grandSlam', prize: F.SLAM_PRIZE * 10 });
      marks = new Array(NZ).fill(0);
      setNow = new Set();
    }
    const expired: number[] = [];
    for (let z = 0; z < NZ; z++) {
      if (marks[z] > 0 && !setNow.has(z)) {
        marks[z] -= 1;
        if (marks[z] === 0) expired.push(z);
      }
    }
    if (expired.length) emit({ type: 'markExpire', zones: expired });
    winT += spinT;
    const add = Math.min(ext, F.MAX_REMAINING - remaining);
    if (add > 0) {
      remaining += add;
      awarded += add;
      emit({ type: 'extraExchange', added: add, total: awarded, reason: replay && add === 1 && ext === 1 ? 'replay' : 'scatter' });
    }
    emit({ type: 'exchangeEnd', exchange: played, win: spinT * 10, points, bonusWin: Math.min(winT, capRoom) * 10, marks: [...marks] });
    emit({ type: 'setTotalWin', amount: Math.min(baseT + winT, wincapT) * 10 });
    if (baseT + winT >= wincapT) {
      capped = true;
      emit({ type: 'wincap', amount: wincapT * 10 });
      break;
    }
  }
  return { winT: Math.min(winT, capRoom), capped, exchanges: played, points };
}
