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
.veil { position: absolute; inset: 0; z-index: 40; background: rgba(4, 12, 16, .74); display: grid; place-items: center; padding: calc(12px + var(--safe-t)) 12px calc(12px + var(--safe-b)); }
  .box {
    width: min(860px, 100%); max-height: min(88vh, 100%); display: flex; flex-direction: column;
    background: var(--panel); border: 1px solid var(--gold); border-radius: 20px; box-shadow: var(--shadow); outline: none;
  }
  header { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 18px; border-bottom: 1px solid var(--line); }
  h2 { margin: 0; font-family: var(--font-title); font-weight: 700; letter-spacing: .06em; font-size: clamp(18px, 4.6vw, 24px); color: var(--gold-hi); }
  .x { flex: none; width: 44px; height: 44px; border-radius: 50%; background: rgba(242,229,195,.06); color: var(--cream); border: 1px solid var(--line); font-size: 16px; }
  .x:hover { border-color: var(--gold); }
  .content { overflow-y: auto; overscroll-behavior: contain; padding: 16px 18px 22px; -webkit-overflow-scrolling: touch; line-height: 1.5; }
</style>
