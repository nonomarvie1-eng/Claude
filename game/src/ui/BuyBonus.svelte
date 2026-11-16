<script lang="ts">
  // Game-mode picker: Normal / Bonus Chance (spin modes) and the two direct buys.
  // Every price and statistic comes from RULES.modes (exported by the maths).
  import { game } from '../game/state.svelte';
  import { money } from '../game/format';
  import { fmt } from '../i18n/strings';
  import { RULES } from '../engine/rules';
  import type { ModeName } from '../engine/types';
  import type { Controller } from '../game/controller';
  import emblem from '../assets/img/ui_tiebreak.webp?url';
  import scatter from '../assets/img/sym_S.webp?url';
  import ball from '../assets/img/sym_L1.webp?url';
  let { ctrl }: { ctrl: Controller | null } = $props();
  const t = $derived(game.t);
  const M = RULES.modes;
  const lv = RULES.bonusLevels;
  let confirm = $state<null | 'buy_rally' | 'buy_final'>(null);
  const price = (m: ModeName) => Math.round(game.bet * M[m].cost);
  const fmtMoney = (v: number) => money(v, game.currency, game.prefs.lang);
  const rtp = (m: ModeName) => (M[m].rtp ? (M[m].rtp! * 100).toFixed(2) : '—');
  const showRtp = $derived(game.jurisdiction.displayRTP !== false);
  const oneIn = (x: number | null) => (x ? Math.round(x).toLocaleString(game.prefs.lang) : '—');
  const buys = $derived(!game.jurisdiction.disabledBuyBonus);
  const chance = $derived(!game.jurisdiction.disabledBonusChance);

  function choose(m: 'base' | 'bonus_chance') {
    game.spinMode = m;
    game.modal = null;
  }
  async function doBuy() {
    const m = confirm;
    if (!m) return;
    confirm = null;
    game.modal = null;
    await ctrl?.buyBonus(m);
  }
</script>

{#if confirm}
  {@const m = confirm}
  <div class="confirm" data-testid="buy-confirm-step">
    <img src={emblem} alt="" class:super={m === 'buy_final'} />
    <h3 class:super={m === 'buy_final'}>{m === 'buy_final' ? t.modeBuyStb : t.modeBuyTb}</h3>
    <p class="big" data-testid="buy-price">{fmtMoney(price(m))}</p>
    <p>{fmt(t.confirmText, { mode: m === 'buy_final' ? t.modeBuyStb : t.modeBuyTb, amount: fmtMoney(price(m)), x: M[m].cost, bet: fmtMoney(game.bet) })}</p>
    <p class="small">{fmt(m === 'buy_final' ? t.modeBuyStbDesc : t.modeBuyTbDesc, { n: M[m].spins ?? '' })}</p>
    {#if showRtp}<p class="small">{fmt(t.buyRtp, { rtp: rtp(m) })}</p>{/if}
    {#if price(m) > game.balance}<p class="warn">{t.insufficient}</p>{/if}
    <div class="actions">
      <button class="ghost" onclick={() => (confirm = null)}>{t.back}</button>
      <button class="go" onclick={doBuy} disabled={price(m) > game.balance} data-testid="buy-confirm">{t.buyConfirm}</button>
    </div>
  </div>
{:else}
  <p class="intro">{t.buyText}</p>
  <div class="cards">
    <article class="card" class:on={game.spinMode === 'base'}>
      <header><img src={ball} alt="" /><h3>{t.modeNormal}</h3></header>
      <p class="desc">{t.modeNormalDesc}</p>
      <dl>
        <dt>{t.modeSpinCost}</dt><dd>{fmtMoney(price('base'))}</dd>
        {#if showRtp}<dt>RTP</dt><dd>{rtp('base')} %</dd>{/if}
        <dt>{t.colBonus}</dt><dd>1 / {oneIn(M.base.bonusOneIn)}</dd>
      </dl>
      <button class="sel" onclick={() => choose('base')} disabled={game.spinMode === 'base'} data-testid="mode-base">{game.spinMode === 'base' ? t.modeActive : t.modeChoose}</button>
    </article>

    {#if chance}
      <article class="card chance" class:on={game.spinMode === 'bonus_chance'}>
        <header><img src={scatter} alt="" /><h3>{t.modeChance}</h3><span class="x">×{M.bonus_chance.cost}</span></header>
        <p class="desc">{fmt(t.modeChanceDesc, { x: M.bonus_chance.cost, b: oneIn(M.bonus_chance.bonusOneIn), b0: oneIn(M.base.bonusOneIn), s: oneIn(M.bonus_chance.finalOneIn), s0: oneIn(M.base.finalOneIn) })}</p>
        <dl>
          <dt>{t.modeSpinCost}</dt><dd>{fmtMoney(price('bonus_chance'))}</dd>
          {#if showRtp}<dt>RTP</dt><dd>{rtp('bonus_chance')} %</dd>{/if}
        </dl>
        <button class="sel" onclick={() => choose('bonus_chance')} disabled={game.spinMode === 'bonus_chance'} data-testid="mode-chance">{game.spinMode === 'bonus_chance' ? t.modeActive : t.modeChoose}</button>
      </article>
    {/if}

    {#if buys}
      <article class="card buy">
        <header><img src={emblem} alt="" /><h3>{t.modeBuyTb}</h3><span class="x">×{M.buy_rally.cost}</span></header>
        <p class="desc">{fmt(t.modeBuyTbDesc, { n: M.buy_rally.spins ?? '' })}</p>
        <dl>
          <dt>{t.colCost}</dt><dd>{fmtMoney(price('buy_rally'))}</dd>
          {#if showRtp}<dt>RTP</dt><dd>{rtp('buy_rally')} %</dd>{/if}
        </dl>
        <button class="sel buy-btn" onclick={() => (confirm = 'buy_rally')} disabled={price('buy_rally') > game.balance} data-testid="buy-tb">{t.modeBuy}</button>
      </article>
      <article class="card buy super">
        <header><img src={emblem} alt="" /><h3>{t.modeBuyStb}</h3><span class="x">×{M.buy_final.cost}</span></header>
        <p class="desc">{fmt(t.modeBuyStbDesc, { n: M.buy_final.spins ?? '' })}</p>
        <dl>
          <dt>{t.colCost}</dt><dd>{fmtMoney(price('buy_final'))}</dd>
          {#if showRtp}<dt>RTP</dt><dd>{rtp('buy_final')} %</dd>{/if}
        </dl>
        <button class="sel buy-btn" onclick={() => (confirm = 'buy_final')} disabled={price('buy_final') > game.balance} data-testid="buy-stb">{t.modeBuy}</button>
      </article>
    {/if}
  </div>
{/if}

<style>
  .intro { margin: 0 0 12px; color: var(--muted); font-size: 14px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
  .card { display: flex; flex-direction: column; gap: 8px; padding: 12px; border-radius: 14px; background: rgba(242, 229, 195, 0.04); border: 1px solid var(--line-soft); }
  .card.on { border-color: var(--gold); box-shadow: inset 0 0 0 1px var(--gold); }
  .card.chance { border-color: rgba(55, 182, 255, 0.45); }
  .card.chance.on { border-color: #37b6ff; box-shadow: inset 0 0 0 1px #37b6ff; }
  .card.super { background: linear-gradient(180deg, rgba(11, 31, 74, 0.85), rgba(8, 27, 35, 0.6)); border-color: rgba(55, 182, 255, 0.6); }
  header { display: flex; align-items: center; gap: 8px; }
  header img { width: 40px; height: 40px; flex: none; }
  h3 { margin: 0; font-family: var(--font-title); font-size: 15px; color: var(--gold-hi); line-height: 1.15; flex: 1; }
  .super h3, h3.super { color: #cfeaff; }
  .x { font-family: var(--font-title); font-weight: 700; color: var(--cream); font-size: 14px; }
  .desc { margin: 0; font-size: 13px; line-height: 1.45; color: var(--cream); flex: 1; }
  dl { display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; margin: 0; font-size: 13px; }
  dt { color: var(--muted); }
  dd { margin: 0; text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }
  .sel { min-height: 44px; border-radius: 999px; border: 1px solid var(--line); background: rgba(242, 229, 195, 0.06); color: var(--cream); font-weight: 800; letter-spacing: 0.04em; }
  .sel:disabled { opacity: 0.55; cursor: default; }
  .buy-btn { background: var(--gold-btn); color: var(--night); border: none; }
  .super .buy-btn { background: linear-gradient(180deg, #ffffff, #bfe6ff 55%, #37b6ff); }
  .buy-btn:disabled { opacity: 0.4; }
  .confirm { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 6px; }
  .confirm img { width: 110px; height: 110px; }
  .confirm img.super { filter: drop-shadow(0 0 14px #37b6ff); }
  .confirm h3 { flex: none; font-size: 20px; }
  .big { font-family: var(--font-title); font-weight: 700; font-size: 30px; color: var(--gold-hi); margin: 2px 0; }
  .confirm p { margin: 2px 0; line-height: 1.5; max-width: 460px; }
  .small { color: var(--muted); font-size: 13px; }
  .warn { color: var(--danger); }
  .actions { display: flex; justify-content: center; gap: 12px; margin-top: 10px; flex-wrap: wrap; }
  .actions button { min-height: 48px; font-weight: 800; letter-spacing: 0.06em; font-size: 15px; padding: 10px 24px; border-radius: 999px; }
  .ghost { background: transparent; color: var(--cream); border: 1px solid var(--line); }
  .go { background: var(--gold-btn); color: var(--night); border: none; }
  .go:disabled { opacity: 0.4; }
</style>
