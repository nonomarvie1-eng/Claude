// ACE! — opening cinematic (HTML5 / PixiJS part).
//
// One ball, one stadium, one continuous camera:
//   S1  the official stadium, the ACE! logo in the foreground, stable camera;
//   S2  the ball of the "!" leaves its socket (the letters stay still and fade out),
//       falls onto the court — the camera follows it down — bounces (gravity,
//       restitution, contact shadow, squash), turning progressively into the
//       photographic ball, rolls and comes to rest at the hand-off point;
//   S3–S5 the player picks the ball up and serves it towards the camera:
//       EXTERNAL CLIP (see ServeClip / docs/ACE_CINEMATIC.md).  Without the
//       clip, the camera pushes in on the same ball until it fills the frame
//       (no stand-in character is ever drawn);
//   S6  while the ball covers the whole frame, the real reels of the game are
//       switched in underneath; the ball then clears the frame.
//
// The cinematic never touches the game logic: it only calls `onOcclude`
// (show the real game under the ball) when the frame is fully covered.
import { BlurFilter, Container, Graphics, Sprite, Texture } from 'pixi.js';
import { audio } from '../audio/audio';
import { ease, type Tweener } from './tween';

export interface Rect { x: number; y: number; w: number; h: number }

/** The ball of the ACE! logo (measured on the provided logo, 1774 x 887 px). */
export const LOGO_BALL = { cx: 1495 / 1774, cy: 609.5 / 887, r: 96.5 / 1774 };
/** `ace_logo_ball` is the logo's own ball, cut out with a 6 px margin: visible diameter / image size. */
const CUT_FILL = 193 / 206;
/** `loading_ball` (photographic ball) fills 89 % of its image. */
const PHOTO_FILL = 0.89;

/**
 * External player sequence (S3–S5), to be produced (live action or rigged 3D)
 * on the official stadium, 1080 x 1920, and dropped in src/assets/cinematic/.
 * All positions are fractions of the clip frame.
 */
export interface ServeClip {
  src: string;
  width: number;
  height: number;
  /** clip time (s) at which the frame shows the ball exactly where the HTML5 ball hands over */
  handoffAt: number;
  /** ball position and visible diameter in the clip at `handoffAt` */
  ball: { x: number; y: number; d: number };
  /** clip time of the racket / ball contact (impact sound) */
  contactAt: number;
  /** clip time from which the clip's own ball covers the whole frame (used when there is no `exit`) */
  occludedAt: number;
  /** optional: clip time at which the struck ball leaves the clip — the frame freezes and the HTML5 ball,
   *  placed exactly over it (x, y, d as for `ball`), rushes to the lens in `ms` (default 320) */
  exit?: { at: number; x: number; y: number; d: number; ms?: number };
  /** optional sound cues on the clip's clock (bounces of the ball by the player, ...); `contactAt` adds the racket */
  cues?: { t: number; sound: 'bounce' | 'racket' | 'serve' | 'pop'; volume?: number }[];
}

/** Camera at the end of the fall: a 12 % push about the composition's bottom centre (it follows the ball down). */
export const CAMERA_REST = { zoom: 1.12, ax: 0.5, ay: 1.0 };
/** Where the ball comes to rest after its bounces, as seen on screen: fractions of the 9:16 composition
 *  (= of the 1080 x 1920 clip frame; x, y of width / height, d of width).  First frame of the player clip. */
export const BALL_REST = { x: 0.6, y: 0.84, d: 0.115 };

export interface CinematicHost {
  app: { screen: { width: number; height: number }; ticker: { add(f: (t: { deltaMS: number }) => void): void; remove(f: (t: { deltaMS: number }) => void): void } };
  tw: Tweener;
  root: Container; // the intro root (camera)
  stadium: Sprite;
  comp: Rect; // the 9:16 composition rectangle (where the stadium image is fully shown)
  tex: Record<string, Texture>;
}

export interface CinematicResult {
  usedClip: boolean;
  skipped: boolean;
  bounces: number;
  /** QA: the logo ball and the falling ball are the same object at the handover */
  continuity: { logoBallX: number; logoBallY: number; fallStartX: number; fallStartY: number; dStart: number; dLogo: number };
  occludedAt: number; // ms since start
  /** where the ball rests at the hand-off (screen fractions of the clip frame) */
  rest?: { x: number; y: number; d: number };
  clipStalled?: boolean;
  /** how the frame got covered: camera push (no clip), the clip's own ball, or the HTML5 ball leaving the clip */
  ending?: 'push' | 'occludedAt' | 'exit';
  /** sound cues played on the clip clock */
  cues?: number;
  totalMs: number;
}

export class AceCinematic {
  private layer = new Container();
  private logo = new Sprite();
  private cutBall = new Sprite(); // the logo's own ball (illustrated)
  private photoBall = new Sprite(); // the same ball, photographic rendering
  private ballC = new Container(); // holds both renderings: ONE ball object
  private shadow = new Graphics();
  private stadiumBlur = new BlurFilter({ strength: 0, quality: 3 });
  private skipping = false;
  private t0 = 0;
  /** QA */
  qa = { bounces: 0, phase: '' };

  constructor(private h: CinematicHost) {}

  skip() {
    this.skipping = true;
  }

  private setBallD(d: number) {
    this.cutBall.width = this.cutBall.height = d / CUT_FILL;
    this.photoBall.width = this.photoBall.height = d / PHOTO_FILL;
  }

  async play(opts: { clip?: ServeClip | null; onOcclude: () => void; video?: HTMLVideoElement | null }): Promise<CinematicResult> {
    const { tw, root, comp, tex } = this.h;
    this.t0 = performance.now();
    const W = this.h.app.screen.width, H = this.h.app.screen.height;
    // ---- set up: logo layers, one ball, contact shadow
    this.logo.texture = tex.ace_logo_noball;
    this.logo.anchor.set(0.5);
    this.cutBall.texture = tex.ace_logo_ball;
    this.cutBall.anchor.set(0.5);
    this.photoBall.texture = tex.loading_ball;
    this.photoBall.anchor.set(0.5);
    this.photoBall.alpha = 0;
    this.ballC.addChild(this.photoBall, this.cutBall);
    this.layer.addChild(this.shadow, this.logo, this.ballC);
    root.addChild(this.layer);
    this.h.stadium.filters = [this.stadiumBlur];
    // logo: in the reserved upper area of the 9:16 composition, 86 % of its width
    // (the visible width: on narrow phones the stadium is cropped on the sides)
    const visW = Math.min(comp.w, W);
    const lw = Math.min(visW * 0.84, comp.h * 0.42);
    const ls = lw / this.logo.texture.width;
    this.logo.scale.set(ls);
    const lx = W / 2, ly = comp.y + comp.h * 0.17;
    this.logo.position.set(lx, ly);
    const lh = this.logo.texture.height * ls;
    // the ball sits exactly in the logo's socket: same position, same size
    const bx0 = lx - lw / 2 + LOGO_BALL.cx * lw;
    const by0 = ly - lh / 2 + LOGO_BALL.cy * lh;
    const d0 = 2 * LOGO_BALL.r * lw;
    this.ballC.position.set(bx0, by0);
    this.setBallD(d0);
    this.logo.alpha = this.ballC.alpha = 0;
    const res: CinematicResult = { usedClip: false, skipped: false, bounces: 0, continuity: { logoBallX: bx0, logoBallY: by0, fallStartX: 0, fallStartY: 0, dStart: 0, dLogo: d0 }, occludedAt: 0, totalMs: 0 };
    const speed0 = tw.speed;
    tw.speed = () => (this.skipping ? 8 : 1) * speed0();

    // ---- S1: the logo, perfectly sharp, stable camera (0.35 s in, 0.75 s hold)
    this.qa.phase = 'logo';
    await tw.tween(350, (u) => (this.logo.alpha = this.ballC.alpha = ease.outCubic(u)));
    await tw.wait(750);

    // ---- S2a: the ball leaves its socket (a short lift, the rest of the logo fades out discreetly)
    this.qa.phase = 'detach';
    const lift = d0 * 0.22;
    void tw.tween(520, (u) => (this.logo.alpha = 1 - ease.inOutCubic(u)));
    await tw.tween(240, (u) => {
      this.ballC.y = by0 - lift * ease.outCubic(u);
      this.ballC.rotation = -0.12 * ease.outCubic(u);
    });
    res.continuity.fallStartX = this.ballC.x;
    res.continuity.fallStartY = this.ballC.y;
    res.continuity.dStart = d0;

    // ---- S2b: free fall onto the court (gravity: y ~ t^2), progressive photographic look.
    // The camera follows the fall: a slight push / tilt down onto the court (CAMERA_REST), while the
    // logo, already fading, goes up out of frame with the stadium.  The ball keeps the small horizontal
    // speed that brings it, after its bounces, to rest exactly at the hand-off point (BALL_REST or the clip's).
    this.qa.phase = 'fall';
    const Z = CAMERA_REST.zoom;
    const A = { x: comp.x + comp.w * CAMERA_REST.ax, y: comp.y + comp.h * CAMERA_REST.ay };
    const setCam = (k: number) => {
      const z = 1 + (Z - 1) * k;
      root.scale.set(z);
      root.position.set(A.x * (1 - z), A.y * (1 - z));
    };
    // hand-off point: screen-space fractions of the composition (= of the 9:16 clip frame) -> intro-root space
    const restFrame = opts.clip ? clipRect(comp, opts.clip) : comp;
    const rs = opts.clip ? opts.clip.ball : BALL_REST;
    const toLocal = (sx: number, sy: number) => ({ x: A.x + (sx - A.x) / Z, y: A.y + (sy - A.y) / Z });
    const restL = toLocal(restFrame.x + rs.x * restFrame.w, restFrame.y + rs.y * restFrame.h);
    const dGround = (rs.d * restFrame.w) / Z;
    const groundY = restL.y + dGround / 2; // contact line on the court
    const yTop = this.ballC.y;
    const xTop = this.ballC.x;
    const fallMs = 640;
    const shadowAt = (x: number, ballBottom: number, d: number) => {
      const hgt = Math.max(0, groundY - ballBottom);
      const k = 1 - Math.min(1, hgt / (comp.h * 0.6));
      this.shadow.clear().ellipse(x, groundY + d * 0.06, d * (0.32 + 0.22 * k), d * (0.07 + 0.05 * k)).fill({ color: 0x020812, alpha: 0.18 + 0.4 * k });
    };
    const groundCenter = (d: number) => groundY - d / 2;
    // restitution ~0.55 on a hard court: each rebound reaches ~30 % of the previous height
    const fallH = groundCenter(dGround) - yTop;
    const hops = [0.3, 0.09, 0.025].map((r) => ({ h: fallH * r, ms: 2 * Math.sqrt(r) * fallMs }));
    const rollMs = 300;
    // constant horizontal speed over the flight, then a decelerating roll (the last 18 % of the distance)
    const flightMs = fallMs + hops.reduce((s, x) => s + x.ms, 0);
    const xFlightEnd = xTop + (restL.x - xTop) * 0.82;
    let flightT = 0;
    const xAt = (dt: number) => {
      flightT += dt;
      return xTop + (xFlightEnd - xTop) * Math.min(1, flightT / flightMs);
    };
    let prevU = 0;
    const camMs = fallMs + hops[0].ms;
    void tw.tween(camMs, (u) => setCam(ease.inOutCubic(u)));
    await tw.tween(fallMs, (u) => {
      const d = d0 + (dGround - d0) * u;
      this.setBallD(d);
      this.ballC.x = xAt((u - prevU) * fallMs);
      prevU = u;
      this.ballC.y = yTop + (groundCenter(d) - yTop) * u * u;
      this.ballC.rotation -= 0.035;
      // the illustrated ball becomes the photographic ball (same object, same place, same size)
      const m = Math.min(1, u / 0.45);
      this.photoBall.alpha = ease.inOutCubic(m);
      this.cutBall.alpha = 1 - ease.inOutCubic(m);
      shadowAt(this.ballC.x, this.ballC.y + d / 2, d);
    });
    const impact = async (vol: number) => {
      res.bounces++;
      this.qa.bounces++;
      audio.play('bounce', { volume: vol });
      await tw.tween(70 * Math.max(0.5, vol), (u) => {
        const q = Math.sin(u * Math.PI);
        this.ballC.scale.set(1 + 0.07 * q * vol, 1 - 0.1 * q * vol);
        this.ballC.y = groundCenter(dGround) + dGround * 0.05 * q * vol;
      });
      this.ballC.scale.set(1);
    };
    const hop = async (height: number, ms: number) => {
      let p = 0;
      const step = (u: number) => {
        this.ballC.x = xAt((u - p) * (ms / 2));
        p = u;
        this.ballC.rotation -= 0.02;
        shadowAt(this.ballC.x, this.ballC.y + dGround / 2, dGround);
      };
      await tw.tween(ms / 2, (u) => {
        this.ballC.y = groundCenter(dGround) - height * (1 - (1 - u) * (1 - u));
        step(u);
      });
      p = 0;
      await tw.tween(ms / 2, (u) => {
        this.ballC.y = groundCenter(dGround) - height * (1 - u * u);
        step(u);
      });
    };
    const vols = [0.85, 0.5, 0.28];
    for (let i = 0; i < hops.length; i++) {
      await impact(vols[i]);
      if (i === 0) this.qa.phase = 'bounce';
      await hop(hops[i].h, hops[i].ms);
    }
    await impact(0.14);
    // ---- the ball rolls a little and comes to rest at the hand-off point
    this.qa.phase = 'roll';
    const xr0 = this.ballC.x;
    await tw.tween(rollMs, (u) => {
      const k = ease.outCubic(u);
      const nx = xr0 + (restL.x - xr0) * k;
      this.ballC.rotation += ((nx - this.ballC.x) / (dGround / 2)) * 1;
      this.ballC.x = nx;
      this.ballC.y = groundCenter(dGround);
      shadowAt(this.ballC.x, this.ballC.y + dGround / 2, dGround);
    });
    this.ballC.position.set(restL.x, groundCenter(dGround));
    setCam(1);
    this.qa.phase = 'rest';
    res.rest = this.screenBall(restFrame);

    // ---- S3–S5: external player clip, if provided (its first frame = this exact frame)
    if (opts.clip && opts.video && !this.skipping) {
      res.usedClip = await this.playClip(opts.clip, opts.video, opts.onOcclude, res);
      if (res.usedClip) {
        res.totalMs = performance.now() - this.t0;
        tw.speed = speed0;
        return res;
      }
    }

    // ---- without the clip: the camera pushes in on the SAME ball until it fills the frame
    // (no stand-in character is ever drawn)
    await tw.wait(this.skipping ? 0 : 220);
    this.qa.phase = 'push';
    const fx = this.ballC.x, fy = this.ballC.y;
    const z0 = root.scale.x;
    const sx0 = root.x + fx * z0, sy0 = root.y + fy * z0;
    const fullD = 2.3 * Math.hypot(W, H);
    const z1 = fullD / dGround;
    void tw.tween(420, (u) => (this.stadiumBlur.strength = 14 * u));
    await tw.tween(this.skipping ? 160 : 700, (u) => {
      const k = Math.pow(u, 2.2);
      const z = z0 + (z1 - z0) * k;
      root.scale.set(z);
      // the ball comes towards the lens and drifts to the frame centre
      const cx = sx0 + (W / 2 - sx0) * k, cy = sy0 + (H / 2 - sy0) * k;
      root.position.set(cx - fx * z, cy - fy * z);
      this.shadow.alpha = 1 - k;
    });
    res.ending = 'push';
    this.occlude(opts.onOcclude, res);
    await this.clearFrame(root);
    res.totalMs = performance.now() - this.t0;
    tw.speed = speed0;
    return res;
  }

  /** QA: the ball's on-screen position and diameter, as fractions of `frame` (x, y of height; d of width) */
  private screenBall(frame: Rect) {
    const g = this.ballC.getGlobalPosition();
    const z = this.h.root.scale.x;
    const d = (this.photoBall.width * PHOTO_FILL) * z;
    return { x: (g.x - frame.x) / frame.w, y: (g.y - frame.y) / frame.h, d: d / frame.w };
  }

  /** S6: the frame is fully covered by the ball -> the real reels are switched in underneath */
  private occlude(onOcclude: () => void, res: CinematicResult) {
    this.qa.phase = 'occluded';
    res.occludedAt = performance.now() - this.t0;
    // only the ball stays in the intro canvas; the stadium image goes away under it
    for (const c of this.h.root.children) if (c !== this.layer) c.visible = false;
    this.logo.visible = false;
    this.shadow.visible = false;
    onOcclude();
  }

  /** the ball leaves the lens: it keeps growing slightly and clears, revealing the reels */
  private async clearFrame(root: Container) {
    this.qa.phase = 'reveal';
    const z0 = root.scale.x;
    const p0 = { x: root.position.x, y: root.position.y };
    const W = this.h.app.screen.width, H = this.h.app.screen.height;
    await this.h.tw.tween(260, (u) => {
      const z = z0 * (1 + 0.35 * u);
      root.scale.set(z);
      root.position.set(W / 2 - (W / 2 - p0.x) * (z / z0), H / 2 - (H / 2 - p0.y) * (z / z0));
      this.layer.alpha = 1 - ease.inCubic(u);
    });
    this.layer.visible = false;
  }

  /** S3–S5 from an external clip.  Its first frame (`handoffAt`) shows the stadium with the ball at rest
   *  exactly where the HTML5 ball lies: a short cross-fade hands over.  Sound cues follow the clip's clock.
   *  End: `exit` mode (the HTML5 ball takes the ball over and rushes to the lens over the frozen clip)
   *  or `occludedAt` mode (the clip's own ball fills the frame).  Returns false if the clip cannot start. */
  private async playClip(clip: ServeClip, video: HTMLVideoElement, onOcclude: () => void, res: CinematicResult): Promise<boolean> {
    const { tw, comp, root } = this.h;
    try {
      video.muted = true; // the sounds are played by the game, in sync with the clip timeline
      video.playsInline = true;
      video.currentTime = clip.handoffAt;
      await video.play();
    } catch {
      return false;
    }
    this.qa.phase = 'clip';
    const sp = new Sprite(Texture.from(video));
    // the clip covers the 9:16 composition in SCREEN space; the camera (root) is static now,
    // so the sprite gets the inverse camera transform
    const fr = clipRect(comp, clip);
    const z = root.scale.x;
    const toL = (x: number, y: number) => ({ x: (x - root.x) / z, y: (y - root.y) / z });
    const p = toL(fr.x, fr.y);
    sp.position.set(p.x, p.y);
    sp.scale.set(fr.w / clip.width / z);
    sp.alpha = 0;
    const blur = new BlurFilter({ strength: 0, quality: 3 });
    sp.filters = [blur];
    root.addChildAt(sp, root.getChildIndex(this.layer));
    // same frame, same ball: an imperceptible cross-fade
    await tw.tween(120, (u) => {
      sp.alpha = u;
      this.ballC.alpha = this.shadow.alpha = 1 - u;
    });
    this.ballC.visible = false;
    this.ballC.alpha = 1;
    this.h.stadium.visible = false;
    const cues = [...(clip.cues ?? []), { t: clip.contactAt, sound: 'racket' as const, volume: 1 }].sort((a, b) => a.t - b.t);
    let next = 0;
    const endAt = clip.exit ? clip.exit.at : clip.occludedAt;
    let lastT = -1, lastMove = performance.now();
    const stalled = await new Promise<boolean>((resolve) => {
      const tick = () => {
        const t = video.currentTime;
        while (next < cues.length && t >= cues[next].t) {
          audio.play(cues[next].sound, { volume: cues[next].volume ?? 1 });
          next++;
          res.cues = next;
        }
        if (t !== lastT) {
          lastT = t;
          lastMove = performance.now();
        }
        const stall = performance.now() - lastMove > 2500; // network or decoder stall: never block the player
        if (t >= endAt || video.ended || this.skipping || stall) {
          this.h.app.ticker.remove(tick);
          resolve(stall);
        }
      };
      this.h.app.ticker.add(tick);
    });
    video.pause();
    res.clipStalled = stalled;
    const W = this.h.app.screen.width, H = this.h.app.screen.height;
    const fullD = (2.3 * Math.hypot(W, H)) / z;
    this.photoBall.alpha = 1;
    this.cutBall.alpha = 0;
    this.ballC.rotation = 0;
    this.ballC.visible = true;
    if (clip.exit && !this.skipping && !stalled) {
      res.ending = 'exit';
      // exit mode: the frame is frozen on the struck ball; the HTML5 ball covers it exactly and rushes to the lens
      this.qa.phase = 'exit';
      const e = clip.exit;
      const s0 = toL(fr.x + e.x * fr.w, fr.y + e.y * fr.h);
      const d0 = (e.d * fr.w) / z;
      const c = toL(W / 2, H / 2);
      this.ballC.position.set(s0.x, s0.y);
      this.setBallD(d0);
      const bb = new BlurFilter({ strength: 0, quality: 2 });
      this.ballC.filters = [bb];
      await tw.tween(e.ms ?? 320, (u) => {
        // apparent size ~ 1 / distance: slow growth then a rush into the lens
        const k = ease.inCubic(u);
        const d = Math.min(fullD, d0 / Math.max(0.001, 1 - 0.995 * k));
        this.setBallD(d);
        this.ballC.position.set(s0.x + (c.x - s0.x) * k, s0.y + (c.y - s0.y) * k);
        bb.strength = 6 * Math.sin(u * Math.PI);
        blur.strength = 10 * k;
      });
      this.ballC.filters = [];
    }
    res.ending ??= 'occludedAt';
    // the ball covers the frame: full-frame photographic ball, the reels go in underneath
    const cc = toL(W / 2, H / 2);
    this.ballC.position.set(cc.x, cc.y);
    this.setBallD(fullD);
    sp.visible = false;
    this.occlude(onOcclude, res);
    await this.clearFrame(root);
    return true;
  }
}

/** The clip frame (cover of the composition, centred), in screen space. */
export function clipRect(comp: Rect, clip: { width: number; height: number }): Rect {
  const s = Math.max(comp.w / clip.width, comp.h / clip.height);
  return { x: comp.x + (comp.w - clip.width * s) / 2, y: comp.y + (comp.h - clip.height * s) / 2, w: clip.width * s, h: clip.height * s };
}
