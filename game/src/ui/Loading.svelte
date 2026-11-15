<script lang="ts">
  import { game } from '../game/state.svelte';
  import logo from '../assets/img/logo.png?url';
  let { onstart }: { onstart: () => void } = $props();
  const t = $derived(game.t);
</script>

<div class="loading" role="dialog" aria-label="Golden Rally">
  <img class="logo" src={logo} alt="Golden Rally" />
  {#if game.phase === 'loading'}
    <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={Math.round(game.loadProgress * 100)}>
      <div class="fill" style="width:{Math.round(game.loadProgress * 100)}%"></div>
    </div>
    <p class="hint">{t.loading}</p>
  {:else}
    <button class="start" onclick={onstart} data-testid="start">{t.tapToStart}</button>
  {/if}
  <p class="demo">{t.demoNotice}</p>
</div>

<style>
  .loading {
    position: absolute; inset: 0; z-index: 50; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 22px; padding: 16px;
    background: radial-gradient(ellipse at 50% 40%, #1f6b47 0%, #0b2a1e 45%, #020a06 100%);
  }
  .logo { width: min(620px, 86vw); filter: drop-shadow(0 8px 24px rgba(0,0,0,.6)); }
  .bar { width: min(420px, 70vw); height: 6px; border-radius: 6px; background: rgba(255,255,255,.08); overflow: hidden; border: 1px solid rgba(227,181,82,.4); }
  .fill { height: 100%; background: var(--gold-grad); transition: width .2s; }
  .hint { color: var(--muted); letter-spacing: .12em; font-size: 14px; margin: 0; }
  .start {
    font-family: var(--font-title); font-size: 20px; letter-spacing: .2em; padding: 16px 40px; border-radius: 999px;
    border: 1px solid var(--gold); background: linear-gradient(180deg, #2a7a52, #0c3121); box-shadow: 0 0 30px rgba(227,181,82,.25), inset 0 1px 0 rgba(255,255,255,.2);
    animation: breathe 2.4s ease-in-out infinite;
  }
  @keyframes breathe { 50% { box-shadow: 0 0 46px rgba(227,181,82,.45), inset 0 1px 0 rgba(255,255,255,.2); } }
  @media (prefers-reduced-motion: reduce) { .start { animation: none; } }
  .demo { max-width: 520px; text-align: center; color: var(--muted); font-size: 13px; line-height: 1.5; margin: 0; }
</style>
