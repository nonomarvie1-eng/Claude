<script lang="ts">
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import type { Controller } from '../game/controller';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const time = (ms: number) => new Date(ms).toLocaleTimeString(game.prefs.lang === 'fr' ? 'fr-FR' : 'en-US');
</script>

{#if game.history.length === 0}
  <p class="empty">{t.noHistory}</p>
{:else}
  <table data-testid="history-table">
    <thead><tr><th>#</th><th>{t.bet}</th><th>{t.win}</th><th></th><th></th></tr></thead>
    <tbody>
      {#each game.history as h, i}
        <tr>
          <td>{h.id}<br /><small>{time(h.time)}</small></td>
          <td>{money(h.bet, game.currency, game.prefs.lang)}</td>
          <td class:won={h.win > 0}>{money(h.win, game.currency, game.prefs.lang)}<br /><small>×{(h.payoutMultiplier / 100).toFixed(2)}</small></td>
          <td>{#if h.bonus}<span class="tag">BONUS</span>{/if}{#if h.forced}<span class="tag f">{t.forced}</span>{/if}</td>
          <td><button onclick={() => ctrl?.replay(i)} disabled={game.phase !== 'idle'}>{t.replay}</button></td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
.empty { color: var(--muted); }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th { text-align: left; color: var(--gold); font-weight: 700; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; padding: 6px; }
  td { padding: 8px 6px; border-top: 1px solid var(--line-soft); vertical-align: middle; font-variant-numeric: tabular-nums; }
  small { color: var(--muted); }
  .won { color: var(--gold-hi); }
  .tag { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--gold); color: var(--gold-hi); margin-right: 4px; }
  .tag.f { border-color: var(--tennis); color: var(--tennis); }
  button { min-height: 40px; padding: 6px 14px; border-radius: 999px; border: 1px solid var(--line); background: rgba(242,229,195,.06); color: var(--cream); font-size: 13px; font-weight: 600; }
  button:disabled { opacity: .4; }
</style>
