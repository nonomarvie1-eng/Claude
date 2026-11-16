<script lang="ts">
  import { game } from '../game/state.svelte';
  import type { Controller } from '../game/controller';
  import type { DemoRgs } from '../rgs/demoRgs';
  import { PROTO, type ProtoMode } from '../engine/rallyPath';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);

  async function force(f: 'bonus3' | 'bonus4' | 'bonus5') {
    game.modal = null;
    await ctrl?.spin(f);
  }
  const scenarios = Object.entries(PROTO.scenarios);
  async function lab(mode: ProtoMode, scenario: string | null = null) {
    game.modal = null;
    await ctrl?.labRound(mode, scenario);
  }
  function toggleLab(on: boolean) {
    game.labOn = on;
    if (game.phase === 'idle') ctrl?.scene.setProto(on);
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
  <section class="demo lab" data-testid="lab">
    <h3>{t.labTitle}</h3>
    <p>{t.labNotice}</p>
    <label class="row"><span>{t.labToggle}</span><input type="checkbox" checked={game.labOn} onchange={(e) => toggleLab(e.currentTarget.checked)} disabled={game.phase !== 'idle'} data-testid="lab-toggle" /></label>
    <h3>{t.labRandom}</h3>
    <div class="btns">
      <button onclick={() => lab('base')} disabled={game.phase !== 'idle'} data-testid="lab-base">Rally Path</button>
      <button onclick={() => lab('rally')} disabled={game.phase !== 'idle'} data-testid="lab-rally">Rally Challenge</button>
      <button onclick={() => lab('final')} disabled={game.phase !== 'idle'} data-testid="lab-final">The Grand Final</button>
    </div>
    <h3>{t.labScenarios}</h3>
    <div class="btns">
      {#each scenarios as [key, sc] (key)}
        <button onclick={() => lab(sc.mode, key)} disabled={game.phase !== 'idle'} data-testid={`lab-sc-${key}`}>{sc.label}</button>
      {/each}
    </div>
  </section>
{/if}

<style>
.rows { display: grid; gap: 2px; }
  .row { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 2px; border-bottom: 1px solid var(--line-soft); min-height: 48px; }
  input[type='checkbox'] { width: 22px; height: 22px; accent-color: var(--gold); }
  input[type='range'] { width: min(260px, 48vw); accent-color: var(--gold); }
  select { background: var(--night); color: var(--ink); border: 1px solid var(--line); border-radius: 10px; padding: 8px 10px; font-family: inherit; min-height: 40px; }
  .demo { margin-top: 18px; padding: 12px; border: 1px dashed var(--tennis); border-radius: 12px; }
  .demo p { color: var(--cream); line-height: 1.5; margin-top: 0; }
  h3 { font-family: var(--font-title); font-size: 15px; color: var(--gold-hi); }
  .btns { display: flex; flex-wrap: wrap; gap: 8px; }
  button { min-height: 44px; padding: 10px 16px; border-radius: 999px; border: 1px solid var(--line); background: rgba(242,229,195,.06); color: var(--cream); font-weight: 600; }
  button:hover:not(:disabled) { border-color: var(--gold); }
  button:disabled { opacity: .4; }
  .refill { margin-top: 12px; }
  .lab { border-color: var(--gold); }
  .lab .btns button { font-size: 13px; }
</style>
