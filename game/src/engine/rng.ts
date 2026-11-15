/** Unbiased uniform integer in [0, n) from the platform CSPRNG.
 *  Used ONLY by the local demo simulator.  On Stake Engine, outcomes are
 *  selected server-side by the RGS; the browser never decides a result. */
export function cryptoInt(n: number): number {
  if (!Number.isInteger(n) || n <= 0 || n > 2 ** 32) throw new RangeError('bad range');
  const limit = Math.floor(2 ** 32 / n) * n; // rejection sampling removes modulo bias
  const buf = new Uint32Array(1);
  for (;;) {
    crypto.getRandomValues(buf);
    if (buf[0] < limit) return buf[0] % n;
  }
}

export type StopDrawer = (lengths: number[]) => number[];

export const cryptoDrawer: StopDrawer = (lengths) => lengths.map((n) => cryptoInt(n));

/** Replays recorded stops (parity tests, faithful replays). */
export function listDrawer(stops: number[][]): StopDrawer {
  let i = 0;
  return () => {
    if (i >= stops.length) throw new Error('replay exhausted');
    return [...stops[i++]];
  };
}
