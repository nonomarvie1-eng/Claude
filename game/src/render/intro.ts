// GOLDEN RALLY — loading + entry scene (PixiJS, own canvas).
// Separate from the gameplay scene: created first with the three loading
// assets only (stadium, loading bar, tennis ball), it shows the REAL loading
// progress of the game, then hands over to the reels and is destroyed.
// It never touches results, the RGS or the gameplay logic.
import { Application, BlurFilter, Container, FillGradient, Graphics, Sprite, Text, type Texture } from 'pixi.js';
import { audio } from '../audio/audio';
import { ease, Tweener } from './tween';
import { AceCinematic, type CinematicResult, type ServeClip } from './aceCinematic';

export interface Rect { x: number; y: number; w: number; h: number }

/** Usable track of `loading_bar` (inner ivory channel, between the two end caps),
 *  in fractions of the image, measured on the provided PNG (see docs). */
export const TRACK = { x0: 0.0773, x1: 0.924, y0: 0.468, y1: 0.558 };
/** Outer tube (gold rails included), fractions of the image height. */
const TUBE = { y0: 0.4448, y1: 0.587 };
/** The ball fills 89 % of its image (measured): sprite size = visible diameter / 0.89. */
const BALL_FILL = 0.89;
/** Layout (portrait reference): logo area reserved at the top centre, bar below it. */
const LOGO_AREA = { y0: 0.075, y1: 0.235 };
const BAR_CY = 0.29; // bar centre, fraction of the viewport height
const BAR_W = 0.53; // bar width, fraction of the (portrait-equivalent) viewport width
const BALL_D = 2.3; // visible ball diameter in tube heights

const C = { night: 0x071826, navy: 0x0b2440, gold: 0xe7c877, champagne: 0xd6b36a, ivory: 0xf4e9d4 };

export class IntroScene {
  app = new Application();
  tw!: Tweener;
  private root = new Container();
  private stadium = new Sprite();
  private backdrop = new Sprite(); // wide screens: the same stadium, blurred and darkened, fills the sides
  private barLayer = new Container();
  private bar = new Sprite();
  private fill = new Graphics();
  private sweep = new Graphics();
  private trackMask = new Graphics();
  private ballShadow = new Graphics();
  private ball = new Sprite();
  private veil = new Graphics(); // only behind the first-visit card
  private card = new Container();
  private progress = 0;
  private shown = 0; // displayed progress: eased towards the real value, never ahead of it
  private track = { x0: 0, x1: 0, y: 0, h: 0 };
  private ballR = 10;
  private lastBallX = 0;
  private bounce = 0; // vertical offset of the completion bounce
  private completing = false;
  reducedMotion = false;
  /** QA */
  qa = { maxShown: 0, completed: false, bounced: false, swept: false, transitionMs: 0, transitionAnimMs: 0, fps: 0, ballAtEnd: false, ballOffTrack: false };
  private clock = 0;
  private ro: ResizeObserver | null = null;
  private destroyed = false;
  private tick = (tk: { deltaMS: number }) => {
    this.clock += tk.deltaMS;
    this.update(tk.deltaMS);
  };

  constructor(private tex: Record<string, Texture>, private strings: { preparing: string; ready: string; subtitle: string }) {}

  async init(host: HTMLElement) {
    await this.app.init({ resizeTo: host, antialias: true, backgroundColor: C.night, resolution: Math.min(window.devicePixelRatio || 1, 2), autoDensity: true });
    host.appendChild(this.app.canvas);
    this.app.canvas.setAttribute('aria-hidden', 'true');
    this.tw = new Tweener(this.app.ticker, () => 1);
    this.stadium.texture = this.tex.loading_stadium;
    this.stadium.anchor.set(0.5);
    this.backdrop.texture = this.tex.loading_stadium;
    this.backdrop.anchor.set(0.5);
    this.backdrop.filters = [new BlurFilter({ strength: 18, quality: 3 })];
    this.backdrop.tint = 0x8a93a8;
    this.backdrop.alpha = 0.55;
    this.bar.texture = this.tex.loading_bar;
    this.bar.anchor.set(0.5);
    this.ball.texture = this.tex.loading_ball;
    this.ball.anchor.set(0.5);
    this.fill.mask = this.trackMask;
    this.sweep.mask = this.trackMask;
    this.sweep.blendMode = 'add';
    this.sweep.visible = false;
    this.barLayer.addChild(this.bar, this.fill, this.sweep, this.trackMask, this.ballShadow, this.ball);
    this.veil.alpha = 0;
    this.root.addChild(this.backdrop, this.stadium, this.veil, this.barLayer, this.card);
    this.app.stage.addChild(this.root);
    this.app.ticker.add(this.tick);
    this.ro = new ResizeObserver(() => this.layout());
    this.ro.observe(host);
    this.layout();
  }

  /** kept for compatibility: the loading scene needs no other texture */
  addTextures(t: Record<string, Texture>) {
    this.tex = { ...t, ...this.tex };
  }

  /** real loading progress in [0, 1] (monotonic) */
  setProgress(p: number) {
    this.progress = Math.max(this.progress, Math.min(1, p));
  }

  /** the reserved logo area (for a future logo), CSS px */
  logoArea(): Rect {
    const w = this.app.screen.width, h = this.app.screen.height;
    return { x: w * 0.15, y: h * LOGO_AREA.y0, w: w * 0.7, h: h * (LOGO_AREA.y1 - LOGO_AREA.y0) };
  }

  private layout() {
    if (this.destroyed) return;
    const w = this.app.screen.width, h = this.app.screen.height;
    // stadium: the 9:16 composition is always kept.  Narrower than 9:16 -> cover (sides
    // cropped); wider (landscape, desktop) -> full height, the sides are filled with the
    // same stadium, blurred and darkened (no stretched or cropped composition).
    const st = this.stadium.texture;
    const wide = w / h > st.width / st.height;
    const s = wide ? h / st.height : Math.max(w / st.width, h / st.height);
    this.stadium.scale.set(s);
    this.stadium.position.set(w / 2, h / 2);
    this.backdrop.visible = wide;
    if (wide) {
      const bs2 = Math.max(w / st.width, h / st.height) * 1.05;
      this.backdrop.scale.set(bs2);
      this.backdrop.position.set(w / 2, h / 2);
    }
    this.veil.clear().rect(0, 0, w, h).fill({ color: C.night });
    // bar: ~53 % of a portrait-equivalent width, centred below the logo area
    const bt = this.bar.texture;
    const bw = BAR_W * Math.min(w, h * 0.5625);
    const bs = bw / bt.width;
    this.bar.scale.set(bs);
    this.bar.position.set(w / 2, h * BAR_CY);
    const left = w / 2 - bw / 2, top = h * BAR_CY - (bt.height * bs) / 2;
    const y0 = top + TRACK.y0 * bt.height * bs, y1 = top + TRACK.y1 * bt.height * bs;
    this.track = { x0: left + TRACK.x0 * bw, x1: left + TRACK.x1 * bw, y: (y0 + y1) / 2, h: y1 - y0 };
    this.trackMask.clear().roundRect(this.track.x0, y0, this.track.x1 - this.track.x0, this.track.h, this.track.h / 2).fill(0xffffff);
    const tubeH = (TUBE.y1 - TUBE.y0) * bt.height * bs;
    this.ballR = (BALL_D * tubeH) / 2;
    this.ball.width = this.ball.height = (this.ballR * 2) / BALL_FILL;
    this.lastBallX = this.ballX();
    this.drawProgress();
    this.layoutCard();
  }

  /** ball centre for the displayed progress: always inside the usable track */
  private ballX() {
    return this.track.x0 + (this.track.x1 - this.track.x0) * this.shown;
  }

  private fillGrad: FillGradient | null = null;
  private drawProgress() {
    const t = this.track;
    const len = (t.x1 - t.x0) * this.shown;
    const g = this.fill.clear();
    if (len > 0.5) {
      if (!this.fillGrad) {
        this.fillGrad = new FillGradient({ type: 'linear', start: { x: 0, y: 0 }, end: { x: 0, y: 1 }, textureSpace: 'local',
          colorStops: [{ offset: 0, color: '#F4E2AE' }, { offset: 0.45, color: '#DDBA6E' }, { offset: 1, color: '#B98A3A' }] });
      }
      g.roundRect(t.x0, t.y - t.h / 2, Math.max(len, t.h), t.h, t.h / 2).fill({ fill: this.fillGrad, alpha: 0.88 });
    }
    const x = this.ballX();
    // very subtle rolling: rotation follows the distance travelled (no extra spin)
    if (!this.reducedMotion) this.ball.rotation += (x - this.lastBallX) / Math.max(1, this.ballR);
    this.lastBallX = x;
    this.ball.position.set(x, t.y - this.bounce);
    const k = 1 - Math.min(1, this.bounce / (this.ballR * 2));
    this.ballShadow.clear().ellipse(x, t.y + this.ballR * 0.78, this.ballR * 0.78 * (0.6 + 0.4 * k), this.ballR * 0.16 * (0.6 + 0.4 * k)).fill({ color: 0x000000, alpha: 0.28 * k });
    if (x < t.x0 - 0.5 || x > t.x1 + 0.5) this.qa.ballOffTrack = true;
  }

  private update(dt: number) {
    if (this.destroyed) return;
    // smooth interpolation towards the real progress (never shows more than what is loaded)
    if (this.shown < this.progress) {
      const step = this.reducedMotion ? 1 : 1 - Math.exp(-dt / 140);
      this.shown = Math.min(this.progress, this.shown + Math.max(0.0006 * dt, (this.progress - this.shown) * step));
      if (this.progress - this.shown < 0.0005) this.shown = this.progress;
    }
    this.qa.maxShown = Math.max(this.qa.maxShown, this.shown);
    this.drawProgress();
  }

  ready() {
    /* the completion sequence is played by complete() */
  }

  /**
   * Real loading reached 100 %: the ball reaches the end of the track, makes one
   * small bounce (impact sound if the sound is already unlocked), a restrained
   * highlight travels across the filled bar, then the bar and the ball fade out.
   * ~1 s; 0.2 s fade with reduced motion.
   */
  async complete() {
    if (this.completing) return;
    this.completing = true;
    this.progress = 1;
    // let the displayed progress arrive at the end (real value is already 100 %)
    while (this.shown < 1 && !this.destroyed) await this.tw.wait(16);
    this.qa.ballAtEnd = Math.abs(this.ball.x - this.track.x1) < 1;
    this.qa.completed = true;
    if (this.reducedMotion) {
      await this.tw.tween(200, (u) => (this.barLayer.alpha = 1 - u));
      return;
    }
    // one small, realistic bounce: up (decelerating) then down (accelerating), short squash on landing
    const H = this.ballR * 0.9;
    const base = this.ball.scale.x;
    await this.tw.tween(170, (u) => (this.bounce = H * ease.outCubic(u)));
    await this.tw.tween(150, (u) => (this.bounce = H * (1 - u * u)));
    this.bounce = 0;
    this.qa.bounced = true;
    audio.play('bounce', { volume: 0.55 });
    const sweepDone = this.runSweep();
    await this.tw.tween(110, (u) => {
      const q = Math.sin(u * Math.PI);
      this.ball.scale.set(base * (1 + 0.06 * q), base * (1 - 0.08 * q));
    });
    this.ball.scale.set(base);
    await sweepDone;
    await this.tw.tween(240, (u) => (this.barLayer.alpha = 1 - ease.inOutCubic(u)));
  }

  /** a restrained highlight travelling across the filled bar */
  private async runSweep() {
    const t = this.track;
    const w = (t.x1 - t.x0) * 0.16;
    const g = this.sweep;
    const grad = new FillGradient({ type: 'linear', start: { x: 0, y: 0 }, end: { x: 1, y: 0 }, textureSpace: 'local',
      colorStops: [{ offset: 0, color: 'rgba(255,248,226,0)' }, { offset: 0.5, color: 'rgba(255,248,226,0.55)' }, { offset: 1, color: 'rgba(255,248,226,0)' }] });
    g.clear().rect(0, t.y - t.h / 2, w, t.h).fill({ fill: grad });
    g.visible = true;
    await this.tw.tween(520, (u) => (g.x = t.x0 - w + (t.x1 - t.x0 + w) * ease.inOutCubic(u)));
    g.visible = false;
    this.qa.swept = true;
  }

  // ------------------------------------------------------------ first-visit feature card
  private cardBuilt = false;
  showFeatureCard(gameTex: Record<string, Texture>, s: { title: string; name: string; text1: string; text2: string; zone: string }) {
    this.cardBuilt = true;
    const c = this.card;
    c.removeChildren().forEach((x) => x.destroy({ children: true }));
    const W = 560, H = 690;
    const panel = new Graphics().roundRect(-W / 2, -H / 2, W, H, 26).fill({ color: C.navy, alpha: 0.96 }).stroke({ color: C.gold, width: 3 });
    panel.roundRect(-W / 2 + 9, -H / 2 + 9, W - 18, H - 18, 20).stroke({ color: C.ivory, width: 1, alpha: 0.22 });
    const logoTex = gameTex.ace_logo ?? gameTex.logo ?? this.tex.logo;
    const parts: Container[] = [panel];
    if (logoTex) {
      const logo = new Sprite(logoTex);
      logo.anchor.set(0.5);
      logo.scale.set(Math.min((W * 0.62) / logo.texture.width, 120 / logo.texture.height));
      logo.y = -H / 2 + 74;
      parts.push(logo);
    }
    const kick = new Text({ text: s.title, style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 19, fill: '#D6B36A', letterSpacing: 5 } });
    kick.anchor.set(0.5);
    kick.y = -H / 2 + 150;
    const name = new Text({ text: s.name, style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 36, fill: '#FFF4D6', letterSpacing: 3 } });
    name.anchor.set(0.5);
    name.y = -H / 2 + 192;
    if (name.width > W - 60) name.scale.set((W - 60) / name.width);
    // illustration: a strip of the real grid (6 reels x 3 rows), the Golden Ball serving the centre zone
    const ill = new Container();
    const cell = 76, gw = cell * 6, gh = cell * 3;
    const frame = new Graphics().roundRect(-gw / 2 - 10, -gh / 2 - 10, gw + 20, gh + 20, 14).fill({ color: 0x0e322b }).stroke({ color: C.champagne, width: 2 });
    ill.addChild(frame);
    const syms = [['H2', 'L3', 'H4', 'L1', 'W', 'L2'], ['G', 'H3', 'L5', 'H1', 'L4', 'H2'], ['L4', 'L2', 'H2', 'L3', 'H4', 'L5']];
    const zx0 = -gw / 2 + 2 * cell, zx1 = zx0 + 2 * cell;
    syms.forEach((row, r) => row.forEach((k, i) => {
      const tx = gameTex[`sym_${k}`];
      if (!tx) return;
      const sp = new Sprite(tx);
      sp.anchor.set(0.5);
      sp.width = sp.height = cell * 0.86;
      sp.position.set(-gw / 2 + cell * (i + 0.5), -gh / 2 + cell * (r + 0.5));
      if (i < 2 || i > 3) sp.alpha = k === 'G' ? 1 : 0.55;
      ill.addChild(sp);
    }));
    const zone = new Graphics().roundRect(zx0 + 3, -gh / 2 + 3, 2 * cell - 6, gh - 6, 12).stroke({ color: C.gold, width: 5 });
    const tag = new Text({ text: s.zone, style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 16, fill: '#071826', letterSpacing: 2 } });
    tag.anchor.set(0.5);
    const tagBg = new Graphics().roundRect(-tag.width / 2 - 12, -14, tag.width + 24, 28, 14).fill({ color: C.gold });
    const tagC = new Container();
    tagC.addChild(tagBg, tag);
    tagC.position.set((zx0 + zx1) / 2, -gh / 2 - 12);
    const traj = new Graphics();
    const sx = -gw / 2 + cell * 0.5, sy = 0;
    const ex = (zx0 + zx1) / 2, ey = gh * 0.1;
    for (let k = 0; k <= 16; k += 2) {
      const u = k / 16;
      traj.circle(sx + (ex - sx) * u, sy + (ey - sy) * u - Math.sin(u * Math.PI) * cell * 0.9, 3.2).fill({ color: 0xf2cf6b });
    }
    const spinMarks = new Graphics();
    for (const x of [zx0 + cell / 2, zx0 + 1.5 * cell]) {
      spinMarks.moveTo(x, gh / 2 + 18).lineTo(x - 9, gh / 2 + 30).moveTo(x, gh / 2 + 18).lineTo(x + 9, gh / 2 + 30).stroke({ color: C.gold, width: 3 });
      spinMarks.moveTo(x, gh / 2 + 18).lineTo(x, gh / 2 + 44).stroke({ color: C.gold, width: 3 });
    }
    ill.addChild(zone, traj, tagC, spinMarks);
    ill.y = -H / 2 + 370;
    const style = { fontFamily: 'Inter', fontWeight: '500' as const, fontSize: 25, fill: '#F4E9D4', wordWrap: true, wordWrapWidth: W - 50, align: 'center' as const, lineHeight: 34 };
    const t1 = new Text({ text: s.text1, style });
    t1.anchor.set(0.5, 0);
    t1.y = -H / 2 + 515;
    const t2 = new Text({ text: s.text2, style: { ...style, fontSize: 22, lineHeight: 30, fill: '#D6B36A' } });
    t2.anchor.set(0.5, 0);
    t2.y = t1.y + t1.height + 10;
    c.addChild(...parts, kick, name, ill, t1, t2);
    const used = t2.y + t2.height - -H / 2;
    if (used > H - 30) panel.clear().roundRect(-W / 2, -H / 2, W, used + 40, 26).fill({ color: C.navy, alpha: 0.96 }).stroke({ color: C.gold, width: 3 });
    (c as Container & { H?: number }).H = Math.max(H, used + 40);
    c.alpha = 0;
    this.barLayer.visible = false;
    this.layoutCard();
    if (this.reducedMotion) {
      c.alpha = 1;
      this.veil.alpha = 0.45;
    } else void this.tw.tween(260, (u) => {
      c.alpha = u;
      this.veil.alpha = 0.45 * u;
    });
  }

  shortLandscape() {
    return this.app.screen.height < 500 && this.app.screen.width > this.app.screen.height;
  }

  private layoutCard() {
    if (!this.cardBuilt) return;
    const w = this.app.screen.width, h = this.app.screen.height;
    const H = (this.card as Container & { H?: number }).H ?? 720;
    if (this.shortLandscape()) {
      const s = Math.min((h - 28) / H, (w * 0.56) / 560);
      this.card.scale.set(s);
      this.card.position.set(w * 0.36, h / 2);
      return;
    }
    const avail = h - 185; // the DOM buttons (PLAY + skip + demo notice) take the bottom ~175 px
    const s = Math.min((w * 0.96) / 560, (avail * 0.96) / H, 1.2);
    this.card.scale.set(s);
    this.card.position.set(w / 2, 12 + avail * 0.5);
  }

  /** card bottom in CSS px (the DOM buttons sit under it) */
  cardBottom() {
    if (!this.cardBuilt) return null;
    if (this.shortLandscape()) return 0; // buttons are beside the card
    const H = (this.card as Container & { H?: number }).H ?? 720;
    return this.card.y + (H / 2) * this.card.scale.x;
  }

  // ------------------------------------------------------------ transition to the reels
  private skip = false;
  skipTransition() {
    this.skip = true;
  }

  /**
   * Transition into the slot game, preserving the stadium: the card (if any) and
   * what is left of the loading layer fade, the stadium makes a very slight push
   * towards the reels while the game crossfades in (~0.5 s; 0.18 s fade with
   * reduced motion).  `target` is the real board rectangle of the game scene.
   */
  async enter(target: Rect, onReveal: () => void) {
    const t0 = performance.now();
    const c0 = this.clock;
    let frames = 0;
    const count = () => frames++;
    this.app.ticker.add(count);
    const done = () => {
      this.app.ticker.remove(count);
      this.qa.transitionMs = performance.now() - t0;
      this.qa.transitionAnimMs = this.clock - c0;
      this.qa.fps = Math.round((frames * 1000) / Math.max(1, this.qa.transitionMs));
    };
    // QA only (demo builds): __rallyTimeScale slows the presentation for frame captures
    const qa = () => (import.meta.env.VITE_ENABLE_RGS === '1' ? 1 : ((window as unknown as { __rallyTimeScale?: number }).__rallyTimeScale ?? 1));
    this.tw.speed = () => (this.skip ? 6 : 1) * qa();
    if (this.reducedMotion) {
      onReveal();
      await this.tw.tween(180, (u) => (this.root.alpha = 1 - u));
      done();
      return;
    }
    const T = 500;
    const cx = target.x + target.w / 2, cy = target.y + target.h / 2;
    const card0 = this.card.alpha, veil0 = this.veil.alpha, bar0 = this.barLayer.alpha;
    let revealed = false;
    const seg = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / (b - a)));
    await this.tw.tween(T, (u) => {
      const t = u * T;
      this.card.alpha = card0 * (1 - seg(t, 0, 120));
      this.veil.alpha = veil0 * (1 - seg(t, 0, 160));
      this.barLayer.alpha = bar0 * (1 - seg(t, 0, 120));
      const z = 1 + 0.035 * ease.outCubic(seg(t, 0, T));
      this.root.scale.set(z);
      this.root.position.set(cx * (1 - z), cy * (1 - z));
      if (t > 140 && !revealed) {
        revealed = true;
        onReveal();
      }
      this.root.alpha = 1 - ease.inOutCubic(seg(t, 160, T));
    });
    if (!revealed) onReveal();
    done();
  }

  /** the 9:16 composition rectangle: where the stadium image is shown in full height */
  compRect(): Rect {
    const w = this.app.screen.width, h = this.app.screen.height;
    const st = this.stadium.texture;
    const s = this.stadium.scale.x;
    const cw = Math.min(w, st.width * s), ch = Math.min(h, st.height * s);
    return { x: (w - cw) / 2, y: (h - ch) / 2, w: cw, h: ch };
  }

  // ------------------------------------------------------------ ACE! opening cinematic
  cinematic: AceCinematic | null = null;
  cinematicResult: CinematicResult | null = null;
  /**
   * Plays the ACE! opening on this stadium (the loading bar and the card are
   * already gone).  `onOcclude` must show the real game under the ball.
   */
  async playCinematic(opts: { clip?: ServeClip | null; video?: HTMLVideoElement | null; onOcclude: () => void }) {
    this.barLayer.visible = false;
    if (this.card.children.length) await this.tw.tween(160, (u) => {
      this.card.alpha = 1 - u;
      this.veil.alpha = 0.45 * (1 - u);
    });
    this.card.visible = false;
    this.veil.alpha = 0;
    // QA only (demo builds): __rallyTimeScale slows the presentation for frame captures
    const qa = () => (import.meta.env.VITE_ENABLE_RGS === '1' ? 1 : ((window as unknown as { __rallyTimeScale?: number }).__rallyTimeScale ?? 1));
    this.tw.speed = () => qa();
    const c0 = this.clock;
    this.cinematic = new AceCinematic({ app: this.app, tw: this.tw, root: this.root, stadium: this.stadium, comp: this.compRect(), tex: this.tex });
    if (this.cineSkipRequested) this.cinematic.skip();
    this.cinematicResult = await this.cinematic.play(opts);
    this.qa.transitionAnimMs = this.clock - c0;
    this.qa.transitionMs = this.cinematicResult.totalMs;
    return this.cinematicResult;
  }

  hasCinematicAssets() {
    return !!(this.tex.ace_logo_noball && this.tex.ace_logo_ball && this.tex.loading_ball);
  }

  private cineSkipRequested = false;
  skipCinematic() {
    this.cineSkipRequested = true; // also honoured if the opening has not started yet
    this.cinematic?.skip();
  }

  destroy() {
    this.destroyed = true;
    this.ro?.disconnect();
    this.app.ticker.remove(this.tick);
    this.app.destroy({ removeView: true }, { children: true, texture: false });
  }
}
