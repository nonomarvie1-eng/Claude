// THE FINAL SET — match director.
// Turns the bonus events of a book into broadcast-style animations.  It never
// decides anything: every zone, shot, Hawk-Eye call, mark and amount it shows
// is read from the event it receives (MOTEUR -> RÉSULTAT -> ÉVÉNEMENT ->
// CINÉMATIQUE -> AFFICHAGE DU GAIN).  All long sequences can be skipped with a
// tap (they only get faster: the result is already fixed).
import { ColorMatrixFilter, Container, Graphics, Sprite, Text } from 'pixi.js';
import { audio } from '../audio/audio';
import { RULES } from '../engine/rules';
import type { BookEvent, ShotType } from '../engine/types';
import { money } from '../game/format';
import { fmt } from '../i18n/strings';
import { ease } from './tween';
import { CELL, FRAME_H, FRAME_M, FRAME_W, type RallyScene } from './scene';

type Ev<T extends BookEvent['type']> = Extract<BookEvent, { type: T }>;
type P = { x: number; y: number };

const BLUE = 0x2f8cff;
const ELECTRIC = 0x37b6ff;
const GOLD = 0xd5a64b;
const CREAM = 0xf2e5c3;
const TENNIS = 0xd4e948;
const NIGHT = 0x081b23;
const RED = 0xff5a5f;

const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

/** zone rectangle in board coordinates */
export function zoneRect(z: number) {
  const c = z % 3;
  const deep = z < 3;
  return { x: FRAME_M + c * 2 * CELL, y: FRAME_M + (deep ? 0 : 3 * CELL), w: 2 * CELL, h: (deep ? 3 : 2) * CELL };
}
const zoneCenter = (z: number): P => {
  const r = zoneRect(z);
  return { x: r.x + r.w / 2, y: r.y + r.h / 2 };
};

export class Match {
  court = new Container();
  private lines = new Graphics();
  private zoneFx = new Graphics();
  private chips: Text[] = [];
  private markBadges: Container[] = [];
  private ballLayer = new Container();
  private ball = new Sprite();
  private shadow = new Graphics();
  private trail = new Graphics();
  private hitFrames = new Graphics();
  private labels = new Container();
  private level: 'rally' | 'final' = 'rally';
  private marks = [0, 0, 0, 0, 0, 0];
  private pendingHawk: Ev<'hawkEye'> | null = null;
  private desat = new ColorMatrixFilter();
  /** tap during a sequence: everything runs 5x faster (never changes the result) */
  skip = false;
  /** last ball landing (board coords), used by the camera */
  private lastLanding: P = { x: FRAME_W / 2, y: FRAME_H / 2 };

  constructor(private s: RallyScene) {
    this.court.visible = false;
    this.court.addChild(this.zoneFx, this.lines, this.hitFrames, this.labels, this.ballLayer);
    for (let z = 0; z < 6; z++) {
      const chip = new Text({ text: '', style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 36, fill: '#F2E5C3', stroke: { color: '#081B23', width: 8, join: 'round' } } });
      chip.anchor.set(0, 0);
      this.chips.push(chip);
      this.court.addChild(chip);
      const badge = new Container();
      badge.visible = false;
      this.markBadges.push(badge);
      this.court.addChild(badge);
    }
    this.ball.anchor.set(0.5);
    this.ballLayer.addChild(this.trail, this.shadow, this.ball);
    this.ballLayer.visible = false;
    this.desat.desaturate();
  }

  get rm() {
    return this.s.prefs.reducedMotion;
  }

  /** time factor: turbo / skip shorten, reduced motion shortens and removes camera moves */
  private d(ms: number) {
    return ms * (this.rm ? 0.5 : 1);
  }

  // ------------------------------------------------------------ court
  private colour() {
    return this.level === 'final' ? GOLD : ELECTRIC;
  }

  private drawLines() {
    const g = this.lines.clear();
    const col = this.colour();
    // zone borders (court lines) and the net along the bottom edge
    for (let z = 0; z < 6; z++) {
      const r = zoneRect(z);
      // alternate tints so the six zones read at a glance, even on a phone
      g.rect(r.x, r.y, r.w, r.h).fill({ color: z % 2 ? 0xffffff : col, alpha: 0.05 });
      g.rect(r.x + 4, r.y + 4, r.w - 8, r.h - 8).stroke({ color: col, width: 6, alpha: 0.8 });
    }
    g.moveTo(FRAME_M, FRAME_M + 3 * CELL).lineTo(FRAME_W - FRAME_M, FRAME_M + 3 * CELL).stroke({ color: CREAM, width: 6, alpha: 0.85 }); // service line
    g.moveTo(FRAME_W / 2, FRAME_M + 3 * CELL).lineTo(FRAME_W / 2, FRAME_H - FRAME_M).stroke({ color: CREAM, width: 4, alpha: 0.5 }); // centre line
    g.rect(FRAME_M, FRAME_H - FRAME_M - 10, FRAME_W - 2 * FRAME_M, 10).fill({ color: CREAM, alpha: 0.9 }); // net tape
    this.ball.texture = this.s.tex.sym_L1;
    this.ball.width = this.ball.height = 64;
  }

  enter(level: 'rally' | 'final') {
    this.level = level;
    this.marks = [0, 0, 0, 0, 0, 0];
    this.drawLines();
    this.renderMarks();
    this.court.visible = true;
    this.court.alpha = 0;
    void this.s.tw.tween(this.d(500), (u) => (this.court.alpha = u));
  }

  leave() {
    this.court.visible = false;
    this.clearExchange();
    for (const c of this.chips) c.text = '';
    this.marks = [0, 0, 0, 0, 0, 0];
    this.renderMarks();
  }

  /** zone values of the board just revealed (from the reveal event) */
  async showCourt(values: number[]) {
    values.forEach((v, z) => {
      const r = zoneRect(z);
      const c = this.chips[z];
      c.text = money(Math.round((this.s.bet * v) / 100), this.s.currency, this.s.lang);
      c.position.set(r.x + 14, r.y + 10);
      c.alpha = v > 0 ? 1 : 0.45;
    });
    if (!this.rm) await this.s.tw.wait(220);
  }

  private renderMarks() {
    this.marks.forEach((m, z) => {
      const b = this.markBadges[z];
      b.removeChildren().forEach((c) => c.destroy());
      b.visible = m > 0;
      if (!m) return;
      const r = zoneRect(z);
      const g = new Graphics()
        .roundRect(r.x + 8, r.y + 8, r.w - 16, r.h - 16, 18).stroke({ color: GOLD, width: 5, alpha: 0.95 })
        .circle(r.x + r.w - 34, r.y + 34, 22).fill({ color: GOLD }).stroke({ color: NIGHT, width: 3 });
      const t = new Text({ text: String(m), style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 26, fill: '#081B23' } });
      t.anchor.set(0.5);
      t.position.set(r.x + r.w - 34, r.y + 34);
      b.addChild(g, t);
    });
  }

  private clearExchange() {
    this.zoneFx.clear();
    this.hitFrames.clear();
    this.trail.clear();
    this.labels.removeChildren().forEach((c) => c.destroy());
    this.ballLayer.visible = false;
  }

  // ------------------------------------------------------------ camera (world transform)
  private async camera(target: P | null, k: number, ms: number) {
    if (this.rm) return;
    const w = this.s.world;
    const gp = target ? this.s.board.toGlobal(target) : { x: w.pivot.x, y: w.pivot.y };
    const from = { s: w.scale.x, px: w.pivot.x, py: w.pivot.y };
    const to = target ? { s: k, px: gp.x, py: gp.y } : { s: 1, px: from.px, py: from.py };
    if (from.s === 1 && target) {
      w.pivot.set(gp.x, gp.y);
      w.position.set(gp.x, gp.y);
      from.px = gp.x;
      from.py = gp.y;
    }
    await this.s.tw.tween(ms, (u) => {
      const sc = from.s + (to.s - from.s) * u;
      w.scale.set(sc);
    }, ease.inOutCubic);
    if (!target) {
      w.pivot.set(0, 0);
      w.position.set(0, 0);
      w.scale.set(1);
    }
  }

  private shake(px: number, ms: number) {
    if (this.rm) return;
    const w = this.s.world;
    const x0 = w.position.x, y0 = w.position.y;
    void this.s.tw.tween(ms, (u) => {
      const a = (1 - u) * px;
      w.position.set(x0 + (Math.random() - 0.5) * a, y0 + (Math.random() - 0.5) * a);
    }).then(() => w.position.set(x0, y0));
  }

  // ------------------------------------------------------------ ball flight
  /** ball from `a` to `b` (board coords) with a height profile; shadow on the ground */
  private async fly(a: P, b: P, ms: number, peak: number, opts: { spin?: number; trail?: number; scaleFrom?: number } = {}) {
    this.ballLayer.visible = true;
    const sc0 = opts.scaleFrom ?? 1;
    const tr = this.trail;
    const pts: P[] = [];
    await this.s.tw.tween(ms, (u) => {
      const x = a.x + (b.x - a.x) * u;
      const gy = a.y + (b.y - a.y) * u;
      const h = Math.sin(Math.PI * u) * peak + (opts.scaleFrom ? (1 - u) * peak * 0.6 : 0);
      this.ball.position.set(x, gy - h);
      this.ball.rotation += opts.spin ?? 0.2;
      const k = sc0 + (1 - sc0) * u;
      this.ball.scale.set((64 / this.ball.texture.width) * k * (1 + h / 900));
      this.shadow.clear().ellipse(x, gy + 26, 26 / (1 + h / 300), 9 / (1 + h / 300)).fill({ color: 0x000000, alpha: 0.35 });
      if (opts.trail) {
        pts.push({ x, y: gy - h });
        if (pts.length > opts.trail) pts.shift();
        tr.clear();
        pts.forEach((p, i) => tr.circle(p.x, p.y, 4 + i * 0.6).fill({ color: this.colour(), alpha: (i / pts.length) * 0.5 }));
      }
    }, (u) => u);
    this.lastLanding = b;
  }

  private impact(z: number, colour: number, strength = 1) {
    const c = zoneCenter(z);
    const r = zoneRect(z);
    audio.play('bounce', { volume: 0.5 + 0.3 * strength });
    this.zoneFx.rect(r.x + 4, r.y + 4, r.w - 8, r.h - 8).fill({ color: colour, alpha: 0.18 });
    const ring = new Graphics();
    this.labels.addChild(ring);
    void this.s.tw.tween(this.d(420), (u) => {
      ring.clear().circle(c.x, c.y, 20 + u * 140 * strength).stroke({ color: colour, width: 6 * (1 - u), alpha: 1 - u });
    }).then(() => ring.destroy());
  }

  private hitCells(cells: { reel: number; row: number }[], colour: number) {
    for (const p of cells) {
      const x = FRAME_M + p.reel * CELL + 6, y = FRAME_M + p.row * CELL + 6;
      this.hitFrames.roundRect(x, y, CELL - 12, CELL - 12, 20).stroke({ color: NIGHT, width: 8, alpha: 0.7 });
      this.hitFrames.roundRect(x, y, CELL - 12, CELL - 12, 20).stroke({ color: colour, width: 4 });
    }
  }

  private label(text: string, at: P, colour = '#F2E5C3', size = 40) {
    const t = new Text({ text, style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: size, fill: colour, stroke: { color: '#081B23', width: 8, join: 'round' }, align: 'center' } });
    t.anchor.set(0.5);
    t.position.set(at.x, at.y);
    this.labels.addChild(t);
    if (!this.rm) void this.s.tw.tween(this.d(500), (u) => t.scale.set(0.6 + 0.4 * ease.outBack(u)));
    return t;
  }

  private broadcastBanner(title: string, sub: string, colour: number, ms: number) {
    // lower-third style caption (screen space, above the HUD)
    const sw = this.s.app.screen.width, sh = this.s.app.screen.height;
    const c = new Container();
    const w = Math.min(sw - 24, 620), h = 74;
    const g = new Graphics().roundRect(0, 0, w, h, 12).fill({ color: NIGHT, alpha: 0.92 }).stroke({ color: colour, width: 3 })
      .rect(0, 0, 10, h).fill({ color: colour });
    const t1 = new Text({ text: title, style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 26, fill: '#F2E5C3', letterSpacing: 2 } });
    t1.position.set(24, 8);
    const t2 = new Text({ text: sub, style: { fontFamily: 'Inter', fontWeight: '700', fontSize: 16, fill: '#9fdcff' } });
    t2.position.set(24, 44);
    if (t1.width > w - 34) t1.scale.set((w - 34) / t1.width);
    if (t2.width > w - 34) t2.scale.set((w - 34) / t2.width);
    c.addChild(g, t1, t2);
    const y = this.s.insets.top + 8; // top of the screen: never over the grid's win plate or the HUD
    c.position.set(-w, y);
    this.s.aceLayer.addChild(c);
    const x1 = (sw - w) / 2;
    void this.s.tw.tween(this.d(260), (u) => (c.x = -w + (x1 + w) * ease.outCubic(u)))
      .then(() => this.s.tw.wait(ms))
      .then(() => this.s.tw.tween(this.d(220), (u) => (c.alpha = 1 - u)))
      .then(() => c.destroy({ children: true }));
  }

  // ------------------------------------------------------------ events
  async exchangeStart(e: Ev<'exchangeStart'>) {
    this.skip = false;
    this.clearExchange();
    this.marks = [...e.marks];
    this.renderMarks();
    if (e.championshipPoint) await this.championshipPoint();
  }

  /** CHAMPIONSHIP POINT: crowd falls silent, slow push-in on the court */
  private async championshipPoint() {
    audio.stopLoop('ambience');
    audio.play('match_point', { volume: 0.8 });
    const t = this.s.t;
    const c = this.s.makeOverlay();
    const inner = c.children[1] as Container;
    (c.children[0] as Graphics).alpha = 0.55;
    const title = this.s.goldText(t.cpTitle, 84);
    this.s.fit(title, 680);
    const sub = this.s.plainText(t.cpSub, 26);
    sub.y = 90;
    inner.addChild(title, sub);
    c.relayout?.();
    const push = this.camera({ x: FRAME_W / 2, y: FRAME_H / 2 }, 1.06, this.d(1800));
    await this.s.fadeOverlay(c, this.d(300), this.d(300), () => this.s.waitTapOr(this.rm ? 900 : 1700));
    await push;
  }

  hawkEye(e: Ev<'hawkEye'>) {
    this.pendingHawk = e; // played inside the shot, at the moment the ball lands
  }

  /** HAWK-EYE: freeze, ground-level reconstruction, slow ball, verdict computed by the engine */
  private async hawkEyeSequence(e: Ev<'hawkEye'>) {
    const t = this.s.t;
    audio.stopLoop('ambience');
    this.s.world.filters = [this.desat];
    const c = this.s.makeOverlay();
    const inner = c.children[1] as Container;
    const title = this.s.plainText('HAWK-EYE', 44, '#F2E5C3', '800');
    title.y = -300;
    const zone = this.s.plainText(fmt(t.hawkZone, { z: t.zoneNames[e.zone] }), 22, '#9fdcff', '700');
    zone.y = -252;
    // perspective court: ground plane, the line, the ball track
    const g = new Graphics();
    g.poly([-420, 220, 420, 220, 220, -160, -220, -160]).fill({ color: 0x0f4a3d }).stroke({ color: CREAM, width: 2, alpha: 0.5 });
    g.poly([-30, 220, 30, 220, 14, -160, -14, -160]).fill({ color: CREAM }); // the line
    const track = new Graphics();
    const ball = new Sprite(this.s.tex.sym_L1);
    ball.anchor.set(0.5);
    const mark = new Graphics();
    const verdict = this.s.plainText('', 120, '#D4E948', '800');
    verdict.y = 300;
    inner.addChild(g, track, mark, ball, title, zone, verdict);
    c.relayout?.();
    const isIn = e.call === 'in';
    // the contact point is chosen from the engine verdict: touching the line (IN) or just outside (OUT)
    const end = { x: isIn ? 34 : 64, y: 40 };
    const start = { x: -360, y: -140 };
    audio.play('pop', { volume: 0.4 });
    await this.s.fadeOverlay(c, this.d(260), this.d(280), async () => {
      await this.s.tw.tween(this.d(1900), (u) => {
        const x = start.x + (end.x - start.x) * u;
        const y = start.y + (end.y - start.y) * u - Math.sin(Math.PI * u) * 90;
        ball.position.set(x, y);
        ball.width = ball.height = 30 + 40 * u;
        track.circle(x, y, 3).fill({ color: 0xffffff, alpha: 0.6 });
      }, ease.outCubic);
      audio.play('bounce', { volume: 0.7 });
      mark.ellipse(end.x, end.y + 16, 30, 10).fill({ color: isIn ? TENNIS : RED, alpha: 0.85 });
      await this.s.tw.wait(this.d(500));
      verdict.text = isIn ? 'IN' : 'OUT';
      verdict.style.fill = isIn ? '#D4E948' : '#FF5A5F';
      audio.play(isIn ? 'mult_up' : 'line_tick', { volume: 0.8 });
      this.s.cheer(isIn ? 1 : 0.3);
      await this.s.waitTapOr(this.rm ? 700 : 1200);
    });
    this.s.world.filters = [];
    audio.startLoop('ambience', 0.5);
  }

  async shot(e: Ev<'shot'>) {
    const t = this.s.t;
    const name = e.shot as ShotType;
    const colour = this.colour();
    const origin: P = { x: FRAME_W / 2, y: FRAME_H + 140 };
    const hawk = this.pendingHawk;
    this.pendingHawk = null;
    this.broadcastBanner(t.shotNames[name], t.shotDesc[name], colour, this.d(name === 'GOLDEN' ? 2600 : 1300));
    audio.play(name === 'ACE' || name === 'SMASH' ? 'serve' : 'racket', { volume: 0.7 });
    const path = e.path;
    // 1) the ball travels exactly to the zones chosen by the engine
    if (name === 'ACE') {
      await this.camera(zoneCenter(path[0]), 1.08, this.d(250));
      await this.fly(origin, zoneCenter(path[0]), this.d(380), 40, { trail: 14, spin: 0.6 });
    } else if (name === 'SMASH') {
      await this.camera({ x: FRAME_W / 2, y: FRAME_H / 2 }, 0.94, this.d(300));
      await this.fly({ x: zoneCenter(path[0]).x, y: -260 }, zoneCenter(path[0]), this.d(520), 0, { trail: 10, scaleFrom: 2.6, spin: 0.5 });
      this.shake(18, this.d(380));
    } else if (name === 'PASSING') {
      let from = origin;
      for (const z of path) {
        const to = zoneCenter(z);
        const follow = this.camera(to, 1.05, this.d(300));
        await this.fly(from, to, this.d(330), 30, { trail: 12, spin: 0.4 });
        await follow;
        from = to;
      }
    } else if (name === 'DROP') {
      await this.fly(origin, zoneCenter(path[0]), this.d(950), 260, { spin: 0.1 });
    } else if (name === 'GOLDEN') {
      let from = origin;
      for (let i = 0; i < path.length; i++) {
        const to = zoneCenter(path[i]);
        await this.fly(from, to, this.d(300), 120, { trail: 8 });
        const z = path[i];
        this.impact(z, GOLD, 0.8);
        const cnt = this.label(`${i + 1}/${path.length}`, { x: to.x, y: to.y - 70 }, '#F2D58A', 30);
        void this.s.tw.wait(this.d(500)).then(() => cnt.destroy());
        from = { x: FRAME_W / 2 + (i % 2 ? 1 : -1) * FRAME_W * 0.3, y: FRAME_H + 120 };
      }
    } else {
      await this.fly(origin, zoneCenter(path[0]), this.d(520), 140, { spin: 0.3 });
    }
    // 2) Hawk-Eye at the landing (verdict from the engine)
    if (hawk) await this.hawkEyeSequence(hawk);
    if (e.hawkEye === 'out') {
      this.label(t.outReplay, zoneCenter(path[0]), '#FF5A5F', 44);
      await this.s.tw.wait(this.d(700));
    }
    // 3) consequences: collected zones, mark prizes, prizes, new marks
    for (const h of e.hits) {
      if (name !== 'GOLDEN') this.impact(h.zone, h.markPrize > 0 ? GOLD : colour, name === 'SMASH' ? 1.4 : 1);
      this.hitCells(h.cells, h.markPrize > 0 ? GOLD : colour);
      const amt = money(Math.round((this.s.bet * (h.value + h.markPrize)) / 100), this.s.currency, this.s.lang);
      const at = zoneCenter(h.zone);
      this.label(`+${amt}`, at, h.markPrize > 0 ? '#F2D58A' : '#F2E5C3', 40);
      if (h.markPrize > 0) this.label(t.markHit, { x: at.x, y: at.y + 50 }, '#F2D58A', 26);
      if (h.extraExchanges > 0) this.label(fmt(t.extraN, { n: h.extraExchanges }), { x: at.x, y: at.y - 56 }, '#9fdcff', 26);
      if (this.marks[h.zone] > 0) this.marks[h.zone] = 0; // mark consumed (book: markPrize)
      if (name === 'SMASH' || name === 'PASSING') await this.s.tw.wait(this.d(140));
    }
    if (e.prize > 0 && !e.grandSlam) {
      const p = money(Math.round((this.s.bet * e.prize) / 100), this.s.currency, this.s.lang);
      this.label(`${name === 'ACE' ? 'ACE' : 'HAWK-EYE'} +${p}`, { x: FRAME_W / 2, y: FRAME_M + 60 }, '#F2D58A', 36);
    }
    for (const m of e.marksSet) this.marks[m.zone] = Math.max(this.marks[m.zone], m.duration);
    this.renderMarks();
    const plate = money(Math.round((this.s.bet * e.win) / 100), this.s.currency, this.s.lang);
    this.s.setPlate(`${t.shotNames[name]} · ${plate}`);
    if (e.win > 0) this.s.cheer(Math.min(1.3, 0.4 + e.win / 1000));
    await this.camera(null, 1, this.d(260));
    await this.s.tw.wait(this.d(name === 'GOLDEN' || name === 'SMASH' ? 900 : 650));
  }

  async grandSlam(e: Ev<'grandSlam'>) {
    const t = this.s.t;
    audio.play('bonus_trigger', { volume: 0.9 });
    this.s.cheer(1.5);
    for (let z = 0; z < 6; z++) this.impact(z, GOLD, 1.2);
    const c = this.s.makeOverlay();
    const inner = c.children[1] as Container;
    (c.children[0] as Graphics).alpha = 0.5;
    const title = this.s.goldText('GRAND SLAM', 110);
    this.s.fit(title, 680);
    const sub = this.s.plainText(t.slamSub, 26);
    sub.y = 92;
    const amt = this.s.goldText('+' + money(Math.round((this.s.bet * e.prize) / 100), this.s.currency, this.s.lang), 72);
    amt.y = 180;
    inner.addChild(title, sub, amt);
    c.relayout?.();
    await this.s.fadeOverlay(c, this.d(300), this.d(300), () => this.s.waitTapOr(this.rm ? 900 : 1800));
    this.marks = [0, 0, 0, 0, 0, 0];
    this.renderMarks();
  }

  async marksExpire(e: Ev<'markExpire'>) {
    for (const z of e.zones) this.marks[z] = 0;
    this.renderMarks();
  }

  async extraExchange(e: Ev<'extraExchange'>) {
    const t = this.s.t;
    this.broadcastBanner(e.reason === 'replay' ? t.replayPoint : fmt(t.extraN, { n: e.added }), fmt(t.exchangesTotal, { n: e.total }), TENNIS, this.d(900));
    await this.s.tw.wait(this.d(250));
  }

  async exchangeEnd(e: Ev<'exchangeEnd'>) {
    this.marks = [...e.marks]; // authoritative state from the book
    this.renderMarks();
  }

  // ------------------------------------------------------------ intros
  async intro(e: Ev<'bonusStart'>) {
    this.level = e.bonus;
    if (e.bonus === 'final') await this.introFinal(e);
    else await this.introRally(e);
    this.enter(e.bonus);
  }

  /** RALLY CHALLENGE: fast electric-blue broadcast opener (5 s, skippable) */
  private async introRally(e: Ev<'bonusStart'>) {
    const t = this.s.t;
    audio.play('rally', { volume: 0.8 });
    const c = this.s.makeOverlay();
    const inner = c.children[1] as Container;
    const bar = new Graphics().rect(-560, -70, 1120, 140).fill({ color: BLUE, alpha: 0.9 }).rect(-560, -70, 1120, 6).fill({ color: CREAM });
    bar.y = -120;
    const title = this.s.plainText('RALLY CHALLENGE', 76, '#FFFFFF', '800');
    title.y = -120;
    this.s.fit(title, 1000);
    const n = this.s.goldText(String(e.exchanges), 140);
    n.y = 70;
    const lbl = this.s.plainText(t.exchangesLabel, 32, '#9fdcff', '800');
    lbl.y = 160;
    const sub = this.s.plainText(t.rallyIntroSub, 22);
    sub.y = 250;
    const tap = this.s.plainText(t.tapToContinue, 20, '#D4E948', '700');
    tap.y = 350;
    inner.addChild(bar, title, n, lbl, sub, tap);
    c.relayout?.();
    void this.s.aceSay(t.aceRally, 1200, !this.rm);
    await this.s.fadeOverlay(c, this.d(300), this.d(300), async () => {
      if (!this.rm) await this.s.tw.tween(500, (u) => (bar.scale.x = ease.outBack(u)));
      await this.s.waitTapOr(this.rm ? 1500 : 3600);
    });
  }

  /** THE GRAND FINAL: aerial stadium shot, floodlights switch on, the crowd, the scoreboard (≈7 s, skippable) */
  private async introFinal(e: Ev<'bonusStart'>) {
    const t = this.s.t;
    const s = this.s;
    const bg = s.bg;
    const world = s.world;
    const bs0 = { x: bg.scale.x, px: bg.position.x, py: bg.position.y };
    const skip = { now: false };
    s.onOverlayTap = () => (skip.now = true);
    world.alpha = 1;
    // 1) aerial: the whole stadium, lights off
    if (!this.rm) {
      void s.tw.tween(400, (u) => (world.alpha = 1 - u));
      s.flags.alpha = 0;
      const sw = s.app.screen.width, sh = s.app.screen.height;
      const zoomOut = 0.72;
      bg.scale.set(bs0.x * zoomOut);
      bg.position.set(sw / 2 - (sw / 2 - bs0.px) * zoomOut, sh / 2 - (sh / 2 - bs0.py) * zoomOut);
      audio.play('pop', { volume: 0.3 });
      // 2) floodlights switch on one after the other
      for (let i = 0; i < 3 && !skip.now; i++) {
        await s.tw.wait(380);
        audio.play('reel_stop', { volume: 0.6, rate: 0.7 });
        s.flags.alpha = (i + 1) / 3;
      }
      s.cheer(1.3);
      audio.play('win_3', { volume: 0.5 });
      // 3) the camera descends towards the court
      if (!skip.now) await s.tw.tween(1500, (u) => {
        const k = zoomOut + (1 - zoomOut) * ease.inOutCubic(u);
        bg.scale.set(bs0.x * k);
        bg.position.set(sw / 2 - (sw / 2 - bs0.px) * k, sh / 2 - (sh / 2 - bs0.py) * k);
      });
    }
    bg.scale.set(bs0.x);
    bg.position.set(bs0.px, bs0.py);
    s.onOverlayTap = null;
    // 4) the scoreboard
    const c = s.makeOverlay();
    const inner = c.children[1] as Container;
    (c.children[0] as Graphics).alpha = 0.45;
    const board = new Graphics().roundRect(-470, -250, 940, 360, 24).fill({ color: NIGHT, alpha: 0.95 }).stroke({ color: GOLD, width: 4 })
      .roundRect(-450, -230, 900, 320, 16).stroke({ color: CREAM, width: 1, alpha: 0.3 });
    const k1 = new Text({ text: 'GOLDEN RALLY', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 34, fill: '#D5A64B', letterSpacing: 10 } });
    k1.anchor.set(0.5);
    k1.y = -190;
    const title = s.goldText('THE GRAND FINAL', 82);
    title.y = -110;
    s.fit(title, 860);
    const ex = s.plainText(fmt(t.finalIntroLine, { n: e.exchanges }), 30, '#F2E5C3', '700');
    ex.y = -20;
    const sub = s.plainText(t.finalIntroSub, 22);
    sub.y = 50;
    const tap = s.plainText(t.tapToContinue, 20, '#D4E948', '700');
    tap.y = 170;
    inner.addChild(board, k1, title, ex, sub, tap);
    c.relayout?.();
    world.alpha = 1;
    void s.aceSay(t.aceFinal, 1400, false);
    await s.fadeOverlay(c, this.d(400), this.d(350), () => s.waitTapOr(this.rm ? 1500 : 3400));
    s.flags.alpha = 1;
  }

  // ------------------------------------------------------------ end of match
  async outro(e: Ev<'bonusEnd'>, amount: number, bonusWin: number) {
    const t = this.s.t;
    const s = this.s;
    this.leave();
    const c = s.makeOverlay();
    const inner = c.children[1] as Container;
    const fin = e.bonus === 'final';
    const card = new Graphics().roundRect(-360, -310, 720, 620, 28).fill({ color: fin ? 0x0b1f4a : NIGHT, alpha: 0.96 }).stroke({ color: fin ? GOLD : ELECTRIC, width: 3 });
    const kicker = new Text({ text: fin ? 'THE GRAND FINAL' : 'RALLY CHALLENGE', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 28, fill: fin ? '#D5A64B' : '#9fdcff', letterSpacing: 6 } });
    kicker.anchor.set(0.5);
    kicker.y = -260;
    const title = s.goldText(t.matchOver, 52);
    title.y = -195;
    s.fit(title, 620);
    const l1 = s.plainText(fmt(t.recapExchanges, { n: e.exchanges }), 28);
    l1.y = -110;
    const l2 = s.plainText(fmt(t.recapPoints, { n: e.points }), 28);
    l2.y = -64;
    const sub = s.plainText(t.totalWin.toUpperCase(), 26, '#D5A64B', '800');
    sub.y = 10;
    const amt = s.goldText(money(0, s.currency, s.lang), 92);
    amt.y = 100;
    const tap = s.plainText(t.tapToContinue, 20, '#D4E948', '700');
    tap.y = 240;
    inner.addChild(card, kicker, title, l1, l2, sub, amt, tap);
    c.relayout?.();
    const skip = { now: false };
    audio.play('bonus_end', { volume: 0.8 });
    await s.fadeOverlay(c, this.d(350), this.d(300), async () => {
      s.onOverlayTap = () => (skip.now = true);
      await s.countUp(amt, amount, this.rm ? 600 : 1500, skip);
      await s.waitTapOr(this.rm ? 1200 : 2000);
    });
    void bonusWin;
    if (e.ceremony !== 'none') await this.ceremony(e.ceremony, amount);
  }

  /** CEREMONY: only above the published thresholds (CEREMONY_X); bigger for 'grand' */
  private async ceremony(level: 'trophy' | 'grand', amount: number) {
    const t = this.s.t;
    const s = this.s;
    const grand = level === 'grand';
    const c = s.makeOverlay();
    const inner = c.children[1] as Container;
    const rays = new Sprite(s.tex.glow);
    rays.anchor.set(0.5);
    rays.blendMode = 'add';
    rays.tint = GOLD;
    rays.width = rays.height = grand ? 980 : 720;
    rays.alpha = 0.6;
    rays.y = -120;
    const trophy = new Sprite(s.tex.sym_H2);
    trophy.anchor.set(0.5);
    trophy.width = trophy.height = grand ? 360 : 280;
    trophy.y = -120;
    const title = s.goldText(grand ? t.ceremonyGrand : t.ceremonyTrophy, grand ? 76 : 60);
    title.y = 110;
    s.fit(title, 680);
    const amt = s.goldText(money(amount, s.currency, s.lang), grand ? 88 : 70);
    amt.y = 215;
    inner.addChild(rays, trophy, title, amt);
    c.relayout?.();
    audio.play('win_3', { volume: 0.9 });
    s.cheer(1.5);
    let raining = true;
    const confetti = async () => {
      const cols = [GOLD, CREAM, TENNIS, ELECTRIC, 0xff3fb4];
      while (raining && !this.rm) {
        const g = new Graphics().rect(-6, -3, 12, 6).fill({ color: cols[Math.floor(Math.random() * cols.length)] });
        g.position.set(Math.random() * s.app.screen.width, -10);
        g.rotation = Math.random() * 3;
        s.overlay.addChild(g);
        const vx = (Math.random() - 0.5) * 80, vy = 180 + Math.random() * 160;
        void s.tw.tween(2600, (u) => {
          g.x += vx * 0.016;
          g.y += vy * 0.016;
          g.rotation += 0.1;
          g.alpha = 1 - u;
        }).then(() => g.destroy());
        await s.tw.wait(grand ? 25 : 45);
      }
    };
    void confetti();
    void s.aceSay(grand ? t.aceGrand : t.aceTrophy, 1600, false);
    await s.fadeOverlay(c, this.d(400), this.d(400), async () => {
      if (!this.rm) await s.tw.tween(700, (u) => (trophy.scale.set((trophy.texture.width ? (grand ? 360 : 280) / trophy.texture.width : 1) * ease.outBack(u))));
      await s.waitTapOr(this.rm ? 1200 : grand ? 4200 : 2600);
    });
    raining = false;
  }
}

export const clampN = clamp;
