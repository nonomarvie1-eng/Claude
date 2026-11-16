<script lang="ts">
  import { game } from '../game/state.svelte';
  import type { Controller } from '../game/controller';
  import type { DemoRgs } from '../rgs/demoRgs';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);

  async function force(f: 'bonus3' | 'bonus4' | 'bonus5') {
    game.modal = null;
    await ctrl?.spin(f);
  }
  async function refill() {
    if (!ctrl || ctrl.rgs.kind !== 'demo' || game.phase !== 'idle') return;
    (ctrl.rgs as DemoRgs).reset();
    game.balance = (await ctrl.rgs.balance()).amount;
  }
</script>

<div class="rows">
  <label class="row"><span>{t.sound}</span><input type="checkbox" bind:checked={game.prefs.sound} data-testid="set-sound" /></label>
  <label class="row"><span>{t.master}</span><input type="range" min="0" max="1" step="0.05" bind:value={game.prefs.master} /></label>
  <label class="row"><span>{t.music}</span><input type="range" min="0" max="1" step="0.05" bind:value={game.prefs.music} /></label>
  <label class="row"><span>{t.effects}</span><input type="range" min="0" max="1" step="0.05" bind:value={game.prefs.sfx} /></label>
  <label class="row"><span>{t.reducedMotion}</span><input type="checkbox" bind:checked={game.prefs.reducedMotion} data-testid="set-reduced" /></label>
  {#if !game.jurisdiction.disabledTurbo}
    <label class="row"><span>{t.turbo}</span><input type="checkbox" bind:checked={game.prefs.turbo} data-testid="set-turbo" /></label>
  {/if}
  <label class="row"><span>{t.language}</span>
    <select bind:value={game.prefs.lang}>
      <option value="fr">Français</option>
      <option value="en">English</option>
    </select>
  </label>
</div>

{#if game.isDemo}
  <section class="demo">
    <p>{t.demoNotice}</p>
    <h3>{t.testBonus}</h3>
    <div class="btns">
      <button onclick={() => force('bonus3')} disabled={game.phase !== 'idle'} data-testid="force-bonus3">3 × BONUS</button>
      <button onclick={() => force('bonus4')} disabled={game.phase !== 'idle'}>4 × BONUS</button>
      <button onclick={() => force('bonus5')} disabled={game.phase !== 'idle'}>5 × BONUS</button>
    </div>
    <button class="refill" onclick={refill} disabled={game.phase !== 'idle'}>{t.resetCredits}</button>
  </section>
{/if}

<style>
  .rows { display: grid; gap: 4px; }
  .row { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 4px; border-bottom: 1px solid rgba(255,255,255,.06); }
  input[type='checkbox'] { width: 22px; height: 22px; accent-color: var(--gold); }
  input[type='range'] { width: min(260px, 50vw); accent-color: var(--gold); }
  select { background: var(--deep-2); color: var(--ink); border: var(--chunky); box-shadow: var(--pop); border-radius: 8px; padding: 6px 10px; font-family: inherit; }
  .demo { margin-top: 18px; padding: 12px; border: 1px dashed #dcef4c; border-radius: 12px; }
  .demo p { color: #eef6c4; line-height: 1.5; margin-top: 0; }
  h3 { font-family: var(--font-title); font-size: 15px; color: var(--gold-hi); }
  .btns { display: flex; flex-wrap: wrap; gap: 8px; }
  button { padding: 10px 16px; border-radius: 999px; border: var(--chunky); box-shadow: var(--pop); background: radial-gradient(circle at 40% 30%, #2a7a5a, #06241a); color: var(--gold); }
  button:disabled { opacity: .4; }
  .refill { margin-top: 12px; }
</style>
