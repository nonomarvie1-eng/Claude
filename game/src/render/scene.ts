// PixiJS presentation layer.  It only *displays* books: no outcome logic here.
// Every value shown (boards, wins, spins, multiplier, totals) is received from
// the book player, which reads it verbatim from the RGS book.
import { Application, BlurFilter, Container, FillGradient, Graphics, Sprite, Text, Texture, type Ticker } from 'pixi.js';
import { audio } from '../audio/audio';
import { STRIPS } from '../engine/engine';
import { RULES } from '../engine/rules';
import type { Board, BonusLevel, GameType, ModeName, Position, SymbolName, WinLine } from '../engine/types';
import type { View, WinTier } from '../game/player';
import { money } from '../game/format';
import type { Strings } from '../i18n/strings';
import { ease, Tweener } from './tween';
import LAYERS from '../assets/layers.json';
import { fmt as fmtS } from '../i18n/strings';

const imgs = import.meta.glob('../assets/img/*.{webp,jpg}', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
// PNG fallbacks for browsers without WebP decoding (excluded from the single-file demo build)
const pngs = (import.meta.env.VITE_NO_PNG_FALLBACK === '1'
  ? {}
  : import.meta.glob('../assets/img-png/*.png', { eager: false, query: '?url', import: 'default' })) as Record<string, () => Promise<string>>;

const CELL = 170;
const NR = RULES.reels;
const NROWS = RULES.rows;
const FRAME_M = 30;
const FRAME_W = NR * CELL + 2 * FRAME_M;
const FRAME_H = NROWS * CELL + 2 * FRAME_M;
const SYM_SIZE = 164;
const PLATE_H = 64; // win plate, centred on the frame's bottom edge (board units)

// palette (art direction)
const C = {
  night: 0x081b23,
  emerald: 0x093a31,
  gold: 0xd5a64b,
  cream: 0xf2e5c3,
  tennis: 0xd4e948,
};

export interface Prefs {
  reducedMotion: boolean;
  turbo: boolean;
}

export interface Insets {
  top: number;
  bottom: number;
  left?: number;
  right?: number;
}

const mod = (a: number, n: number) => ((a % n) + n) % n;
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

function decode(url: string): Promise<HTMLImageElement> {
  const img = new Image();
  img.decoding = 'async';
  img.src = url;
  return img.decode().then(() => img);
}

export async function loadTextures(onProgress: (p: number) => void): Promise<Record<string, Texture>> {
  const entries = Object.entries(imgs);
  const out: Record<string, Texture> = {};
  let done = 0;
  await Promise.all(
    entries.map(async ([k, url]) => {
      const name = k.split('/').pop()!.replace(/\.(webp|jpg)$/, '');
      let img: HTMLImageElement;
      try {
        img = await decode(url);
      } catch (e) {
        // WebP not supported: fall back to the PNG export of the same sprite
        const fb = Object.entries(pngs).find(([p]) => p.endsWith(`/${name}.png`))?.[1];
        if (!fb) throw e;
        img = await decode(await fb());
      }
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
  /** sprite showing visible row r when at rest */
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

/** Layout rectangles in CSS pixels (exposed for automated layout checks). */
export interface SceneLayout {
  board: { x: number; y: number; w: number; h: number };
  header: { x: number; y: number; w: number; h: number };
  portrait: boolean;
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
  insets: Insets = { top: 0, bottom: 0 };
  layoutInfo: SceneLayout | null = null;

  private bg = new Container();
  private sky = new Sprite();
  private crowd = new Sprite();
  private fore = new Sprite();
  private flags = new Sprite();
  private cheerAmp = 0;
  private flashLayer = new Container();
  private flashes: { s: Sprite; life: number }[] = [];
  private mpText: Text | null = null;
  private layerBase = { crowdY: 0 };
  private time = 0;
  private bonusMix = 0; // 0 = night match, 1 = Tie-Break ambience
  private world = new Container();
  private dustLayer = new Container();
  // header: logo (base game) / Tie-Break panel (free spins)
  private header = new Container();
  private logo = new Sprite();
  private logoShine = new Graphics();
  private logoMask = new Sprite();
  private nextShine = 4;
  private tb = new Container();
  private tbRound!: Text;
  private tbMult!: Text;
  private tbTotal!: Text;
  private tbMultCell = new Container();
  private headerBox = { x: 0, y: 0, w: 0, h: 0 };
  private bonusInfo = { cur: 0, total: 0, mult: 1, win: 0 };
  // board
  private board = new Container();
  private frameLight = new Graphics();
  private frame = new Sprite();
  private reelLayer = new Container();
  private reelMask = new Graphics();
  private reels: Reel[] = [];
  private winLayer = new Container();
  private lineGfx = new Graphics();
  private glowLayer = new Container();
  private badgeLayer = new Container();
  private antGfx = new Graphics();
  private plate = new Container();
  private plateBg = new Graphics();
  private winText!: Text;
  // Ace, the ball-boy dog (mascot) — appears only at key moments
  private aceLayer = new Container();
  private ace = new Container();
  private aceBubble = new Container();
  private aceBusy = false;
  private fx = new Container();
  private overlay = new Container();
  private particles: Particle[] = [];
  private dust: Particle[] = [];
  private mode: GameType = 'basegame';
  private portrait = false;
  onOverlayTap: (() => void) | null = null;
  onLayout: ((l: SceneLayout) => void) | null = null;

  async init(host: HTMLElement, tex: Record<string, Texture>, t: Strings) {
    this.tex = tex;
    this.t = t;
    await this.app.init({
      resizeTo: host,
      antialias: true,
      backgroundColor: C.night,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true,
      powerPreference: 'high-performance',
    });
    host.appendChild(this.app.canvas);
    this.app.canvas.setAttribute('aria-hidden', 'true');
    this.tw = new Tweener(this.app.ticker, () => (this.prefs.turbo ? 1.8 : 1));

    this.bg.addChild(this.sky, this.crowd, this.flashLayer, this.fore, this.flags);
    this.flags.blendMode = 'add';
    this.app.stage.addChild(this.bg, this.dustLayer, this.world);

    // header
    this.logo.texture = tex.logo;
    this.logo.anchor.set(0.5);
    this.logoMask.texture = tex.logo;
    this.logoMask.anchor.set(0.5);
    this.logoShine.mask = this.logoMask;
    this.logoShine.blendMode = 'add';
    this.header.addChild(this.logo, this.logoMask, this.logoShine);
    this.tb.visible = false;

    // board
    this.frameLight.alpha = 0;
    this.board.addChild(this.frameLight);
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
    this.board.addChild(this.reelLayer, this.antGfx);
    this.winLayer.x = FRAME_M;
    this.winLayer.y = FRAME_M;
    this.winLayer.addChild(this.glowLayer, this.lineGfx, this.badgeLayer);
    this.board.addChild(this.winLayer);
    // win plate: sits on the bottom edge of the frame, never over the symbols
    this.winText = new Text({ text: '', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 40, fill: '#F2E5C3', letterSpacing: 2, align: 'center' } });
    this.winText.anchor.set(0.5);
    this.plate.addChild(this.plateBg, this.winText);
    this.plate.position.set(FRAME_W / 2, FRAME_H);
    this.plate.visible = false;
    this.board.addChild(this.plate);

    this.world.addChild(this.header, this.board, this.tb, this.fx);
    this.app.stage.addChild(this.overlay, this.aceLayer);
    this.overlay.eventMode = 'static';
    this.overlay.on('pointertap', () => this.onOverlayTap?.());
    this.buildAce();

    this.spawnDust();
    this.app.ticker.add((tk) => this.update(tk));
    window.addEventListener('resize', () => this.layout());
    new ResizeObserver(() => this.layout()).observe(host);
    this.layout();
  }

  /** Space taken by the DOM top bar and HUD (CSS px): the board is laid out between them. */
  setInsets(i: Insets) {
    const c = this.insets;
    if (i.top === c.top && i.bottom === c.bottom && (i.left ?? 0) === (c.left ?? 0) && (i.right ?? 0) === (c.right ?? 0)) return;
    this.insets = i;
    if (this.tex) this.layout();
  }

  private goldFill() {
    return new FillGradient({
      type: 'linear',
      start: { x: 0, y: 0 },
      end: { x: 0, y: 1 },
      colorStops: [
        { offset: 0, color: '#FBF1D3' },
        { offset: 0.45, color: '#E9C677' },
        { offset: 0.56, color: '#B8862F' },
        { offset: 1, color: '#F2D58A' },
      ],
      textureSpace: 'local',
    });
  }

  private goldText(text: string, size: number) {
    const t = new Text({
      text,
      style: {
        fontFamily: 'Cinzel', fontWeight: '700', fontSize: size, fill: this.goldFill(),
        stroke: { color: '#081B23', width: Math.max(4, size / 12), join: 'round' },
        letterSpacing: size / 16, align: 'center', lineHeight: size * 1.08,
        dropShadow: { color: '#000000', alpha: 0.6, blur: size / 6, distance: size / 22, angle: Math.PI / 2 },
      },
    });
    t.anchor.set(0.5);
    return t;
  }

  private fit(t: Text, maxW = 640) {
    if (t.width > maxW) t.scale.set(maxW / t.width);
    return t;
  }

  private plainText(text: string, size: number, color = '#F2E5C3', weight: '500' | '700' | '800' = '500') {
    const t = new Text({ text, style: { fontFamily: 'Inter', fontWeight: weight, fontSize: size, fill: color, align: 'center', wordWrap: true, wordWrapWidth: 640, lineHeight: size * 1.4, letterSpacing: size > 24 ? 1 : 0.5 } });
    t.anchor.set(0.5);
    return t;
  }

  // ---------------------------------------------------------------- Tie-Break panel
  private tbVariant: 'wide' | 'compact' | 'tall' | null = null;
  private tbLabels: Text[] = [];
  private panelInHeader = true;

  /**
   * Tie-Break panel ("GOLDEN RALLY — TIE-BREAK": spin x / y, multiplier, total
   * win).  Three arrangements so it stays legible everywhere: a side column
   * (landscape with room beside the reels), a wide band or a compact band
   * (header, portrait).
   */
  private buildTieBreakPanel(variant: 'wide' | 'compact' | 'tall') {
    if (this.tbVariant === variant) return;
    this.tbVariant = variant;
    this.tb.removeChildren().forEach((c) => c.destroy({ children: true }));
    const [W, H] = variant === 'tall' ? [300, 560] : variant === 'wide' ? [1000, 200] : [640, 196];
    const bg = new Graphics();
    const sup = this.level === 'super';
    bg.roundRect(-W / 2, -H / 2, W, H, 24).fill({ color: sup ? 0x0b1f4a : C.night, alpha: 0.92 }).stroke({ color: sup ? 0x37b6ff : C.gold, width: sup ? 4 : 3 });
    bg.roundRect(-W / 2 + 9, -H / 2 + 9, W - 18, H - 18, 17).stroke({ color: C.cream, width: 1, alpha: 0.22 });
    this.tb.addChild(bg);
    const lblSize = variant === 'tall' ? 22 : 24;
    const valSize = variant === 'tall' ? 58 : variant === 'wide' ? 58 : 48;
    const mk = (label: string, x: number, y: number, maxW: number, color = '#F2E5C3') => {
      const l = new Text({ text: label, style: { fontFamily: 'Inter', fontWeight: '800', fontSize: lblSize, fill: '#D5A64B', letterSpacing: 3 } });
      l.anchor.set(0.5);
      l.position.set(x, y);
      if (l.width > maxW) l.scale.set(maxW / l.width);
      const v = new Text({ text: '', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: valSize, fill: color, letterSpacing: 1 } });
      v.anchor.set(0.5);
      v.position.set(x, y + lblSize / 2 + valSize * 0.62);
      (v as Text & { maxW?: number }).maxW = maxW;
      this.tb.addChild(l, v);
      return { l, v };
    };
    let cells: { l: Text; v: Text }[];
    if (variant === 'tall') {
      const kicker = new Text({ text: 'GOLDEN RALLY', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 22, fill: '#D5A64B', letterSpacing: 6 } });
      kicker.anchor.set(0.5);
      kicker.y = -H / 2 + 40;
      const title = this.goldText(this.level === 'super' ? this.t.stbTitle : this.t.tbTitle, this.level === 'super' ? 34 : 46);
      title.y = -H / 2 + 86;
      if (title.width > W - 36) title.scale.set((W - 36) / title.width);
      this.tb.addChild(kicker, title);
      const y0 = -H / 2 + 150;
      const step = 128;
      for (let i = 1; i < 3; i++) bg.moveTo(-W / 2 + 34, y0 + i * step - 22).lineTo(W / 2 - 34, y0 + i * step - 22).stroke({ color: C.gold, width: 1.5, alpha: 0.45 });
      bg.moveTo(-W / 2 + 34, y0 - 22).lineTo(W / 2 - 34, y0 - 22).stroke({ color: C.gold, width: 1.5, alpha: 0.45 });
      cells = [mk(this.t.tbRound, 0, y0, W - 40), mk(this.t.tbMult, 0, y0 + step, W - 40, '#D4E948'), mk(this.t.tbTotal, 0, y0 + 2 * step, W - 40)];
    } else {
      const title = this.goldText(`GOLDEN RALLY · ${this.level === 'super' ? this.t.stbTitle : this.t.tbTitle}`, variant === 'wide' ? 40 : 34);
      title.y = -H / 2 + 38;
      if (title.width > W - 150) title.scale.set((W - 150) / title.width);
      this.tb.addChild(title);
      for (const sx of [-1, 1]) {
        const ball = new Sprite(this.tex.ui_golden_ball);
        ball.anchor.set(0.5);
        ball.width = ball.height = 58;
        ball.scale.x *= sx;
        ball.position.set(sx * (W / 2 - 44), -H / 2 + 40);
        this.tb.addChild(ball);
      }
      const y = -H / 2 + 92;
      for (const x of [-W / 6, W / 6]) bg.moveTo(x, y - 14).lineTo(x, H / 2 - 18).stroke({ color: C.gold, width: 1.5, alpha: 0.45 });
      const cw = W / 3 - 24;
      cells = [mk(this.t.tbRound, -W / 3, y, cw), mk(this.t.tbMult, 0, y, cw, '#D4E948'), mk(this.t.tbTotal, W / 3, y, cw)];
    }
    this.tbRound = cells[0].v;
    this.tbMult = cells[1].v;
    this.tbTotal = cells[2].v;
    this.tbLabels = cells.map((c) => c.l);
    this.tbMultCell = new Container();
    this.tbMultCell.position.copyFrom(this.tbMult.position);
    this.tb.addChild(this.tbMultCell);
    this.refreshPanel();
  }

  private refreshPanel() {
    if (!this.tbRound) return;
    const i = this.bonusInfo;
    this.tbRound.text = `${i.cur} / ${i.total}`;
    this.tbMult.text = `×${i.mult}`;
    this.tbTotal.text = money(i.win, this.currency, this.lang);
    for (const v of [this.tbRound, this.tbMult, this.tbTotal]) {
      v.scale.set(1);
      const maxW = (v as Text & { maxW?: number }).maxW ?? 300;
      if (v.width > maxW) v.scale.set(maxW / v.width);
    }
  }

  /** Values come from the HUD adapter (book events: updateFreeSpin / rallyUp / setTotalWin). */
  setBonusInfo(cur: number, total: number, mult: number, win: number) {
    const prevMult = this.bonusInfo.mult;
    this.bonusInfo = { cur, total, mult, win };
    if (this.tbRound) this.refreshPanel();
    if (mult !== prevMult && mult > 1 && !this.prefs.reducedMotion && this.tw) {
      void this.tw.tween(420, (u) => this.tbMult.scale.set(1 + 0.35 * Math.sin(u * Math.PI)));
    }
  }

  private relabelPanel() {
    const v = this.tbVariant;
    this.tbVariant = null;
    if (v) this.buildTieBreakPanel(v);
  }

  // ---------------------------------------------------------------- Ace
  private buildAce() {
    const disc = new Sprite(this.tex.sym_H1);
    disc.anchor.set(0.5);
    disc.width = disc.height = 240;
    const shadow = new Graphics().ellipse(0, 128, 92, 16).fill({ color: 0x000000, alpha: 0.35 });
    this.ace.addChild(shadow, disc);
    const bub = new Graphics();
    const txt = new Text({ text: '', style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 30, fill: '#081B23', align: 'center' } });
    txt.anchor.set(0.5);
    this.aceBubble.addChild(bub, txt);
    (this.aceBubble as Container & { draw?: (s: string) => void }).draw = (s: string) => {
      txt.text = s;
      const w = txt.width + 44, h = 64;
      bub.clear();
      bub.roundRect(-w / 2, -h / 2, w, h, 32).fill(C.cream).stroke({ color: C.gold, width: 3 });
      bub.poly([-w / 2 + 30, h / 2 - 2, -w / 2 + 20, h / 2 + 22, -w / 2 + 56, h / 2 - 2]).fill(C.cream);
      this.aceBubble.pivot.set(-w / 2 + 20, h / 2 + 22);
    };
    this.ace.addChild(this.aceBubble);
    this.aceBubble.position.set(70, -110);
    this.aceBubble.visible = false;
    this.ace.visible = false;
    this.aceLayer.addChild(this.ace);
  }

  private aceSize() {
    const w = this.app.screen.width, h = this.app.screen.height;
    return clamp(Math.min(w, h) * 0.2, 84, 190);
  }

  /**
   * Home position, chosen so that Ace never covers a symbol: in the left
   * gutter beside the reels when there is room (landscape), otherwise at the
   * left end of the header band (portrait), over the logo only.
   */
  private aceHome() {
    const L = this.layoutInfo;
    const pad = Math.max(8, this.app.screen.width * 0.015) + (this.insets.left ?? 0);
    let size = this.aceSize();
    if (L && L.board.x - pad >= size * 1.05) {
      return { x: pad + size / 2, y: L.board.y + L.board.h - size * 0.55, scale: size / 240, bubbleUp: true };
    }
    if (L) {
      size = Math.min(size, L.header.h * 1.05);
      return { x: L.header.x + size / 2, y: L.header.y + L.header.h / 2, scale: size / 240, bubbleUp: false };
    }
    return { x: pad + size / 2, y: this.app.screen.height / 2, scale: size / 240, bubbleUp: true };
  }

  /**
   * Ace walks in, says a short line, and leaves.  Purely decorative: called
   * only after the result is known, and never implies a reward.
   */
  async aceSay(text: string, hold = 1800, bringBall = false) {
    if (this.aceBusy) return;
    this.aceBusy = true;
    const home = this.aceHome();
    const rm = this.prefs.reducedMotion;
    const a = this.ace;
    a.visible = true;
    a.scale.set(home.scale);
    a.position.set(rm ? home.x : -200 * home.scale - 40, home.y);
    a.alpha = rm ? 0 : 1;
    (this.aceBubble as Container & { draw?: (s: string) => void }).draw?.(text);
    this.aceBubble.visible = false;
    // bubble: on-screen text never smaller than ~14 px; above Ace, or to its right in the header
    const bs = Math.max(1, 0.47 / home.scale);
    this.aceBubble.position.set(home.bubbleUp ? 70 : 128, home.bubbleUp ? -110 : 0);
    if (!home.bubbleUp) {
      // beside Ace (header band): bubble body centred vertically on Ace, tail hidden behind him
      const lb = this.aceBubble.getLocalBounds();
      this.aceBubble.pivot.set(lb.minX + 10, (lb.minY + lb.maxY - 22) / 2);
    }
    audio.play('pop', { volume: 0.35 });
    const x0 = a.x;
    await this.tw.tween(rm ? 220 : 520, (u) => {
      if (rm) a.alpha = u;
      else {
        a.x = x0 + (home.x - x0) * ease.outBack(u, 0.9);
        a.y = home.y - Math.abs(Math.sin(u * Math.PI * 3)) * 18 * home.scale * (1 - u);
        a.rotation = Math.sin(u * Math.PI * 3) * 0.06 * (1 - u);
      }
    });
    a.rotation = 0;
    this.aceBubble.visible = true;
    this.aceBubble.scale.set(rm ? bs : 0.4 * bs);
    if (!rm) void this.tw.tween(260, (u) => this.aceBubble.scale.set(bs * (0.4 + 0.6 * ease.outBack(u))));
    if (bringBall && !rm) {
      const from = { x: a.x + 60 * home.scale, y: a.y - 40 * home.scale };
      const to = { x: this.app.screen.width / 2, y: this.app.screen.height * 0.45 };
      await this.ballArc(from, to, 900);
    }
    await this.tw.wait(hold);
    this.aceBubble.visible = false;
    const x1 = a.x;
    await this.tw.tween(rm ? 200 : 420, (u) => {
      if (rm) a.alpha = 1 - u;
      else a.x = x1 + (-260 * home.scale - 40 - x1) * ease.inCubic(u);
    });
    a.visible = false;
    this.aceBusy = false;
  }

  /** Golden tennis ball flying with a bounce (transition flourish). */
  private async ballArc(from: { x: number; y: number }, to: { x: number; y: number }, ms: number) {
    const s = new Sprite(this.tex.ui_golden_ball);
    s.anchor.set(0.5);
    const size = clamp(Math.min(this.app.screen.width, this.app.screen.height) * 0.12, 48, 120);
    s.width = s.height = size;
    const shadow = new Graphics().ellipse(0, 0, size * 0.35, size * 0.1).fill({ color: 0x000000, alpha: 0.3 });
    this.aceLayer.addChildAt(shadow, 0);
    this.aceLayer.addChild(s);
    audio.play('serve', { volume: 0.6 });
    let bounced = false;
    const peak = Math.min(from.y, to.y) - this.app.screen.height * 0.22;
    await this.tw.tween(ms, (u) => {
      // two hops: a high arc to 70 %, then a small bounce
      let x: number, y: number;
      if (u < 0.7) {
        const k = u / 0.7;
        x = from.x + (to.x - from.x) * 0.85 * k;
        y = (1 - k) ** 2 * from.y + 2 * (1 - k) * k * peak + k * k * (to.y + 40);
      } else {
        if (!bounced) {
          bounced = true;
          audio.play('bounce', { volume: 0.5 });
        }
        const k = (u - 0.7) / 0.3;
        x = from.x + (to.x - from.x) * (0.85 + 0.15 * k);
        y = to.y + 40 - Math.sin(k * Math.PI) * 70 - 40 * k;
      }
      s.position.set(x, y);
      s.rotation += 0.25;
      shadow.position.set(x, to.y + 60);
      shadow.alpha = 0.3 + 0.4 * u;
    }, (u) => u);
    this.burst(s.x, s.y, 16, 'sparkle', this.aceLayer, { speed: 200, life: 0.6, scale: 0.4 });
    await this.tw.tween(200, (u) => (s.alpha = shadow.alpha = 1 - u));
    s.destroy();
    shadow.destroy();
  }

  /** Start screen: only the stadium is shown (reels hidden). */
  setIntro(on: boolean) {
    if (on) {
      this.world.visible = false;
      return;
    }
    this.world.visible = true;
    this.world.alpha = 0;
    void this.tw.tween(this.prefs.reducedMotion ? 150 : 600, (u) => (this.world.alpha = u));
  }

  /** Launch: Ace welcomes the player (once, after the start screen). */
  welcome() {
    void this.aceSay(this.t.aceHello, 1600);
  }

  // ---------------------------------------------------------------- layout
  layout() {
    const w = this.app.screen.width;
    const h = this.app.screen.height;
    this.portrait = h > w * 1.05;
    // background: cover
    const key = this.portrait ? 'portrait' : 'landscape';
    const L = LAYERS[key];
    this.sky.texture = this.tex[`bg_${key}`];
    this.crowd.texture = this.tex[`crowd_${key}`];
    this.fore.texture = this.tex[`fore_${key}`];
    this.flags.texture = this.tex[`flags_${key}`];
    for (const sp of [this.sky, this.crowd, this.fore, this.flags]) sp.scale.set(L.width / sp.texture.width);
    this.crowd.y = L.crowdY;
    this.fore.y = L.foreY;
    this.flags.y = L.flagsY;
    this.layerBase = { crowdY: L.crowdY };
    const bs = Math.max(w / L.width, h / L.height);
    this.bg.scale.set(bs);
    this.bg.position.set((w - L.width * bs) / 2, (h - L.height * bs) / 2);

    // play area between the DOM top bar and HUD
    const padX = Math.max(8, Math.round(w * 0.015));
    const top = this.insets.top + 4;
    const bottom = this.insets.bottom + 6;
    const left = (this.insets.left ?? 0) + padX;
    const right = (this.insets.right ?? 0) + padX;
    const aw = w - left - right;
    const cx = left + aw / 2;
    const ah = Math.max(120, h - top - bottom);
    const gap = Math.round(clamp(ah * 0.015, 4, 14));
    const minHead = this.portrait ? clamp(ah * 0.12, 48, 110) : clamp(ah * 0.11, 40, 96);
    const plateR = PLATE_H / 2 + 2;
    let s = Math.min(aw / FRAME_W, (ah - minHead - gap) / (FRAME_H + plateR));
    if (!this.portrait) s = Math.min(s, (aw * 0.8) / FRAME_W);
    const bw = FRAME_W * s, bh = (FRAME_H + plateR) * s;
    const maxHead = this.portrait ? aw * 0.36 : clamp(ah * 0.2, 60, 190);
    const headH = clamp(ah - bh - gap, minHead, maxHead);
    const blockH = headH + gap + bh;
    const y0 = top + Math.max(0, (ah - blockH) / 2);
    this.board.scale.set(s);
    this.board.position.set(cx - bw / 2, y0 + headH + gap);
    // header box
    const headW = Math.min(aw, Math.max(bw, headH * 3));
    const hx = cx, hy = y0 + headH / 2;
    this.header.position.set(hx, hy);
    const ls = Math.min((headW * 0.92) / this.tex.logo.width, (headH * 0.98) / this.tex.logo.height);
    this.logo.scale.set(ls);
    this.logoMask.scale.set(ls);
    this.headerBox = { x: hx, y: hy, w: headW, h: headH };
    // Tie-Break panel placement
    const gutter = Math.min(this.board.x - left, w - right - (this.board.x + bw));
    if (!this.portrait && gutter >= 220) {
      this.buildTieBreakPanel('tall');
      const ps = Math.min((gutter * 0.86) / 300, (FRAME_H * s * 0.92) / 560, 1.3);
      this.tb.scale.set(ps);
      this.tb.position.set(this.board.x + bw + gutter / 2, this.board.y + (FRAME_H * s) / 2);
      this.panelInHeader = false;
    } else {
      this.buildTieBreakPanel(headW / headH >= 4.4 ? 'wide' : 'compact');
      const [PW, PH] = this.tbVariant === 'wide' ? [1000, 200] : [640, 196];
      this.tb.scale.set(Math.min(headW / PW, headH / PH));
      this.tb.position.set(hx, hy);
      this.panelInHeader = true;
    }
    if (this.mode === 'freegame') {
      this.tb.visible = true;
      this.logo.visible = !this.panelInHeader;
    }
    if (this.mpText) this.fitMatchPoint();
    this.layoutInfo = {
      board: { x: this.board.x, y: this.board.y, w: bw, h: FRAME_H * s },
      header: { x: hx - headW / 2, y: y0, w: headW, h: headH },
      portrait: this.portrait,
    };
    this.onLayout?.(this.layoutInfo);
    for (const o of this.overlay.children) (o as Container & { relayout?: () => void }).relayout?.();
    if (this.ace.visible) {
      const home = this.aceHome();
      this.ace.position.set(home.x, home.y);
      this.ace.scale.set(home.scale);
    }
    this.drawFrameLight();
  }

  private drawFrameLight() {
    const g = this.frameLight.clear();
    for (let i = 0; i < 4; i++) {
      const o = 8 + i * 10;
      const sup = this.level === 'super';
      g.roundRect(-o, -o, FRAME_W + 2 * o, FRAME_H + 2 * o, 24 + o).stroke({
        color: i === 0 ? (sup ? 0xfff3c8 : C.gold) : sup ? 0x37b6ff : C.tennis,
        width: i === 0 ? 4 : 8,
        alpha: i === 0 ? 0.95 : (sup ? 0.3 : 0.16) - i * 0.04,
      });
    }
  }

  // ---------------------------------------------------------------- per-frame
  private update(tk: Ticker) {
    const dt = tk.deltaMS / 1000;
    const rm = this.prefs.reducedMotion;
    this.time += dt;
    // ambience blend (night match ↔ Tie-Break): cooler stadium, brighter floodlights
    const target = this.mode === 'freegame' ? 1 : 0;
    this.bonusMix += clamp(target - this.bonusMix, -dt * 1.2, dt * 1.2);
    const k = this.bonusMix;
    const sup = this.level === 'super';
    // Tie-Break: warmer emerald/gold night; Super Tie-Break: electric blue + white gold
    this.sky.tint = lerpColor(0xffffff, sup ? 0x5f8cff : 0xc9d8b8, k);
    this.crowd.tint = lerpColor(0xffffff, sup ? 0x5878d8 : 0xb7c79a, k);
    this.fore.tint = lerpColor(0xffffff, sup ? 0x8fb8f0 : 0xd8e8c0, k);
    this.frameLight.alpha = k * (rm ? 1 : 0.85 + 0.15 * Math.sin(this.time * 2));
    if (!rm) {
      const jump = this.cheerAmp > 0 ? -Math.abs(Math.sin(this.time * 9)) * 18 * this.cheerAmp : 0;
      this.crowd.y = this.layerBase.crowdY + Math.sin(this.time * 2.2) * 1.5 + jump;
      this.cheerAmp = Math.max(0, this.cheerAmp - dt * 0.35);
      // floodlight beams breathe slowly
      this.flags.alpha = (0.6 + 0.2 * Math.sin(this.time * 0.7)) * (1 + 0.6 * k);
      // occasional camera flashes in the stands (more when the crowd cheers)
      const L = LAYERS[this.portrait ? 'portrait' : 'landscape'];
      if (Math.random() < (0.02 + this.cheerAmp * 0.4) * dt * 60) {
        const fl = new Sprite(this.tex.sparkle);
        fl.anchor.set(0.5);
        fl.blendMode = 'add';
        fl.scale.set(0.2 + Math.random() * 0.25);
        fl.position.set(Math.random() * L.width, L.crowdY + 40 + Math.random() * (L.crowdH - 90));
        this.flashLayer.addChild(fl);
        this.flashes.push({ s: fl, life: 0 });
      }
      if (this.mpText) this.mpText.scale.set(((this.mpText as Text & { base?: number }).base ?? 1) * (1 + 0.04 * Math.sin(this.time * 8)));
      // logo: a light sweep every few seconds (base game only)
      this.nextShine -= dt;
      if (this.nextShine <= 0 && this.logo.visible) {
        this.nextShine = 7 + Math.random() * 3;
        this.sweepLogo();
      }
    } else {
      this.crowd.y = this.layerBase.crowdY;
      this.flags.alpha = 0.7;
    }
    for (let i = this.flashes.length - 1; i >= 0; i--) {
      const fl = this.flashes[i];
      fl.life += dt;
      fl.s.alpha = Math.max(0, 1 - fl.life / 0.16);
      if (fl.life > 0.16) {
        fl.s.destroy();
        this.flashes.splice(i, 1);
      }
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
    const w = this.app.screen.width;
    const h = this.app.screen.height;
    for (const d of this.dust) {
      d.s.visible = !rm;
      if (rm) continue;
      d.s.x += d.vx * dt;
      d.s.y += d.vy * dt;
      d.life += dt;
      d.s.alpha = 0.12 + 0.12 * Math.sin(d.life * 1.3 + d.spin);
      if (d.s.y < -20) {
        d.s.y = h + 20;
        d.s.x = Math.random() * w;
      }
    }
  }

  private sweepLogo() {
    const g = this.logoShine;
    const lw = this.tex.logo.width, lh = this.tex.logo.height;
    g.clear().poly([-60, -lh / 2, 30, -lh / 2, -40, lh / 2, -130, lh / 2]).fill({ color: 0xfff3d0, alpha: 0.55 });
    g.scale.set(this.logo.scale.x);
    void this.tw.tween(1100, (u) => (g.x = (-lw / 2 + (lw + 200) * u) * this.logo.scale.x), ease.inOutCubic).then(() => g.clear());
  }

  private spawnDust() {
    for (let i = 0; i < 26; i++) {
      const s = new Sprite(this.tex.glow);
      s.anchor.set(0.5);
      s.scale.set(0.05 + Math.random() * 0.08);
      s.blendMode = 'add';
      s.tint = 0xf2e5c3;
      s.x = Math.random() * 1920;
      s.y = Math.random() * 1920;
      this.dustLayer.addChild(s);
      this.dust.push({ s, vx: (Math.random() - 0.5) * 6, vy: -4 - Math.random() * 8, g: 0, life: Math.random() * 10, max: 1e9, spin: Math.random() * 6 });
    }
  }

  private burst(x: number, y: number, n: number, texName = 'sparkle', parent: Container = this.fx, opts: { speed?: number; g?: number; life?: number; scale?: number } = {}) {
    if (this.prefs.reducedMotion) n = Math.ceil(n / 4);
    for (let i = 0; i < n; i++) {
      const s = new Sprite(this.tex[texName]);
      s.anchor.set(0.5);
      s.scale.set((opts.scale ?? 0.5) * (0.5 + Math.random()));
      s.blendMode = texName.startsWith('ui_') ? 'normal' : 'add';
      s.position.set(x, y);
      parent.addChild(s);
      const a = Math.random() * Math.PI * 2;
      const sp = (opts.speed ?? 260) * (0.3 + Math.random());
      this.particles.push({ s, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - (opts.g ? 300 : 0), g: opts.g ?? 0, life: 0, max: (opts.life ?? 0.9) * (0.6 + Math.random() * 0.6), spin: (Math.random() - 0.5) * 6 });
    }
  }

  /** centre of a visible cell in screen coordinates */
  private cellWorld(reel: number, row: number) {
    const sc = this.board.scale.x;
    return { x: this.board.x + (FRAME_M + reel * CELL + CELL / 2) * sc, y: this.board.y + (FRAME_M + row * CELL + CELL / 2) * sc };
  }

  /** short floating text (presentation only) */
  private callout(text: string, x: number, y: number, size: number) {
    const t = this.goldText(text, size);
    t.position.set(x, y);
    this.fx.addChild(t);
    void this.tw.tween(this.prefs.reducedMotion ? 500 : 1100, (u) => {
      t.y = y - 40 * u;
      t.alpha = u < 0.7 ? 1 : 1 - (u - 0.7) / 0.3;
      t.scale.set(this.prefs.reducedMotion ? 1 : 0.7 + 0.3 * ease.outBack(Math.min(1, u * 3)));
    }).then(() => t.destroy());
  }

  /** crowd celebration (presentation only) */
  cheer(strength = 1) {
    this.cheerAmp = Math.min(1.5, Math.max(this.cheerAmp, strength));
  }

  private squash(reel: Reel) {
    if (this.prefs.reducedMotion) return;
    const base = SYM_SIZE / reel.sprites[0].texture.width;
    void this.tw.tween(240, (u) => {
      const k = u < 0.4 ? 1 - 0.06 * (u / 0.4) : 0.94 + 0.06 * ease.outElastic((u - 0.4) / 0.6);
      for (const sp of reel.sprites) {
        sp.scale.y = base * k;
        sp.scale.x = base * (2 - k);
      }
    });
  }

  // ---------------------------------------------------------------- View API
  /** Bonus level being played ('super' = Super Tie-Break look). */
  level: BonusLevel = 'tiebreak';

  setMode(mode: GameType, level: BonusLevel | null = null) {
    if (mode === 'freegame' && level && level !== this.level) {
      this.level = level;
      const v = this.tbVariant;
      this.tbVariant = null;
      if (v) this.buildTieBreakPanel(v);
      this.drawFrameLight();
    }
    if (mode === this.mode) return;
    this.mode = mode;
    const toBonus = mode === 'freegame';
    // Tie-Break panel fades in (replacing the logo when it lives in the header)
    const fadeLogo = this.panelInHeader;
    this.tb.visible = true;
    this.logo.visible = true;
    this.logoShine.clear();
    const d = this.prefs.reducedMotion ? 120 : 500;
    void this.tw.tween(d, (u) => {
      this.tb.alpha = toBonus ? u : 1 - u;
      if (fadeLogo) this.logo.alpha = toBonus ? 1 - u : u;
    }).then(() => {
      this.tb.visible = toBonus;
      this.tb.alpha = 1;
      this.logo.alpha = 1;
      this.logo.visible = !(toBonus && this.panelInHeader);
    });
    if (!toBonus) this.setBonusInfo(0, 0, 1, 0);
    audio.setMusic(toBonus ? 'music_free' : 'music_base');
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

  async spinTo(_board: Board, stops: number[], gameType: GameType, anticipation: number[], quick: boolean, betMode: ModeName = 'base') {
    // the stops index the reel set of the round's bet mode
    const strips = gameType === 'freegame' ? STRIPS.free : betMode === 'bonus_chance' ? STRIPS.bonusChance : STRIPS.base;
    const rm = this.prefs.reducedMotion;
    const turbo = this.prefs.turbo;
    const baseT = quick ? 260 : rm ? 420 : turbo ? 650 : gameType === 'freegame' ? 900 : 1050;
    const stagger = quick ? 40 : rm ? 60 : turbo ? 90 : 160;
    const antExtra = quick || rm ? 0 : turbo ? 600 : 1300;
    if (!quick) {
      audio.play('spin_start', { volume: 0.7 });
      audio.startLoop('spin_loop', 0.45);
    }
    let landedScatters = 0;
    let antOn = false;
    const tasks = this.reels.map(async (reel, r) => {
      const ant = anticipation[r] === 1;
      let extraBefore = 0;
      for (let k = 0; k <= r; k++) if (anticipation[k]) extraBefore += antExtra;
      const T = baseT + r * stagger + extraBefore;
      // short wind-up (reel lifts slightly) — skipped in reduced motion
      const start = reel.pos;
      if (!rm && !quick) await this.tw.tween(100, (u) => { reel.pos = start + 0.2 * u; reel.render(); }, ease.outCubic);
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
      const easing = rm ? ease.outCubic : (u: number) => ease.outBack(u, 0.45);
      await this.tw.tween(T, (u) => {
        reel.pos = s0 - D * easing(u);
        const speed = Math.abs(last - reel.pos);
        last = reel.pos;
        reel.blur.strengthY = Math.min(14, speed * 28);
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
        audio.play('reel_stop', { volume: 0.5, rate: 0.96 + r * 0.02 });
        this.squash(reel);
        const col = Array.from({ length: NROWS }, (_, row) => reel.strip[(stops[r] + row) % n]);
        if (col.includes('S')) {
          landedScatters++;
          audio.play(`scatter_${Math.min(3, landedScatters)}` as 'scatter_1', { volume: 0.7 });
          const row = col.indexOf('S');
          const p = this.cellWorld(r, row);
          this.burst(p.x, p.y, 10, 'sparkle', this.fx, { speed: 160, life: 0.6, scale: 0.35 });
          this.pulse(reel.cell(row), 1.1, 380);
        }
        if (col.includes('W')) {
          audio.play('wild_land', { volume: 0.45 });
          this.pulse(reel.cell(col.indexOf('W')), 1.08, 320);
        }
      }
    });
    await Promise.all(tasks);
    this.hideAnticipation();
    audio.stopLoop('spin_loop');
  }

  private showAnticipation(fromReel: number) {
    // MATCH POINT: 2 Centre Court symbols already landed (the outcome is already
    // fixed; this only stages the reveal of the remaining reels)
    if (!this.mpText) {
      const t = this.goldText(this.t.matchPoint, 72);
      this.world.addChild(t);
      this.mpText = t;
      this.fitMatchPoint();
      this.header.alpha = 0.12;
      this.cheer(0.4);
      audio.play('match_point', { volume: 0.8 });
    }
    const g = this.antGfx;
    g.clear();
    for (let r = fromReel; r < NR; r++) g.roundRect(FRAME_M + r * CELL + 5, FRAME_M + 5, CELL - 10, NROWS * CELL - 10, 16).stroke({ color: C.tennis, width: 4, alpha: 0.95 });
    g.alpha = 0;
    void this.tw.tween(250, (u) => (g.alpha = u));
  }

  private hideAnticipation() {
    this.antGfx.clear();
    if (this.mpText) {
      this.mpText.destroy();
      this.mpText = null;
    }
    this.header.alpha = 1;
  }

  /** MATCH POINT callout sits in the header band, never over the reels. */
  private fitMatchPoint() {
    const t = this.mpText!;
    const H = this.headerBox;
    t.scale.set(1);
    const k = Math.min((H.w * 0.9) / t.width, (H.h * 0.8) / t.height);
    t.scale.set(k);
    (t as Text & { base?: number }).base = k;
    t.position.set(H.x, H.y);
  }

  private pulse(s: Sprite, k: number, ms: number) {
    if (this.prefs.reducedMotion) return;
    const base = SYM_SIZE / s.texture.width;
    void this.tw.tween(ms, (u) => s.scale.set(base * (1 + (k - 1) * Math.sin(u * Math.PI))));
  }

  private setPlate(text: string) {
    this.winText.text = text;
    this.plate.visible = !!text;
    if (!text) return;
    const w = Math.max(320, this.winText.width + 80);
    this.plateBg.clear()
      .roundRect(-w / 2, -PLATE_H / 2, w, PLATE_H, PLATE_H / 2).fill({ color: C.night, alpha: 0.94 }).stroke({ color: C.gold, width: 3 })
      .roundRect(-w / 2 + 6, -PLATE_H / 2 + 6, w - 12, PLATE_H - 12, PLATE_H / 2 - 6).stroke({ color: C.cream, width: 1, alpha: 0.25 });
  }

  clearWins() {
    this.clearGroupGfx();
    this.setPlate('');
    for (const r of this.reels) for (const s of r.sprites) {
      s.alpha = 1;
      s.rotation = 0;
      s.tint = 0xffffff;
      s.width = s.height = SYM_SIZE;
    }
  }

  /** Colour of each symbol's connection (its dominant colour in the art). */
  private static SYM_COLOR: Record<string, number> = {
    W: 0xff3fb4, S: 0x37b6ff, H1: 0xe8a74a, H2: 0xf2c54b, H3: 0x8fb0ff, H4: 0xdfe4ec,
    L1: 0xd4e948, L2: 0x7fb2ff, L3: 0xff8a4c, L4: 0x2f8cff, L5: 0xff4d5e,
  };

  private symName(sym: string) {
    const info = RULES.symbolInfo[sym as SymbolName];
    return info ? (this.lang === 'fr' ? info.fr : info.label) : sym;
  }

  /**
   * Draws one winning combination exactly as returned by the engine:
   * frames on its symbols (reel 1 .. reel k), a connector from reel 1 to the
   * last reel through the matched cells, and the per-reel counts whose
   * product is the number of ways.  Static: readable without animation.
   */
  private drawGroup(w: WinLine, alpha = 1, connector = true) {
    const g = this.lineGfx;
    const color = RallyScene.SYM_COLOR[w.symbol] ?? C.gold;
    const cx = (r: number) => r * CELL + CELL / 2;
    const cy = (row: number) => row * CELL + CELL / 2;
    for (const p of w.positions) {
      const x = p.reel * CELL + 6, y = p.row * CELL + 6, sz = CELL - 12;
      g.roundRect(x, y, sz, sz, 22).stroke({ color: 0x081b23, width: 9, alpha: alpha * 0.8 });
      g.roundRect(x, y, sz, sz, 22).stroke({ color, width: 5, alpha });
    }
    if (w.kind !== 'ways' || !connector) return;
    const reels = Array.from({ length: w.count }, (_, r) => w.positions.filter((p) => p.reel === r).map((p) => p.row));
    const hub = reels.map((rows) => rows.reduce((a, x) => a + x, 0) / rows.length);
    const path = (width: number, col: number, a: number) => {
      g.moveTo(cx(0) - CELL * 0.42, cy(hub[0]));
      reels.forEach((_, r) => g.lineTo(cx(r), cy(hub[r])));
      g.stroke({ color: col, width, alpha: a, cap: 'round', join: 'round' });
      reels.forEach((rows, r) => rows.forEach((row) => {
        if (row === hub[r]) return;
        g.moveTo(cx(r), cy(hub[r])).lineTo(cx(r), cy(row) + (row < hub[r] ? CELL * 0.3 : -CELL * 0.3));
        g.stroke({ color: col, width: width * 0.7, alpha: a, cap: 'round' });
      }));
    };
    path(14, 0x081b23, alpha * 0.55);
    path(6, color, alpha);
    // start marker (reel 1) and end cap (last reel of the combination)
    const sx = cx(0) - CELL * 0.42, sy = cy(hub[0]);
    g.poly([sx - 14, sy - 16, sx + 12, sy, sx - 14, sy + 16]).fill({ color, alpha }).stroke({ color: 0x081b23, width: 3, alpha });
    g.circle(cx(w.count - 1), cy(hub[w.count - 1]), 10).fill({ color, alpha }).stroke({ color: 0x081b23, width: 3, alpha });
    // per-reel counts in the top margin of the frame (product = ways)
    reels.forEach((rows, r) => {
      g.roundRect(cx(r) - 22, -FRAME_M + 2, 44, FRAME_M - 4, 12).fill({ color, alpha: alpha * 0.95 });
    });
    for (const [r, rows] of reels.entries()) {
      const t = new Text({ text: String(rows.length), style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 22, fill: '#081B23' } });
      t.anchor.set(0.5);
      t.position.set(cx(r), -FRAME_M / 2);
      t.alpha = alpha;
      this.badgeLayer.addChild(t);
    }
  }

  private groupLabel(w: WinLine) {
    const amt = money(Math.round((this.bet * w.win) / 100), this.currency, this.lang);
    if (w.kind === 'scatter') return `${w.count} × ${this.symName('S')} · ${amt}`;
    const per = Array.from({ length: w.count }, (_, r) => w.positions.filter((p) => p.reel === r).length);
    const ways = `${per.join('×')} = ${w.ways} ${w.ways === 1 ? this.t.wayOne : this.t.ways}`;
    const reels = fmtS(this.t.reelsN, { n: w.count });
    return `${this.symName(w.symbol)} · ${reels} · ${ways}${w.multiplier > 1 ? ` · ×${w.multiplier}` : ''} · ${amt}`;
  }

  private setDim(active: Set<string>) {
    this.reels.forEach((reel, r) => {
      for (let row = 0; row < NROWS; row++) reel.cell(row).alpha = active.has(`${r}:${row}`) ? 1 : 0.32;
    });
  }

  /** Last displayed wins (for the "show wins again" button). */
  lastWins: { wins: WinLine[]; multiplier: number } | null = null;

  async showWins(wins: WinLine[], multiplier: number, tier: WinTier) {
    this.lastWins = { wins, multiplier };
    // demo/QA only: lets the browser tests compare what is drawn with the book
    if (import.meta.env.VITE_ENABLE_RGS !== '1') (window as unknown as { __rallyShownWins: unknown }).__rallyShownWins = wins.map((w) => ({ symbol: w.symbol, kind: w.kind, count: w.count, ways: w.ways, win: w.win, positions: w.positions }));
    const key = (p: Position) => `${p.reel}:${p.row}`;
    const all = new Set<string>();
    for (const w of wins) for (const p of w.positions) all.add(key(p));
    const rm = this.prefs.reducedMotion;
    // 1) all winning combinations together
    this.setDim(all);
    if (!rm) for (const k of all) {
      const [r, row] = k.split(':').map(Number);
      this.pulse(this.reels[r].cell(row), 1.06, 520);
    }
    for (const w of wins) this.drawGroup(w, 1, wins.length === 1);
    const total = wins.reduce((a, w) => a + w.win, 0);
    const amt = Math.round((this.bet * total) / 100);
    const totalLabel = (multiplier > 1 ? `×${multiplier} · ` : '') + money(amt, this.currency, this.lang);
    this.setPlate(wins.length === 1 ? this.groupLabel(wins[0]) : totalLabel);
    // sound: wins not exceeding the bet are not celebrated
    if (tier === 'ldw') audio.play('line_tick', { volume: 0.35 });
    else if (tier === 'small') audio.play(amt / this.bet >= 3 ? 'win_1' : 'win_0', { volume: 0.7 });
    else if (tier !== 'none') audio.play('win_2', { volume: 0.8 });
    if (tier !== 'ldw' && tier !== 'none') audio.play('racket', { volume: 0.5 });
    const free = this.mode === 'freegame';
    await this.tw.wait(wins.length === 1 ? (free ? 900 : 1200) : 800);
    if (wins.length === 1 || this.prefs.turbo) return;
    // 2) each combination on its own: its symbols, connector, counts and amount
    const each = free ? 1000 : 1150;
    for (const w of wins.slice(0, free ? 4 : 8)) {
      this.clearGroupGfx();
      this.setDim(new Set(w.positions.map(key)));
      this.drawGroup(w);
      this.setPlate(this.groupLabel(w));
      await this.tw.wait(each);
    }
    // 3) back to all together, with the total
    this.clearGroupGfx();
    this.setDim(all);
    for (const w of wins) this.drawGroup(w, 0.85, false);
    this.setPlate(totalLabel);
  }

  private clearGroupGfx() {
    this.lineGfx.clear();
    this.glowLayer.removeChildren().forEach((c) => c.destroy());
    this.badgeLayer.removeChildren().forEach((c) => c.destroy());
  }

  /** Shows the last wins again (button "show wins"); visual only. */
  async replayWins() {
    if (!this.lastWins) return;
    this.clearWins();
    await this.showWins(this.lastWins.wins, this.lastWins.multiplier, 'none');
  }

  async scatterCelebrate(positions: Position[]) {
    for (const p of positions) {
      const s = this.reels[p.reel].cell(p.row);
      this.pulse(s, 1.15, 700);
      const c = this.cellWorld(p.reel, p.row);
      this.burst(c.x, c.y, 14, 'sparkle', this.fx, { speed: 200, life: 0.8, scale: 0.4 });
    }
    await this.tw.wait(500);
  }

  // ---------------------------------------------------------------- overlays
  private makeOverlay(): Container & { relayout?: () => void } {
    const c = new Container() as Container & { relayout?: () => void };
    const veil = new Graphics();
    c.addChild(veil);
    c.relayout = () => {
      veil.clear().rect(0, 0, this.app.screen.width, this.app.screen.height).fill({ color: C.night, alpha: 0.78 });
      const inner = c.children[1] as Container | undefined;
      if (inner) {
        // fit between the top bar and the HUD so no text runs under the controls
        const dw = this.portrait ? 720 : 1100;
        const il = this.insets.left ?? 0, ir = this.insets.right ?? 0;
        const aw = this.app.screen.width - il - ir;
        const ah = Math.max(200, this.app.screen.height - this.insets.top - this.insets.bottom);
        const s = Math.min(aw / dw, ah / 820);
        inner.scale.set(s);
        inner.position.set(il + aw / 2, this.insets.top + ah / 2);
      }
    };
    c.addChild(new Container());
    this.overlay.addChild(c);
    c.relayout();
    return c;
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
      if (!this.prefs.reducedMotion) inner.scale.set(s0 * (0.92 + 0.08 * ease.outCubic(u)));
    });
    inner.scale.set(s0);
    await hold();
    await this.tw.tween(outMs, (u) => (c.alpha = 1 - u));
    c.destroy({ children: true });
  }

  private superText(text: string, size: number) {
    const t = new Text({
      text,
      style: {
        fontFamily: 'Cinzel', fontWeight: '700', fontSize: size, align: 'center', letterSpacing: size / 14,
        fill: new FillGradient({ type: 'linear', start: { x: 0, y: 0 }, end: { x: 0, y: 1 }, textureSpace: 'local',
          colorStops: [{ offset: 0, color: '#FFFFFF' }, { offset: 0.5, color: '#FFF3C8' }, { offset: 0.56, color: '#8FD3FF' }, { offset: 1, color: '#FFFFFF' }] }),
        stroke: { color: '#0B1F4A', width: Math.max(4, size / 11), join: 'round' },
        dropShadow: { color: '#37B6FF', alpha: 0.8, blur: size / 4, distance: 0 },
      },
    });
    t.anchor.set(0.5);
    return t;
  }

  /** Ace's Super Tie-Break entrance: jump, full turn and a burst of balls (visual only). */
  private async aceSuper() {
    if (this.prefs.reducedMotion) return this.aceSay(this.t.aceSuper, 900);
    const w = this.app.screen.width, h = this.app.screen.height;
    const size = clamp(Math.min(w, h) * 0.26, 110, 240);
    const a = this.ace;
    a.visible = true;
    a.alpha = 1;
    a.scale.set(size / 240);
    this.aceBubble.visible = false;
    const y0 = h - this.insets.bottom + size, yTop = this.insets.top + (h - this.insets.top - this.insets.bottom) * 0.42;
    audio.play('pop', { volume: 0.5 });
    await this.tw.tween(700, (u) => {
      a.position.set(w / 2, y0 + (yTop - y0) * ease.outBack(u, 0.8));
      a.rotation = Math.PI * 2 * ease.inOutCubic(u);
    });
    a.rotation = 0;
    for (let i = 0; i < 3; i++) this.burst(w / 2, yTop, 1, 'ui_golden_ball', this.aceLayer, { speed: 420, life: 1.1, scale: 0.12 });
    this.burst(w / 2, yTop, 30, 'sparkle', this.aceLayer, { speed: 360, life: 1, scale: 0.5 });
    await this.tw.wait(500);
    await this.tw.tween(380, (u) => a.position.set(w / 2, yTop + (y0 - yTop) * ease.inCubic(u)));
    a.visible = false;
  }

  async bonusIntro(spins: number, level: BonusLevel = 'tiebreak', startMultiplier = 1, _bought = false) {
    const sup = level === 'super';
    this.cheer(sup ? 1.5 : 1.2);
    audio.play('bonus_trigger', { volume: 0.9 });
    // Ace brings the ball (Tie-Break) or makes his Super entrance (transition only)
    if (!sup) await this.aceSay(this.t.aceBonus, 200, true);
    audio.play('tiebreak', { volume: 0.8, rate: sup ? 1.12 : 1 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    if (sup) {
      const halo = new Sprite(this.tex.glow);
      halo.anchor.set(0.5);
      halo.blendMode = 'add';
      halo.tint = 0x37b6ff;
      halo.width = halo.height = 760;
      halo.alpha = 0.55;
      halo.y = -190;
      inner.addChild(halo);
    }
    const emblem = new Sprite(this.tex.ui_tiebreak);
    emblem.anchor.set(0.5);
    emblem.width = emblem.height = sup ? 300 : 360;
    emblem.y = sup ? -150 : -200;
    inner.addChild(emblem);
    if (sup) {
      const t = this.superText(this.t.stbTitle, 76);
      t.y = -330;
      this.fit(t, 680);
      inner.addChild(t);
    }
    const num = sup ? this.superText(String(spins), 130) : this.goldText(String(spins), 150);
    num.y = 60;
    const lbl = this.plainText(this.t.freeSpins.toUpperCase(), 34, sup ? '#8FD3FF' : '#D5A64B', '800');
    lbl.y = 150;
    const sub = this.plainText(sup ? fmtS(this.t.bonusIntroSubSuper, { m: startMultiplier }) : this.t.bonusIntroSub, 24);
    sub.y = 240;
    const tap = this.plainText(this.t.tapToContinue, 20, '#D4E948', '700');
    tap.y = 350;
    inner.addChild(num, lbl, sub, tap);
    c.relayout?.();
    await this.fadeOverlay(c, 380, 300, async () => {
      this.burst(this.app.screen.width / 2, this.app.screen.height / 2, sup ? 44 : 28, 'sparkle', this.overlay, { speed: 380, life: 1.1, scale: 0.5 });
      // Super: Ace's entrance plays over the introduction screen, never over the reels
      if (sup) void this.aceSuper();
      await this.waitTapOr(3800);
    });
  }

  async wind(positions: Position[], _collected: number, multiplier: number, previous: number) {
    // energy flies from each wild to the multiplier on the Tie-Break panel
    const target = this.tbMultCell.getGlobalPosition();
    const flights = positions.map(async (p, i) => {
      const s = this.reels[p.reel].cell(p.row);
      this.pulse(s, 1.14, 500);
      const from = this.cellWorld(p.reel, p.row);
      const orb = new Sprite(this.tex.ui_golden_ball);
      orb.anchor.set(0.5);
      orb.width = orb.height = clamp(CELL * this.board.scale.x * 0.5, 28, 80);
      this.fx.addChild(orb);
      orb.position.set(from.x, from.y);
      await this.tw.wait(i * 110);
      const ctrl = { x: (from.x + target.x) / 2 + 60, y: Math.min(from.y, target.y) - 120 };
      await this.tw.tween(this.prefs.reducedMotion ? 150 : 520, (u) => {
        const x = (1 - u) ** 2 * from.x + 2 * (1 - u) * u * ctrl.x + u * u * target.x;
        const y = (1 - u) ** 2 * from.y + 2 * (1 - u) * u * ctrl.y + u * u * target.y;
        orb.position.set(x, y);
        orb.rotation += 0.3;
      }, ease.inOutCubic);
      orb.destroy();
    });
    audio.play('racket', { volume: 0.7 });
    await Promise.all(flights);
    if (multiplier !== previous) {
      const bc = { x: this.board.x + (FRAME_W * this.board.scale.x) / 2, y: this.board.y + (FRAME_H * this.board.scale.y) / 2 };
      this.callout(fmtS(this.t.rallyCall, { m: multiplier }), bc.x, bc.y, clamp(110 * this.board.scale.x, 28, 72));
      audio.play('mult_up', { volume: 0.8 });
      this.burst(target.x, target.y, 18, 'sparkle', this.fx, { speed: 200, life: 0.7, scale: 0.4 });
    }
  }

  async retrigger(added: number, _total: number) {
    audio.play('bonus_trigger', { volume: 0.6 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const t1 = this.goldText(`+${added}`, 160);
    t1.y = -40;
    const t2 = this.fit(this.plainText(this.t.retrigger, 40, '#F2E5C3', '800'));
    t2.y = 100;
    inner.addChild(t1, t2);
    c.relayout?.();
    await this.fadeOverlay(c, 300, 260, () => this.waitTapOr(1500));
  }

  private async countUp(text: Text, amount: number, ms: number, skip: { now: boolean }) {
    let lastTick = 0;
    await this.tw.tween(ms, (u) => {
      const v = skip.now ? amount : Math.round(amount * u);
      text.text = money(v, this.currency, this.lang);
      if (u - lastTick > 0.05 && u < 1 && !skip.now) {
        lastTick = u;
        audio.play('count_tick', { volume: 0.2 });
      }
    }, ease.outCubic);
    text.text = money(amount, this.currency, this.lang);
  }

  /** Final Tie-Break recap: spins played, final multiplier, total win (all from the book). */
  async bonusOutro(amount: number) {
    audio.play('bonus_end', { volume: 0.8 });
    const info = this.bonusInfo;
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const card = new Graphics()
      .roundRect(-340, -300, 680, 600, 30).fill({ color: this.level === 'super' ? 0x0b1f4a : C.emerald, alpha: 0.96 }).stroke({ color: this.level === 'super' ? 0x37b6ff : C.gold, width: 3 })
      .roundRect(-326, -286, 652, 572, 22).stroke({ color: C.cream, width: 1, alpha: 0.25 });
    const kicker = new Text({ text: 'GOLDEN RALLY', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 26, fill: '#D5A64B', letterSpacing: 8 } });
    kicker.anchor.set(0.5);
    kicker.y = -240;
    const title = this.level === 'super' ? this.fit(this.superText(this.t.bonusEndSuper, 44), 600) : this.fit(this.goldText(this.t.bonusEnd, 46), 600);
    title.y = -180;
    const l1 = this.plainText(fmtS(this.t.recapSpins, { n: info.cur || info.total }), 30);
    l1.y = -90;
    const l2 = this.plainText(fmtS(this.t.recapMult, { m: info.mult }), 30);
    l2.y = -40;
    const sub = this.plainText(this.t.totalWin.toUpperCase(), 28, '#D5A64B', '800');
    sub.y = 40;
    const amt = this.goldText(money(0, this.currency, this.lang), 96);
    amt.y = 130;
    const tap = this.plainText(this.t.tapToContinue, 20, '#D4E948', '700');
    tap.y = 240;
    inner.addChild(card, kicker, title, l1, l2, sub, amt, tap);
    c.relayout?.();
    const skip = { now: false };
    void this.aceSay(this.t.aceEnd, 1800);
    await this.fadeOverlay(c, 350, 300, async () => {
      this.onOverlayTap = () => (skip.now = true);
      await this.countUp(amt, amount, 1600, skip);
      await this.waitTapOr(2600);
    });
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
    halo.tint = 0xd5a64b;
    halo.width = halo.height = 820;
    halo.alpha = 0.35;
    const t1 = this.fit(this.goldText(title, 104), 660);
    t1.y = -90;
    const amt = this.goldText(money(0, this.currency, this.lang), 96);
    amt.y = 110;
    inner.addChild(halo, t1, amt);
    c.relayout?.();
    const skip = { now: false };
    const dur = tier === 'epic' ? 5200 : tier === 'mega' ? 3800 : 2600;
    let showering = true;
    const shower = async () => {
      while (showering && !this.prefs.reducedMotion) {
        const w = this.app.screen.width;
        this.burst(Math.random() * w, -30, 2, 'sparkle', this.overlay, { speed: 80, g: 500, life: 2, scale: 0.45 });
        await this.tw.wait(110);
      }
    };
    void shower();
    void this.aceSay(this.t.aceBig, 1600);
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
    const t = this.fit(this.goldText(this.t.winCap, 62), 660);
    inner.addChild(t);
    c.relayout?.();
    await this.fadeOverlay(c, 300, 300, () => this.waitTapOr(2200));
  }

  /** Language switch: refresh texts owned by the scene. */
  setStrings(t: Strings) {
    this.t = t;
    if (this.tbRound) this.relabelPanel();
  }

  pause(ms: number) {
    return this.tw.wait(ms);
  }
}

function lerpColor(a: number, b: number, k: number) {
  const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
  const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
  return (Math.round(ar + (br - ar) * k) << 16) | (Math.round(ag + (bg - ag) * k) << 8) | Math.round(ab + (bb - ab) * k);
}
