<script lang="ts">
  import { game } from '../game/state.svelte';
  import logo from '../assets/img/logo.webp?url';
  import ace from '../assets/img/sym_H5.webp?url';
  import ball from '../assets/img/ui_golden_ball.webp?url';
  let { onstart }: { onstart: () => void } = $props();
  const t = $derived(game.t);
  const rm = $derived(game.prefs.reducedMotion);
</script>

<!-- Start screen: the night stadium is rendered by the game scene behind this
     layer (reels hidden); this layer only adds the title, Ace and the button. -->
<div class="intro" class:ready={game.phase !== 'loading'} class:rm role="dialog" aria-label="Golden Rally — Match Point">
  <div class="vignette" aria-hidden="true"></div>
  <div class="center">
    <div class="logo-wrap">
      <img class="logo" src={logo} alt="Golden Rally — Match Point" />
      {#if !rm}<img class="ball" src={ball} alt="" aria-hidden="true" />{/if}
    </div>
    <p class="hint">{t.startHint}</p>
    {#if game.phase === 'loading'}
      <div class="bar" role="progressbar" aria-label={t.loading} aria-valuemin="0" aria-valuemax="100" aria-valuenow={Math.round(game.loadProgress * 100)}>
        <div class="fill" style="width:{Math.round(game.loadProgress * 100)}%"></div>
      </div>
      <p class="loading">{t.loading}</p>
    {:else}
      <button class="start" onclick={onstart} data-testid="start">{t.tapToStart}</button>
    {/if}
  </div>
  <img class="ace" src={ace} alt="Ace" />
  <p class="demo">{t.demoNotice}</p>
</div>

<style>
  .intro {
    position: absolute; inset: 0; z-index: 50; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: calc(16px + var(--safe-t)) 16px calc(16px + var(--safe-b));
    background: radial-gradient(ellipse at 50% 18%, #12404a 0%, #0b2a33 38%, #081b23 72%);
    transition: background-color .6s;
  }
  /* once loaded the real stadium (canvas) shows through */
  .intro.ready { background: transparent; }
  .vignette {
    position: absolute; inset: 0; pointer-events: none;
    background: radial-gradient(ellipse at 50% 42%, rgba(8, 27, 35, .15) 0%, rgba(8, 27, 35, .55) 60%, rgba(8, 27, 35, .9) 100%);
  }
  .center { position: relative; display: flex; flex-direction: column; align-items: center; gap: clamp(12px, 2.6vh, 22px); width: 100%; margin-top: -6vh; }
  .logo-wrap { position: relative; width: min(620px, 88vw); }
  .logo { display: block; width: 100%; filter: drop-shadow(0 10px 28px rgba(0, 0, 0, .65)); animation: rise .9s cubic-bezier(.2, .8, .2, 1) both; }
  .ball {
    position: absolute; width: 13%; left: -14%; top: 8%; pointer-events: none;
    animation: cross 1.5s cubic-bezier(.35, .1, .35, 1) .55s both;
  }
  @keyframes rise { from { opacity: 0; transform: translateY(14px) scale(.97); } }
  @keyframes cross {
    0% { opacity: 0; transform: translate(0, 40%) rotate(0); }
    12% { opacity: 1; }
    50% { transform: translate(520%, -55%) rotate(300deg); }
    88% { opacity: 1; }
    100% { opacity: 0; transform: translate(1020%, 30%) rotate(620deg); }
  }
  .hint { margin: 0; color: var(--cream); opacity: .85; font-size: clamp(12px, 1.6vw, 15px); font-weight: 500; letter-spacing: .14em; text-transform: uppercase; text-align: center; animation: fade .8s .5s both; }
  @keyframes fade { from { opacity: 0; } }
  .bar { width: min(360px, 70vw); height: 4px; border-radius: 4px; background: rgba(242, 229, 195, .14); overflow: hidden; }
  .fill { height: 100%; background: var(--gold); transition: width .2s; }
  .loading { margin: 0; color: var(--gold); font-size: 13px; letter-spacing: .14em; }
  .start {
    min-width: 230px; min-height: 56px; padding: 14px 44px; border-radius: 999px; border: none;
    font-family: var(--font-title); font-weight: 700; font-size: 20px; letter-spacing: .22em; color: var(--night);
    background: var(--gold-btn);
    box-shadow: inset 0 0 0 2px rgba(255, 246, 214, .5), inset 0 -4px 10px rgba(80, 52, 10, .35), 0 10px 28px rgba(0, 0, 0, .5);
    animation: fade .6s .9s both; transition: transform .12s, filter .15s;
  }
  .start:hover { filter: brightness(1.06); }
  .start:active { transform: scale(.97); }
  .ace {
    position: absolute; left: calc(14px + var(--safe-l)); bottom: calc(86px + var(--safe-b)); width: clamp(70px, 12vmin, 120px);
    filter: drop-shadow(0 8px 16px rgba(0, 0, 0, .5)); animation: peek .7s cubic-bezier(.3, 1.4, .5, 1) 1.3s both;
  }
  @keyframes peek { from { opacity: 0; transform: translateX(-130%) rotate(-12deg); } }
  .demo {
    position: absolute; left: 50%; bottom: calc(14px + var(--safe-b)); transform: translateX(-50%);
    width: min(560px, calc(100% - 32px)); margin: 0; text-align: center; font-size: 12px; line-height: 1.5; color: var(--cream);
    background: rgba(8, 27, 35, .82); border: 1px solid var(--line); padding: 8px 14px; border-radius: 12px;
  }
  @media (max-aspect-ratio: 1/1) { .ace { bottom: calc(118px + var(--safe-b)); } }
  @media (max-height: 460px) { .ace { display: none; } .center { margin-top: -10vh; } .logo-wrap { width: min(440px, 60vw); } }
  .rm .logo, .rm .hint, .rm .start, .rm .ace { animation: none; }
</style>
