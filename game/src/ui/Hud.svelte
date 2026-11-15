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
  function open(m: 'paytable' | 'settings' | 'history') {
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
    <button class="spin" class:busy onclick={() => ctrl?.spin()} disabled={busy} aria-label={t.spinAria} data-testid="spin">
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <defs>
          <radialGradient id="sg" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#fbffb0"/><stop offset=".55" stop-color="#d9ef3b"/><stop offset="1" stop-color="#a9c21c"/></radialGradient>
        </defs>
        <g class="teeth">
          <circle cx="50" cy="50" r="45" fill="url(#sg)" stroke="#1b1410" stroke-width="5"/>
          <path d="M8,36 C30,40 30,82 22,88 M92,64 C70,60 70,18 78,12" fill="none" stroke="#fffde8" stroke-width="5" stroke-linecap="round"/>
        </g>
        <path d="M68,40a20,20 0 1 0 1,16" fill="none" stroke="#1b1410" stroke-width="7" stroke-linecap="round" />
        <path d="M71,28v14H57" fill="none" stroke="#1b1410" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
  </div>

  <div class="cell win">
    <span class="label">{game.inBonus ? t.totalWin : t.win}</span>
    <span class="value" class:hot={game.win > 0} data-testid="win" aria-live="polite">{money(game.win, game.currency, game.prefs.lang)}</span>
  </div>
</div>

<style>
  .top { position: absolute; top: 0; left: 0; right: 0; display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 12px; z-index: 20; pointer-events: none; gap: 8px; }
  .top > * { pointer-events: auto; }
  .demo { font-size: 12px; padding: 6px 12px; border-radius: 999px; background: #fff3d6; border: var(--chunky); box-shadow: var(--pop); color: var(--ink-line); max-width: 52vw; }
  nav { display: flex; gap: 8px; margin-left: auto; }
  @media (max-width: 600px) { .demo { font-size: 9px; padding: 4px 8px; max-width: 30vw; line-height: 1.25; } nav { gap: 5px; } }
  .icon { width: 42px; height: 42px; border-radius: 50%; border: var(--chunky); box-shadow: var(--pop); background: #fff3d6; color: var(--ink-line); display: grid; place-items: center; font-family: var(--font-title); font-weight: 700; font-size: 18px; color: var(--ink-line); }

  .hud {
    position: absolute; left: 0; right: 0; bottom: 0; z-index: 20;
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 12px;
    padding: 10px max(16px, env(safe-area-inset-left)) calc(10px + var(--safe-b));
    background: linear-gradient(180deg, #2b7a3f, #1f5e3a);
    border-top: 4px solid var(--ink-line);
  }
  .cell { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
  .cell.win { align-items: flex-end; text-align: right; }
  .label { font-family: var(--font-deco); font-size: 14px; letter-spacing: .08em; text-transform: uppercase; color: var(--gold); text-shadow: 0 2px 0 var(--ink-line); }
  .value { font-family: var(--font-title); font-size: clamp(18px, 2.4vw, 28px); color: #fff; white-space: nowrap; -webkit-text-stroke: 1.5px var(--ink-line); text-shadow: 0 3px 0 var(--ink-line); letter-spacing: .03em; }
  .value.hot { color: var(--gold); }
  .center { display: flex; align-items: center; gap: 18px; }
  .bet { display: flex; align-items: center; gap: 10px; }
  .betval { display: flex; flex-direction: column; align-items: center; min-width: 92px; }
  .round { width: 46px; height: 46px; border-radius: 50%; border: var(--chunky); box-shadow: var(--pop); background: linear-gradient(180deg, #ffd23f, #f08a12); color: var(--ink-line); font-family: var(--font-title); font-size: 28px; line-height: 1; }
  .round:disabled { opacity: .35; cursor: default; }
  .fs { display: flex; flex-direction: column; align-items: center; min-width: 190px; }
  .fs .value { font-size: 30px; }
  .mult { font-family: var(--font-title); color: var(--gold); font-size: 22px; -webkit-text-stroke: 1px var(--ink-line); }
  .spin { width: 100px; height: 100px; border: none; background: none; padding: 0; border-radius: 50%; filter: drop-shadow(0 5px 0 #1b1410); transition: transform .12s; margin-top: -26px; }
  .spin svg { width: 100%; height: 100%; display: block; }
  .spin:hover:not(:disabled) { transform: scale(1.04); }
  .spin:active:not(:disabled) { transform: scale(.96); }
  .spin.busy .teeth { animation: turn 1.2s linear infinite; transform-origin: 50px 50px; }
  .spin:disabled { cursor: default; filter: grayscale(.4) brightness(.8); }
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
