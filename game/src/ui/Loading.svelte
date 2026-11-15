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
    background: linear-gradient(180deg, #3f9fe0 0%, #9fdcf6 60%, #3e9b4f 60%, #2b7a3f 100%);
  }
  .logo { width: min(620px, 86vw); filter: drop-shadow(0 8px 24px rgba(0,0,0,.6)); }
  .bar { width: min(420px, 70vw); height: 6px; border-radius: 6px; background: rgba(255,255,255,.08); overflow: hidden; border: 3px solid var(--ink-line); }
  .fill { height: 100%; background: var(--gold-grad); transition: width .2s; }
  .hint { color: var(--ink-line); letter-spacing: .12em; font-size: 14px; margin: 0; }
  .start {
    font-family: var(--font-title); font-size: 26px; letter-spacing: .06em; padding: 16px 40px; border-radius: 999px; color: var(--ink-line);
    border: var(--chunky); box-shadow: var(--pop); background: linear-gradient(180deg, #ffe066, #ffb21e); box-shadow: 0 6px 0 var(--ink-line);
    animation: breathe 2.4s ease-in-out infinite;
  }
  @keyframes breathe { 50% { filter: brightness(1.15) saturate(1.2); } }
  @media (prefers-reduced-motion: reduce) { .start { animation: none; } }
  .demo { max-width: 520px; text-align: center; color: var(--ink); background: rgba(27,20,16,.55); padding: 8px 12px; border-radius: 12px; font-size: 13px; line-height: 1.5; margin: 0; }
</style>
