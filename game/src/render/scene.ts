// PixiJS presentation layer.  It only *displays* books: no outcome logic here.
// Every value shown (boards, wins, spins, multiplier, totals) is received from
// the book player, which reads it verbatim from the RGS book.
import { Application, BlurFilter, Container, FillGradient, Graphics, Sprite, Text, Texture, type Ticker } from 'pixi.js';
import { audio } from '../audio/audio';
import { STRIPS } from '../engine/engine';
import { PROTO } from '../engine/rallyPath';
import { GS } from '../engine/goldenServe';
import { Court } from './court';
import { RS as RSDATA } from '../engine/returnSpins';
import { RULES } from '../engine/rules';
import type { Board, BonusLevel, BookEvent, GameType, ModeName, Position, SymbolName, WinLine } from '../engine/types';
import { Match } from './match';
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

export const CELL = 170;
const NR = RULES.reels;
const NROWS = RULES.rows;
export const FRAME_M = 30;
export const FRAME_W = NR * CELL + 2 * FRAME_M;
export const FRAME_H = NROWS * CELL + 2 * FRAME_M;
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

/** Names of the images needed by the loading / entry scene (loaded first). */
export function introImages(_portrait?: boolean) {
  // the three provided loading assets: night stadium, loading bar, tennis ball
  return ['loading_stadium', 'loading_bar', 'loading_ball'];
}

/** Decodes the game images.  `only` restricts the set; `have` are already decoded (not decoded twice).
 *  onProgress receives the real fraction of images decoded. */
export async function loadTextures(onProgress: (p: number) => void, only?: string[], have: Record<string, Texture> = {}): Promise<Record<string, Texture>> {
  const all = Object.entries(imgs).filter(([k]) => {
    const n = k.split('/').pop()!.replace(/\.(webp|jpg)$/, '');
    return !only || only.includes(n);
  });
  const entries = all.filter(([k]) => !(k.split('/').pop()!.replace(/\.(webp|jpg)$/, '') in have));
  const out: Record<string, Texture> = { ...have };
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

  bg = new Container();
  private sky = new Sprite();
  crowd = new Sprite();
  private fore = new Sprite();
  flags = new Sprite();
  private cheerAmp = 0;
  private flashLayer = new Container();
  private flashes: { s: Sprite; life: number }[] = [];
  private mpText: Text | null = null;
  private layerBase = { crowdY: 0 };
  private time = 0;
  private bonusMix = 0; // 0 = night match, 1 = Tie-Break ambience
  world = new Container();
  private dustLayer = new Container();
  // header: logo (base game) / Tie-Break panel (free spins)
  header = new Container();
  private logo = new Sprite();
  private logoShine = new Graphics();
  private logoMask = new Sprite();
  private nextShine = 4;
  tb = new Container();
  private tbRound!: Text;
  private tbMult!: Text;
  private tbTotal!: Text;
  private tbMultCell = new Container();
  private headerBox = { x: 0, y: 0, w: 0, h: 0 };
  bonusInfo = { cur: 0, total: 0, mult: 1, win: 0 };
  // board
  board = new Container();
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
  // Rally Path prototype: path layer and its own plate (separate from the ways win)
  private rpGfx = new Graphics();
  private rpLayer = new Container();
  private rpPlate = new Container();
  private rpPlateBg = new Graphics();
  private rpText!: Text;
  /** Rally Path lab active: prototype strips + prototype panel labels (demo only). */
  proto = false;
  protoEvent = '—';
  private plate = new Container();
  private plateBg = new Graphics();
  private winText!: Text;
  // Ace, the ball-boy dog (mascot) — appears only at key moments
  aceLayer = new Container();
  ace = new Container();
  private aceBubble = new Container();
  private aceBusy = false;
  fx = new Container();
  overlay = new Container();
  private particles: Particle[] = [];
  private dust: Particle[] = [];
  private mode: GameType = 'basegame';
  portrait = false;
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
    // QA only (demo builds): __rallyTimeScale slows the presentation down for frame-by-frame captures
    const qaScale = () => (import.meta.env.VITE_ENABLE_RGS === '1' ? 1 : ((window as unknown as { __rallyTimeScale?: number }).__rallyTimeScale ?? 1));
    this.tw = new Tweener(this.app.ticker, () => (this.prefs.turbo ? 1.8 : 1) * (this.match?.skip ? 5 : 1) * qaScale());
    // presentation clock (QA): time the animations actually advanced, independent of the frame rate
    this.app.ticker.add((tk) => (this.animClock += tk.deltaMS));

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
    this.winLayer.addChild(this.glowLayer, this.lineGfx, this.badgeLayer, this.rpGfx, this.rpLayer, this.gsLayer);
    this.board.addChild(this.winLayer);
    this.match = new Match(this);
    this.board.addChild(this.match.court);
    // win plate: sits on the bottom edge of the frame, never over the symbols
    this.winText = new Text({ text: '', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 40, fill: '#F2E5C3', letterSpacing: 2, align: 'center' } });
    this.winText.anchor.set(0.5);
    this.plate.addChild(this.plateBg, this.winText);
    this.plate.position.set(FRAME_W / 2, FRAME_H);
    this.plate.visible = false;
    this.board.addChild(this.plate);
    this.rpText = new Text({ text: '', style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 44, fill: '#FFF4D6', letterSpacing: 2, align: 'center' } });
    this.rpText.anchor.set(0.5);
    this.rpPlate.addChild(this.rpPlateBg, this.rpText);
    this.rpPlate.position.set(FRAME_W / 2, 0);
    this.rpPlate.visible = false;
    this.board.addChild(this.rpPlate);

    this.world.addChild(this.header, this.board, this.tb, this.fx);
    this.app.stage.addChild(this.overlay, this.aceLayer);
    this.overlay.eventMode = 'static';
    this.app.stage.eventMode = 'static';
    this.app.stage.hitArea = this.app.screen;
    this.app.stage.on('pointertap', () => {
      if (this.mode === 'freegame' || this.rpBusy || this.court?.root.visible) this.match.skip = true; // fast-forward only: the result is fixed
    });
    this.overlay.on('pointertap', () => this.onOverlayTap?.());
    this.buildAce();
    this.court = new Court(this);
    this.court.init();
    this.app.stage.addChildAt(this.court.root, this.app.stage.getChildIndex(this.overlay));

    this.spawnDust();
    this.exposeQA();
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

  goldText(text: string, size: number) {
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

  fit(t: Text, maxW = 640) {
    if (t.width > maxW) t.scale.set(maxW / t.width);
    return t;
  }

  plainText(text: string, size: number, color = '#F2E5C3', weight: '500' | '700' | '800' = '500') {
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
    const sup = this.level === 'rally';
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
      const title = this.goldText(this.level === 'final' ? 'THE GRAND FINAL' : 'RALLY CHALLENGE', 30);
      title.y = -H / 2 + 86;
      if (title.width > W - 36) title.scale.set((W - 36) / title.width);
      this.tb.addChild(kicker, title);
      const y0 = -H / 2 + 150;
      const step = 128;
      for (let i = 1; i < 3; i++) bg.moveTo(-W / 2 + 34, y0 + i * step - 22).lineTo(W / 2 - 34, y0 + i * step - 22).stroke({ color: C.gold, width: 1.5, alpha: 0.45 });
      bg.moveTo(-W / 2 + 34, y0 - 22).lineTo(W / 2 - 34, y0 - 22).stroke({ color: C.gold, width: 1.5, alpha: 0.45 });
      cells = [mk(this.proto || this.gsMode || this.rsMode ? this.t.rpSpins : this.t.tbRound, 0, y0, W - 40), mk(this.proto || this.gsMode || this.rsMode ? this.t.rpEvent : this.t.tbPoints, 0, y0 + step, W - 40, '#D4E948'), mk(this.t.tbTotal, 0, y0 + 2 * step, W - 40)];
    } else {
      const title = this.goldText(this.level === 'final' ? 'THE GRAND FINAL' : 'RALLY CHALLENGE', variant === 'wide' ? 40 : 34);
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
      cells = [mk(this.proto || this.gsMode || this.rsMode ? this.t.rpSpins : this.t.tbRound, -W / 3, y, cw), mk(this.proto || this.gsMode || this.rsMode ? this.t.rpEvent : this.t.tbPoints, 0, y, cw, '#D4E948'), mk(this.t.tbTotal, W / 3, y, cw)];
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
    this.tbMult.text = this.proto || this.gsMode || this.rsMode ? this.protoEvent : String(i.mult);
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
    if (mult !== prevMult && mult > 0 && !this.prefs.reducedMotion && this.tw) {
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
  setIntro(on: boolean, fadeMs?: number) {
    if (on) {
      this.world.visible = false;
      return;
    }
    this.world.visible = true;
    this.world.alpha = 0;
    void this.tw.tween(fadeMs ?? (this.prefs.reducedMotion ? 150 : 600), (u) => (this.world.alpha = u));
  }

  /** Launch: Ace welcomes the player (once, after the start screen). */
  welcome() {
    void this.aceSay(this.t.aceHello, 1600);
  }

  // ---------------------------------------------------------------- layout
  layout() {
    if (this.court?.root.visible) this.court.layout();
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
      const sup = this.level === 'rally';
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
    const sup = this.level === 'rally';
    // Rally Challenge: warmer emerald/gold night; Super Tie-Break: electric blue + white gold
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

  burst(x: number, y: number, n: number, texName = 'sparkle', parent: Container = this.fx, opts: { speed?: number; g?: number; life?: number; scale?: number } = {}) {
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
  cellWorld(reel: number, row: number) {
    const sc = this.board.scale.x;
    return { x: this.board.x + (FRAME_M + reel * CELL + CELL / 2) * sc, y: this.board.y + (FRAME_M + row * CELL + CELL / 2) * sc };
  }

  /** short floating text (presentation only) */
  callout(text: string, x: number, y: number, size: number) {
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
  /** Bonus being played ('rally' = electric-blue look, 'final' = gold Grand Final). */
  level: BonusLevel = 'rally';
  match!: Match;

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
    if (!toBonus) this.setBonusInfo(0, 0, 0, 0);
    audio.setMusic(toBonus ? 'music_free' : 'music_base');
  }

  /** Shows a board immediately (initial screen / resume). */
  setBoard(stops: number[], gameType: GameType) {
    const strips = this.rsMode ? RSDATA.strips[gameType === 'freegame' ? 'free' : 'base'] : this.gsMode ? GS.strips[gameType === 'freegame' ? 'free' : 'base'] : this.proto ? PROTO.strips[gameType === 'freegame' ? 'free' : 'base'] : gameType === 'freegame' ? STRIPS.free : STRIPS.base;
    this.reels.forEach((r, i) => {
      r.strip = strips[i];
      r.pos = stops[i];
      r.render();
    });
  }

  async spinTo(_board: Board, stops: number[], gameType: GameType, anticipation: number[], quick: boolean, betMode: ModeName = 'base') {
    // the stops index the reel set of the round's bet mode
    const strips = this.rsMode ? RSDATA.strips[gameType === 'freegame' ? 'free' : 'base'] : this.gsMode ? GS.strips[gameType === 'freegame' ? 'free' : 'base'] : this.proto ? PROTO.strips[gameType === 'freegame' ? 'free' : 'base'] : gameType === 'freegame' ? STRIPS.free : betMode === 'bonus_chance' ? STRIPS.bonusChance : STRIPS.base;
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

  setPlate(text: string) {
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
    this.clearRally();
    this.clearServe();
    if (this.zoneGfx) this.clearZone();
    for (const r of this.reels) for (const s of r.sprites) {
      s.alpha = 1;
      s.rotation = 0;
      s.tint = 0xffffff;
      s.width = s.height = SYM_SIZE;
    }
  }

  /** Colour of each symbol's connection (its dominant colour in the art). */
  private static SYM_COLOR: Record<string, number> = {
    G: 0xf2cf6b, W: 0xff3fb4, S: 0x37b6ff, H1: 0xe8a74a, H2: 0xf2c54b, H3: 0x8fb0ff, H4: 0xdfe4ec,
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
  makeOverlay(): Container & { relayout?: () => void } {
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
  waitTapOr(ms: number): Promise<void> {
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

  async fadeOverlay(c: Container, inMs: number, outMs: number, hold: () => Promise<void>) {
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

  superText(text: string, size: number) {
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

  // ---------------------------------------------------------------- THE FINAL SET (delegated to the match director)
  async bonusIntro(e: Extract<BookEvent, { type: 'bonusStart' }>) {
    this.cheer(1.2);
    audio.play('bonus_trigger', { volume: 0.9 });
    await this.match.intro(e);
  }
  exchangeStart(e: Extract<BookEvent, { type: 'exchangeStart' }>) {
    return this.match.exchangeStart(e);
  }
  showCourt(v: number[]) {
    return this.match.showCourt(v);
  }
  async hawkEye(e: Extract<BookEvent, { type: 'hawkEye' }>) {
    this.match.hawkEye(e);
  }
  shot(e: Extract<BookEvent, { type: 'shot' }>) {
    return this.match.shot(e);
  }
  grandSlam(e: Extract<BookEvent, { type: 'grandSlam' }>) {
    return this.match.grandSlam(e);
  }
  marksExpire(e: Extract<BookEvent, { type: 'markExpire' }>) {
    return this.match.marksExpire(e);
  }
  extraExchange(e: Extract<BookEvent, { type: 'extraExchange' }>) {
    return this.match.extraExchange(e);
  }
  exchangeEnd(e: Extract<BookEvent, { type: 'exchangeEnd' }>) {
    return this.match.exchangeEnd(e);
  }
  bonusOutro(e: Extract<BookEvent, { type: 'bonusEnd' }>, amount: number, bonusWin: number) {
    return this.match.outro(e, amount, bonusWin);
  }

  async countUp(text: Text, amount: number, ms: number, skip: { now: boolean }) {
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

  async bigWin(amount: number, tier: WinTier) {
    if (this.gsMode || this.rsMode) {
      // proportionate celebration: plate glow for 'big', Championship Point from 50x
      if (tier === 'mega' || tier === 'epic') return this.championshipPoint(amount, tier);
      this.cheer(0.8);
      audio.play('win_2', { volume: 0.7 });
      return;
    }
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

  // ---------------------------------------------------------------- CHAMPIONSHIP DUEL (court view)
  court!: Court;
  private duelTotal = 0;
  private duelSingle = false;
  async duelStart(e: Extract<BookEvent, { type: 'duelStart' }>) {
    this.duelTotal = e.points;
    this.duelSingle = !!e.single;
    if (!e.single) {
      audio.play('bonus_trigger', { volume: 0.85 });
      const c = this.makeOverlay();
      const inner = c.children[1] as Container;
      const gf = e.level === 'final';
      const t1 = this.fit(gf ? this.goldText('THE GRAND FINAL', 80) : this.superText('TIE-BREAK DUEL', 80), 680);
      t1.y = -40;
      const t2 = this.plainText(fmtS(gf ? this.t.duelIntroGf : this.t.duelIntroTb, { n: e.points }), 30, gf ? '#F4E9D4' : '#BFE6FF', '700');
      t2.y = 60;
      inner.addChild(t1, t2);
      c.relayout?.();
      await this.fadeOverlay(c, 220, 220, () => this.waitTapOr(this.prefs.reducedMotion ? 500 : 1000));
    }
    await this.court.enter(e.level, e.points);
  }
  async duelPoint(e: Extract<BookEvent, { type: 'duelPoint' }>, prize: number, bonusTotal: number) {
    this.match.skip = false;
    this.rpBusy = true;
    await this.court.playPoint(e, this.duelTotal, prize, bonusTotal, this.duelSingle);
    this.court.setBoard(e.point, this.duelTotal, bonusTotal, this.duelSingle);
    this.rpBusy = false;
  }
  async duelEnd(e: Extract<BookEvent, { type: 'duelEnd' }>, bonusWin: number, debit: number) {
    if (!this.duelSingle) await this.court.summary(bonusWin, debit);
    else await this.tw.wait(250);
    await this.court.leave();
    void e;
  }


  // ---------------------------------------------------------------- GOLDEN SERVE (prototypes A / B)
  // Presentation only: every trajectory, hit, transformation and exchange is
  // read from the goldenServe event (computed by the engine before the
  // animation).  Skipping only accelerates; the final grid is always forced to
  // the event's board, so an interrupted animation never leaves a wrong grid.
  private gsLayer = new Container();
  private boardHome: { x: number; y: number } | null = null;
  gsMode = false;
  animClock = 0;
  /** QA counters (demo build only): what the animation actually did */
  qa = { strokes: 0, hits: 0, flips: 0, swaps: 0, smash: 0 };
  private exposeQA() {
    if (import.meta.env.VITE_ENABLE_RGS === '1') return;
    const names = new Map<Texture, string>();
    for (const [k, t] of Object.entries(this.tex)) if (k.startsWith('sym_')) names.set(t, k.slice(4));
    (window as unknown as { __rallyScene: unknown }).__rallyScene = {
      grid: () => this.reels.map((r) => Array.from({ length: NROWS }, (_, row) => names.get(r.cell(row).texture) ?? '?')),
      qa: () => ({ ...this.qa }),
      court: () => ({ ...this.court.qa, visible: this.court.root.visible }),
      rs: () => JSON.parse(JSON.stringify(this.qaRs)),
      leftovers: () => ({ court: this.court.root.visible, overlay: this.overlay.children.length, gsLayer: this.gsLayer.children.length, rpPlate: this.rpPlate.visible, fx: this.fx.children.length }),
    };
  }

  /** Central reset at the start of every round: nothing from the previous round survives. */
  resetRound() {
    this.court?.reset();
    this.clearZone?.();
    this.onOverlayTap = null;
    this.match.skip = false;
    this.rpBusy = false;
    this.overlay.removeChildren().forEach((c) => c.destroy({ children: true }));
    this.fx.removeChildren().forEach((c) => c.destroy({ children: true }));
    this.particles.length = 0;
    this.protoEvent = '—';
    this.clearWins();
    this.restoreBoardPos();
  }

  private restoreBoardPos() {
    if (this.boardHome) {
      this.board.position.set(this.boardHome.x, this.boardHome.y);
      this.boardHome = null;
    }
  }

  private clearServe() {
    this.gsLayer.removeChildren().forEach((c) => c.destroy({ children: true }));
  }

  private setCell(reel: number, row: number, sym: string) {
    const s = this.reels[reel].cell(row);
    s.texture = this.tex['sym_' + sym];
    s.width = s.height = SYM_SIZE;
    s.rotation = 0;
    s.alpha = 1;
  }

  private dimAllBut(keep: Set<string>, a: number, ms: number) {
    const sprites: Sprite[] = [];
    this.reels.forEach((r, i) => { for (let row = 0; row < NROWS; row++) if (!keep.has(`${i}:${row}`)) sprites.push(r.cell(row)); });
    const a0 = sprites.map((s) => s.alpha);
    return this.tw.tween(ms, (u) => sprites.forEach((s, k) => (s.alpha = a0[k] + (a - a0[k]) * u)));
  }

  private shake(ms: number, amp: number) {
    if (this.prefs.reducedMotion) return Promise.resolve();
    if (!this.boardHome) this.boardHome = { x: this.board.x, y: this.board.y };
    const h = this.boardHome;
    return this.tw.tween(ms, (u) => {
      const k = amp * (1 - u);
      this.board.position.set(h.x + Math.sin(u * 60) * k, h.y + Math.cos(u * 47) * k * 0.6);
    }).then(() => this.restoreBoardPos());
  }

  /** (A) Golden Ball reveal ≈ 0.4 s: short spin, glow, lift, rest of the reels dimmed. */
  private async ballReveal(o: Position) {
    const rm = this.prefs.reducedMotion;
    const s = this.reels[o.reel].cell(o.row);
    const x = o.reel * CELL + CELL / 2, y = o.row * CELL + CELL / 2;
    const halo = new Sprite(this.tex.glow);
    halo.anchor.set(0.5);
    halo.blendMode = 'add';
    halo.tint = 0xf2cf6b;
    halo.width = halo.height = CELL * 1.5;
    halo.position.set(x, y);
    halo.alpha = 0;
    this.gsLayer.addChild(halo);
    audio.play('mult_up', { volume: 0.55, rate: 1.15 });
    const base = SYM_SIZE / s.texture.width;
    const y0 = s.y;
    void this.dimAllBut(new Set([`${o.reel}:${o.row}`]), 0.55, rm ? 80 : 200);
    await this.tw.tween(rm ? 160 : 400, (u) => {
      halo.alpha = 0.75 * Math.sin(Math.min(1, u * 1.4) * Math.PI / 2);
      if (rm) return;
      s.rotation = Math.sin(u * Math.PI * 2) * 0.22 * (1 - u);
      s.y = y0 - 12 * ease.outCubic(u);
      s.scale.set(base * (1 + 0.12 * ease.outBack(u)));
    });
    return { halo, y0 };
  }

  private impact(x: number, y: number, strong: boolean) {
    const ring = new Graphics().circle(0, 0, CELL * 0.3).stroke({ color: 0xf4e9d4, width: strong ? 7 : 5 });
    ring.position.set(x, y);
    this.gsLayer.addChild(ring);
    void this.tw.tween(strong ? 300 : 240, (u) => {
      ring.scale.set(0.6 + 0.9 * u);
      ring.alpha = 1 - u;
    }).then(() => ring.destroy());
  }

  /** flip a cell to a new symbol (scale X 1 -> 0, swap texture, 0 -> 1) */
  private async flip(reel: number, row: number, sym: string, ms = 160) {
    this.qa.flips++;
    const s = this.reels[reel].cell(row);
    if (this.prefs.reducedMotion) return this.setCell(reel, row, sym);
    const base = SYM_SIZE / s.texture.width;
    await this.tw.tween(ms / 2, (u) => (s.scale.x = base * (1 - u)));
    this.setCell(reel, row, sym);
    const b2 = SYM_SIZE / s.texture.width;
    s.scale.set(0, b2 * 1.12);
    await this.tw.tween(ms / 2, (u) => s.scale.set(b2 * (1 + 0.12 * (1 - u)) * u + 0.0001, b2 * (1 + 0.12 * (1 - u))));
    s.scale.set(b2);
  }

  /** racket sprite (racket symbol art, same family) */
  private makeRacket(smash: boolean) {
    const r = new Sprite(this.tex.sym_H4);
    r.anchor.set(0.32, 0.86); // pivot near the grip
    r.width = r.height = CELL * 2;
    r.rotation = smash ? -2.5 : -0.35;
    this.gsLayer.addChild(r);
    return r;
  }

  /** (B / C) the stroke: racket in, toss, swing, contact.  Returns the ball sprite at contact point. */
  private async stroke(o: Position, smash: boolean, again: boolean, ball: Sprite) {
    const rm = this.prefs.reducedMotion;
    const x = o.reel * CELL + CELL / 2, y = o.row * CELL + CELL / 2;
    const racket = this.makeRacket(smash);
    // grip position: left of reel 1 (serve) or high above the server (smash)
    // kept inside the frame so the stroke is visible on narrow phones
    const gx = smash ? x - CELL * 0.05 : x - CELL * 0.36;
    const gy = smash ? y - CELL * 0.15 : y + CELL * 0.4;
    racket.position.set(gx - CELL * (again ? 0.4 : 1.2), gy);
    racket.alpha = 0;
    await this.tw.tween(rm ? 80 : again ? 140 : 280, (u) => {
      racket.alpha = u;
      racket.x = gx - CELL * (again ? 0.4 : 1.2) * (1 - ease.outCubic(u));
    });
    // toss: the ball rises to the strings
    const tossY = smash ? y - CELL * 1.25 : y - CELL * 0.62;
    const by0 = ball.y;
    await this.tw.tween(rm ? 80 : smash ? 340 : 300, (u) => {
      ball.y = by0 + (tossY - by0) * ease.outCubic(u);
      ball.rotation += 0.12;
      racket.rotation = (smash ? -2.5 : -0.35) - (smash ? 0.5 : 0.75) * ease.inOutCubic(u); // wind-up
    });
    if (smash && !rm) {
      // very brief slow-down before the strike
      audio.play('wind', { volume: 0.35 });
      await this.tw.wait(140);
    }
    // swing: fast, accelerating, through the ball
    const r0 = racket.rotation, r1 = smash ? -0.35 : 0.9;
    await this.tw.tween(rm ? 60 : smash ? 120 : 110, (u) => (racket.rotation = r0 + (r1 - r0) * ease.inCubic(u)));
    audio.play('racket', { volume: smash ? 1 : 0.85, rate: smash ? 0.85 : 1.05 });
    this.qa.strokes++;
    if (smash) this.qa.smash++;
    this.impact(ball.x, ball.y, smash);
    // follow-through and exit
    void this.tw.tween(rm ? 80 : 260, (u) => {
      racket.rotation = r1 + 0.5 * ease.outCubic(u);
      racket.alpha = 1 - u;
    }).then(() => racket.destroy());
  }

  /** ball flight along one trajectory; calls onHit(reel,row) at each bounce */
  private async flight(ball: Sprite, path: Position[], smash: boolean, onHit: (p: Position) => void | Promise<void>, trail: Graphics) {
    const rm = this.prefs.reducedMotion;
    const shadow = new Graphics().ellipse(0, 0, 20, 7).fill({ color: 0x000000, alpha: 0.35 });
    this.gsLayer.addChildAt(shadow, 0);
    const pt = (p: Position) => ({ x: p.reel * CELL + CELL / 2, y: p.row * CELL + CELL / 2 });
    let from = { x: ball.x, y: ball.y };
    const hop = rm ? 60 : smash ? 85 : 135;
    for (let k = 1; k < path.length; k++) {
      const to = pt(path[k]);
      const f0 = { ...from };
      const arc = smash ? 10 : k === 1 ? 70 : 34;
      await this.tw.tween(hop * (k === 1 ? 1.3 : 1), (u) => {
        const e = smash ? ease.inCubic(Math.min(1, u * 1.1)) : ease.inOutCubic(u);
        ball.x = f0.x + (to.x - f0.x) * e;
        const ground = f0.y + (to.y - f0.y) * e;
        ball.y = ground - (rm ? 0 : Math.sin(u * Math.PI) * arc);
        ball.rotation += smash ? 0.4 : 0.22;
        shadow.position.set(ball.x, ground + 26);
        shadow.alpha = 0.5 - 0.3 * Math.sin(u * Math.PI);
      });
      trail.moveTo(f0.x, f0.y + (k === 1 ? 0 : 0)).lineTo(to.x, to.y).stroke({ color: 0xe7c877, width: smash ? 8 : 5, alpha: 0.55 });
      this.impact(to.x, to.y, smash);
      audio.play('bounce', { volume: smash ? 0.6 : 0.4, rate: 0.9 + k * 0.05 });
      this.qa.hits++;
      await onHit(path[k]);
      from = to;
    }
    // ball leaves the court on the right
    const fx0 = ball.x, fy0 = ball.y;
    await this.tw.tween(rm ? 60 : 160, (u) => {
      ball.x = fx0 + CELL * 0.9 * u;
      ball.y = fy0 - 20 * u;
      ball.alpha = 1 - u;
      shadow.alpha = 0.3 * (1 - u);
    });
    shadow.destroy();
  }

  async goldenServe(e: Extract<BookEvent, { type: 'goldenServe' }>) {
    this.rpBusy = true;
    this.match.skip = false;
    const rm = this.prefs.reducedMotion;
    const smash = e.shot === 'smash';
    const o = e.origin;
    const changeAt = new Map(e.changes.map((c) => [`${c.reel}:${c.row}`, c.to]));
    const { halo } = await this.ballReveal(o);
    // the Golden Ball leaves its cell: a ball sprite takes over
    const gsprite = this.reels[0].cell(o.row);
    const ball = new Sprite(this.tex.sym_G);
    ball.anchor.set(0.5);
    ball.width = ball.height = 70;
    ball.position.set(CELL / 2, o.row * CELL + CELL / 2 - (rm ? 0 : 12));
    this.gsLayer.addChild(ball);
    gsprite.alpha = 0.25;
    gsprite.rotation = 0;
    gsprite.y = o.row * CELL + CELL / 2;
    if (smash) {
      this.setRpPlate('GOLDEN SMASH', true);
      void this.dimAllBut(new Set([`0:${o.row}`]), 0.4, 160);
      this.cheer(0.6);
      void this.aceSay(this.t.aceSmash, 1200);
    } else this.setRpPlate(e.shot === 'double' ? 'DOUBLE SERVE' : 'GOLDEN SERVE', false);
    this.protoEvent = smash ? 'SMASH' : e.shot === 'double' ? 'DOUBLE' : 'SERVE';
    this.refreshPanel();
    const trail = new Graphics();
    this.gsLayer.addChildAt(trail, 0);
    const hitA = async (p: Position) => {
      const k = `${p.reel}:${p.row}`;
      const s = this.reels[p.reel].cell(p.row);
      s.alpha = 1;
      if (e.concept === 'A' && changeAt.has(k)) await this.flip(p.reel, p.row, changeAt.get(k)!, smash ? 120 : 170);
      else this.pulse(s, 1.1, 200);
    };
    const paths = e.paths;
    // serve 1 (smash: both rows of the band are hit together, two balls)
    await this.stroke(o, smash, false, ball);
    if (smash) {
      const ball2 = new Sprite(this.tex.sym_G);
      ball2.anchor.set(0.5);
      ball2.width = ball2.height = 62;
      ball2.position.copyFrom(ball.position);
      this.gsLayer.addChild(ball2);
      await Promise.all([this.flight(ball, paths[0], true, hitA, trail), this.flight(ball2, paths[1], true, hitA, trail)]);
      void this.shake(240, 9);
      this.cheer(1);
    } else {
      await this.flight(ball, paths[0], false, hitA, trail);
      if (e.shot === 'double' && paths[1]) {
        // second serve from the same server
        const b2 = new Sprite(this.tex.sym_G);
        b2.anchor.set(0.5);
        b2.width = b2.height = 70;
        b2.position.set(CELL / 2, o.row * CELL + CELL / 2);
        this.gsLayer.addChild(b2);
        await this.stroke(o, false, true, b2);
        await this.flight(b2, paths[1], false, hitA, trail);
      }
    }
    // COURT SWITCH: exchanges across the net, then the server's cell takes the returned symbol
    if (e.concept === 'B' && e.swaps) {
      for (const sw of e.swaps) await this.swapCells(sw.a, sw.b);
    }
    const g0 = changeAt.get(`0:${o.row}`);
    if (g0) await this.flip(0, o.row, g0, 160);
    // guarantee: the grid shown is exactly the engine's transformed board
    for (let r = 0; r < NR; r++) for (let row = 0; row < NROWS; row++) this.setCell(r, row, e.board[r][row]);
    halo.destroy();
    trail.alpha = 0.5;
    await this.tw.wait(rm ? 80 : 180);
    this.rpBusy = false;
  }

  private async swapCells(a: Position & { sym: string }, b: Position & { sym: string }) {
    if (a.sym === b.sym) return;
    this.qa.swaps++;
    const sa = this.reels[a.reel].cell(a.row), sb = this.reels[b.reel].cell(b.row);
    const ta = new Sprite(sa.texture), tb = new Sprite(sb.texture);
    const pa = { x: a.reel * CELL + CELL / 2, y: a.row * CELL + CELL / 2 }, pb = { x: b.reel * CELL + CELL / 2, y: b.row * CELL + CELL / 2 };
    for (const [t, p] of [[ta, pa], [tb, pb]] as const) {
      t.anchor.set(0.5);
      t.width = t.height = SYM_SIZE;
      t.position.set(p.x, p.y);
      this.gsLayer.addChild(t);
    }
    sa.alpha = sb.alpha = 0;
    audio.play('pop', { volume: 0.4 });
    await this.tw.tween(this.prefs.reducedMotion ? 120 : 420, (u) => {
      const e = ease.inOutCubic(u);
      ta.position.set(pa.x + (pb.x - pa.x) * e, pa.y + (pb.y - pa.y) * e - Math.sin(u * Math.PI) * CELL * 0.45);
      tb.position.set(pb.x + (pa.x - pb.x) * e, pb.y + (pa.y - pb.y) * e + Math.sin(u * Math.PI) * CELL * 0.45);
    });
    this.setCell(a.reel, a.row, b.sym);
    this.setCell(b.reel, b.row, a.sym);
    ta.destroy();
    tb.destroy();
  }

  /** CHAMPIONSHIP POINT: exceptional results only (≥ 50× the stake); proportionate. */
  async championshipPoint(amount: number, tier: WinTier) {
    const epic = tier === 'epic';
    this.cheer(epic ? 1.5 : 1.1);
    audio.play(epic ? 'win_3' : 'win_2', { volume: 0.9 });
    audio.play('match_point', { volume: 0.7 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const panel = new Graphics();
    const W = 640, H = 300;
    panel.roundRect(-W / 2, -H / 2, W, H, 22).fill({ color: 0x0b2440, alpha: 0.97 }).stroke({ color: 0xe7c877, width: 4 });
    panel.roundRect(-W / 2 + 10, -H / 2 + 10, W - 20, H - 20, 16).stroke({ color: 0xf4e9d4, width: 1, alpha: 0.35 });
    panel.moveTo(-W / 2 + 40, -40).lineTo(W / 2 - 40, -40).stroke({ color: 0xe7c877, width: 1.5, alpha: 0.5 });
    const kick = this.plainText('GOLDEN RALLY · NIGHT FINAL', 20, '#D6B36A', '800');
    kick.y = -H / 2 + 38;
    const title = this.fit(this.goldText('CHAMPIONSHIP POINT', 46), W - 60);
    title.y = -78;
    const amt = this.fit(new Text({ text: money(0, this.currency, this.lang), style: { fontFamily: 'Cinzel', fontWeight: '700', fontSize: 92, fill: '#FFF4D6', letterSpacing: 2 } }), W - 60);
    amt.anchor.set(0.5);
    amt.y = 50;
    inner.addChild(panel, kick, title, amt);
    c.relayout?.();
    const skip = { now: false };
    // subtle camera move for the biggest results only
    const s0 = this.world.scale.x;
    if (epic && !this.prefs.reducedMotion) void this.tw.tween(900, (u) => this.world.scale.set(s0 * (1 + 0.025 * ease.outCubic(u))));
    if (epic) void this.aceSay(this.t.aceBig, 1500);
    await this.fadeOverlay(c, 260, 260, async () => {
      this.onOverlayTap = () => (skip.now = true);
      await this.countUp(amt, amount, epic ? 2200 : 1400, skip);
      await this.waitTapOr(epic ? 1100 : 700);
    });
    if (epic && !this.prefs.reducedMotion) await this.tw.tween(300, (u) => this.world.scale.set(s0 * (1 + 0.025 * (1 - u))));
    this.world.scale.set(s0);
  }


  // ---------------------------------------------------------------- GOLDEN SERVE — RETURN SPINS
  // The reels stay the centre of the game: a Golden Ball strikes a zone of
  // two reels (four for a Golden Smash); only those reels spin again.  Every
  // value shown comes from the book (serve / respin / stageWin events).
  rsMode = false;
  private zoneGfx = new Graphics();
  private zoneTag = new Container();
  qaRs = { serves: 0, returns: 0, smashes: 0, respins: 0, movedReels: [] as number[][], stablePositions: true };

  private zoneRect(reels: number[]) {
    const x0 = Math.min(...reels) * CELL, x1 = (Math.max(...reels) + 1) * CELL;
    return { x0, x1, cx: (x0 + x1) / 2 };
  }

  private showZone(reels: number[], label: string, smash: boolean) {
    const { x0, x1, cx } = this.zoneRect(reels);
    const g = this.zoneGfx.clear();
    g.roundRect(x0 + 4, 4, x1 - x0 - 8, NROWS * CELL - 8, 18).stroke({ color: smash ? 0xffe39a : 0xe7c877, width: smash ? 8 : 6, alpha: 0.95 });
    g.roundRect(x0 + 4, 4, x1 - x0 - 8, NROWS * CELL - 8, 18).fill({ color: 0xe7c877, alpha: 0.06 });
    this.zoneTag.removeChildren().forEach((c) => c.destroy());
    const t = new Text({ text: label, style: { fontFamily: 'Inter', fontWeight: '800', fontSize: 30, fill: '#071826', letterSpacing: 2 } });
    t.anchor.set(0.5);
    const bg = new Graphics().roundRect(-t.width / 2 - 18, -24, t.width + 36, 48, 24).fill({ color: smash ? 0xffe39a : 0xe7c877 });
    this.zoneTag.addChild(bg, t);
    this.zoneTag.position.set(cx, -6);
    this.zoneTag.visible = true;
    if (!this.zoneGfx.parent) this.winLayer.addChild(this.zoneGfx, this.zoneTag);
  }
  private clearZone() {
    this.zoneGfx.clear();
    this.zoneTag.visible = false;
  }

  /** a return: flat forehand from the opposite side (mirrored racket, no toss) */
  private async returnStroke(o: Position, ball: Sprite) {
    const rm = this.prefs.reducedMotion;
    const x = o.reel * CELL + CELL / 2, y = o.row * CELL + CELL / 2;
    const r = this.makeRacket(false);
    const fromRight = o.reel < 3; // the racket comes from the side facing the court
    const dir = fromRight ? -1 : 1;
    r.scale.x = Math.abs(r.scale.x) * (fromRight ? -1 : 1);
    const gx = x - dir * CELL * 0.42, gy = y + CELL * 0.35;
    r.position.set(gx - dir * CELL * 0.8, gy);
    r.alpha = 0;
    r.rotation = dir * 0.9;
    await this.tw.tween(rm ? 60 : 150, (u) => {
      r.alpha = u;
      r.x = gx - dir * CELL * 0.8 * (1 - ease.outCubic(u));
    });
    // the ball rises off the reel to hip height
    const y0 = ball.y;
    await this.tw.tween(rm ? 60 : 140, (u) => {
      ball.y = y0 - CELL * 0.25 * ease.outCubic(u);
      r.rotation = dir * (0.9 + 0.5 * u); // short take-back
    });
    const r0 = r.rotation, r1 = -dir * 0.7;
    await this.tw.tween(rm ? 50 : 95, (u) => (r.rotation = r0 + (r1 - r0) * ease.inCubic(u)));
    audio.play('racket', { volume: 0.8, rate: 1.15 });
    this.qa.strokes++;
    this.impact(ball.x, ball.y, false);
    void this.tw.tween(rm ? 60 : 220, (u) => {
      r.rotation = r1 - dir * 0.4 * u;
      r.alpha = 1 - u;
    }).then(() => r.destroy());
  }

  async rsServe(e: Extract<BookEvent, { type: 'serve' }>) {
    this.rpBusy = true;
    this.match.skip = false;
    this.clearWins();
    const rm = this.prefs.reducedMotion;
    const o = e.origin;
    this.qaRs.serves++;
    if (e.kind === 'return') this.qaRs.returns++;
    if (e.smash) this.qaRs.smashes++;
    this.protoEvent = e.kind === 'return' ? fmtS(this.t.rsReturnN, { n: e.returnIndex, m: e.maxReturns }) : e.smash ? 'GOLDEN SMASH' : 'GOLDEN SERVE';
    this.refreshPanel();
    const { halo } = await this.ballReveal(o);
    const gs = this.reels[o.reel].cell(o.row);
    const ball = new Sprite(this.tex.sym_G);
    ball.anchor.set(0.5);
    ball.width = ball.height = 74;
    ball.position.set(o.reel * CELL + CELL / 2, o.row * CELL + CELL / 2 - (rm ? 0 : 12));
    this.gsLayer.addChild(ball);
    // the Golden Ball has been played: its symbol stays on the reel, dimmed (used)
    gs.alpha = 0.4;
    gs.rotation = 0;
    gs.y = o.row * CELL + CELL / 2;
    gs.scale.set(SYM_SIZE / gs.texture.width);
    if (e.kind === 'return' && !e.smash) await this.returnStroke(o, ball);
    else await this.stroke(o, e.smash, e.kind === 'return', ball);
    // flight to the struck zone (engine decision), landing in its centre
    const { cx } = this.zoneRect(e.reels);
    const tx = cx, ty = NROWS * CELL * 0.5;
    const fx = ball.x, fy = ball.y;
    const shadow = new Graphics().ellipse(0, 0, 22, 8).fill({ color: 0x000000, alpha: 0.35 });
    this.gsLayer.addChildAt(shadow, 0);
    const trail = new Graphics();
    this.gsLayer.addChildAt(trail, 0);
    let lx = fx, ly = fy;
    const ms = rm ? 150 : e.smash ? 260 : e.kind === 'return' ? 380 : 430;
    const apex = e.smash ? 30 : e.kind === 'return' ? CELL * 0.7 : CELL * 1.1;
    await this.tw.tween(ms, (u) => {
      const k = e.smash ? ease.inCubic(u) : ease.inOutCubic(u);
      ball.x = fx + (tx - fx) * k;
      const ground = fy + (ty - fy) * k;
      ball.y = ground - (rm ? 0 : Math.sin(u * Math.PI) * apex);
      ball.rotation += e.smash ? 0.45 : 0.25;
      ball.scale.set((74 / ball.texture.width) * (1 + 0.25 * Math.sin(u * Math.PI)));
      shadow.position.set(ball.x, ground + 30);
      trail.moveTo(lx, ly).lineTo(ball.x, ball.y).stroke({ color: 0xe7c877, width: e.smash ? 9 : 6, alpha: 0.6 });
      lx = ball.x;
      ly = ball.y;
    });
    // impact: the struck reels react, the others stay perfectly still
    audio.play('bounce', { volume: e.smash ? 0.9 : 0.6 });
    this.impact(tx, ty, e.smash);
    const zoneName = e.smash ? 'GOLDEN SMASH' : fmtS(this.t.rsZone, { z: (this.t as unknown as Record<string, string>)[`rsZone_${e.zone}`] ?? e.zone });
    this.showZone(e.reels, zoneName, e.smash);
    if (e.smash) {
      this.cheer(1.1);
      void this.shake(220, 7);
    }
    const sq = e.reels.map((r) => this.reels[r]);
    await Promise.all(sq.map((reel) => (this.prefs.reducedMotion ? Promise.resolve() : this.tw.tween(160, (u) => {
      const k = 1 - 0.07 * Math.sin(u * Math.PI);
      for (const sp of reel.sprites) sp.scale.y = (SYM_SIZE / sp.texture.width) * k;
    }))));
    await this.tw.tween(rm ? 60 : 140, (u) => {
      ball.alpha = 1 - u;
      shadow.alpha = 0.35 * (1 - u);
      trail.alpha = 1 - u;
    });
    ball.destroy();
    shadow.destroy();
    trail.destroy();
    halo.destroy();
    this.rpBusy = false;
  }

  /** only the struck reels spin again; every other reel keeps its exact position */
  async rsRespin(e: Extract<BookEvent, { type: 'respin' }>) {
    this.rpBusy = true;
    const strips = RSDATA.strips[e.gameType === 'freegame' ? 'free' : 'base'];
    const before = this.reels.map((r) => r.pos);
    this.qaRs.respins++;
    this.qaRs.movedReels.push([...e.reels]);
    const rm = this.prefs.reducedMotion;
    const turbo = this.prefs.turbo;
    audio.play('spin_start', { volume: 0.5 });
    await Promise.all(e.reels.map(async (r, k) => {
      const reel = this.reels[r];
      reel.strip = strips[r];
      const n = strips[r].length;
      const s0 = reel.pos;
      const T = (rm ? 380 : turbo ? 520 : 760) + k * (rm ? 40 : 120);
      const D0 = Math.max(4, Math.round((24 * T) / 1000 * 0.62));
      const D = D0 + mod(Math.floor(s0) - D0 - e.stops[r], n) + (s0 - Math.floor(s0));
      reel.blur.enabled = !rm;
      let last = s0;
      await this.tw.tween(T, (u) => {
        reel.pos = s0 - D * (rm ? ease.outCubic(u) : ease.outBack(u, 0.45));
        reel.blur.strengthY = Math.min(14, Math.abs(last - reel.pos) * 28);
        last = reel.pos;
        reel.render();
      });
      reel.pos = e.stops[r];
      reel.blur.enabled = false;
      reel.blur.strengthY = 0;
      reel.render();
      audio.play('reel_stop', { volume: 0.5, rate: 0.96 + r * 0.02 });
      this.squash(reel);
    }));
    // QA: the reels that were not struck did not move at all
    this.reels.forEach((reel, i) => {
      if (!e.reels.includes(i) && reel.pos !== before[i]) this.qaRs.stablePositions = false;
    });
    this.clearZone();
    this.rpBusy = false;
  }

  /** amount of one stop, then the cumulated total (shown apart from the combinations) */
  async rsStage(e: Extract<BookEvent, { type: 'stageWin' }>, amount: number, total: number, hadEvent: boolean) {
    if (!hadEvent && e.stage === 0) return; // ordinary spin: the normal win display is enough
    const label = fmtS(this.t.rsStagePlate, { n: e.stage + 1, a: money(amount, this.currency, this.lang), t: money(total, this.currency, this.lang) });
    this.setPlate(label);
    await this.tw.wait(amount === 0 ? (this.prefs.turbo ? 250 : 450) : this.prefs.turbo ? 400 : 700);
  }

  // ---------------------------------------------------------------- RALLY PATH (prototype, demo lab)
  // Presentation only: length, path and reward arrive in the book event,
  // computed by the engine before the animation; skipping never changes them.
  private rpBusy = false;

  private clearRally() {
    this.rpGfx.clear();
    this.rpLayer.removeChildren().forEach((c) => c.destroy());
    this.rpPlate.visible = false;
  }

  private setRpPlate(text: string, cs: boolean) {
    this.rpText.text = text;
    this.rpPlate.visible = !!text;
    if (!text) return;
    const h = 66;
    const w = Math.min(FRAME_W - 20, Math.max(300, this.rpText.width + 70));
    this.rpText.scale.set(Math.min(1, (w - 50) / (this.rpText.width / this.rpText.scale.x)));
    this.rpPlateBg.clear()
      .roundRect(-w / 2, -h / 2, w, h, h / 2).fill({ color: cs ? 0x3a2a08 : 0x0b2440, alpha: 0.96 }).stroke({ color: 0xe7c877, width: 3 })
      .roundRect(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12, h / 2 - 6).stroke({ color: 0xf4e9d4, width: 1, alpha: 0.35 });
  }

  async rallyPath(e: Extract<BookEvent, { type: 'rallyPath' }>) {
    this.rpBusy = true;
    this.match.skip = false;
    const rm = this.prefs.reducedMotion;
    const cx = (r: number) => r * CELL + CELL / 2;
    const cy = (row: number) => row * CELL + CELL / 2;
    const gold = 0xe7c877;
    const amt = Math.round((this.bet * e.reward) / 100);
    // (1) Golden Ball reveal (~0.3 s)
    const serve = e.path[0];
    const ring = new Graphics().circle(0, 0, CELL * 0.47).stroke({ color: gold, width: 6 });
    ring.position.set(cx(serve.reel), cy(serve.row));
    this.rpLayer.addChild(ring);
    audio.play('serve', { volume: 0.7 });
    this.pulse(this.reels[serve.reel].cell(serve.row), 1.12, 300);
    await this.tw.tween(rm ? 120 : 300, (u) => ring.scale.set(0.6 + 0.4 * ease.outBack(u)));
    if (e.length === 1) {
      // no return: short, clean stop
      this.setRpPlate(this.t.rpNoReturn, false);
      await this.tw.wait(rm ? 300 : 450);
      this.rpBusy = false;
      return;
    }
    // (2) the ball travels racket to racket (≈0.2 s per shot)
    const ball = new Sprite(this.tex.sym_G);
    ball.anchor.set(0.5);
    ball.width = ball.height = 62;
    ball.position.set(cx(serve.reel), cy(serve.row));
    this.rpLayer.addChild(ball);
    const hop = rm ? 90 : Math.max(150, Math.min(240, 1100 / (e.length - 1)));
    for (let k = 1; k < e.path.length; k++) {
      const a = e.path[k - 1];
      const b = e.path[k];
      const x0 = cx(a.reel), y0 = cy(a.row), x1 = cx(b.reel), y1 = cy(b.row);
      await this.tw.tween(hop, (u) => {
        ball.x = x0 + (x1 - x0) * u;
        ball.y = y0 + (y1 - y0) * u - (rm ? 0 : Math.sin(u * Math.PI) * 46);
      }, ease.inOutCubic);
      this.rpGfx.moveTo(x0, y0).lineTo(x1, y1).stroke({ color: gold, width: 7, alpha: 0.9 }).circle(x1, y1, CELL * 0.44).stroke({ color: gold, width: 4 });
      const n = this.goldText(String(k + 1), 30);
      n.position.set(x1 + CELL * 0.33, y1 - CELL * 0.33);
      this.rpLayer.addChild(n);
      audio.play('racket', { volume: 0.55, rate: 0.95 + k * 0.04 });
      this.pulse(this.reels[b.reel].cell(b.row), 1.1, 240);
    }
    ball.destroy();
    // (3) clean stop: length + reward on the Rally Path plate (separate from the ways win)
    if (e.championshipShot) {
      await this.championshipShot(amt);
    } else {
      audio.play(e.length >= 4 ? 'win_2' : 'win_1', { volume: 0.7 });
      const p = this.cellWorld(e.path[e.path.length - 1].reel, e.path[e.path.length - 1].row);
      if (!rm) this.burst(p.x, p.y, 8 + 4 * e.length, 'sparkle', this.fx, { speed: 180, life: 0.6, scale: 0.35 });
    }
    this.protoEvent = e.championshipShot ? 'CHAMPIONSHIP SHOT' : `RALLY ×${e.length}`;
    this.refreshPanel();
    this.setRpPlate(`${fmtS(this.t.rpPlate, { n: e.length })} · ${money(amt, this.currency, this.lang)}`, e.championshipShot);
    await this.tw.wait(rm ? 300 : 650);
    this.rpBusy = false;
  }

  /** 6-shot rally: 2–3 s moment; the amount was drawn by the engine (CS table). */
  private async championshipShot(amount: number) {
    this.cheer(1.5);
    audio.play('match_point', { volume: 0.9 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const halo = new Sprite(this.tex.glow);
    halo.anchor.set(0.5);
    halo.blendMode = 'add';
    halo.tint = 0xe7c877;
    halo.width = halo.height = 760;
    halo.alpha = 0.4;
    const t1 = this.fit(this.goldText('CHAMPIONSHIP SHOT', 84), 600);
    t1.y = -70;
    const amt = this.goldText(money(0, this.currency, this.lang), 88);
    amt.y = 90;
    inner.addChild(halo, t1, amt);
    c.relayout?.();
    const skip = { now: false };
    if (!this.prefs.reducedMotion) {
      const w = this.app.screen.width;
      for (let i = 0; i < 4; i++) this.burst(Math.random() * w, this.app.screen.height * 0.4, 12, 'sparkle', this.overlay, { speed: 260, life: 1.2, scale: 0.4 });
    }
    await this.fadeOverlay(c, 250, 250, async () => {
      this.onOverlayTap = () => (skip.now = true);
      await this.countUp(amt, amount, 1300, skip);
      await this.waitTapOr(700);
    });
  }

  /** Prototype bonus opener (≤ 1.5 s). RC electric blue, GF night blue + champagne gold. */
  async protoBonusStart(e: Extract<BookEvent, { type: 'protoBonusStart' }>) {
    this.protoEvent = '—';
    audio.play('bonus_trigger', { volume: 0.85 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const gf = e.bonus === 'final';
    const t1 = this.fit(gf ? this.goldText(this.rsMode ? 'CHAMPIONSHIP NIGHT' : 'THE GRAND FINAL', 86) : this.superText('RALLY CHALLENGE', 86), 680);
    t1.y = -40;
    const t2 = this.plainText(fmtS(this.rsMode ? (gf ? this.t.rsIntroGf : this.t.rsIntroRc) : this.gsMode ? (gf ? this.t.gsIntroGf : this.t.gsIntroRc) : gf ? this.t.rpIntroGf : this.t.rpIntroRc, { n: e.spins }), 30, gf ? '#F4E9D4' : '#BFE6FF', '700');
    t2.y = 60;
    inner.addChild(t1, t2);
    c.relayout?.();
    await this.fadeOverlay(c, 220, 220, () => this.waitTapOr(this.prefs.reducedMotion ? 500 : 900));
  }

  protoSpinStart(_e: Extract<BookEvent, { type: 'spinStart' }>) {
    this.protoEvent = '—';
    this.refreshPanel();
  }

  /** Switches the reels to the prototype strips (lab on) or back to the normal game. */
  setProto(on: boolean) {
    if (this.proto === on) return;
    this.proto = on;
    const v = this.tbVariant;
    this.tbVariant = null;
    if (v) this.buildTieBreakPanel(v);
    // no board reset: the next spin switches strips while the reels move
  }

  /** SECOND SERVE: +1 independent free spin (< 1.5 s). */
  async secondServe(_e: Extract<BookEvent, { type: 'secondServe' }>) {
    this.protoEvent = 'SECOND SERVE';
    this.refreshPanel();
    audio.play('serve', { volume: 0.8 });
    const p = this.cellWorld(2.5, 2);
    const t = this.fit(this.goldText('SECOND SERVE  +1', 64), FRAME_W * this.board.scale.x * 0.9);
    t.position.set(p.x, p.y);
    this.fx.addChild(t);
    const k0 = t.scale.x;
    await this.tw.tween(this.prefs.reducedMotion ? 500 : 1100, (u) => {
      t.alpha = u < 0.15 ? u / 0.15 : u > 0.8 ? (1 - u) / 0.2 : 1;
      t.scale.set(k0 * (this.prefs.reducedMotion ? 1 : 0.85 + 0.15 * ease.outBack(Math.min(1, u * 4))));
    });
    t.destroy();
  }

  async protoBonusEnd(e: Extract<BookEvent, { type: 'protoBonusEnd' }>, amount: number) {
    audio.play('bonus_end', { volume: 0.8 });
    const c = this.makeOverlay();
    const inner = c.children[1] as Container;
    const t1 = this.fit(this.goldText(e.bonus === 'final' ? (this.rsMode ? 'CHAMPIONSHIP NIGHT' : 'THE GRAND FINAL') : 'RALLY CHALLENGE', 60), 680);
    t1.y = -80;
    const t2 = this.plainText(fmtS(this.t.rpOutro, { n: e.spins }), 28, '#F4E9D4', '700');
    t2.y = -10;
    const amt = this.goldText(money(amount, this.currency, this.lang), 84);
    amt.y = 80;
    inner.addChild(t1, t2, amt);
    c.relayout?.();
    await this.fadeOverlay(c, 220, 220, () => this.waitTapOr(1400));
  }
}

function lerpColor(a: number, b: number, k: number) {
  const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
  const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
  return (Math.round(ar + (br - ar) * k) << 16) | (Math.round(ag + (bg - ag) * k) << 8) | Math.round(ab + (bb - ab) * k);
}
