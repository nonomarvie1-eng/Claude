import type { Ticker } from 'pixi.js';

export const ease = {
  linear: (u: number) => u,
  inCubic: (u: number) => u * u * u,
  outCubic: (u: number) => 1 - (1 - u) ** 3,
  inOutCubic: (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2),
  outBack: (u: number, s = 1.2) => 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2,
  outElastic: (u: number) => (u === 0 || u === 1 ? u : 2 ** (-10 * u) * Math.sin((u * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1),
};

export class Tweener {
  // time left over by a tween that ended between two frames; a tween started
  // in the same frame (chained `await`) starts with it, so sequences do not
  // lose up to one frame per step on slow devices.
  private carry = 0;
  private carryAt = -1;
  constructor(private ticker: Ticker, public speed = () => 1) {}

  tween(ms: number, fn: (u: number) => void, easing: (u: number) => number = ease.linear): Promise<void> {
    if (ms / this.speed() <= 0) {
      fn(1);
      return Promise.resolve();
    }
    return new Promise((resolve) => {
      let t = this.carryAt === this.ticker.lastTime ? this.carry : 0;
      // speed is sampled every frame: "skip" / turbo also accelerate running animations
      const tick = (tk: Ticker) => {
        t += tk.deltaMS * this.speed();
        const u = Math.min(1, t / ms);
        fn(easing(u));
        if (u >= 1) {
          this.ticker.remove(tick);
          this.carry = Math.min(t - ms, 100);
          this.carryAt = this.ticker.lastTime;
          resolve();
        }
      };
      this.ticker.add(tick);
    });
  }

  wait(ms: number): Promise<void> {
    return this.tween(ms, () => {});
  }
}
