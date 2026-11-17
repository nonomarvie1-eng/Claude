// ACE! — opening cinematic (HTML5 / PixiJS part).
//
// One ball, one stadium, one continuous camera:
//   S1  the official stadium, the ACE! logo in the foreground, stable camera;
//   S2  the ball of the "!" leaves its socket (the rest of the logo fades out),
//       falls onto the court and bounces (gravity, restitution, contact
//       shadow, squash), turning progressively into the photographic ball;
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
  /** clip time from which the ball covers the whole frame */
  occludedAt: number;
}

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

    // ---- S2b: free fall onto the court (gravity: y ~ t^2), progressive photographic look
    this.qa.phase = 'fall';
    const groundY = comp.y + comp.h * 0.86; // foreground court, in front of the baseline
    const dGround = Math.min(d0 * 1.35, visW * 0.16); // slight growth: the ball comes nearer to the camera
    const yTop = this.ballC.y;
    const fallMs = 640;
    const shadowAt = (x: number, ballBottom: number, d: number) => {
      const hgt = Math.max(0, groundY - ballBottom);
      const k = 1 - Math.min(1, hgt / (comp.h * 0.6));
      this.shadow.clear().ellipse(x, groundY + d * 0.06, d * (0.32 + 0.22 * k), d * (0.07 + 0.05 * k)).fill({ color: 0x020812, alpha: 0.18 + 0.4 * k });
    };
    const groundCenter = (d: number) => groundY - d / 2;
    await tw.tween(fallMs, (u) => {
      const d = d0 + (dGround - d0) * u;
      this.setBallD(d);
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
      const sx = this.photoBall.scale.x;
      await tw.tween(70, (u) => {
        const q = Math.sin(u * Math.PI);
        this.ballC.scale.set(1 + 0.07 * q * vol, 1 - 0.1 * q * vol);
        this.ballC.y = groundCenter(dGround) + dGround * 0.05 * q * vol;
      });
      this.ballC.scale.set(1);
      void sx;
    };
    const hop = async (height: number, ms: number) => {
      await tw.tween(ms / 2, (u) => {
        this.ballC.y = groundCenter(dGround) - height * (1 - (1 - u) * (1 - u));
        this.ballC.rotation -= 0.02;
        shadowAt(this.ballC.x, this.ballC.y + dGround / 2, dGround);
      });
      await tw.tween(ms / 2, (u) => {
        this.ballC.y = groundCenter(dGround) - height * (1 - u * u);
        this.ballC.rotation -= 0.02;
        shadowAt(this.ballC.x, this.ballC.y + dGround / 2, dGround);
      });
    };
    // restitution ~0.55 on a hard court: each rebound reaches ~30 % of the previous height
    const fallH = groundCenter(dGround) - yTop;
    await impact(0.85);
    this.qa.phase = 'bounce';
    await hop(fallH * 0.3, 2 * Math.sqrt(0.3) * fallMs);

    // ---- S3–S5: external player clip, if provided
    if (opts.clip && opts.video && !this.skipping) {
      res.usedClip = await this.playClip(opts.clip, opts.video, dGround, opts.onOcclude, res);
      if (res.usedClip) {
        res.totalMs = performance.now() - this.t0;
        tw.speed = speed0;
        return res;
      }
    }

    // ---- without the clip: the camera pushes in on the SAME ball until it fills the frame
    await impact(0.5);
    this.qa.phase = 'push';
    const fx = this.ballC.x, fy = this.ballC.y;
    const fullD = 2.3 * Math.hypot(W, H);
    const z1 = fullD / dGround;
    void tw.tween(420, (u) => (this.stadiumBlur.strength = 14 * u));
    await tw.tween(this.skipping ? 160 : 700, (u) => {
      const k = Math.pow(u, 2.2);
      const z = 1 + (z1 - 1) * k;
      root.scale.set(z);
      // keep the ball on its spot while it comes towards the lens, drift it to the frame centre
      const cx = fx + (W / 2 - fx) * k, cy = fy + (H / 2 - fy) * k;
      root.position.set(cx - fx * z, cy - fy * z);
      this.shadow.alpha = 1 - k;
    });
    this.occlude(opts.onOcclude, res);
    await this.clearFrame(root);
    res.totalMs = performance.now() - this.t0;
    tw.speed = speed0;
    return res;
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

  /** S3–S5 from an external clip: hand the ball over at `handoffAt`, impact sound at
   *  `contactAt`, occlusion at `occludedAt`.  Returns false if the clip cannot play. */
  private async playClip(clip: ServeClip, video: HTMLVideoElement, dGround: number, onOcclude: () => void, res: CinematicResult): Promise<boolean> {
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
    const tex = Texture.from(video);
    const sp = new Sprite(tex);
    // cover the 9:16 composition rectangle (same framing as the stadium image)
    const s = Math.max(comp.w / clip.width, comp.h / clip.height);
    sp.scale.set(s);
    sp.position.set(comp.x + (comp.w - clip.width * s) / 2, comp.y + (comp.h - clip.height * s) / 2);
    sp.alpha = 0;
    root.addChildAt(sp, root.getChildIndex(this.layer));
    // the HTML5 ball moves to the clip's ball (position and size at handoffAt), then the clip takes over
    const tx = sp.x + clip.ball.x * clip.width * s, ty = sp.y + clip.ball.y * clip.height * s, td = clip.ball.d * clip.width * s;
    const x0 = this.ballC.x, y0 = this.ballC.y;
    await tw.tween(160, (u) => {
      this.ballC.x = x0 + (tx - x0) * u;
      this.ballC.y = y0 + (ty - y0) * u;
      this.setBallD(dGround + (td - dGround) * u);
      sp.alpha = u;
      this.shadow.alpha = 1 - u;
    });
    this.ballC.visible = false;
    this.h.stadium.visible = false;
    let contacted = false;
    await new Promise<void>((resolve) => {
      const tick = () => {
        if (!contacted && video.currentTime >= clip.contactAt) {
          contacted = true;
          audio.play('racket', { volume: 1 });
        }
        if (video.currentTime >= clip.occludedAt || video.ended || this.skipping) {
          this.h.app.ticker.remove(tick);
          resolve();
        }
      };
      this.h.app.ticker.add(tick);
    });
    // the clip's ball covers the frame: the photographic ball overlay takes the same full-frame cover, reels go in underneath
    const W = this.h.app.screen.width, H = this.h.app.screen.height;
    this.ballC.visible = true;
    this.ballC.alpha = 1;
    this.photoBall.alpha = 1;
    this.cutBall.alpha = 0;
    this.ballC.position.set(W / 2, H / 2);
    this.setBallD(2.3 * Math.hypot(W, H));
    video.pause();
    sp.visible = false;
    this.occlude(onOcclude, res);
    await this.clearFrame(root);
    return true;
  }
}
