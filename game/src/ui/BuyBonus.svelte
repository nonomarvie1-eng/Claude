<script lang="ts">
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import { fmt } from '../i18n/strings';
  import { RULES } from '../engine/rules';
  import type { Controller } from '../game/controller';
  import trophy from '../assets/img/ui_tiebreak.webp?url';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const cost = RULES.buyBonus.cost;
  const price = $derived(game.bet * cost);
  const enough = $derived(price <= game.balance);
  async function buy() {
    game.modal = null;
    await ctrl?.buyBonus();
  }
</script>

<div class="buy">
  <img src={trophy} alt="" />
  <div>
    <p>{t.buyText}</p>
    <p class="price" data-testid="buy-price">{fmt(t.buyCost, { x: cost, amount: money(price, game.currency, game.prefs.lang) })}</p>
    {#if RULES.buyBonus.rtp && game.jurisdiction.displayRTP !== false}
      <p class="small">{fmt(t.buyRtp, { rtp: (RULES.buyBonus.rtp * 100).toFixed(2) })}</p>
    {/if}
    {#if !enough}<p class="warn">{t.insufficient}</p>{/if}
  </div>
</div>
<div class="actions">
  <button class="ghost" onclick={() => (game.modal = null)}>{t.cancel}</button>
  <button class="go" onclick={buy} disabled={!enough} data-testid="buy-confirm">{t.buyConfirm}</button>
</div>

<style>
.buy { display: flex; gap: 16px; align-items: center; }
  img { width: 120px; height: 120px; flex: none; }
  p { line-height: 1.5; margin: 6px 0; }
  .price { font-family: var(--font-title); font-weight: 700; font-size: 22px; color: var(--gold-hi); }
  .small { color: var(--muted); font-size: 14px; }
  .warn { color: var(--danger); }
  .actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
  button { min-height: 48px; font-weight: 800; letter-spacing: .06em; font-size: 15px; padding: 10px 24px; border-radius: 999px; }
  .ghost { background: transparent; color: var(--cream); border: 1px solid var(--line); }
  .go { background: var(--gold-btn); color: var(--night); border: none; }
  .go:disabled { opacity: .4; }
  @media (max-width: 480px) { .buy { flex-direction: column; text-align: center; } }
</style>
