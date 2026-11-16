// CHAMPIONSHIP DUEL — court view (PixiJS, 2.5D).
// Presentation only: every point is drawn from its duelPoint event (outcome,
// prize, serve side, target, number of shots, finish), computed by the engine
// before the animation.  The drawing is fully deterministic (no Math.random):
// the same book always shows the same point.  Skipping only accelerates.
import { Container, Graphics, Sprite, Text } from 'pixi.js';
import { audio } from '../audio/audio';
import type { BookEvent } from '../engine/types';
import { money } from '../game/format';
import { fmt } from '../i18n/strings';
import type { RallyScene } from './scene';
import { ease } from './tween';

type PointEv = Extract<BookEvent, { type: 'duelPoint' }>;
type V3 = { x: number; y: number; z: number };

// court geometry in metres (ITF): length 23.77, doubles 10.97, singles 8.23, service line 6.40 from the net
const LEN = 23.77, NET = LEN / 2, HD = 10.97 / 2, HS = 8.23 / 2, SVC = 6.4;
const K = 0.0514; // perspective: far baseline drawn at ~45 % of the near width
const C = { night: 0x071826, navy: 0x0b2440, gold: 0xe7c877, champagne: 0xd6b36a, ivory: 0xf4e9d4, court: 0x16483e, surround: 0x0e322b, tennis: 0xd9ef38 };

export class Court {
  root = new Container();
  private bg = new Graphics();
  private crowd = new Sprite();
  private lights: Sprite[] = [];
  private surface = new Graphics();
  private netG = new Graphics();
  private shadow = new Graphics();
  private ball = new Graphics();
  private trail = new Graphics();
  private rNear = new Sprite();
  private rFar = new Sprite();
  private flash = new Graphics();
  private board = new Container(); // scoreboard
  private boardBg = new Graphics();
  private bTitle!: Text;
  private bPoint!: Text;
  private bTotal!: Text;
  private caption = new Container();
  private golden = false;
  private ballPos: V3 = { x: 0, y: -1, z: 1 };
  // projection parameters (set by layout)
  private cx = 0;
  private U = 1;
  private yNear = 0;
  private yFar = 0;
  private sFar = 1 / (1 + K * LEN);
  level: 'tiebreak' | 'final' = 'tiebreak';
  /** QA: what the court actually drew for the last point */
  qa = { points: 0, serves: 0, bounces: 0, strokes: 0, lastCaption: '', durations: [] as { outcome: string; ms: number; animMs: number; actionMs: number; frames: number }[] };
  private resultClock = 0;
  private feet = new Graphics();

  constructor(private s: RallyScene) {
    this.root.visible = false;
    this.crowd.anchor.set(0.5, 0);
    this.crowd.alpha = 0.55;
    for (let i = 0; i < 2; i++) {
      const l = new Sprite();
      l.anchor.set(0.5);
      l.blendMode = 'add';
      l.alpha = 0.35;
      this.lights.push(l);
    }
    this.rNear.anchor.set(0.3, 0.88);
    this.rFar.anchor.set(0.3, 0.88);
    this.root.addChild(this.bg, this.crowd, ...this.lights, this.surface, this.feet, this.shadow, this.trail, this.rFar, this.netG, this.ball, this.rNear, this.flash, this.board, this.caption);
    this.boardBg.eventMode = 'none';
    this.board.addChild(this.boardBg);
  }

  init() {
    const tex = this.s.tex;
    this.crowd.texture = tex.crowd_portrait ?? tex.crowd_landscape;
    for (const l of this.lights) l.texture = tex.glow;
    this.rNear.texture = tex.sym_H4;
    this.rFar.texture = tex.sym_H4;
    this.bTitle = this.s.goldText('TIE-BREAK DUEL', 30);
    this.bPoint = this.s.plainText('', 22, '#F4E9D4', '800');
    this.bTotal = new Text({ text: '', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 34, fill: '#FFF4D6' } });
    this.bTotal.anchor.set(0.5);
    this.board.addChild(this.bTitle, this.bPoint, this.bTotal);
  }

  // ------------------------------------------------------------ projection
  private sc(y: number) {
    return 1 / (1 + K * y);
  }
  private P(p: V3) {
    const s = this.sc(p.y);
    const Y = this.yFar + ((this.yNear - this.yFar) * (s - this.sFar)) / (1 - this.sFar);
    return { x: this.cx + p.x * this.U * s, y: Y - p.z * this.U * s * 0.9, s };
  }

  layout() {
    const app = this.s.app;
    const w = app.screen.width, h = app.screen.height;
    // leave room for the DOM banner (test / forced result) under the top bar
    const top = this.s.insets.top + 34, bottom = this.s.insets.bottom;
    const boardH = Math.min(120, Math.max(84, h * 0.11));
    this.yFar = top + boardH + h * 0.09;
    this.yNear = h - bottom - Math.max(18, h * 0.03);
    const depth = this.yNear - this.yFar;
    this.U = Math.min((w * 0.44) / HD, (depth * 0.62) / HD);
    this.cx = w / 2;
    this.bg.clear().rect(0, 0, w, h).fill({ color: C.night });
    this.crowd.width = w;
    this.crowd.scale.y = this.crowd.scale.x;
    this.crowd.position.set(w / 2, top + boardH - 6);
    this.lights[0].position.set(w * 0.08, top + boardH);
    this.lights[1].position.set(w * 0.92, top + boardH);
    for (const l of this.lights) l.width = l.height = Math.min(w, h) * 0.7;
    this.drawCourt();
    // scoreboard (top)
    const bw = Math.min(w - 24, 560);
    this.boardBg.clear()
      .roundRect(-bw / 2, 0, bw, boardH, 16).fill({ color: C.navy, alpha: 0.96 }).stroke({ color: C.gold, width: 2.5 })
      .roundRect(-bw / 2 + 6, 6, bw - 12, boardH - 12, 12).stroke({ color: C.ivory, width: 1, alpha: 0.25 });
    this.board.position.set(w / 2, top + 4);
    const k = boardH / 110;
    this.bTitle.scale.set(k);
    if (this.bTitle.width > bw - 30) this.bTitle.scale.set((k * (bw - 30)) / this.bTitle.width);
    this.bTitle.position.set(0, boardH * 0.27);
    this.bPoint.scale.set(k);
    this.bPoint.position.set(-bw / 4, boardH * 0.68);
    this.bTotal.scale.set(k);
    this.bTotal.position.set(bw / 4, boardH * 0.68);
    this.flash.clear().rect(0, 0, w, h).fill({ color: 0xfff1c8 });
    this.flash.alpha = 0;
    this.placeRackets();
    this.drawBall();
  }

  private poly(g: Graphics, pts: V3[], fill: number, alpha = 1) {
    const q = pts.map((p) => this.P(p));
    g.poly(q.flatMap((p) => [p.x, p.y])).fill({ color: fill, alpha });
  }
  private line(g: Graphics, a: V3, b: V3, width: number, color = C.ivory, alpha = 0.95) {
    const p = this.P(a), q = this.P(b);
    g.moveTo(p.x, p.y).lineTo(q.x, q.y).stroke({ color, width: width * ((p.s + q.s) / 2), alpha });
  }

  private drawCourt() {
    const g = this.surface.clear();
    const z = 0;
    this.poly(g, [{ x: -9, y: -6, z }, { x: 9, y: -6, z }, { x: 9, y: LEN + 6, z }, { x: -9, y: LEN + 6, z }], C.surround);
    this.poly(g, [{ x: -HD, y: 0, z }, { x: HD, y: 0, z }, { x: HD, y: LEN, z }, { x: -HD, y: LEN, z }], this.level === 'final' ? 0x123f52 : C.court);
    const lw = Math.max(1.6, this.U * 0.05);
    for (const x of [-HD, HD, -HS, HS]) this.line(g, { x, y: 0, z }, { x, y: LEN, z }, lw);
    for (const y of [0, LEN]) this.line(g, { x: -HD, y, z }, { x: HD, y, z }, lw * 1.4);
    for (const y of [NET - SVC, NET + SVC]) this.line(g, { x: -HS, y, z }, { x: HS, y, z }, lw);
    this.line(g, { x: 0, y: NET - SVC, z }, { x: 0, y: NET + SVC, z }, lw);
    for (const y of [0, LEN]) this.line(g, { x: 0, y, z }, { x: 0, y: y === 0 ? 0.3 : LEN - 0.3, z }, lw);
    // net: mesh band + white tape + posts
    const n = this.netG.clear();
    this.poly(n, [{ x: -6.4, y: NET, z: 0 }, { x: 6.4, y: NET, z: 0 }, { x: 6.4, y: NET, z: 1.07 }, { x: 0, y: NET, z: 0.914 }, { x: -6.4, y: NET, z: 1.07 }], 0x05101a, 0.62);
    this.line(n, { x: -6.4, y: NET, z: 1.07 }, { x: 0, y: NET, z: 0.914 }, lw * 1.6, C.ivory, 1);
    this.line(n, { x: 0, y: NET, z: 0.914 }, { x: 6.4, y: NET, z: 1.07 }, lw * 1.6, C.ivory, 1);
    for (const x of [-6.4, 6.4]) this.line(n, { x, y: NET, z: 0 }, { x, y: NET, z: 1.07 }, lw * 2, C.champagne, 1);
  }

  private drawBall() {
    const p = this.P(this.ballPos);
    const g = this.P({ ...this.ballPos, z: 0 });
    const r = Math.max(4, 0.16 * this.U * p.s);
    this.ball.clear();
    if (this.golden) this.ball.circle(0, 0, r * 2.2).fill({ color: 0xf2cf6b, alpha: 0.22 });
    this.ball.circle(0, 0, r).fill({ color: this.golden ? 0xf2c14e : C.tennis }).stroke({ color: this.golden ? 0xfff4d6 : 0x9fb52a, width: Math.max(1, r * 0.18) });
    this.ball.position.set(p.x, p.y);
    const h = Math.min(1, this.ballPos.z / 4);
    this.shadow.clear().ellipse(0, 0, r * (1.3 - 0.4 * h), r * 0.45 * (1.3 - 0.4 * h)).fill({ color: 0x000000, alpha: 0.38 * (1 - 0.6 * h) });
    this.shadow.position.set(g.x, g.y);
  }

  // positions of the two players' rackets (grip near the hitting point)
  private near: V3 = { x: 1.2, y: -0.8, z: 1 };
  private far: V3 = { x: -1.5, y: LEN + 0.8, z: 1 };
  /** soft player shadows on the court where each player stands (no character art in the prototype) */
  private drawPlayers() {
    this.feet.clear();
    for (const p of [this.near, this.far]) {
      const q = this.P({ ...p, z: 0 });
      this.feet.ellipse(q.x, q.y, 0.75 * this.U * q.s, 0.24 * this.U * q.s).fill({ color: 0x000000, alpha: 0.32 });
    }
  }
  private placeRackets() {
    this.drawPlayers();
    for (const [r, p, flip] of [[this.rNear, this.near, 1], [this.rFar, this.far, -1]] as const) {
      const q = this.P({ ...p, z: 0.9 });
      r.position.set(q.x, q.y);
      const size = Math.max(44, 1.7 * this.U * q.s);
      r.width = r.height = size;
      r.scale.x = Math.abs(r.scale.x) * flip;
    }
  }

  // ------------------------------------------------------------ motion primitives
  private fly(to: V3, ms: number, apex: number, opts: { trail?: boolean; easing?: (u: number) => number } = {}) {
    const from = { ...this.ballPos };
    const e = opts.easing ?? ((u: number) => u);
    const tr = opts.trail ?? true;
    let last = this.P(from);
    return this.s.tw.tween(ms, (u) => {
      const k = e(u);
      this.ballPos = { x: from.x + (to.x - from.x) * k, y: from.y + (to.y - from.y) * k, z: from.z + (to.z - from.z) * k + 4 * apex * k * (1 - k) };
      this.drawBall();
      if (tr) {
        const p = this.P(this.ballPos);
        this.trail.moveTo(last.x, last.y).lineTo(p.x, p.y).stroke({ color: this.golden ? 0xf2cf6b : 0xf4e9d4, width: Math.max(1.5, 3 * p.s), alpha: 0.35 });
        last = p;
      }
    });
  }
  private bounceAt(p: V3, strong = false) {
    this.qa.bounces++;
    audio.play('bounce', { volume: strong ? 0.7 : 0.45 });
    const q = this.P({ ...p, z: 0 });
    const ring = new Graphics().ellipse(0, 0, 14 * q.s * (this.U / 30), 5 * q.s * (this.U / 30)).stroke({ color: this.golden ? 0xf2cf6b : C.ivory, width: 2 });
    ring.position.set(q.x, q.y);
    this.root.addChildAt(ring, this.root.getChildIndex(this.shadow));
    void this.s.tw.tween(strong ? 420 : 300, (u) => {
      ring.scale.set(1 + (strong ? 2.2 : 1.4) * u);
      ring.alpha = 1 - u;
    }).then(() => ring.destroy());
  }
  /** racket stroke at the ball: wind-up then fast swing (both players) */
  private async swing(who: 'near' | 'far', at: V3, power = 1, overhead = false, quick = false) {
    this.qa.strokes++;
    this.trail.clear(); // only the current shot leaves a trace
    this.drawPlayers();
    const r = who === 'near' ? this.rNear : this.rFar;
    const p = this.P({ ...at, z: overhead ? at.z : Math.max(0.6, at.z) });
    const dir = who === 'near' ? 1 : -1;
    r.position.set(p.x - dir * 6 * p.s, p.y + (overhead ? 0 : 6 * p.s));
    const size = Math.max(44, (overhead ? 2.1 : 1.7) * this.U * p.s);
    r.width = r.height = size;
    if (who === 'far') r.scale.x = -Math.abs(r.scale.x);
    r.alpha = 1;
    const r0 = overhead ? -2.6 : -0.9 * dir, r1 = overhead ? 0.1 : 0.8 * dir;
    if (quick) r.rotation = r0;
    else await this.s.tw.tween(overhead ? 85 : 70, (u) => (r.rotation = r0 * ease.outCubic(u)));
    await this.s.tw.tween(overhead ? 80 : 70, (u) => (r.rotation = r0 + (r1 - r0) * ease.inCubic(u)));
    audio.play('racket', { volume: Math.min(1, 0.55 + 0.3 * power), rate: overhead ? 0.85 : 1 + (power - 1) * 0.1 });
    void this.s.tw.tween(220, (u) => (r.rotation = r1 + 0.4 * dir * u));
  }

  private async show(text: string, amount: number | null, tone: 'neutral' | 'good' | 'great' | 'bad', hold = 650) {
    this.qa.lastCaption = text;
    if (amount !== null && !this.resultClock) this.resultClock = this.s.animClock; // the point's action ends here
    this.caption.removeChildren().forEach((c) => c.destroy());
    const w = this.s.app.screen.width, h = this.s.app.screen.height;
    const size = tone === 'great' ? 64 : 52;
    const t = tone === 'bad' ? this.s.plainText(text, size * 0.62, '#F4E9D4', '800') : this.s.goldText(text, size);
    const maxW = w * 0.86;
    if (t.width > maxW) t.scale.set(maxW / t.width);
    this.caption.addChild(t);
    if (amount !== null) {
      const a = new Text({ text: amount > 0 ? `+ ${money(amount, this.s.currency, this.s.lang)}` : money(0, this.s.currency, this.s.lang), style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 40, fill: amount > 0 ? '#FFF4D6' : '#9FB0BF' } });
      a.anchor.set(0.5);
      a.y = size * 0.95;
      this.caption.addChild(a);
    }
    this.caption.position.set(w / 2, (this.yFar + this.yNear) / 2 - 10);
    const k = Math.min(1, w / 520);
    this.caption.scale.set(k * 0.9);
    this.caption.alpha = 0;
    await this.s.tw.tween(150, (u) => {
      this.caption.alpha = u;
      this.caption.scale.set(k * (0.9 + 0.1 * ease.outBack(u)));
    });
    await this.s.tw.wait(hold);
    await this.s.tw.tween(130, (u) => (this.caption.alpha = 1 - u));
  }

  private flashLights(strength: number, ms: number) {
    if (this.s.prefs.reducedMotion) return Promise.resolve();
    return this.s.tw.tween(ms, (u) => {
      this.flash.alpha = strength * Math.sin(u * Math.PI);
      for (const l of this.lights) l.alpha = 0.35 + strength * 1.2 * Math.sin(u * Math.PI);
    });
  }

  // ------------------------------------------------------------ public API
  enter(level: 'tiebreak' | 'final', points: number) {
    this.level = level;
    this.root.visible = true;
    this.root.alpha = 0;
    this.s.world.visible = false;
    this.s.aceLayer.visible = false; // the mascot never covers the court
    this.layout();
    this.setBoard(0, points, 0);
    return this.s.tw.tween(260, (u) => (this.root.alpha = u));
  }
  async leave() {
    await this.s.tw.tween(220, (u) => (this.root.alpha = 1 - u));
    this.reset();
  }
  /** immediate cleanup (new round, error): the reels come back */
  reset() {
    this.root.visible = false;
    this.root.alpha = 1;
    this.caption.removeChildren().forEach((c) => c.destroy());
    this.trail.clear();
    this.flash.alpha = 0;
    this.s.world.visible = true;
    this.s.aceLayer.visible = true;
  }
  setBoard(point: number, total: number, amount: number, single = false) {
    this.bTitle.text = single ? 'TEST · 1 POINT' : this.level === 'final' ? 'THE GRAND FINAL' : 'TIE-BREAK DUEL';
    this.bPoint.text = fmt(this.s.t.duelPointOf, { n: Math.max(point, 1), t: total });
    this.bTotal.text = money(amount, this.s.currency, this.s.lang);
  }

  /** Plays one point exactly as described by its event. */
  async playPoint(e: PointEv, total: number, prizeAmount: number, bonusAmount: number, single: boolean) {
    const t0 = performance.now();
    const c0 = this.s.animClock;
    this.resultClock = 0;
    let frames = 0;
    const count = () => frames++;
    this.s.app.ticker.add(count);
    try {
      await this.playPointInner(e, total, prizeAmount, bonusAmount, single);
    } finally {
      this.s.app.ticker.remove(count);
      const end = this.s.animClock;
      this.qa.durations.push({ outcome: e.outcome, ms: Math.round(performance.now() - t0), animMs: Math.round(end - c0), actionMs: Math.round((this.resultClock || end) - c0), frames });
    }
  }

  private async playPointInner(e: PointEv, total: number, prizeAmount: number, bonusAmount: number, single: boolean) {
    this.qa.points++;
    this.trail.clear();
    this.golden = false;
    this.setBoard(e.point, total, bonusAmount - prizeAmount, single);
    const deuce = e.side === 'deuce';
    // server stands on the near baseline, right of centre for deuce, left for ad
    const sx = deuce ? 1.1 : -1.1;
    this.near = { x: sx, y: -0.6, z: 1 };
    // receiver diagonally opposite
    this.far = { x: deuce ? -3.0 : 3.0, y: LEN + 0.8, z: 1 };
    this.placeRackets();
    if (e.goldenMatchPoint) {
      this.golden = true;
      audio.play('match_point', { volume: 0.8 });
      void this.flashLights(0.18, 700);
      await this.show('GOLDEN MATCH POINT', null, 'great', 500);
    }
    // service box target (diagonal box on the far side)
    const boxSign = deuce ? -1 : 1; // x side of the target box
    const tx = e.target === 'T' ? boxSign * 0.35 : e.target === 'wide' ? boxSign * (HS - 0.35) : boxSign * 2.1;
    const tIn: V3 = { x: tx, y: NET + SVC - 0.9, z: 0 };
    const serve = async (kind: 'in' | 'net' | 'long' | 'ace', second: boolean) => {
      this.qa.serves++;
      this.ballPos = { x: sx + 0.2, y: -0.4, z: 1.1 };
      this.drawBall();
      audio.play('serve', { volume: 0.5 });
      // toss
      await this.fly({ x: sx + 0.25, y: -0.3, z: 2.9 }, second ? 110 : 160, 0, { trail: false, easing: ease.outCubic });
      await this.swing('near', this.ballPos, kind === 'ace' ? 1.4 : second ? 0.8 : 1.1, true);
      const fast = kind === 'ace' ? 230 : second ? 260 : 240;
      if (kind === 'net') {
        await this.fly({ x: tx * 0.5, y: NET - 0.05, z: 0.55 }, fast * 0.6, 0.3);
        await this.fly({ x: tx * 0.5, y: NET - 0.4, z: 0 }, 90, 0.1);
        this.bounceAt(this.ballPos);
        return;
      }
      const land = kind === 'long' ? { x: tx * 1.05, y: NET + SVC + 1.0, z: 0 } : tIn;
      await this.fly(land, fast, second ? 1.1 : 0.4, { easing: (u) => u });
      this.bounceAt(land, kind === 'ace');
    };
    let lost = false;
    // ---- first serve
    if (e.firstServe === 'ACE') {
      await serve('ace', false);
      // receiver lunges too late, ball flies to the back fence
      void this.swing('far', { x: this.far.x * 0.6, y: LEN, z: 0.8 }, 0.6);
      await this.fly({ x: tx * 1.4, y: LEN + 4.5, z: 0.6 }, 240, 0.5);
      this.s.cheer(0.9);
      await this.show(this.s.t.duelAce, prizeAmount, 'good');
      return;
    }
    if (e.firstServe === 'FAULT') {
      await serve(e.point % 2 === 0 ? 'net' : 'long', false);
      void this.show(this.s.t.duelFault, null, 'bad', 160);
      if (e.secondServe === 'DOUBLE_FAULT') {
        await serve(e.point % 2 === 0 ? 'long' : 'net', true);
        await this.show(this.s.t.duelDoubleFault, 0, 'bad', 420);
        return;
      }
      if (e.secondServe === 'ACE') {
        await serve('ace', true);
        await this.fly({ x: tx * 1.4, y: LEN + 4.5, z: 0.6 }, 260, 0.5);
        this.s.cheer(0.9);
        await this.show(this.s.t.duelAce, prizeAmount, 'good');
        return;
      }
      await serve('in', true);
    } else await serve('in', false);
    // ---- rally: strokes alternate, starting with the return; the last stroke
    // is ours for WINNER / GOLDEN, the opponent's for LOST (winner past us) and
    // RALLY_WON (opponent error into the net).
    const usLast = e.outcome === 'WINNER' || e.outcome === 'GOLDEN';
    // two or three strokes after the serve (brief): stroke 1 is the return (opponent);
    // an even count ends with our shot, an odd count with the opponent's
    let strokes = Math.min(3, Math.max(1, e.shots));
    if ((strokes % 2 === 0) !== usLast) strokes = strokes === 3 ? 2 : strokes + 1;
    const lane = (i: number) => (((i * 7 + e.point * 3 + (e.finish === 'line' ? 1 : 0)) % 5) - 2) * 1.35; // deterministic placement
    for (let i = 1; i <= strokes; i++) {
      const byUs = i % 2 === 0;
      const last = i === strokes;
      const hitter = byUs ? 'near' : 'far';
      // hitter meets the ball
      const at = { ...this.ballPos, z: 0.9 };
      if (byUs) this.near = { x: at.x, y: Math.min(at.y, -0.3), z: 1 };
      else this.far = { x: at.x, y: Math.max(at.y, LEN + 0.3), z: 1 };
      const overhead = last && e.outcome === 'GOLDEN' && this.level === 'final';
      if (overhead) {
        // lob from the opponent, then the GOLDEN SMASH
        this.golden = true;
        await this.s.tw.wait(120); // very brief slow-down
        await this.swing('near', { ...this.ballPos, z: 2.6 }, 1.6, true);
        const land: V3 = { x: (e.finish === 'cross' ? -1 : 1) * (HS - 1.2), y: NET + 3.4, z: 0 };
        await this.fly(land, 190, 0.2, { easing: ease.inCubic });
        this.bounceAt(land, true);
        audio.play('wind', { volume: 0.4 });
        void this.flashLights(0.32, 520);
        if (!this.s.prefs.reducedMotion) void this.shake(260, 8);
        this.s.cheer(1.5);
        await this.fly({ x: land.x * 1.6, y: LEN + 5, z: 3.5 }, 260, 1.2);
        await this.show(this.s.t.duelGoldenSmash, prizeAmount, 'great', 900);
        return;
      }
      await this.swing(hitter, at, last ? 1.3 : 0.9, false, true);
      if (last && e.outcome === 'RALLY_WON') {
        // opponent's error: into the net
        await this.fly({ x: at.x * 0.6, y: NET + 0.05, z: 0.4 }, 300, 0.6);
        await this.fly({ x: at.x * 0.6, y: NET + 0.4, z: 0 }, 140, 0.05);
        this.bounceAt(this.ballPos);
        await this.show(this.s.t.duelPointWon, prizeAmount, 'neutral', 520);
        return;
      }
      const targetY = byUs ? LEN - 2.2 - (i % 3) * 1.4 : 2.0 + (i % 3) * 1.6;
      let tx2 = lane(i);
      if (last) tx2 = (byUs ? (e.finish === 'line' ? 1 : -1) : e.finish === 'cross' ? -1 : 1) * (HS - 0.7) * (e.finish === 'inside-out' ? -1 : 1);
      if (last && e.outcome === 'GOLDEN') this.golden = true;
      const land: V3 = { x: tx2, y: targetY, z: 0 };
      await this.fly(land, last ? 220 : 225, last ? 0.9 : 1.6);
      this.bounceAt(land, last);
      if (last) {
        // the other player cannot reach it: ball runs on past the baseline
        void this.swing(byUs ? 'far' : 'near', { x: land.x * 0.7, y: byUs ? LEN : 0, z: 0.7 }, 0.5);
        await this.fly({ x: land.x * 1.25, y: byUs ? LEN + 4 : -4, z: 0.5 }, 190, 0.5);
        lost = !byUs;
        break;
      }
      // continue to the next hitter
      const nextY = byUs ? LEN + 0.6 : -0.6;
      await this.fly({ x: land.x * 0.8 + lane(i + 1) * 0.2, y: nextY, z: 0.9 }, 130, 0.8);
    }
    if (lost) {
      await this.show(this.s.t.duelPointLost, 0, 'bad', 520);
      return;
    }
    if (e.outcome === 'GOLDEN') {
      void this.flashLights(0.22, 500);
      this.s.cheer(1.3);
      await this.show(this.s.t.duelGoldenWinner, prizeAmount, 'great', 800);
      return;
    }
    this.s.cheer(0.8);
    await this.show(this.s.t.duelWinner, prizeAmount, e.goldenMatchPoint ? 'great' : 'good');
  }

  private shake(ms: number, amp: number) {
    const x0 = this.root.x, y0 = this.root.y;
    return this.s.tw.tween(ms, (u) => this.root.position.set(x0 + Math.sin(u * 50) * amp * (1 - u), y0 + Math.cos(u * 41) * amp * 0.6 * (1 - u))).then(() => this.root.position.set(x0, y0));
  }

  /** end of the bonus: total on the scoreboard (proportionate) */
  async summary(bonusAmount: number, debit: number) {
    const x = bonusAmount / Math.max(1, debit);
    this.setBoard(0, 0, bonusAmount);
    this.bPoint.text = this.s.t.duelFinal;
    const tone = x >= 50 ? 'great' : x >= 10 ? 'good' : 'neutral';
    if (x >= 50) {
      this.s.cheer(1.4);
      audio.play('win_3', { volume: 0.8 });
      void this.flashLights(0.2, 700);
    }
    await this.show(this.level === 'final' ? 'THE GRAND FINAL' : 'TIE-BREAK DUEL', bonusAmount, tone, x >= 50 ? 1400 : 900);
  }
}
