// GOLDEN RALLY — THE FIRST SERVE: loading + entry scene (PixiJS, own canvas).
// Separate from the gameplay scene: it is created first with the stadium
// assets only, shows the REAL loading progress of the game, and is destroyed
// once the player is on the reels.  It never touches results or the RGS.
import { Application, Container, Graphics, Sprite, Text, type Texture } from 'pixi.js';
import LAYERS from '../assets/layers.json';
import { ease, Tweener } from './tween';

export interface Rect { x: number; y: number; w: number; h: number }
const FRAME_RATIO = 1080 / 910; // reel frame (6 x 5 cells + margins), same as the game board

const C = { night: 0x071826, navy: 0x0b2440, gold: 0xe7c877, champagne: 0xd6b36a, ivory: 0xf4e9d4, court: 0x16483e };

export class IntroScene {
  app = new Application();
  tw!: Tweener;
  private root = new Container();
  private bg = new Container();
  private sky = new Sprite();
  private crowd = new Sprite();
  private fore = new Sprite();
  private flags = new Sprite();
  private dark = new Graphics();
  private lights: { glow: Sprite; cone: Graphics; on: number; x: number; y: number }[] = [];
  private board = new Container();
  private boardBg = new Graphics();
  private logo = new Sprite();
  private logoMask = new Graphics();
  private subtitle!: Text;
  private baseline = new Graphics();
  private ball = new Sprite();
  private ballShadow = new Graphics();
  private caption!: Text;
  private card = new Container();
  private progress = 0;
  private shown = 0; // displayed progress (eased towards the real value, never ahead of it)
  private boardRect: Rect = { x: 0, y: 0, w: 0, h: 0 };
  private portrait = true;
  reducedMotion = false;
  /** QA */
  qa = { lightsOn: 0, maxShown: 0, transitionMs: 0, transitionAnimMs: 0, fps: 0 };
  private clock = 0;

  constructor(private tex: Record<string, Texture>, private strings: { preparing: string; ready: string; subtitle: string }) {}

  async init(host: HTMLElement) {
    await this.app.init({ resizeTo: host, antialias: true, backgroundColor: C.night, resolution: Math.min(window.devicePixelRatio || 1, 2), autoDensity: true });
    host.appendChild(this.app.canvas);
    this.app.canvas.setAttribute('aria-hidden', 'true');
    this.tw = new Tweener(this.app.ticker, () => 1);
    this.bg.addChild(this.sky, this.crowd, this.fore, this.flags);
    this.flags.blendMode = 'add';
    for (let i = 0; i < 4; i++) {
      const glow = new Sprite(this.tex.glow);
      glow.anchor.set(0.5);
      glow.blendMode = 'add';
      glow.tint = 0xfff1d0;
      glow.alpha = 0;
      const cone = new Graphics();
      cone.blendMode = 'add';
      cone.alpha = 0;
      this.lights.push({ glow, cone, on: 0, x: 0, y: 0 });
    }
    this.logo.texture = this.tex.logo;
    this.logo.anchor.set(0.5);
    this.logo.mask = this.logoMask;
    this.subtitle = new Text({ text: this.strings.subtitle, style: { fontFamily: 'Cinzel', fontWeight: '600', fontSize: 22, fill: '#D6B36A', letterSpacing: 7 } });
    this.subtitle.anchor.set(0.5);
    this.subtitle.alpha = 0;
    this.board.addChild(this.boardBg, this.logo, this.logoMask, this.subtitle);
    this.ball.texture = this.tex.sym_G;
    this.ball.anchor.set(0.5);
    this.caption = new Text({ text: this.strings.preparing, style: { fontFamily: 'Inter', fontWeight: '700', fontSize: 13, fill: '#F4E9D4', letterSpacing: 3 } });
    this.caption.anchor.set(0.5);
    this.caption.alpha = 0.8;
    this.root.addChild(this.bg, ...this.lights.map((l) => l.cone), this.dark, ...this.lights.map((l) => l.glow), this.board, this.baseline, this.ballShadow, this.ball, this.caption, this.card);
    this.app.stage.addChild(this.root);
    this.app.ticker.add((tk) => {
      this.clock += tk.deltaMS;
      this.update(tk.deltaMS);
    });
    this.ro = new ResizeObserver(() => this.layout());
    this.ro.observe(host);
    this.layout();
  }

  /** game images decoded later (other orientation, flags) */
  addTextures(t: Record<string, Texture>) {
    this.tex = { ...t, ...this.tex };
    this.layout();
  }

  /** real loading progress in [0, 1] (monotonic) */
  setProgress(p: number) {
    this.progress = Math.max(this.progress, Math.min(1, p));
  }

  private ro: ResizeObserver | null = null;
  private destroyed = false;

  private layout() {
    if (this.destroyed) return;
    const w = this.app.screen.width, h = this.app.screen.height;
    this.portrait = h > w * 1.05;
    const key = this.portrait ? 'portrait' : 'landscape';
    const L = LAYERS[key];
    // only the current orientation is loaded first; the other one arrives with the game images
    const pick = (n: string) => this.tex[`${n}_${key}`] ?? this.tex[`${n}_${this.portrait ? 'landscape' : 'portrait'}`];
    const parts: [Sprite, string][] = [[this.sky, 'bg'], [this.crowd, 'crowd'], [this.fore, 'fore'], [this.flags, 'flags']];
    for (const [sp, n] of parts) {
      const tx = pick(n);
      sp.visible = !!tx;
      if (tx) {
        sp.texture = tx;
        sp.scale.set(L.width / tx.width);
      }
    }
    this.crowd.y = L.crowdY;
    this.fore.y = L.foreY;
    this.flags.y = L.flagsY;
    const bs = Math.max(w / L.width, h / L.height);
    this.bg.scale.set(bs);
    this.bg.position.set((w - L.width * bs) / 2, (h - L.height * bs) / 2);
    this.dark.clear().rect(0, 0, w, h).fill({ color: C.night });
    // floodlight banks (positions of the light rigs painted in the sky layer)
    const rigs = this.portrait ? [[0.1, 0.035], [0.9, 0.035], [0.3, 0.02], [0.7, 0.02]] : [[0.06, 0.06], [0.94, 0.06], [0.3, 0.03], [0.7, 0.03]];
    this.lights.forEach((l, i) => {
      l.x = this.bg.x + rigs[i][0] * L.width * bs;
      l.y = this.bg.y + rigs[i][1] * L.height * bs;
      l.glow.position.set(l.x, l.y);
      l.glow.width = l.glow.height = Math.min(w, h) * 0.55;
      const tx = w / 2 + (l.x - w / 2) * 0.25;
      l.cone.clear().poly([l.x - 14, l.y, l.x + 14, l.y, tx + w * 0.22, h * 0.95, tx - w * 0.22, h * 0.95]).fill({ color: 0xfff1d0, alpha: 0.07 });
    });
    // scoreboard: where the reels will be (6:5 frame)
    const bw = Math.min(w * (this.portrait ? 0.9 : 0.5), (h * 0.5) * FRAME_RATIO);
    const bh = bw / FRAME_RATIO;
    const by = this.portrait ? h * 0.27 : h * 0.18;
    this.boardRect = { x: (w - bw) / 2, y: by, w: bw, h: bh };
    this.drawBoard(this.boardRect, 1);
    // baseline progress: near baseline of the court
    this.drawBaseline();
    this.caption.position.set(w / 2, this.baseY() + Math.max(26, h * 0.035));
    this.caption.scale.set(Math.min(1.25, Math.max(0.9, w / 520)));
    this.ball.width = this.ball.height = Math.max(30, Math.min(52, w * 0.085));
    this.layoutCard();
  }

  private baseY() {
    return this.app.screen.height * (this.portrait ? 0.8 : 0.84);
  }
  private baseX() {
    const w = this.app.screen.width;
    const half = Math.min(w * 0.42, 420);
    return [w / 2 - half, w / 2 + half];
  }

  private drawBoard(r: Rect, logoAlpha: number) {
    const g = this.boardBg.clear();
    g.roundRect(r.x, r.y, r.w, r.h, 18).fill({ color: C.navy, alpha: 0.93 }).stroke({ color: C.gold, width: 3 });
    g.roundRect(r.x + 7, r.y + 7, r.w - 14, r.h - 14, 13).stroke({ color: C.ivory, width: 1, alpha: 0.22 });
    // scoreboard lamp rows (top and bottom)
    const n = 18;
    for (const yy of [r.y + 18, r.y + r.h - 18]) for (let i = 0; i < n; i++) {
      const x = r.x + 26 + ((r.w - 52) * i) / (n - 1);
      g.circle(x, yy, Math.max(1.5, r.w / 260)).fill({ color: C.champagne, alpha: 0.35 });
    }
    const ls = Math.min((r.w * 0.82) / this.tex.logo.width, (r.h * 0.5) / this.tex.logo.height);
    this.logo.scale.set(ls);
    this.logo.position.set(r.x + r.w / 2, r.y + r.h * 0.44);
    this.logo.alpha = logoAlpha;
    this.subtitle.position.set(r.x + r.w / 2, r.y + r.h * 0.77);
    this.subtitle.scale.set(Math.min(1, (r.w * 0.8) / (this.subtitle.width / this.subtitle.scale.x)));
  }

  private drawBaseline() {
    const [x0, x1] = this.baseX();
    const y = this.baseY();
    const k = this.shown;
    const g = this.baseline.clear();
    g.moveTo(x0, y).lineTo(x1, y).stroke({ color: C.ivory, width: 4, alpha: 0.55 });
    const xe = x0 + (x1 - x0) * k;
    if (k > 0) {
      g.moveTo(x0, y).lineTo(xe, y).stroke({ color: 0xf2cf6b, width: 6, alpha: 1 });
      g.moveTo(x0, y).lineTo(xe, y).stroke({ color: 0xf2cf6b, width: 16, alpha: 0.18 });
    }
    this.ball.position.set(xe, y - this.ball.height * 0.55);
    this.ballShadow.clear().ellipse(xe, y + 2, this.ball.width * 0.45, this.ball.width * 0.12).fill({ color: 0x000000, alpha: 0.35 });
  }

  private update(dt: number) {
    // displayed value follows the real progress quickly (never shows more than what is loaded)
    if (this.shown < this.progress) this.shown = Math.min(this.progress, this.shown + Math.max(0.0025 * dt, (this.progress - this.shown) * 0.2));
    this.qa.maxShown = Math.max(this.qa.maxShown, this.shown);
    if (!this.entering) {
      this.drawBaseline();
      this.ball.rotation += dt * 0.006;
      // the stadium wakes up: light banks switch on one by one with the progress
      this.dark.alpha = 0.82 - 0.6 * this.shown;
      this.lights.forEach((l, i) => {
        const th = [0.12, 0.35, 0.6, 0.85][i];
        if (this.shown >= th && l.on === 0) {
          l.on = 1;
          this.qa.lightsOn++;
          if (this.reducedMotion) {
            l.glow.alpha = 0.55;
            l.cone.alpha = 1;
          } else void this.tw.tween(260, (u) => {
            const f = u < 0.3 ? u / 0.3 : u < 0.45 ? 0.4 : u < 0.6 ? 1 : 0.85 + 0.15 * u; // short flicker
            l.glow.alpha = 0.55 * f;
            l.cone.alpha = f;
          });
        }
      });
      // the logo is revealed on the scoreboard as the game gets ready
      const r = this.boardRect;
      const rev = Math.max(0, Math.min(1, (this.shown - 0.1) / 0.85));
      this.logoMask.clear().rect(r.x, r.y, r.w * rev, r.h).fill(0xffffff);
      this.subtitle.alpha = Math.max(0, (this.shown - 0.85) / 0.15);
    }
  }

  ready() {
    this.caption.text = this.strings.ready;
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
    const logo = new Sprite(this.tex.logo);
    logo.anchor.set(0.5);
    logo.scale.set(Math.min((W * 0.62) / logo.texture.width, 120 / logo.texture.height));
    logo.y = -H / 2 + 74;
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
      const sp = new Sprite(gameTex[`sym_${k}`] ?? this.tex.sym_G);
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
    // trajectory: from the Golden Ball (reel 1, middle row) to the centre zone
    const traj = new Graphics();
    const sx = -gw / 2 + cell * 0.5, sy = 0;
    const ex = (zx0 + zx1) / 2, ey = gh * 0.1;
    for (let k = 0; k <= 16; k++) {
      const u = k / 16;
      const x = sx + (ex - sx) * u, y = sy + (ey - sy) * u - Math.sin(u * Math.PI) * cell * 0.9;
      if (k % 2 === 0) traj.circle(x, y, 3.2).fill({ color: 0xf2cf6b });
    }
    // respin marks on the two struck reels
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
    c.addChild(panel, logo, kick, name, ill, t1, t2);
    // fit the texts
    const used = t2.y + t2.height - (-H / 2);
    if (used > H - 30) panel.clear().roundRect(-W / 2, -H / 2, W, used + 40, 26).fill({ color: C.navy, alpha: 0.96 }).stroke({ color: C.gold, width: 3 });
    (c as Container & { H?: number }).H = Math.max(H, used + 40);
    c.alpha = 0;
    for (const o of [this.board, this.baseline, this.ball, this.ballShadow, this.caption]) o.visible = false;
    this.layoutCard();
    if (this.reducedMotion) c.alpha = 1;
    else void this.tw.tween(260, (u) => (c.alpha = u));
  }

  shortLandscape() {
    return this.app.screen.height < 500 && this.app.screen.width > this.app.screen.height;
  }

  private layoutCard() {
    if (!this.cardBuilt) return;
    const w = this.app.screen.width, h = this.app.screen.height;
    const H = (this.card as Container & { H?: number }).H ?? 720;
    if (this.shortLandscape()) {
      // short landscape (phone on its side): card on the left at full height, buttons on the right
      const s = Math.min((h - 28) / H, (w * 0.56) / 560);
      this.card.scale.set(s);
      this.card.position.set(w * 0.36, h / 2);
      return;
    }
    // leave room at the bottom for the DOM buttons
    const avail = h - 185; // the DOM buttons (PLAY + skip + demo notice) take the bottom ~175 px
    const s = Math.min((w * 0.96) / 560, (avail * 0.96) / H, 1.2);
    this.card.scale.set(s);
    this.card.position.set(w / 2, 12 + (avail * 0.5));
  }

  /** card rect in CSS px (to place the DOM buttons under it) */
  cardBottom() {
    if (!this.cardBuilt) return null;
    if (this.shortLandscape()) return 0; // buttons are beside the card, not below
    const H = (this.card as Container & { H?: number }).H ?? 720;
    return this.card.y + (H / 2) * this.card.scale.x;
  }

  // ------------------------------------------------------------ transition to the reels
  private entering = false;
  private skip = false;
  skipTransition() {
    this.skip = true;
  }

  /**
   * Ball bounces on the court, the scoreboard becomes the reel frame, slight
   * camera push.  `target` is the real board rectangle of the game scene.
   * ~0.65 s (0.18 s crossfade with reduced motion); `onReveal` is called when
   * the reels must start to show through.
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
    this.entering = true;
    this.shown = this.progress = 1;
    this.drawBaseline();
    // QA only (demo builds): __rallyTimeScale slows the presentation for frame captures
    const qa = () => (import.meta.env.VITE_ENABLE_RGS === '1' ? 1 : ((window as unknown as { __rallyTimeScale?: number }).__rallyTimeScale ?? 1));
    const speed = () => (this.skip ? 6 : 1) * qa();
    this.tw.speed = speed;
    if (this.reducedMotion) {
      this.card.visible = false;
      this.board.visible = true;
      onReveal();
      await this.tw.tween(180, (u) => (this.root.alpha = 1 - u));
      done();
      return;
    }
    // One timeline of 600 ms (overlapping phases, a single frame-synchronised tween):
    //   0-90 ms    the feature card (if any) fades out
    //   0-180 ms   the Golden Ball bounces once on the court, towards the centre
    //   100-440 ms the scoreboard becomes the reel frame + slight camera push
    //   ~290 ms    the reels start to show through (onReveal)
    //   470-600 ms the stadium of the game takes over
    const T = 600;
    const bx0 = this.ball.x, by0 = this.ball.y, w = this.app.screen.width;
    const bx1 = w / 2, by1 = this.baseY() - this.ball.height * 0.55;
    this.caption.alpha = 0;
    const from = { ...this.boardRect };
    const cxT = target.x + target.w / 2, cyT = target.y + target.h / 2;
    const card0 = this.card.alpha;
    for (const o of [this.board, this.baseline, this.ball, this.ballShadow]) o.visible = true;
    let revealed = false;
    const seg = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / (b - a)));
    await this.tw.tween(T, (u) => {
      const t = u * T;
      this.card.alpha = card0 * (1 - seg(t, 0, 90));
      const ub = seg(t, 0, 180);
      this.ball.x = bx0 + (bx1 - bx0) * ub;
      this.ball.y = by0 + (by1 - by0) * ub - Math.abs(Math.sin(ub * Math.PI)) * this.app.screen.height * 0.06;
      this.ball.rotation += 0.3;
      this.ballShadow.clear().ellipse(this.ball.x, this.baseY() + 2, this.ball.width * 0.45, this.ball.width * 0.12).fill({ color: 0x000000, alpha: 0.3 });
      const um = seg(t, 100, 440);
      const k = ease.inOutCubic(um);
      const r = { x: from.x + (target.x - from.x) * k, y: from.y + (target.y - from.y) * k, w: from.w + (target.w - from.w) * k, h: from.h + (target.h - from.h) * k };
      this.drawBoard(r, 1 - k);
      this.logoMask.clear().rect(r.x, r.y, r.w, r.h).fill(0xffffff);
      this.subtitle.alpha = 1 - k;
      const z = 1 + 0.05 * Math.sin((um * Math.PI) / 2);
      this.root.scale.set(z);
      this.root.position.set(cxT * (1 - z), cyT * (1 - z));
      this.ball.alpha = this.baseline.alpha = this.ballShadow.alpha = 1 - k;
      if (um > 0.55 && !revealed) {
        revealed = true;
        onReveal();
      }
      this.root.alpha = 1 - seg(t, 470, T);
    });
    this.card.visible = false;
    if (!revealed) onReveal();
    done();
  }

  destroy() {
    this.destroyed = true;
    this.ro?.disconnect();
    this.app.destroy({ removeView: true }, { children: true, texture: false });
  }
}
