// Orchestrates one round: RGS play -> present the returned book -> end round.
import { audio } from '../audio/audio';
import type { DemoRgs, ForcedScenario } from '../rgs/demoRgs';
import { RgsError, validateRound, type RgsClient, type Round } from '../rgs/types';
import type { RallyScene } from '../render/scene';
import { playBook, type Hud } from './player';
import { game } from './state.svelte';
import { RULES } from '../engine/rules';
import type { ModeName } from '../engine/types';
import { PROTO, playProtoRound, type ProtoMode } from '../engine/rallyPath';
import { cryptoDrawer, listDrawer } from '../engine/rng';
import { FINAL_SET_BUILD, GOLDEN_SERVE_BUILD, RALLY_PATH_BUILD } from '../engine/gameplay';

export interface AutoplayConfig {
  count: number;
  lossLimit: number; // money units; autoplay stops once net loss reaches it
  singleWinLimit: number | null; // stop when one round wins at least this
  stopOnBonus: boolean;
}

export class Controller {
  lastRound: Round | null = null;
  // HUD adapter: values come verbatim from the book events; the Tie-Break
  // panel drawn by the scene mirrors the same values.
  private hud: Hud = {
    setWin: (a) => {
      game.win = a;
      this.syncPanel();
    },
    setFreeSpins: (c, t) => {
      game.fsCurrent = c;
      game.fsTotal = t;
      this.syncPanel();
    },
    setMultiplier: (m) => {
      game.multiplier = m;
      this.syncPanel();
    },
    setInBonus: (on) => {
      game.inBonus = on;
      this.syncPanel();
    },
    setBonusLevel: (level) => (game.bonusLevel = level),
    setPoints: (points, lastShot) => {
      game.points = points;
      game.lastShot = lastShot;
      this.syncPanel();
    },
  };

  private syncPanel() {
    if (game.inBonus) this.scene.setBonusInfo(game.fsCurrent, game.fsTotal, game.points, game.win);
  }

  constructor(public rgs: RgsClient, public scene: RallyScene) {}

  async boot() {
    const auth = await this.rgs.authenticate();
    game.balance = auth.balance.amount;
    game.currency = auth.balance.currency;
    game.betLevels = auth.config.betLevels;
    game.jurisdiction = auth.config.jurisdiction ?? {};
    game.isDemo = this.rgs.kind === 'demo';
    if (!game.betLevels.includes(game.bet)) game.bet = auth.config.defaultBetLevel ?? game.betLevels[0];
    if (game.jurisdiction.disabledTurbo) game.prefs.turbo = false;
    this.scene.currency = game.currency;
    this.scene.gsMode = GOLDEN_SERVE_BUILD;
    this.scene.setStrings(game.t); // rebuild the bonus panel with this build's labels
    this.scene.setProto(RALLY_PATH_BUILD);
    this.scene.setBoard(new Array(RULES.reels).fill(0), 'basegame');
    if (auth.round && auth.round.active) {
      // interrupted round (reload, crash, network loss): show it, then close it
      game.notice = game.t.interruptedResume;
      await this.present(validateRound(auth.round), true);
      const end = await this.rgs.endRound();
      game.balance = end.balance.amount;
      this.record(auth.round);
      game.notice = null;
    }
  }

  canSpin() {
    return game.phase === 'idle' && !game.modal && !game.error;
  }

  /** Direct buy of a bonus level (explicit mode; never random between levels). */
  async buyBonus(mode: 'buy_rally' | 'buy_final') {
    if (game.jurisdiction.disabledBuyBonus || !FINAL_SET_BUILD) return;
    await this.spin(null, mode);
  }

  private inFlight = false;

  /** One round in `mode` (default: the spin mode selected by the player). */
  async spin(force: ForcedScenario = null, mode: ModeName = game.spinMode) {
    if (!this.canSpin() || this.inFlight) return; // no accidental double debit
    if (game.labOn && this.rgs.kind === 'demo' && !force && mode === game.spinMode) return this.labRound('base');
    const cost = RULES.modes[mode].cost;
    if (Math.round(game.bet * cost) > game.balance) {
      game.notice = game.t.insufficient;
      setTimeout(() => (game.notice = null), 2500);
      return;
    }
    this.inFlight = true;
    const started = performance.now();
    game.phase = 'spinning';
    game.win = 0;
    game.banner = null;
    try {
      // nothing from the previous round may stay on screen
      this.scene.resetRound();
      if (this.rgs.kind === 'demo') (this.rgs as DemoRgs).concept = game.concept;
      if (force && this.rgs.kind === 'demo') {
        (this.rgs as DemoRgs).forceNext = force;
        game.banner = game.t.forcedBanner;
      }
      if (mode === 'buy_rally') game.banner = game.t.buyBannerTb;
      if (mode === 'buy_final') game.banner = game.t.buyBannerStb;
      const { balance, round } = await this.rgs.play(game.bet, mode);
      round.cost = round.cost ?? cost;
      round.mode = round.mode ?? mode;
      game.balance = balance.amount;
      validateRound(round);
      this.lastRound = round;
      if (this.rgs.kind === 'demo') exposeForQA(round, game.bet);
      await this.present(round, false);
      if (round.active !== false) {
        const end = await this.rgs.endRound();
        game.balance = end.balance.amount;
      }
      this.record(round);
    } catch (e) {
      this.fail(e);
    } finally {
      const minMs = game.jurisdiction.minimumRoundDuration ?? 0;
      const left = minMs - (performance.now() - started);
      if (left > 0) await new Promise((r) => setTimeout(r, left));
      if (game.phase === 'spinning') game.phase = 'idle';
      this.inFlight = false;
    }
  }

  /** Rally Path LAB (demo only): one prototype round, never debited nor credited.
   *  scenario = recorded draws from shared/rally-path-proto.json (exact replay). */
  async labRound(mode: ProtoMode, scenario: string | null = null) {
    if (this.rgs.kind !== 'demo' || !this.canSpin() || this.inFlight) return;
    this.inFlight = true;
    game.modal = null;
    game.phase = 'spinning';
    game.win = 0;
    game.banner = game.t.labBanner;
    const savedWin = game.win;
    try {
      this.scene.setProto(true);
      const sc = scenario ? PROTO.scenarios[scenario] : null;
      const r = playProtoRound(sc ? listDrawer(sc.draws) : cryptoDrawer, sc ? sc.mode : mode);
      (window as unknown as { __rallyLab: unknown }).__rallyLab = { mode: sc ? sc.mode : mode, scenario, events: r.events, bet: game.bet };
      this.scene.bet = game.bet;
      await playBook(r.events, this.scene, this.hud, { bet: game.bet, cost: 1 });
    } catch (e) {
      this.fail(e);
    } finally {
      game.banner = null;
      game.win = savedWin;
      if (game.phase === 'spinning') game.phase = 'idle';
      this.inFlight = false;
    }
  }

  private async present(round: Round, quick: boolean) {
    this.scene.setProto(RALLY_PATH_BUILD);
    this.scene.bet = round.amount;
    await playBook(round.state, this.scene, this.hud, { bet: round.amount, cost: round.cost ?? 1, quick, mode: (round.mode as ModeName) ?? 'base' });
  }

  private record(round: Round) {
    game.addHistory({
      id: round.betID,
      time: Date.now(),
      bet: round.amount,
      cost: round.cost ?? 1,
      mode: (round.mode as ModeName) ?? 'base',
      win: round.payout,
      payoutMultiplier: round.payoutMultiplier,
      bonus: round.state.some((e) => e.type === 'bonusStart' || e.type === 'protoBonusStart' || e.type === 'gsBonusStart'),
      forced: round.forced,
      events: round.state,
    });
  }

  /** Autoplay with mandatory loss limit.  Every round is still a separate,
   *  independent RGS round; autoplay only presses the button for the player. */
  private stopRequested = false;

  async autoplay(cfg: AutoplayConfig) {
    if (game.jurisdiction.disabledAutoplay || !this.canSpin()) return;
    this.stopRequested = false;
    const start = game.balance;
    game.autoplay = { remaining: cfg.count };
    try {
      while (game.autoplay && game.autoplay.remaining > 0 && !this.stopRequested) {
        if (Math.round(game.bet * RULES.modes[game.spinMode].cost) > game.balance) break;
        game.autoplay = { remaining: game.autoplay.remaining - 1 };
        await this.spin();
        if (game.phase !== 'idle') break; // error or interruption
        const r = this.lastRound;
        if (start - game.balance >= cfg.lossLimit) break;
        if (r && cfg.stopOnBonus && r.state.some((e) => e.type === 'bonusStart' || e.type === 'protoBonusStart' || e.type === 'gsBonusStart')) break;
        if (r && cfg.singleWinLimit !== null && r.payout >= cfg.singleWinLimit) break;
        await new Promise((res) => setTimeout(res, game.prefs.turbo ? 150 : 350));
      }
    } finally {
      game.autoplay = null;
      this.stopRequested = false;
    }
  }

  stopAutoplay() {
    this.stopRequested = true;
    if (game.autoplay) game.autoplay = { remaining: 0 };
  }

  /** Replays the last finished round (wins shown again, no effect on balance). */
  async replayLast() {
    if (game.history.length) await this.replay(0);
  }

  /** Faithful replay of a past round from its stored book.  Purely visual. */
  async replay(entryIndex: number) {
    const e = game.history[entryIndex];
    if (!e || game.phase !== 'idle') return;
    game.modal = null;
    game.phase = 'replay';
    game.banner = game.t.replaying;
    const savedWin = game.win;
    this.scene.resetRound();
    try {
      this.scene.bet = e.bet;
      await playBook(e.events, this.scene, this.hud, { bet: e.bet, cost: e.cost ?? 1, mode: e.mode ?? 'base' });
    } finally {
      game.banner = null;
      game.win = savedWin;
      game.phase = 'idle';
    }
  }

  private fail(e: unknown) {
    const t = game.t;
    if (e instanceof RgsError) {
      if (e.code === 'ERR_IPB') {
        game.notice = t.insufficient;
        setTimeout(() => (game.notice = null), 2500);
        return;
      }
      if (e.code === 'ERR_IS' || e.code === 'ERR_ATE') {
        game.error = { message: t.sessionError, retryable: false, fatal: true };
      } else if (e.code === 'ERR_NETWORK' || e.code === 'ERR_TIMEOUT') {
        game.error = { message: t.networkError, retryable: true, fatal: false };
      } else if (e.code === 'ERR_DATA') {
        game.error = { message: t.dataError, retryable: true, fatal: false };
      } else {
        game.error = { message: `${t.genericError} (${e.code})`, retryable: true, fatal: false };
      }
    } else {
      console.error(e);
      game.error = { message: t.genericError, retryable: true, fatal: false };
    }
    game.phase = 'error';
    audio.stopLoop('spin_loop');
  }

  /** Retry after an error: re-authenticate, which resumes any active round. */
  async retry() {
    game.error = null;
    game.phase = 'spinning';
    try {
      await this.boot();
      game.phase = 'idle';
    } catch (e) {
      this.fail(e);
    }
  }
}

/** Demo/QA hook used by the automated browser tests to compare what is
 *  displayed with the round actually returned.  Not present with a real RGS. */
function exposeForQA(round: Round, bet: number) {
  (window as unknown as { __rally: unknown }).__rally = { lastRound: round, bet };
}
