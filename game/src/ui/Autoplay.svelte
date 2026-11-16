<script lang="ts">
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import type { Controller } from '../game/controller';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const counts = [10, 25, 50, 100];
  const lossMult = [10, 25, 50, 100];
  const winMult = [null, 10, 50, 100] as const;
  let count = $state(10);
  let loss = $state(25);
  let win = $state<number | null>(null);
  let stopOnBonus = $state(true);

  async function start() {
    game.modal = null;
    await ctrl?.autoplay({
      count,
      lossLimit: loss * game.bet,
      singleWinLimit: win === null ? null : win * game.bet,
      stopOnBonus,
    });
  }
</script>

<fieldset>
  <legend>{t.autoCount}</legend>
  <div class="chips">
    {#each counts as c}<button class:on={count === c} onclick={() => (count = c)} data-testid="auto-count-{c}">{c}</button>{/each}
  </div>
</fieldset>
<fieldset>
  <legend>{t.autoLoss}</legend>
  <div class="chips">
    {#each lossMult as m}<button class:on={loss === m} onclick={() => (loss = m)}>{money(m * game.bet, game.currency, game.prefs.lang)}</button>{/each}
  </div>
</fieldset>
<fieldset>
  <legend>{t.autoWin}</legend>
  <div class="chips">
    {#each winMult as m}<button class:on={win === m} onclick={() => (win = m)}>{m === null ? t.autoNone : money(m * game.bet, game.currency, game.prefs.lang)}</button>{/each}
  </div>
</fieldset>
<label class="row"><input type="checkbox" bind:checked={stopOnBonus} /> {t.autoBonus}</label>
<p class="note">{t.autoNote}</p>
<div class="actions">
  <button class="ghost" onclick={() => (game.modal = null)}>{t.cancel}</button>
  <button class="go" onclick={start} data-testid="auto-start">{t.autoStart}</button>
</div>

<style>
  fieldset { border: none; padding: 0; margin: 0 0 14px; }
  legend { font-family: var(--font-title); color: var(--gold); margin-bottom: 8px; -webkit-text-stroke: .8px var(--ink-line); }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chips button { min-width: 64px; padding: 8px 14px; border-radius: 999px; border: var(--chunky); box-shadow: var(--pop); background: radial-gradient(circle at 40% 30%, #2a7a5a, #06241a); color: var(--gold); font-family: var(--font-ui); font-size: 16px; }
  .chips button.on { background: radial-gradient(circle at 40% 25%, #fffbe0, #ffd75e 40%, #c58512); color: #3a2404; }
  .row { display: flex; align-items: center; gap: 10px; margin: 8px 0; }
  input[type='checkbox'] { width: 22px; height: 22px; accent-color: var(--gold); }
  .note { color: var(--muted); font-size: 14px; line-height: 1.5; }
  .actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 12px; }
  .actions button { font-family: var(--font-title); font-size: 20px; padding: 10px 24px; border-radius: 999px; border: var(--chunky); box-shadow: var(--pop); }
  .ghost { background: radial-gradient(circle at 40% 30%, #2a7a5a, #06241a); color: var(--gold); }
  .go { background: radial-gradient(circle at 40% 25%, #fffbe0, #ffd75e 40%, #c58512); color: #3a2404; }
</style>
