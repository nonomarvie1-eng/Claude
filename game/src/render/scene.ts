// PixiJS presentation layer.  It only *displays* books: no outcome logic here.
import { Application, BlurFilter, Container, FillGradient, Graphics, Sprite, Text, Texture, type Ticker } from 'pixi.js';
import { audio } from '../audio/audio';
import { STRIPS } from '../engine/engine';
import { RULES } from '../engine/rules';
import type { Board, GameType, Position, SymbolName, WinLine } from '../engine/types';
import type { View, WinTier } from '../game/player';
import { money } from '../game/format';
import type { Strings } from '../i18n/strings';
import { ease, Tweener } from './tween';
import LAYERS from '../assets/layers.json';

const imgs = import.meta.glob('../assets/img/*.{png,jpg}', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;

const CELL = 170;
const NR = RULES.reels;
const NROWS = RULES.rows;
const FRAME_M = 46;
const FRAME_W = NR * CELL + 2 * FRAME_M;
const FRAME_H = NROWS * CELL + 2 * FRAME_M;
const SYM_SIZE = 164;

export interface Prefs {
  reducedMotion: boolean;
  turbo: boolean;
}

const mod = (a: number, n: number) => ((a % n) + n) % n;

export async function loadTextures(onProgress: (p: number) => void): Promise<Record<string, Texture>> {
  const entries = Object.entries(imgs);
  const out: Record<string, Texture> = {};
  let done = 0;
  await Promise.all(
    entries.map(async ([k, url]) => {
      const name = k.split('/').pop()!.replace(/\.(png|jpg)$/, '');
      const img = new Image();
      img.decoding = 'async';
      img.src = url;
      await img.decode();
      out[name] = Texture.from(img);
      done++;
      onProgress(done / entries.length);
    }),
  );
  return out;
}

class Reel {
  container = new Container();
  sprites: Sprite[] = [];
  pos = 0;
  strip: SymbolName[];
  blur = new BlurFilter({ strengthX: 0, strengthY: 0, quality: 2 });
  constructor(private tex: Record<string, Texture>, strip: SymbolName[], public index: number) {
    this.strip = strip;
    for (let j = 0; j < NROWS + 2; j++) {
      const s = new Sprite(tex['sym_L4']);
      s.anchor.set(0.5);
      s.width = s.height = SYM_SIZE;
      s.x = CELL / 2;
      this.container.addChild(s);
      this.sprites.push(s);
    }
    this.container.filters = [this.blur];
    this.blur.enabled = false;
  }
  render() {
    const n = this.strip.length;
    const base = Math.floor(this.pos);
    const f = this.pos - base;
    for (let j = -1; j <= NROWS; j++) {
      const s = this.sprites[j + 1];
      const sym = this.strip[mod(base + j, n)];
      s.texture = this.tex['sym_' + sym];
      s.y = (j - f) * CELL + CELL / 2;
    }
  }
  /** sprite showing visible row r (0..2) when at rest */
  cell(row: number): Sprite {
    return this.sprites[row + 1];
  }
}

interface Particle {
  s: Sprite;
  vx: number;
  vy: number;
  g: number;
  life: number;
  max: number;
  spin: number;
}

export class RallyScene implements View {
  app = new Application();
  tex!: Record<string, Texture>;
  tw!: Tweener;
  prefs: Prefs = { reducedMotion: false, turbo: false };
  bet = 1_000_000;
  currency = 'DEMO';
  lang = 'fr';
  t!: Strings;

  private world = new Container();
  private bg = new Container();
  private sky = new Sprite();
  private crowd = new Sprite();
  private fore = new Sprite();
  private flags = new Sprite();
  private cheerAmp = 0;
  private layerBase = { crowdY: 0 };
  private time = 0;
  private bonusTint = new Graphics();
  private gears: { s: Sprite; speed: number }[] = [];
  private logo = new Sprite();
  private board = new Container();
  private frame = new Sprite();
  private reelLayer = new Container();
  private reelMask = new Graphics();
  private reels: Reel[] = [];
  private winLayer = new Container();
  private lineGfx = new Graphics();
  private glowLayer = new Container();
  private antGfx = new Graphics();
  private winText!: Text;
  private dial = new Container();
  private dialGear = new Sprite();
  private dialHand = new Sprite();
  private dialMult!: Text;
  private fx = new Container();
  private overlay = new Container();
  private particles: Particle[] = [];
  private dust: Particle[] = [];
  private mode: GameType = 'basegame';
  private gearBoost = 0;
  private swayT = 0;
  private portrait = false;
  private currentLadderIndex = 0;
  onOverlayTap: (() => void) | null = null;

  async init(host: HTMLElement, tex: Record<string, Texture>, t: Strings) {
    this.tex = tex;
    this.t = t;
    await this.app.init({
      resizeTo: host,
      antialias: true,
      backgroundColor: 0x3f9fe0,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true,
      powerPreference: 'high-performance',
    });
    host.appendChild(this.app.canvas);
    this.app.canvas.setAttribute('aria-hidden', 'true');
    this.tw = new Tweener(this.app.ticker, () => (this.prefs.turbo ? 1.8 : 1));

    this.bg.addChild(this.sky, this.crowd, this.fore, this.flags);
    this.app.stage.addChild(this.bg, this.bonusTint, this.world);
    // decorative tennis balls and racket (behind the board)
    const g1 = new Sprite(tex.deco_1);
    const g2 = new Sprite(tex.deco_2);
    const g3 = new Sprite(tex.deco_3);
    for (const [s, sp, a, sc] of [[g1, 0.05, 1, 0.55], [g2, 0, 1, 0.5], [g3, -0.09, 1, 0.55]] as const) {
      s.anchor.set(0.5);
      s.scale.set(sc);
      s.alpha = a;
      this.world.addChild(s);
      this.gears.push({ s, speed: sp });
    }
    this.logo.texture = tex.logo;
    this.logo.anchor.set(0.5);
    this.world.addChild(this.logo);

    // board
    this.frame.texture = tex.frame;
    this.frame.width = FRAME_W;
    this.frame.height = FRAME_H;
    this.board.addChild(this.frame);
    this.reelLayer.x = FRAME_M;
    this.reelLayer.y = FRAME_M;
    this.reelMask.rect(0, 0, NR * CELL, NROWS * CELL).fill(0xffffff);
    this.reelLayer.addChild(this.reelMask);
    this.reelLayer.mask = this.reelMask;
    for (let r = 0; r < NR; r++) {
      const reel = new Reel(tex, STRIPS.base[r], r);
      reel.container.x = r * CELL;
      reel.pos = 0;
      reel.render();
      this.reelLayer.addChild(reel.container);
      this.reels.push(reel);
    }
    this.board.addChild(this.antGfx, this.reelLayer);
    this.winLayer.x = FRAME_M;
    this.winLayer.y = FRAME_M;
    this.winLayer.addChild(this.glowLayer, this.lineGfx);
    this.board.addChild(this.winLayer);
    this.winText = new Text({ text: '', style: { fontFamily: 'Luckiest Guy', fontSize: 44, fill: '#ffd23f', stroke: { color: '#1b1410', width: 8 }, align: 'center', dropShadow: { color: '#000', blur: 8, distance: 0, alpha: 0.8 } } });
    this.winText.anchor.set(0.5);
    this.winText.x = FRAME_W / 2;
    this.winText.y = FRAME_H - 10;
    this.board.addChild(this.winText);
    this.world.addChild(this.board);

    // rally dial
    this.dialGear.texture = tex.deco_3;
    this.dialGear.anchor.set(0.5);
    this.dialGear.scale.set(0.5);
    this.dialGear.position.set(-110, -100);
    const dialFace = new Sprite(tex.dial);
    dialFace.anchor.set(0.5);
    dialFace.width = dialFace.height = 300;
    this.dialHand.texture = tex.dial_hand;
    this.dialHand.anchor.set(0.5, 124 / 150);
    this.dialHand.scale.set(0.5);
    this.dialMult = new Text({ text: '×1', style: { fontFamily: 'Luckiest Guy', fontSize: 64, fill: this.goldFill(64), stroke: { color: '#1b1410', width: 10 } } });
    this.dialMult.anchor.set(0.5);
    this.dialMult.y = 10;
    this.dial.addChild(this.dialGear, dialFace, this.dialHand, this.dialMult);
    this.setHand(0);
    this.dial.alpha = 0.8;
    this.world.addChild(this.dial);

    this.world.addChild(this.fx);
    this.app.stage.addChild(this.overlay);
    this.overlay.eventMode = 'static';
    this.overlay.on('pointertap', () => this.onOverlayTap?.());

    this.spawnDust();
    this.app.ticker.add((tk) => this.update(tk));
    window.addEventListener('resize', () => this.layout());
    new ResizeObserver(() => this.layout()).observe(host);
    this.layout();
  }

  private goldFill(_size: number) {
    return new FillGradient({
      type: 'linear',
      start: { x: 0, y: 0 },
      end: { x: 0, y: 1 },
      colorStops: [
        { offset: 0, color: '#fff6c9' },
        { offset: 0.45, color: '#f2c94c' },
        { offset: 0.55, color: '#b8842a' },
        { offset: 1, color: '#f7dc8a' },
      ],
      textureSpace: 'local',
    });
  }

  layout() {
    const w = this.app.screen.width;
    const h = this.app.screen.height;
    this.portrait = h > w * 1.05;
    const DW = this.portrait ? 1080 : 1920;
    const DH = this.portrait ? 1920 : 1080;
    // background: cover
    const key = this.portrait ? 'portrait' : 'landscape';
    const L = LAYERS[key];
    this.sky.texture = this.tex[`bg_${key}`];
    this.crowd.texture = this.tex[`crowd_${key}`];
    this.fore.texture = this.tex[`fore_${key}`];
    this.flags.texture = this.tex[`flags_${key}`];
    // textures may be rendered at a different pixel scale than the design units
    for (const sp of [this.sky, this.crowd, this.fore, this.flags]) sp.scale.set(L.width / sp.texture.width);
    this.crowd.y = L.crowdY;
    this.fore.y = L.foreY;
    this.flags.y = L.flagsY;
    this.layerBase = { crowdY: L.crowdY };
    const bs = Math.max(w / L.width, h / L.height);
    this.bg.scale.set(bs);
    this.bg.position.set((w - L.width * bs) / 2, (h - L.height * bs) / 2);
    this.bonusTint.clear().rect(0, 0, w, h).fill({ color: 0xff8a1e, alpha: 1 });
    this.bonusTint.blendMode = 'add';
    this.bonusTint.alpha = this.mode === 'freegame' ? 0.16 : 0;
    // world: contain the design area (bottom HUD band is reserved)
    const s = Math.min(w / DW, h / DH);
    this.world.scale.set(s);
    this.world.position.set((w - DW * s) / 2, (h - DH * s) / 2);
    if (!this.portrait) {
      this.logo.position.set(960, 92);
      this.logo.scale.set(0.3);
      const bs2 = 800 / FRAME_H;
      this.board.scale.set(bs2);
      this.board.position.set(960 - (FRAME_W * bs2) / 2, 168);
      this.dial.position.set(1690, 470);
      this.dial.scale.set(0.95);
      this.gears[0].s.position.set(170, 830);
      this.gears[1].s.position.set(250, 470);
      this.gears[2].s.position.set(1660, 820);
      this.gears[1].s.scale.set(0.55);
    } else {
      this.logo.position.set(540, 228);
      this.logo.scale.set(0.34);
      const bsc = 1050 / FRAME_W;
      this.board.scale.set(bsc);
      this.board.position.set(15, 318);
      this.dial.position.set(540, 1338);
      this.dial.scale.set(0.6);
      this.gears[0].s.position.set(110, 1370);
      this.gears[1].s.position.set(980, 1330);
      this.gears[2].s.position.set(930, 120);
      this.gears[1].s.scale.set(0.35);
    }
    this.gears[2].s.visible = !this.portrait;
    for (const o of this.overlay.children) (o as Container & { relayout?: () => void }).relayout?.();
  }

  // ---------------------------------------------------------------- per-frame
  private update(tk: Ticker) {
    const dt = tk.deltaMS / 1000;
    const rm = this.prefs.reducedMotion;
    this.time += dt;
    if (!rm) {
      // crowd: gentle idle sway, jumping when cheering
      const jump = this.cheerAmp > 0 ? -Math.abs(Math.sin(this.time * 9)) * 22 * this.cheerAmp : 0;
      this.crowd.y = this.layerBase.crowdY + Math.sin(this.time * 2.2) * 2.5 + jump;
      this.cheerAmp = Math.max(0, this.cheerAmp - dt * 0.35);
      this.flags.skew.x = Math.sin(this.time * 1.6) * 0.015;
      this.flags.y = Math.sin(this.time * 1.3) * 3;
    } else {
      this.crowd.y = this.layerBase.crowdY;
    }
    const boost = 1 + this.gearBoost * 4;
    this.gearBoost = Math.max(0, this.gearBoost - dt * 0.6);
    if (!rm) {
      for (const g of this.gears) g.s.rotation += g.speed * dt * boost * (this.mode === 'freegame' ? 1.8 : 1);
      this.swayT += dt;
      this.gears[1].s.rotation = -0.35 + 0.06 * Math.sin(this.swayT * 0.6);
      this.dialGear.rotation += 0.04 * dt;
    }
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life += dt;
      p.vy += p.g * dt;
      p.s.x += p.vx * dt;
      p.s.y += p.vy * dt;
      p.s.rotation += p.spin * dt;
      p.s.alpha = Math.max(0, 1 - p.life / p.max);
      if (p.life >= p.max) {
        p.s.destroy();
        this.particles.splice(i, 1);
      }
    }
    const w = this.portrait ? 1080 : 1920;
    const h = this.portrait ? 1920 : 1080;
    for (const d of this.dust) {
      d.s.visible = !rm;
      d.s.x += d.vx * dt;
      d.s.y += d.vy * dt;
      d.life += dt;
      d.s.alpha = 0.15 + 0.15 * Math.sin(d.life * 1.3 + d.spin);
      if (d.s.y < -20) {
        d.s.y = h + 20;
        d.s.x = Math.random() * w;
      }
    }
  }

  private spawnDust() {
    for (let i = 0; i < 36; i++) {
      const s = new Sprite(this.tex.glow);
      s.anchor.set(0.5);
      s.scale.set(0.08 + Math.random() * 0.12);
      s.blendMode = 'add';
      s.x = Math.random() * 1920;
      s.y = Math.random() * 1920;
      this.world.addChildAt(s, 3);
      this.dust.push({ s, vx: (Math.random() - 0.5) * 8, vy: -6 - Math.random() * 12, g: 0, life: Math.random() * 10, max: 1e9, spin: Math.random() * 6 });
    }
  }

  private burst(x: number, y: number, n: number, texName = 'sparkle', parent: Container = this.fx, opts: { speed?: number; g?: number; life?: number; scale?: number } = {}) {
    if (this.prefs.reducedMotion) n = Math.ceil(n / 4);
    for (let i = 0; i < n; i++) {
      const s = new Sprite(this.tex[texName]);
      s.anchor.set(0.5);
      s.scale.set((opts.scale ?? 0.5) * (0.5 + Math.random()));
      s.blendMode = texName === 'coin' ? 'normal' : 'add';
      s.position.set(x, y);
      parent.addChild(s);
      const a = Math.random() * Math.PI * 2;
      const sp = (opts.speed ?? 260) * (0.3 + Math.random());
      this.particles.push({ s, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - (opts.g ? 300 : 0), g: opts.g ?? 0, life: 0, max: (opts.life ?? 0.9) * (0.6 + Math.random() * 0.6), spin: (Math.random() - 0.5) * 6 });
    }
  }

  /** centre of a visible cell in world coordinates */
  private cellWorld(reel: number, row: number) {
    const sc = this.board.scale.x;
    return { x: this.board.x + (FRAME_M + reel * CELL + CELL / 2) * sc, y: this.board.y + (FRAME_M + row * CELL + CELL / 2) * sc };
  }

  /** crowd celebration (presentation only) */
  cheer(strength = 1) {
    this.cheerAmp = Math.min(1.5, Math.max(this.cheerAmp, strength));
  }

  private squash(reel: Reel) {
    if (this.prefs.reducedMotion) return;
    const base = SYM_SIZE / reel.sprites[0].texture.width;
    void this.tw.tween(260, (u) => {
      const k = u < 0.4 ? 1 - 0.1 * (u / 0.4) : 0.9 + 0.1 * ease.outElastic((u - 0.4) / 0.6);
      for (const sp of reel.sprites) {
        sp.scale.y = base * k;
        sp.scale.x = base * (2 - k);
      }
    });
  }

  private wiggle(sp: Sprite, ms = 700) {
    if (this.prefs.reducedMotion) return;
    void this.tw.tween(ms, (u) => (sp.rotation = Math.sin(u * Math.PI * 6) * 0.09 * (1 - u)));
  }

  // ---------------------------------------------------------------- View API
  setMode(mode: GameType) {
    if (mode === this.mode) return;
    this.mode = mode;
    const target = mode === 'freegame' ? 0.16 : 0;
    const from = this.bonusTint.alpha;
    void this.tw.tween(900, (u) => (this.bonusTint.alpha = from + (target - from) * u));
    this.dial.alpha = mode === 'freegame' ? 1 : 0.8;
    if (mode === 'basegame') {
      this.setHand(0);
      this.dialMult.text = '×1';
    }
    audio.setMusic(mode === 'freegame' ? 'music_free' : 'music_base');
  }

  /** Shows a board immediately (initial screen / resume). */
  setBoard(stops: number[], gameType: GameType) {
    const strips = gameType === 'freegame' ? STRIPS.free : STRIPS.base;
    this.reels.forEach((r, i) => {
      r.strip = strips[i];
      r.pos = stops[i];
      r.render();
    });
  }

  async spinTo(_board: Board, stops: number[], gameType: GameType, anticipation: number[], quick: boolean) {
    const strips = gameType === 'freegame' ? STRIPS.free : STRIPS.base;
    const rm = this.prefs.reducedMotion;
    const turbo = this.prefs.turbo;
    const baseT = quick ? 260 : rm ? 420 : turbo ? 650 : gameType === 'freegame' ? 900 : 1050;
    const stagger = quick ? 40 : rm ? 60 : turbo ? 90 : 170;
    const antExtra = quick || rm ? 0 : turbo ? 600 : 1300;
    if (!quick) {
      audio.play('spin_start', { volume: 0.7 });
      audio.startLoop('spin_loop', 0.5);
    }
    this.gearBoost = 1;
    let landedScatters = 0;
    let antOn = false;
    const tasks = this.reels.map(async (reel, r) => {
      const ant = anticipation[r] === 1;
      let extraBefore = 0;
      for (let k = 0; k <= r; k++) if (anticipation[k]) extraBefore += antExtra;
      const T = baseT + r * stagger + extraBefore;
      // short wind-up (reel lifts slightly) — skipped in reduced motion
      const start = reel.pos;
      if (!rm && !quick) await this.tw.tween(110, (u) => { reel.pos = start + 0.25 * u; reel.render(); }, ease.outCubic);
      // switch strip set while the reel is moving (hidden by motion)
      const n = strips[r].length;
      if (reel.strip !== strips[r]) {
        reel.strip = strips[r];
        reel.pos = mod(Math.round(reel.pos), n) + (reel.pos - Math.round(reel.pos));
      }
      const s0 = reel.pos;
      const v = turbo ? 30 : 24;
      const D0 = Math.max(4, Math.round((v * T) / 1000 * 0.62));
      const D = D0 + mod(Math.floor(s0) - D0 - stops[r], n) + (s0 - Math.floor(s0));
      let last = s0;
      reel.blur.enabled = !rm && !quick;
      const easing = rm ? ease.outCubic : (u: number) => ease.outBack(u, 0.55);
      await this.tw.tween(T, (u) => {
        reel.pos = s0 - D * easing(u);
        const speed = Math.abs(last - reel.pos);
        last = reel.pos;
        reel.blur.strengthY = Math.min(16, speed * 30);
        reel.render();
        if (ant && !antOn && u > 0.05) {
          antOn = true;
          this.showAnticipation(r);
        }
      });
      reel.pos = stops[r];
      reel.blur.enabled = false;
      reel.blur.strengthY = 0;
      reel.render();
      // landing feedback (strictly informative: the result was fixed before the spin)
      if (!quick) {
        audio.play('reel_stop', { volume: 0.55, rate: 0.96 + r * 0.02 });
        this.squash(reel);
        const col = Array.from({ length: NROWS }, (_, row) => reel.strip[(stops[r] + row) % n]);
        if (col.includes('S')) {
          landedScatters++;
          audio.play(`scatter_${Math.min(3, landedScatters)}` as 'scatter_1', { volume: 0.7 });
          const row = col.indexOf('S');
          const p = this.cellWorld(r, row);
          this.burst(p.x, p.y, 14, 'sparkle', this.fx, { speed: 180, life: 0.7, scale: 0.4 });
          this.pulse(reel.cell(row), 1.12, 380);
        }
        if (col.includes('W')) {
          audio.play('wild_land', { volume: 0.45 });
          const row = col.indexOf('W');
          this.pulse(reel.cell(row), 1.1, 320);
        }
      }
    });
    await Promise.all(tasks);
    this.hideAnticipation();
    audio.stopLoop('spin_loop');
  }

  private showAnticipation(fromReel: number) {
    const g = this.antGfx;
    g.clear();
    for (let r = fromReel; r < NR; r++) g.roundRect(FRAME_M + r * CELL + 4, FRAME_M + 4, CELL - 8, NROWS * CELL - 8, 14).stroke({ color: 0xffd23f, width: 8, alpha: 0.95 });
    g.alpha = 0;
    void this.tw.tween(250, (u) => (g.alpha = u));
  }

  private hideAnticipation() {
    this.antGfx.clear();
  }

  private pulse(s: Sprite, k: number, ms: number) {
    if (this.prefs.reducedMotion) return;
    const base = SYM_SIZE / s.texture.width;
    void this.tw.tween(ms, (u) => s.scale.set(base * (1 + (k - 1) * Math.sin(u * Math.PI))));
  }

  clearWins() {
    this.lineGfx.clear();
    this.glowLayer.removeChildren().forEach((c) => c.destroy());
    this.winText.text = '';
    for (const r of this.reels) for (const s of r.sprites) {
      s.alpha = 1;
      s.rotation = 0;
      s.tint = 0xffffff;
      s.width = s.height = SYM_SIZE;
    }
  }

  private drawGroup(w: WinLine, alpha = 1) {
    const g = this.lineGfx;
    const color = w.kind === 'scatter' ? 0x7cd3ff : 0xffd23f;
    for (const p of w.positions) {
      g.roundRect(p.reel * CELL + 7, p.row * CELL + 7, CELL - 14, CELL - 14, 20).stroke({ color: 0x1b1410, width: 11, alpha });
      g.roundRect(p.reel * CELL + 7, p.row * CELL + 7, CELL - 14, CELL - 14, 20).stroke({ color, width: 5, alpha });
    }
  }

  private groupLabel(w: WinLine) {
    const amt = money(Math.round((this.bet * w.win) / 100), this.currency, this.lang);
    return w.kind === 'scatter' ? amt : `${w.ways} ${this.t.ways}  ·  ${amt}`;
  }

  async showWins(wins: WinLine[], multiplier: number, tier: WinTier) {
    const winning = new Set<string>();
    for (const w of wins) for (const p of w.positions) winning.add(`${p.reel}:${p.row}`);
    // dim the others, glow the winners
    this.reels.forEach((reel, r) => Array.from({ length: NROWS }, (_, i) => i).forEach((row) => {
      const s = reel.cell(row);
      if (!winning.has(`${r}:${row}`)) {
        s.alpha = 0.42;
      } else {
        const glow = new Sprite(this.tex.glow);
        glow.anchor.set(0.5);
        glow.blendMode = 'add';
        glow.width = glow.height = CELL * 1.25;
        glow.position.set(r * CELL + CELL / 2, row * CELL + CELL / 2);
        glow.alpha = 0.55;
        this.glowLayer.addChild(glow);
        this.pulse(s, 1.12, 600);
        if (tier !== 'ldw' && tier !== 'none') this.wiggle(s);
      }
    }));
    for (const w of wins) this.drawGroup(w);
    const total = wins.reduce((a, w) => a + w.win, 0);
    const amt = Math.round((this.bet * total) / 100);
    this.winText.text = (multiplier > 1 ? `×${multiplier}  ·  ` : '') + money(amt, this.currency, this.lang);
    // sound: wins not exceeding the bet are not celebrated
    if (tier === 'ldw') audio.play('line_tick', { volume: 0.35 });
    else if (tier === 'small') audio.play(amt / this.bet >= 3 ? 'win_1' : 'win_0', { volume: 0.7 });
    else if (tier !== 'none') audio.play('win_2', { volume: 0.8 });
    if (tier !== 'ldw' && tier !== 'none') {
      for (const w of wins) for (const p of w.positions.slice(0, 1)) {
        const c = this.cellWorld(p.reel, p.row);
        this.burst(c.x, c.y, 6, 'sparkle', this.fx, { speed: 120, life: 0.6, scale: 0.35 });
      }
    }
    await this.tw.wait(this.mode === 'freegame' ? 750 : 950);
    // cycle through the individual symbol groups once (base game only, up to 4)
    if (this.mode === 'basegame' && wins.length > 1 && !this.prefs.turbo) {
      for (const w of wins.slice(0, 4)) {
        this.lineGfx.clear();
        this.drawGroup(w);
        this.winText.text = this.groupLabel(w);
        await this.tw.wait(620);
      }
      this.lineGfx.clear();
      for (const w of wins) this.drawGroup(w, 0.6);
      this.winText.text = (multiplier > 1 ? `×${multiplier}  ·  ` : '') + money(amt, this.currency, this.lang);
    }
  }

  async scatterCelebrate(positions: Position[]) {
    for (const p of positions) {
      const s = this.reels[p.reel].cell(p.row);
      this.pulse(s, 1.2, 700);
      const c = this.cellWorld(p.reel, p.row);
      this.burst(c.x, c.y, 20, 'sparkle', this.fx, { speed: 220, life: 0.9, scale: 0.45 });
    }
    await this.tw.wait(500);
  }

  // ---------------------------------------------------------------- overlays
  private makeOverlay(): Container & { relayout?: () => void } {
    const c = new Container() as Container & { relayout?: () => void };
    const veil = new Graphics();
    c.addChild(veil);
    c.relayout = () => {
      veil.clear().rect(0, 0, this.app.screen.width, this.app.screen.height).fill({ color: 0x1b1410, alpha: 0.62 });
      const inner = c.children[1] as Container | undefined;
      if (inner) {
        const s = Math.min(this.app.screen.width / 1200, this.app.screen.height / 900);
        inner.scale.set(s);
        inner.position.set(this.app.screen.width / 2, this.app.screen.height / 2);
      }
    };
    c.addChild(new Container());
    this.overlay.addChild(c);
    c.relayout();
    return c;
  }

  private goldText(text: string, size: number, font = 'Luckiest Guy') {
    const t = new Text({ text, style: { fontFamily: font, fontSize: size, fill: this.goldFill(size), stroke: { color: '#1b1410', width: Math.max(6, size / 8), join: 'round' }, letterSpacing: size / 20, align: 'center', dropShadow: { color: '#1b1410', alpha: 1, blur: 0, distance: Math.max(4, size / 14), angle: Math.PI / 3 } } });
    t.anchor.set(0.5);
    return t;
  }

  private plainText(text: string, size: number, color = '#fff3d6') {
    const t = new Text({ text, style: { fontFamily: 'Lilita One', fontSize: size, fill: color, align: 'center', wordWrap: true, wordWrapWidth: 900, lineHeight: size * 1.3, stroke: { color: '#1b1410', width: 6, join: 'round' } } });
    t.anchor.set(0.5);
    return t;
  }

  /** resolves on tap or after `ms` */
  private waitTapOr(ms: number): Promise<void> {
    return new Promise((resolve) => {
      let done = false;
      const finish = () => {
        if (done) return;
        done = true;
        this.onOverlayTap = null;
        resolve();
      };
      this.onOverlayTap = finish;
      void this.tw.wait(ms * (this.prefs.turbo ? 1.8 : 1)).then(finish);
    });
  }

  private async fadeOverlay(c: Container, inMs: number, outMs: number, hold: () => Promise<void>) {
    c.alpha = 0;
    const inner = c.children[1] as Container;
    const s0 = inner.scale.x;
    await this.tw.tween(inMs, (u) => {
      c.alpha = u;
      if (!this.prefs.reducedMotion) inner.scale.set(s0 * (0.85 + 0.15 * ease.outBack(u)));
    });
    await hold();
    await this.tw.tween(outMs, (u) => (c.alpha = 1 - u));
    c.destroy({ children: true });
  }

  async bonusIntro(spins: number) {
    this.cheer(1.2);
    audio.play('bonus_trigger', { volume: 0.9 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const title = this.goldText(this.t.bonusIntroTitle, 84);
    title.y = -170;
    const num = this.goldText(String(spins), 220);
    num.y = 10;
    const sub = this.plainText(this.t.bonusIntroSub, 30);
    sub.y = 190;
    const tap = this.plainText(this.t.tapToContinue, 22, '#ffd23f');
    tap.y = 300;
    const coin = new Sprite(this.tex.dial);
    coin.anchor.set(0.5);
    coin.width = coin.height = 420;
    coin.alpha = 0.18;
    coin.y = 10;
    inner.addChild(coin, title, num, sub, tap);
    c.relayout?.();
    const spinCoin = (tk: Ticker) => (coin.rotation += tk.deltaMS / 4000);
    if (!this.prefs.reducedMotion) this.app.ticker.add(spinCoin);
    await this.fadeOverlay(c, 380, 300, async () => {
      this.burst(this.app.screen.width / 2, this.app.screen.height / 2, 40, 'sparkle', this.overlay, { speed: 420, life: 1.2, scale: 0.6 });
      await this.waitTapOr(3200);
    });
    this.app.ticker.remove(spinCoin);
  }

  private setHand(index: number) {
    const ladder = RULES.rallyLadder;
    const a0 = Math.PI * 0.78;
    const a1 = Math.PI * 2.22;
    const a = a0 + ((a1 - a0) * (index + 0.5)) / ladder.length;
    this.dialHand.rotation = a + Math.PI / 2;
    this.currentLadderIndex = index;
  }

  async wind(positions: Position[], collected: number, multiplier: number, previous: number) {
    const ladder = RULES.rallyLadder;
    const target = Math.min(collected, ladder.length - 1);
    // energy flies from each wild to the dial
    const dialWorld = { x: this.dial.x, y: this.dial.y };
    const flights = positions.map(async (p, i) => {
      const s = this.reels[p.reel].cell(p.row);
      this.pulse(s, 1.18, 500);
      const from = this.cellWorld(p.reel, p.row);
      const orb = new Sprite(this.tex.glow);
      orb.anchor.set(0.5);
      orb.blendMode = 'add';
      orb.scale.set(0.9);
      this.fx.addChild(orb);
      await this.tw.wait(i * 120);
      const ctrl = { x: (from.x + dialWorld.x) / 2, y: Math.min(from.y, dialWorld.y) - 260 };
      await this.tw.tween(this.prefs.reducedMotion ? 150 : 520, (u) => {
        const x = (1 - u) ** 2 * from.x + 2 * (1 - u) * u * ctrl.x + u * u * dialWorld.x;
        const y = (1 - u) ** 2 * from.y + 2 * (1 - u) * u * ctrl.y + u * u * dialWorld.y;
        orb.position.set(x, y);
        if (!this.prefs.reducedMotion && Math.random() < 0.5) this.burst(x, y, 1, 'glow', this.fx, { speed: 20, life: 0.35, scale: 0.25 });
      }, ease.inOutCubic);
      orb.destroy();
    });
    audio.play('wind', { volume: 0.8 });
    await Promise.all(flights);
    const fromIdx = this.currentLadderIndex;
    const g0 = this.dialGear.rotation;
    await this.tw.tween(this.prefs.reducedMotion ? 120 : 600, (u) => {
      const k = fromIdx + (target - fromIdx) * u;
      this.setHand(k);
      this.dialGear.rotation = g0 - (target - fromIdx) * 0.6 * u;
    }, ease.outElastic);
    this.setHand(target);
    if (multiplier !== previous) {
      audio.play('mult_up', { volume: 0.8 });
      this.dialMult.text = `×${multiplier}`;
      this.burst(this.dial.x, this.dial.y, 24, 'sparkle', this.fx, { speed: 260, life: 0.8, scale: 0.5 });
      if (!this.prefs.reducedMotion) await this.tw.tween(420, (u) => this.dialMult.scale.set(1 + 0.5 * Math.sin(u * Math.PI)));
    }
  }

  async retrigger(added: number, _total: number) {
    audio.play('bonus_trigger', { volume: 0.6 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const t1 = this.goldText(`+${added}`, 180);
    t1.y = -40;
    const t2 = this.goldText(this.t.retrigger, 54);
    t2.y = 110;
    inner.addChild(t1, t2);
    c.relayout?.();
    await this.fadeOverlay(c, 300, 260, () => this.waitTapOr(1500));
  }

  private async countUp(text: Text, amount: number, ms: number, skip: { now: boolean }) {
    let lastTick = 0;
    await this.tw.tween(ms, (u) => {
      const v = skip.now ? amount : Math.round(amount * u);
      text.text = money(v, this.currency, this.lang);
      if (u - lastTick > 0.04 && u < 1 && !skip.now) {
        lastTick = u;
        audio.play('count_tick', { volume: 0.25 });
      }
    }, ease.outCubic);
    text.text = money(amount, this.currency, this.lang);
  }

  async bonusOutro(amount: number) {
    audio.play('bonus_end', { volume: 0.8 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const title = this.goldText(this.t.bonusEnd, 64);
    title.y = -150;
    const sub = this.plainText(this.t.totalWin.toUpperCase(), 34);
    sub.y = -50;
    const amt = this.goldText(money(0, this.currency, this.lang), 120);
    amt.y = 70;
    inner.addChild(title, sub, amt);
    c.relayout?.();
    const skip = { now: false };
    await this.fadeOverlay(c, 350, 300, async () => {
      this.onOverlayTap = () => (skip.now = true);
      await this.countUp(amt, amount, 1600, skip);
      await this.waitTapOr(2200);
    });
    this.dialMult.text = '×1';
  }

  async bigWin(amount: number, tier: WinTier) {
    this.cheer(tier === 'big' ? 1 : 1.5);
    const title = tier === 'epic' ? this.t.epicWin : tier === 'mega' ? this.t.megaWin : this.t.bigWin;
    audio.play('win_3', { volume: 0.9 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const halo = new Sprite(this.tex.glow);
    halo.anchor.set(0.5);
    halo.blendMode = 'add';
    halo.width = halo.height = 900;
    halo.alpha = 0.5;
    const t1 = this.goldText(title, 120);
    t1.y = -90;
    const amt = this.goldText(money(0, this.currency, this.lang), 110);
    amt.y = 80;
    inner.addChild(halo, t1, amt);
    c.relayout?.();
    const skip = { now: false };
    const dur = tier === 'epic' ? 5200 : tier === 'mega' ? 3800 : 2600;
    let showering = true;
    const shower = async () => {
      while (showering && !this.prefs.reducedMotion) {
        const w = this.app.screen.width;
        this.burst(Math.random() * w, -30, 3, 'coin', this.overlay, { speed: 120, g: 900, life: 2.2, scale: 0.55 });
        await this.tw.wait(90);
      }
    };
    void shower();
    await this.fadeOverlay(c, 350, 350, async () => {
      this.onOverlayTap = () => (skip.now = true);
      await this.countUp(amt, amount, dur, skip);
      await this.waitTapOr(1600);
    });
    showering = false;
  }

  async wincap() {
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const t = this.goldText(this.t.winCap, 70);
    inner.addChild(t);
    c.relayout?.();
    await this.fadeOverlay(c, 300, 300, () => this.waitTapOr(2200));
  }

  pause(ms: number) {
    return this.tw.wait(ms);
  }
}
