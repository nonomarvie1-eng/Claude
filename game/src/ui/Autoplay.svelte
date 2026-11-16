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
  legend { font-family: var(--font-title); font-weight: 700; color: var(--gold-hi); margin-bottom: 8px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chips button { min-width: 64px; min-height: 44px; padding: 8px 14px; border-radius: 999px; border: 1px solid var(--line); background: rgba(242,229,195,.06); color: var(--cream); font-size: 15px; font-weight: 600; font-variant-numeric: tabular-nums; }
  .chips button.on { background: var(--gold-btn); color: var(--night); border-color: transparent; font-weight: 800; }
  .row { display: flex; align-items: center; gap: 10px; margin: 8px 0; min-height: 44px; }
  input[type='checkbox'] { width: 22px; height: 22px; accent-color: var(--gold); }
  .note { color: var(--muted); font-size: 14px; line-height: 1.5; }
  .actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
  .actions button { min-height: 48px; font-weight: 800; letter-spacing: .06em; font-size: 15px; padding: 10px 24px; border-radius: 999px; }
  .ghost { background: transparent; color: var(--cream); border: 1px solid var(--line); }
  .go { background: var(--gold-btn); color: var(--night); border: none; }
</style>
