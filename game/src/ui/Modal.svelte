<script lang="ts">
  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';
  import { game } from '../game/state.svelte';
  let { title, onclose, children }: { title: string; onclose: () => void; children: Snippet } = $props();
  let box: HTMLDivElement;
  onMount(() => box?.focus());
  function key(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
<div class="veil" onclick={(e) => e.target === e.currentTarget && onclose()} onkeydown={key}>
  <div class="box" role="dialog" aria-modal="true" aria-label={title} tabindex="-1" bind:this={box}>
    <header>
      <h2>{title}</h2>
      <button class="x" onclick={onclose} aria-label={game.t.close}>✕</button>
    </header>
    <div class="content">{@render children()}</div>
  </div>
</div>

<style>
  .veil { position: absolute; inset: 0; z-index: 40; background: rgba(2,8,5, .7); display: grid; place-items: center; padding: 12px; }
  .box {
    width: min(860px, 100%); max-height: min(88vh, 100%); display: flex; flex-direction: column;
    background: linear-gradient(180deg, #0f3626, #06180f); border: 1px solid var(--gold); border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,.6), inset 0 0 0 4px rgba(227,181,82,.08); outline: none;
  }
  header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid rgba(227,181,82,.3); }
  h2 { margin: 0; font-family: var(--font-title); letter-spacing: .12em; font-size: 20px; color: var(--gold-hi); }
  .x { background: none; border: 1px solid rgba(227,181,82,.5); width: 40px; height: 40px; border-radius: 50%; font-size: 16px; }
  .content { overflow-y: auto; padding: 16px 18px 22px; -webkit-overflow-scrolling: touch; }
</style>
