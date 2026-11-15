// Orchestrates one round: RGS play -> present the returned book -> end round.
import { audio } from '../audio/audio';
import type { DemoRgs, ForcedScenario } from '../rgs/demoRgs';
import { RgsError, validateRound, type RgsClient, type Round } from '../rgs/types';
import type { RallyScene } from '../render/scene';
import { playBook, type Hud } from './player';
import { game } from './state.svelte';

export class Controller {
  lastRound: Round | null = null;
  private hud: Hud = {
    setWin: (a) => (game.win = a),
    setFreeSpins: (c, t) => {
      game.fsCurrent = c;
      game.fsTotal = t;
    },
    setMultiplier: (m) => (game.multiplier = m),
    setInBonus: (on) => (game.inBonus = on),
  };

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
    this.scene.setBoard([0, 0, 0, 0, 0], 'basegame');
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

  async spin(force: ForcedScenario = null) {
    if (!this.canSpin()) return;
    if (game.bet > game.balance) {
      game.notice = game.t.insufficient;
      setTimeout(() => (game.notice = null), 2500);
      return;
    }
    const started = performance.now();
    game.phase = 'spinning';
    game.win = 0;
    game.banner = null;
    try {
      if (force && this.rgs.kind === 'demo') {
        (this.rgs as DemoRgs).forceNext = force;
        game.banner = game.t.forcedBanner;
      }
      const { balance, round } = await this.rgs.play(game.bet, 'BASE');
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
    }
  }

  private async present(round: Round, quick: boolean) {
    this.scene.bet = round.amount;
    await playBook(round.state, this.scene, this.hud, { bet: round.amount, quick });
  }

  private record(round: Round) {
    game.addHistory({
      id: round.betID,
      time: Date.now(),
      bet: round.amount,
      win: round.payout,
      payoutMultiplier: round.payoutMultiplier,
      bonus: round.state.some((e) => e.type === 'freeSpinTrigger'),
      forced: round.forced,
      events: round.state,
    });
  }

  /** Faithful replay of a past round from its stored book.  Purely visual. */
  async replay(entryIndex: number) {
    const e = game.history[entryIndex];
    if (!e || game.phase !== 'idle') return;
    game.modal = null;
    game.phase = 'replay';
    game.banner = game.t.replaying;
    const savedWin = game.win;
    try {
      this.scene.bet = e.bet;
      await playBook(e.events, this.scene, this.hud, { bet: e.bet });
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
