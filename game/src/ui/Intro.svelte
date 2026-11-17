<script lang="ts">
  // DOM layer of THE FIRST SERVE: accessible progress, status, slow-network and
  // error messages, first-visit buttons.  The visuals are drawn by IntroScene
  // (PixiJS) in its own canvas, mounted in `host`.
  import { game } from '../game/state.svelte';
  let { host = $bindable(), showCard, entering, cinematic = false, slow, failed, oncontinue, onskipintro, onskiptransition }: {
    host?: HTMLDivElement;
    showCard: boolean;
    entering: boolean;
    cinematic?: boolean;
    slow: boolean;
    failed: boolean;
    oncontinue: () => void;
    onskipintro?: () => void;
    onskiptransition: () => void;
  } = $props();
  const t = $derived(game.t);
  const pct = $derived(Math.round(game.loadProgress * 100));
</script>

<div class="intro" class:entering role="presentation" onpointerdown={() => entering && onskiptransition()}>
  <div class="canvas" bind:this={host}></div>
  <!-- real loading progress, for assistive technologies (the visual bar is the court baseline) -->
  <div class="sr" role="progressbar" aria-label={t.introLoading} aria-valuemin="0" aria-valuemax="100" aria-valuenow={pct} data-testid="intro-progress"></div>
  {#if game.phase === 'loading' && slow && !failed}
    <p class="status" role="status" data-testid="intro-slow">{t.introSlow}</p>
  {/if}
  {#if failed}
    <div class="status err" role="alert" data-testid="intro-error">
      <p>{t.introError}</p>
      <button class="btn" onclick={() => location.reload()}>{t.retry}</button>
    </div>
  {/if}
  {#if showCard && !entering}
    <div class="actions">
      <button class="btn primary" onclick={oncontinue} data-testid="start">{t.introContinue}</button>
      <button class="link" onclick={onskipintro ?? oncontinue} data-testid="intro-skip">{t.introSkip}</button>
    </div>
  {/if}
  {#if cinematic}
    <button class="skipcine" onpointerdown={(e) => e.stopPropagation()} onclick={onskiptransition} data-testid="cine-skip">{t.introSkipShort}</button>
  {/if}
  {#if !entering}<p class="demo">{t.demoNotice}</p>{/if}
</div>

<style>
  .intro { position: absolute; inset: 0; z-index: 50; background: #071826; }
  .canvas { position: absolute; inset: 0; }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .status {
    position: absolute; left: 50%; bottom: calc(120px + var(--safe-b)); transform: translateX(-50%);
    margin: 0; padding: 8px 16px; border-radius: 999px; background: rgba(7, 24, 38, .9); border: 1px solid rgba(231, 200, 119, .5);
    color: #f4e9d4; font-size: 13px; text-align: center; max-width: calc(100% - 32px);
  }
  .status.err { border-radius: 16px; padding: 14px 18px; }
  .status.err p { margin: 0 0 8px; }
  .actions {
    position: absolute; left: 0; right: 0; bottom: calc(52px + var(--safe-b));
    display: flex; flex-direction: column; align-items: center; gap: 6px;
  }
  .btn {
    min-height: 52px; min-width: 230px; padding: 12px 40px; border-radius: 999px; border: none;
    font-family: var(--font-title); font-weight: 700; font-size: 18px; letter-spacing: .2em; color: #071826;
    background: linear-gradient(180deg, #f6e3a8 0%, #e7c877 45%, #b8862f 100%);
    box-shadow: inset 0 0 0 2px rgba(255, 246, 214, .55), 0 10px 26px rgba(0, 0, 0, .5);
  }
  .btn:active { transform: scale(.97); }
  .link { min-height: 40px; background: none; border: none; color: #d6b36a; font-size: 14px; font-weight: 700; letter-spacing: .08em; text-decoration: underline; text-underline-offset: 4px; }
  .demo {
    position: absolute; left: 50%; bottom: calc(10px + var(--safe-b)); transform: translateX(-50%);
    width: min(560px, calc(100% - 32px)); margin: 0; text-align: center; font-size: 11px; line-height: 1.45; color: rgba(244, 233, 212, .75);
  }
  .entering { background: transparent; pointer-events: auto; }
  .skipcine { position: absolute; top: calc(12px + var(--safe-t)); right: calc(12px + var(--safe-r, 0px)); min-height: 40px; padding: 8px 16px; border-radius: 999px; border: 1px solid rgba(231, 200, 119, .6); background: rgba(7, 24, 38, .55); color: #f4e9d4; font: 700 13px/1 Inter, sans-serif; letter-spacing: .12em; }
  /* phone on its side: the card takes the left, the buttons the right */
  @media (max-height: 499px) and (orientation: landscape) {
    .actions { left: auto; right: calc(4% + var(--safe-r, 0px)); bottom: auto; top: 50%; transform: translateY(-60%); width: 34%; }
    .btn { min-width: 0; width: 100%; padding: 12px 18px; font-size: 16px; }
    .demo { left: auto; right: calc(2% + var(--safe-r, 0px)); transform: none; width: 38%; font-size: 10px; text-align: right; }
  }
</style>
