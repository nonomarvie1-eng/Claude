<script lang="ts">
  // First-visit feature explanation, shown OVER THE REAL REELS once the ACE! opening
  // has ended (screen order: loading -> opening -> reels -> explanations).
  // Pure presentation: it reads no result and changes no rule.
  import { onMount } from 'svelte';
  import { game } from '../game/state.svelte';
  import logoUrl from '../assets/img/ace_logo.webp?url';
  const syms = import.meta.glob('../assets/img/sym_*.webp', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
  const sym = (k: string) => syms[`../assets/img/sym_${k}.webp`];
  let { onclose }: { onclose: () => void } = $props();
  const t = $derived(game.t);
  // illustration: a strip of the real grid (6 reels x 3 rows), the Golden Ball serving the centre zone
  const rows = [['H2', 'L3', 'H4', 'L1', 'W', 'L2'], ['G', 'H3', 'L5', 'H1', 'L4', 'H2'], ['L4', 'L2', 'H2', 'L3', 'H4', 'L5']];
  let btn: HTMLButtonElement;
  onMount(() => btn?.focus());
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="veil" data-testid="feature-card" onkeydown={(e) => e.key === 'Escape' && onclose()}>
  <div class="card" role="dialog" aria-modal="true" aria-labelledby="fc-name">
    <img class="logo" src={logoUrl} alt="ACE!" />
    <p class="kick">{t.introFeatureKicker}</p>
    <h2 id="fc-name">GOLDEN SERVE · RETURN SPINS</h2>
    <div class="ill" aria-hidden="true">
      <span class="tag">{t.introZone}</span>
      <div class="grid">
        {#each rows as row, r (r)}
          {#each row as k, i (i)}
            <img src={sym(k)} alt="" class:dim={(i < 2 || i > 3) && k !== 'G'} />
          {/each}
        {/each}
        <div class="zone"></div>
      </div>
      <div class="arrows"><span>↻</span><span>↻</span></div>
    </div>
    <p class="t1">{t.introFeature1}</p>
    <p class="t2">{t.introFeature2}</p>
    <button class="btn" bind:this={btn} onclick={onclose} data-testid="feature-ok">{t.introContinue}</button>
  </div>
</div>

<style>
  .veil { position: absolute; inset: 0; z-index: 45; display: grid; place-items: center; background: rgba(4, 12, 20, .62); padding: calc(10px + var(--safe-t)) 12px calc(10px + var(--safe-b)); animation: fade .26s ease-out; }
  .card {
    width: min(440px, 100%); max-height: 100%; overflow-y: auto; text-align: center;
    background: rgba(11, 36, 64, .97); border: 2px solid #e7c877; border-radius: 22px; padding: 14px 18px 18px;
    box-shadow: inset 0 0 0 7px rgba(11, 36, 64, 1), inset 0 0 0 8px rgba(244, 233, 212, .2), 0 18px 48px rgba(0, 0, 0, .55);
  }
  .logo { width: min(52%, 200px); height: auto; display: block; margin: 0 auto 2px; }
  .kick { margin: 0; font: 800 12px/1.4 Inter, sans-serif; letter-spacing: .3em; color: #d6b36a; }
  h2 { margin: 2px 0 10px; font: 700 clamp(17px, 5vw, 22px)/1.2 Cinzel, serif; letter-spacing: .08em; color: #fff4d6; }
  .ill { position: relative; margin: 14px auto 6px; width: min(100%, 330px); }
  .grid { position: relative; display: grid; grid-template-columns: repeat(6, 1fr); gap: 2px; padding: 6px; border-radius: 10px; background: #0e322b; border: 1.5px solid #f1dfa6; }
  .grid img { width: 100%; aspect-ratio: 1; object-fit: contain; }
  .grid img.dim { opacity: .5; }
  .zone { position: absolute; top: 4px; bottom: 4px; left: calc(6px + (100% - 12px) * 2 / 6); width: calc((100% - 12px) * 2 / 6); border: 3px solid #e7c877; border-radius: 9px; box-shadow: 0 0 14px rgba(231, 200, 119, .55); }
  .tag { position: absolute; z-index: 1; top: -11px; left: 50%; transform: translateX(-50%); padding: 3px 10px; border-radius: 999px; background: #e7c877; color: #071826; font: 800 11px/1.3 Inter, sans-serif; letter-spacing: .12em; white-space: nowrap; }
  .arrows { display: flex; justify-content: center; gap: calc((100% - 12px) / 6 - 14px); color: #e7c877; font-size: 18px; line-height: 1.2; }
  .t1 { margin: 8px 0 6px; font: 500 15px/1.45 Inter, sans-serif; color: #f4e9d4; }
  .t2 { margin: 0 0 12px; font: 500 14px/1.4 Inter, sans-serif; color: #d6b36a; }
  .btn {
    min-height: 50px; min-width: 200px; padding: 12px 36px; border-radius: 999px; border: none;
    font-family: var(--font-title); font-weight: 700; font-size: 17px; letter-spacing: .2em; color: #071826;
    background: linear-gradient(180deg, #f6e3a8 0%, #e7c877 45%, #b8862f 100%);
    box-shadow: inset 0 0 0 2px rgba(255, 246, 214, .55), 0 10px 26px rgba(0, 0, 0, .5);
  }
  @keyframes fade { from { opacity: 0; } }
  :global(html.rm) .veil { animation: none; }
</style>
