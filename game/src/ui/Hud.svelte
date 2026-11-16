<script lang="ts">
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import { audio } from '../audio/audio';
  import type { Controller } from '../game/controller';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const busy = $derived(game.phase !== 'idle');
  const idx = $derived(game.betLevels.indexOf(game.bet));
  const social = $derived(!!game.jurisdiction.socialCasino);

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

<div class="top">
  {#if game.isDemo}<span class="demo" data-testid="demo-badge">{t.demoBadge}</span>{/if}
  <nav aria-label="menu">
    <button class="icon" onclick={() => open('paytable')} aria-label={t.paytable} title={t.paytable} data-testid="btn-paytable">i</button>
    <button class="icon" onclick={() => open('history')} aria-label={t.history} title={t.history} data-testid="btn-history">
      <svg viewBox="0 0 24 24" width="20" height="20"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
    </button>
    <button class="icon" onclick={() => open('settings')} aria-label={t.settings} title={t.settings} data-testid="btn-settings">
      <svg viewBox="0 0 24 24" width="20" height="20"><path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm8.4 4.6-1.6.9a7 7 0 0 1-.6 1.5l.5 1.8-1.8 1.8-1.8-.5c-.5.3-1 .5-1.5.6l-.9 1.6h-2.6l-.9-1.6a7 7 0 0 1-1.5-.6l-1.8.5-1.8-1.8.5-1.8a7 7 0 0 1-.6-1.5l-1.6-.9v-2.6l1.6-.9c.1-.5.3-1 .6-1.5l-.5-1.8 1.8-1.8 1.8.5c.5-.3 1-.5 1.5-.6l.9-1.6h2.6l.9 1.6c.5.1 1 .3 1.5.6l1.8-.5 1.8 1.8-.5 1.8c.3.5.5 1 .6 1.5l1.6.9Z" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>
    </button>
    <button class="icon" onclick={toggleSound} aria-label={t.sound} aria-pressed={game.prefs.sound} title={t.sound} data-testid="btn-sound">
      {#if game.prefs.sound}
        <svg viewBox="0 0 24 24" width="20" height="20"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      {:else}
        <svg viewBox="0 0 24 24" width="20" height="20"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="m16 9 6 6m0-6-6 6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      {/if}
    </button>
    {#if !game.jurisdiction.disabledFullscreen}
      <button class="icon" onclick={fullscreen} aria-label="Fullscreen" title="Fullscreen">
        <svg viewBox="0 0 24 24" width="18" height="18"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>
      </button>
    {/if}
  </nav>
</div>

{#if !game.jurisdiction.disabledBuyBonus && !game.inBonus}
  <button class="buybadge" onclick={() => open('buy')} disabled={busy || !!game.autoplay} data-testid="btn-buy">
    <span class="cupicon" aria-hidden="true">🏆</span><span>{t.buyShort}</span>
  </button>
{/if}

<div class="hud" class:bonus={game.inBonus}>
  <div class="cell balance">
    <span class="label">{game.isDemo ? t.credits : t.balance}</span>
    <span class="value" data-testid="balance">{money(game.balance, game.currency, game.prefs.lang)}</span>
  </div>

  <div class="center">
    {#if game.inBonus}
      <div class="fs" data-testid="fs-counter" aria-live="polite">
        <span class="label">{t.freeSpins}</span>
        <span class="value gold-text">{game.fsCurrent} / {game.fsTotal}</span>
        <span class="mult">×{game.multiplier}</span>
      </div>
    {:else}
      <div class="bet">
        <button class="round" onclick={() => changeBet(-1)} disabled={busy || idx <= 0} aria-label="−" data-testid="bet-minus">−</button>
        <div class="betval">
          <span class="label">{social ? t.socialPlay : t.bet}</span>
          <span class="value" data-testid="bet">{money(game.bet, game.currency, game.prefs.lang)}</span>
        </div>
        <button class="round" onclick={() => changeBet(1)} disabled={busy || idx >= game.betLevels.length - 1} aria-label="+" data-testid="bet-plus">+</button>
      </div>
    {/if}
    {#if game.autoplay}
      <button class="spin stop" onclick={() => ctrl?.stopAutoplay()} aria-label={t.autoStop} data-testid="auto-stop">
        <span class="stopbox">■</span><span class="left">{game.autoplay.remaining}</span>
      </button>
    {:else}
    <button class="spin" class:busy onclick={() => ctrl?.spin()} disabled={busy} aria-label={t.spinAria} data-testid="spin">
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <defs>
          <radialGradient id="sg" cx=".36" cy=".3" r=".85"><stop offset="0" stop-color="#fffbe0"/><stop offset=".35" stop-color="#ffd75e"/><stop offset=".75" stop-color="#c58512"/><stop offset="1" stop-color="#6e4205"/></radialGradient>
        </defs>
        <g class="teeth">
          <circle cx="50" cy="50" r="45" fill="url(#sg)" stroke="#1b1410" stroke-width="5"/>
          <path d="M8,36 C30,40 30,82 22,88 M92,64 C70,60 70,18 78,12" fill="none" stroke="#fff6c8" stroke-width="5" stroke-linecap="round"/>
          <ellipse cx="36" cy="28" rx="13" ry="7" fill="#fff" opacity=".7" transform="rotate(-30 36 28)"/>
        </g>
        <path d="M68,40a20,20 0 1 0 1,16" fill="none" stroke="#1b1410" stroke-width="7" stroke-linecap="round" />
        <path d="M71,28v14H57" fill="none" stroke="#1b1410" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    {/if}
    {#if !game.jurisdiction.disabledAutoplay && !game.inBonus}
      <button class="round auto" onclick={() => open('auto')} disabled={busy || !!game.autoplay} aria-label={t.autoAria} title={t.autoAria} data-testid="btn-auto">
        <svg viewBox="0 0 24 24" width="24" height="24"><path d="M5 12a7 7 0 0 1 12-4.9M19 12a7 7 0 0 1-12 4.9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M17 3v4.5h-4.5M7 21v-4.5h4.5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><text x="12" y="15" text-anchor="middle" font-size="7" font-weight="900" fill="currentColor">A</text></svg>
      </button>
    {/if}
  </div>

  <div class="cell win">
    <span class="label">{game.inBonus ? t.totalWin : t.win}</span>
    <span class="value" class:hot={game.win > 0} data-testid="win" aria-live="polite">{money(game.win, game.currency, game.prefs.lang)}</span>
  </div>
</div>

<style>
  .top { position: absolute; top: 0; left: 0; right: 0; display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 12px; z-index: 20; pointer-events: none; gap: 8px; }
  .top > * { pointer-events: auto; }
  .demo { font-size: 11px; padding: 4px 10px; border-radius: 999px; background: rgba(3,19,12,.7); border: 1px solid rgba(232,177,58,.7); color: var(--gold-hi); letter-spacing: .04em; max-width: 52vw; backdrop-filter: blur(4px); }
  nav { display: flex; gap: 8px; margin-left: auto; }
  @media (max-width: 600px) { .demo { font-size: 10px; padding: 3px 8px; max-width: 34vw; } nav { gap: 7px; } .icon { width: 36px; height: 36px; } }
  .icon { width: 40px; height: 40px; border-radius: 50%; border: none; box-shadow: var(--gold-ring); background: radial-gradient(circle at 40% 30%, #2a7a5a, #06241a); display: grid; place-items: center; font-family: var(--font-title); font-size: 18px; color: var(--gold); }
  .icon:active { transform: scale(.94); }

  .hud {
    position: absolute; left: 0; right: 0; bottom: 0; z-index: 20;
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 12px;
    padding: 10px max(16px, env(safe-area-inset-left)) calc(10px + var(--safe-b));
    background: var(--glass); border-radius: 26px 26px 0 0; box-shadow: 0 -2px 0 #e8b13a, 0 -10px 30px rgba(0,0,0,.45);
    border-top: 4px solid var(--ink-line);
  }
  .cell { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
  .cell.win { align-items: flex-end; text-align: right; }
  .label { font-family: var(--font-deco); font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); opacity: .9; }
  .value { font-family: var(--font-title); font-size: clamp(17px, 2.2vw, 26px); color: var(--ink); white-space: nowrap; letter-spacing: .03em; text-shadow: 0 2px 0 #16120f; }
  .value.hot { color: #ffe17a; text-shadow: 0 2px 0 #16120f, 0 0 12px rgba(255,215,94,.7); }
  .cell.win .value { font-size: clamp(20px, 2.8vw, 32px); }
  .center { display: flex; align-items: center; gap: 14px; }
  .bet { display: flex; align-items: center; gap: 10px; }
  .betval { display: flex; flex-direction: column; align-items: center; min-width: 92px; }
  .round { width: 44px; height: 44px; border-radius: 50%; border: none; box-shadow: var(--gold-ring); background: radial-gradient(circle at 40% 30%, #2a7a5a, #06241a); color: var(--gold); font-family: var(--font-title); font-size: 26px; line-height: 1; }
  .round:disabled { opacity: .35; cursor: default; }
  .fs { display: flex; flex-direction: column; align-items: center; min-width: 190px; }
  .fs .value { font-size: 30px; }
  .mult { font-family: var(--font-title); color: var(--gold); font-size: 22px; -webkit-text-stroke: 1px var(--ink-line); }
  .spin { width: 104px; height: 104px; border: none; background: none; padding: 0; border-radius: 50%; transition: transform .12s; margin-top: -30px; position: relative; filter: drop-shadow(0 6px 8px rgba(0,0,0,.5)); }
  .spin:not(:disabled)::before { content: ''; position: absolute; inset: -8px; border-radius: 50%; box-shadow: 0 0 22px 6px rgba(255,215,94,.55); animation: halo 1.8s ease-in-out infinite; pointer-events: none; }
  @keyframes halo { 50% { box-shadow: 0 0 34px 12px rgba(255,215,94,.8); } }
  @media (prefers-reduced-motion: reduce) { .spin::before { animation: none !important; } }
  .spin svg { width: 100%; height: 100%; display: block; }
  .spin:hover:not(:disabled) { transform: scale(1.04); }
  .spin:active:not(:disabled) { transform: scale(.96); }
  .spin.busy .teeth { animation: turn 1.2s linear infinite; transform-origin: 50px 50px; }
  .spin:disabled { cursor: default; filter: grayscale(.4) brightness(.8); }
  .spin.stop { display: grid; place-items: center; background: radial-gradient(circle at 40% 35%, #ff8a7a, #d93b3b); border: 5px solid var(--ink-line); color: #fff; font-family: var(--font-title); position: relative; }
  .stopbox { font-size: 30px; line-height: 1; }
  .left { position: absolute; bottom: 10px; font-size: 18px; -webkit-text-stroke: 1px var(--ink-line); }
  .round.auto { display: grid; place-items: center; }
  .buybadge {
    position: absolute; z-index: 21; left: max(14px, env(safe-area-inset-left)); bottom: calc(118px + var(--safe-b));
    width: 96px; height: 96px; border-radius: 50%; border: none; box-shadow: 0 0 0 3px #16120f, 0 0 0 7px #e8b13a, 0 0 24px 6px rgba(255,215,94,.45);
    background: radial-gradient(circle at 38% 30%, #fffbe0, #ffd75e 35%, #c58512 75%, #6e4205); color: #3a2404;
    font-family: var(--font-title); font-size: 15px; line-height: 1.05; padding: 8px; transform: rotate(-10deg);
    animation: coin 2.6s ease-in-out infinite;
  }
  @keyframes coin { 50% { box-shadow: 0 0 0 3px #16120f, 0 0 0 7px #e8b13a, 0 0 34px 12px rgba(255,215,94,.7); } }
  .buybadge span { display: block; } .cupicon { font-size: 20px; line-height: 1; filter: saturate(1.2); }
  .buybadge:disabled { opacity: .45; }
  @media (max-aspect-ratio: 1/1) { .buybadge { bottom: calc(178px + var(--safe-b)); width: 74px; height: 74px; font-size: 14px; } }
  @keyframes turn { to { transform: rotate(360deg); } }
  @media (prefers-reduced-motion: reduce) { .spin.busy .teeth { animation: none; } }

  /* portrait phones: two rows */
  @media (max-aspect-ratio: 1/1) {
    .hud { grid-template-columns: 1fr 1fr; grid-template-areas: 'bal win' 'ctr ctr'; row-gap: 6px; }
    .balance { grid-area: bal; }
    .win { grid-area: win; }
    .center { grid-area: ctr; justify-content: center; }
    .value { font-size: 20px; }
    .spin { width: 92px; height: 92px; margin-top: 0; }
  }
  @media (max-height: 420px) and (min-aspect-ratio: 1/1) {
    .spin { width: 76px; height: 76px; }
    .hud { padding-top: 4px; padding-bottom: calc(4px + var(--safe-b)); }
    .value { font-size: 16px; }
  }
</style>
