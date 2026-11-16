<script lang="ts">
  import { onMount } from 'svelte';
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import { audio } from '../audio/audio';
  import type { Controller } from '../game/controller';
  import { RULES } from '../engine/rules';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const busy = $derived(game.phase !== 'idle');
  const idx = $derived(game.betLevels.indexOf(game.bet));
  const social = $derived(!!game.jurisdiction.socialCasino);
  const canBuy = $derived(!game.jurisdiction.disabledBuyBonus && !game.inBonus);
  const canAuto = $derived(!game.jurisdiction.disabledAutoplay && !game.inBonus);

  let topEl: HTMLDivElement;
  let hudEl: HTMLDivElement;

  // The scene lays the reels out between the top bar and the HUD: no control
  // is ever drawn over the symbols.
  onMount(() => {
    const measure = () => {
      if (!topEl || !hudEl) return;
      const W = window.innerWidth, H = window.innerHeight;
      const tb = topEl.getBoundingClientRect();
      const hb = hudEl.getBoundingClientRect();
      // bars spanning the width reserve height; side columns (short landscape) reserve width
      const topRow = tb.width > W * 0.5;
      const hudRow = hb.width > W * 0.5;
      game.insets = {
        top: topRow ? Math.round(tb.bottom) : 0,
        left: topRow ? 0 : Math.round(tb.right),
        bottom: hudRow ? Math.round(H - hb.top) : 0,
        right: hudRow ? 0 : Math.round(W - hb.left),
      };
    };
    const ro = new ResizeObserver(measure);
    ro.observe(topEl);
    ro.observe(hudEl);
    window.addEventListener('resize', measure);
    measure();
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', measure);
    };
  });

  function changeBet(d: number) {
    if (busy) return;
    const i = Math.min(game.betLevels.length - 1, Math.max(0, idx + d));
    game.bet = game.betLevels[i];
    audio.play('button', { volume: 0.5 });
  }
  function open(m: 'paytable' | 'settings' | 'history' | 'buy' | 'auto') {
    if (game.phase === 'spinning' || game.phase === 'replay') return;
    audio.play('button', { volume: 0.5 });
    game.modal = m;
  }
  function toggleSound() {
    game.prefs.sound = !game.prefs.sound;
  }
  function fullscreen() {
    const d = document as Document & { webkitFullscreenElement?: Element };
    if (d.fullscreenElement || d.webkitFullscreenElement) void document.exitFullscreen?.();
    else void document.documentElement.requestFullscreen?.().catch(() => {});
  }
</script>

<div class="top" bind:this={topEl}>
  {#if game.isDemo}<span class="demo" data-testid="demo-badge">{t.demoBadge}</span>{/if}
  <nav aria-label="menu">
    <button class="icon" onclick={() => open('paytable')} aria-label={t.paytable} title={t.paytable} data-testid="btn-paytable">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 10.5V17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="7.3" r="1.2" fill="currentColor"/></svg>
    </button>
    <button class="icon" onclick={() => open('history')} aria-label={t.history} title={t.history} data-testid="btn-history">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
    </button>
    <button class="icon" onclick={() => open('settings')} aria-label={t.settings} title={t.settings} data-testid="btn-settings">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="16" cy="7" r="2.2" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="10" cy="17" r="2.2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
    </button>
    <button class="icon" onclick={toggleSound} aria-label={t.sound} aria-pressed={game.prefs.sound} title={t.sound} data-testid="btn-sound">
      {#if game.prefs.sound}
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z" fill="currentColor"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      {:else}
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z" fill="currentColor"/><path d="m16 9.5 5 5m0-5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      {/if}
    </button>
    {#if !game.jurisdiction.disabledFullscreen}
      <button class="icon fs-btn" onclick={fullscreen} aria-label="Plein écran / Fullscreen" title="Plein écran / Fullscreen">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>
      </button>
    {/if}
  </nav>
</div>

<div class="hud" class:bonus={game.inBonus} bind:this={hudEl}>
  <div class="stat balance">
    <span class="label">{game.isDemo ? t.credits : t.balance}</span>
    <span class="value" data-testid="balance">{money(game.balance, game.currency, game.prefs.lang)}</span>
  </div>

  {#if game.inBonus}
    <div class="stat mid" data-testid="fs-counter" aria-live="polite">
      <span class="label">{t.tbRound}</span>
      <span class="value">{game.fsCurrent} / {game.fsTotal} <span class="mult">×{game.multiplier}</span></span>
    </div>
  {:else}
    <div class="stat mid">
      <span class="label">{social ? t.socialPlay : t.bet}</span>
      <span class="value" data-testid="bet">{money(game.bet, game.currency, game.prefs.lang)}</span>
    </div>
  {/if}

  <div class="stat win">
    <span class="label">{game.inBonus ? t.totalWin : t.win}</span>
    <span class="value" class:hot={game.win > 0} data-testid="win" aria-live="polite">{money(game.win, game.currency, game.prefs.lang)}</span>
  </div>

  <div class="controls">
    <div class="slot side buyslot">
      {#if canBuy}
        <button class="buy" onclick={() => open('buy')} disabled={busy || !!game.autoplay} data-testid="btn-buy" aria-label={t.buyTitle}>
          <span class="buy-top">BONUS</span><span class="buy-x">×{RULES.buyBonus.cost}</span>
        </button>
      {/if}
    </div>
    <button class="round minus" onclick={() => changeBet(-1)} disabled={busy || idx <= 0 || game.inBonus} aria-label="{t.bet} −" data-testid="bet-minus">
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M6 12h12" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>
    </button>
    {#if game.autoplay}
      <button class="spin stop" onclick={() => ctrl?.stopAutoplay()} aria-label={t.autoStop} data-testid="auto-stop">
        <span class="stopbox" aria-hidden="true"></span><span class="left">{game.autoplay.remaining}</span>
      </button>
    {:else}
      <button class="spin" class:busy onclick={() => ctrl?.spin()} disabled={busy} aria-label={t.spinAria} data-testid="spin">
        <svg viewBox="0 0 48 48" aria-hidden="true" class="arrows">
          <path d="M35.5 17A13 13 0 0 0 12 15.5" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/>
          <path d="M37 9.5V17.5H29" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12.5 31A13 13 0 0 0 36 32.5" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/>
          <path d="M11 38.5V30.5H19" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    {/if}
    <button class="round plus" onclick={() => changeBet(1)} disabled={busy || idx >= game.betLevels.length - 1 || game.inBonus} aria-label="{t.bet} +" data-testid="bet-plus">
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M6 12h12M12 6v12" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>
    </button>
    <div class="slot side autoslot">
      {#if canAuto}
        <button class="round auto" onclick={() => open('auto')} disabled={busy || !!game.autoplay} aria-label={t.autoAria} title={t.autoAria} data-testid="btn-auto">
          <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M5 12a7 7 0 0 1 12-4.9M19 12a7 7 0 0 1-12 4.9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M17 3.5v4h-4M7 20.5v-4h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><text x="12" y="14.6" text-anchor="middle" font-size="6.5" font-weight="800" font-family="Inter, sans-serif" fill="currentColor">AUTO</text></svg>
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .top {
    position: absolute; top: 0; left: 0; right: 0; z-index: 20; pointer-events: none;
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    padding: calc(8px + var(--safe-t)) calc(10px + var(--safe-r)) 8px calc(10px + var(--safe-l));
  }
  .top > * { pointer-events: auto; }
  .demo {
    font-size: 11px; font-weight: 700; letter-spacing: .06em; padding: 5px 10px; border-radius: 999px;
    background: rgba(8, 27, 35, .78); border: 1px solid var(--line); color: var(--cream); max-width: 46vw;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  nav { display: flex; gap: 8px; margin-left: auto; }
  .icon {
    width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; color: var(--cream);
    background: rgba(8, 27, 35, .78); border: 1px solid var(--line-soft); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    transition: border-color .15s, color .15s;
  }
  .icon:hover { border-color: var(--gold); color: var(--gold-hi); }
  .icon:active { transform: scale(.95); }
  @media (max-width: 480px) { .fs-btn { display: none; } .demo { white-space: normal; max-width: 112px; font-size: 10px; line-height: 1.2; padding: 4px 10px; border-radius: 12px; } }
  @media (max-width: 380px) { nav { gap: 6px; } .icon { width: 40px; height: 40px; } }

  .hud {
    position: absolute; left: 0; right: 0; bottom: 0; z-index: 20;
    display: grid; align-items: center; column-gap: 14px; row-gap: 6px;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto minmax(0, 1fr);
    grid-template-areas: 'bal mid ctl win';
    padding: 10px calc(18px + var(--safe-r)) calc(10px + var(--safe-b)) calc(18px + var(--safe-l));
    background: var(--panel); border-top: 1px solid var(--line);
    box-shadow: 0 -12px 30px rgba(0, 0, 0, .35);
  }
  .hud.bonus { border-top-color: var(--tennis); }
  .stat { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
  .balance { grid-area: bal; }
  .mid { grid-area: mid; }
  .win { grid-area: win; align-items: flex-end; text-align: right; }
  .controls { grid-area: ctl; display: flex; align-items: center; justify-content: center; gap: 12px; }
  .label { font-size: 11px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--gold); }
  .value {
    font-family: var(--font-title); font-weight: 700; font-size: clamp(16px, 1.9vw, 24px); color: var(--cream);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: .02em; font-variant-numeric: tabular-nums;
  }
  .win .value { font-size: clamp(18px, 2.3vw, 28px); }
  .value.hot { color: var(--gold-hi); }
  .mult { color: var(--tennis); margin-left: 6px; }

  .slot { width: 64px; display: grid; place-items: center; }
  .round {
    width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; color: var(--cream);
    background: rgba(242, 229, 195, .06); border: 1px solid var(--line);
  }
  .round:hover:not(:disabled) { border-color: var(--gold); color: var(--gold-hi); }
  .round:disabled { opacity: .35; cursor: default; }
  .round.auto { width: 48px; height: 48px; }

  .spin {
    width: 84px; height: 84px; border-radius: 50%; padding: 0; display: grid; place-items: center; position: relative;
    color: var(--night); background: var(--gold-btn); border: none;
    box-shadow: inset 0 0 0 3px rgba(255, 246, 214, .55), inset 0 -6px 12px rgba(80, 52, 10, .45), 0 6px 18px rgba(0, 0, 0, .45);
    transition: transform .12s, filter .15s;
  }
  .spin::after { content: ''; position: absolute; inset: 7px; border-radius: 50%; border: 1px solid rgba(8, 27, 35, .35); pointer-events: none; }
  .spin .arrows { width: 52%; height: 52%; }
  .spin:hover:not(:disabled) { filter: brightness(1.06); }
  .spin:active:not(:disabled) { transform: scale(.96); }
  .spin:disabled { cursor: default; filter: saturate(.55) brightness(.75); }
  .spin.busy .arrows { animation: turn 1.1s linear infinite; }
  @keyframes turn { to { transform: rotate(360deg); } }
  :global(.rm) .spin.busy .arrows { animation: none; }
  .spin.stop { background: linear-gradient(180deg, #f2e5c3, #cdbb8e); }
  .stopbox { width: 22px; height: 22px; border-radius: 4px; background: var(--night); }
  .left { position: absolute; bottom: 9px; font-size: 13px; font-weight: 800; color: var(--night); }

  .buy {
    width: 64px; height: 52px; border-radius: 14px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px;
    background: linear-gradient(180deg, rgba(9, 58, 49, .95), rgba(6, 36, 31, .98)); border: 1px solid var(--gold); color: var(--cream);
  }
  .buy-top { font-size: 11px; font-weight: 800; letter-spacing: .12em; }
  .buy-x { font-family: var(--font-title); font-weight: 700; font-size: 16px; color: var(--gold-hi); }
  .buy:hover:not(:disabled) { border-color: var(--gold-hi); }
  .buy:disabled { opacity: .4; cursor: default; }

  /* portrait / narrow: values on one row, controls centred below */
  @media (max-aspect-ratio: 1/1), (max-width: 700px) {
    .hud {
      grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-areas: 'bal mid win' 'ctl ctl ctl';
      padding: 8px calc(12px + var(--safe-r)) calc(8px + var(--safe-b)) calc(12px + var(--safe-l)); column-gap: 8px;
    }
    .mid { align-items: center; text-align: center; }
    .value { font-size: 17px; }
    .win .value { font-size: 18px; }
    .label { font-size: 10px; letter-spacing: .12em; }
    .spin { width: 76px; height: 76px; }
  }
  @media (max-width: 360px) { .controls { gap: 8px; } .slot { width: 58px; } .buy { width: 58px; } .value { font-size: 15px; } }
  /* short landscape (phone on its side): menu as a left column, HUD as a right
     column, so the reels get the full height */
  @media (max-height: 500px) and (min-aspect-ratio: 1/1) {
    .top {
      right: auto; bottom: 0; flex-direction: column; justify-content: flex-start; align-items: center; gap: 6px;
      padding: calc(6px + var(--safe-t)) 6px calc(6px + var(--safe-b)) calc(6px + var(--safe-l));
    }
    .demo { white-space: normal; max-width: 58px; font-size: 9px; line-height: 1.15; padding: 4px 6px; border-radius: 10px; text-align: center; }
    nav { flex-direction: column; margin-left: 0; gap: 6px; }
    .icon { width: 40px; height: 40px; }
    .fs-btn { display: none; }
    .hud {
      left: auto; top: 0; width: calc(184px + var(--safe-r)); align-content: center;
      grid-template-columns: 1fr; grid-template-areas: 'bal' 'mid' 'win' 'ctl'; row-gap: 8px;
      padding: calc(8px + var(--safe-t)) calc(10px + var(--safe-r)) calc(8px + var(--safe-b)) 12px;
      border-top: none; border-left: 1px solid var(--line); box-shadow: -12px 0 30px rgba(0, 0, 0, .35);
    }
    .hud.bonus { border-left-color: var(--tennis); }
    .win, .mid { align-items: flex-start; text-align: left; }
    .value, .win .value { font-size: 16px; }
    .label { font-size: 9px; }
    .controls { display: grid; grid-template-columns: 44px 70px 44px; grid-template-areas: 'minus spin plus' 'buy . auto'; gap: 6px 8px; justify-content: center; align-items: center; }
    .minus { grid-area: minus; } .plus { grid-area: plus; } .spin { grid-area: spin; }
    .buyslot { grid-area: buy; width: auto; } .autoslot { grid-area: auto; width: auto; }
    .controls { grid-template-areas: 'minus spin plus' 'buy buy auto'; }
    .spin { width: 66px; height: 66px; }
    .round { width: 42px; height: 42px; }
    .buy { width: 84px; height: 42px; flex-direction: row; gap: 6px; }
  }
</style>
