<script lang="ts">
  import { game } from '../game/state.svelte';
  import type { Controller } from '../game/controller';
  import type { DemoRgs } from '../rgs/demoRgs';
  import { PROTO, GAME_SCENARIOS, type ProtoMode } from '../engine/rallyPath';
  import { RALLY_PATH_BUILD, GOLDEN_SERVE_BUILD, FINAL_SET_BUILD, DUEL_BUILD } from '../engine/gameplay';
  import { DUEL } from '../engine/duel';
  import { GS } from '../engine/goldenServe';
  import type { ForcedScenario } from '../rgs/demoRgs';
  async function forceGame(k: string) {
    game.modal = null;
    await ctrl?.spin(k as ForcedScenario);
  }
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
    {#if DUEL_BUILD}
    <h3>{t.duelLabTitle}</h3>
    <p>{t.duelLabNotice}</p>
    <div class="btns">
      <button onclick={() => ctrl?.labPoints(['double_fault', 'ace', 'winner'])} disabled={game.phase !== 'idle'} data-testid="duel-demo3">{t.duelDemo3}</button>
      {#each Object.entries(DUEL.pointScenarios) as [k, sc] (k)}
        <button onclick={() => ctrl?.labPoints([k])} disabled={game.phase !== 'idle'} data-testid={`duel-pt-${k}`}>{sc.label}</button>
      {/each}
      <button onclick={() => ctrl?.labPoints(null, 'tiebreak')} disabled={game.phase !== 'idle'} data-testid="duel-random-tb">Point aléatoire · Tie-Break</button>
      <button onclick={() => ctrl?.labPoints(null, 'final')} disabled={game.phase !== 'idle'} data-testid="duel-random-gf">Point aléatoire · Grand Final</button>
    </div>
    <h3>{t.duelRounds}</h3>
    <div class="btns">
      {#each Object.entries(DUEL.roundScenarios) as [k, sc] (k)}
        <button onclick={() => forceGame(`duel_${k}`)} disabled={game.phase !== 'idle'} data-testid={`force-duel-${k}`}>{sc.label}</button>
      {/each}
    </div>
    {:else if GOLDEN_SERVE_BUILD}
    <h3>{t.gsConcept}</h3>
    <div class="btns" role="radiogroup">
      <button class:on={game.concept === 'A'} aria-pressed={game.concept === 'A'} onclick={() => (game.concept = 'A')} disabled={game.phase !== 'idle'} data-testid="concept-A">{t.gsConceptA}</button>
      <button class:on={game.concept === 'B'} aria-pressed={game.concept === 'B'} onclick={() => (game.concept = 'B')} disabled={game.phase !== 'idle'} data-testid="concept-B">{t.gsConceptB}</button>
    </div>
    <h3>{t.gsTitle}</h3>
    <div class="btns">
      {#each Object.entries(GS.scenarios) as [k, sc] (k)}
        <button onclick={() => forceGame(`gs_${k}`)} disabled={game.phase !== 'idle'} data-testid={`force-gs-${k}`}>{sc.label}</button>
      {/each}
    </div>
    {:else if RALLY_PATH_BUILD}
    <h3>{t.testTitle}</h3>
    <div class="btns">
      {#each Object.entries(GAME_SCENARIOS) as [k, sc] (k)}
        <button onclick={() => forceGame(k)} disabled={game.phase !== 'idle'} data-testid={`force-${k}`}>{sc.label}</button>
      {/each}
    </div>
    {:else}
    <h3>{t.testBonus}</h3>
    <div class="btns">
      <button onclick={() => force('bonus3')} disabled={game.phase !== 'idle'} data-testid="force-bonus3">3 × BONUS</button>
      <button onclick={() => force('bonus4')} disabled={game.phase !== 'idle'}>4 × BONUS</button>
      <button onclick={() => force('bonus5')} disabled={game.phase !== 'idle'}>5 × BONUS</button>
    </div>
    {/if}
    <button class="refill" onclick={refill} disabled={game.phase !== 'idle'}>{t.resetCredits}</button>
  </section>
  {#if FINAL_SET_BUILD}
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
  button.on { border-color: #D9EF38; background: rgba(217,239,56,.16); color: #fff; }
  .lab .btns button { font-size: 13px; }
</style>
