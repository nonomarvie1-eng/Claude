<script lang="ts">
  import { game } from '../game/state.svelte';
  import { RULES } from '../engine/rules';
  import { money } from '../game/format';
  import { fmt } from '../i18n/strings';
  import type { SymbolName } from '../engine/types';

  const urls = import.meta.glob('../assets/img/sym_*.webp', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
  const img = (s: string) => Object.entries(urls).find(([k]) => k.endsWith(`sym_${s}.webp`))?.[1];
  const t = $derived(game.t);
  const pay = (pm: number) => money(Math.round((game.bet * pm) / 100), game.currency, game.prefs.lang);
  const order: SymbolName[] = ['H1', 'H2', 'H3', 'H4', 'H5', 'L1', 'L2', 'L3', 'L4', 'L5'];
  const name = (s: SymbolName) => (game.prefs.lang === 'fr' ? RULES.symbolInfo[s].fr : RULES.symbolInfo[s].label);
  const stats = RULES.stats;
  const showRtp = $derived(game.jurisdiction.displayRTP !== false);
</script>

<p class="note">{t.paysInCredits} : <strong>{money(game.bet, game.currency, game.prefs.lang)}</strong></p>

<section class="specials">
  <div class="special">
    <img src={img('W')} alt={name('W')} />
    <div><h3>{name('W')} — WILD</h3><p>{t.rulesWild}</p></div>
  </div>
  <div class="special">
    <img src={img('S')} alt={name('S')} />
    <div><h3>{name('S')} — BONUS</h3><p>{fmt(t.rulesScatter, { s3: pay(RULES.scatterPay['3']), s4: pay(RULES.scatterPay['4']), s5: pay(RULES.scatterPay['5']), s6: pay(RULES.scatterPay['6']) })}</p></div>
  </div>
</section>

<section class="grid">
  {#each order as s}
    <div class="sym">
      <img src={img(s)} alt={name(s)} />
      <div class="nm">{name(s)}</div>
      <table>
        <tbody>
          {#each ['6', '5', '4', '3'] as k}
            <tr><td>{k}×</td><td>{pay(RULES.paytable[s][k])}</td></tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/each}
</section>

<section>
  <h3>Tie-Break — Rally</h3>
  <p>{t.rulesFs}</p>
  <div class="ladder">
    {#each RULES.rallyLadder as m, i}<span class:top={i === RULES.rallyLadder.length - 1}>×{m}</span>{/each}
  </div>
</section>

<section>
  <h3>{t.paylines}</h3>
  <p>{t.rulesLines}</p>
  <div class="ways" aria-hidden="true">
    {#each [0, 1, 2, 3, 4, 5] as reel}
      <div class="col">
        {#each [0, 1, 2, 3, 4] as row}
          <i class:on={(reel === 0 && row === 1) || (reel === 1 && (row === 0 || row === 3)) || (reel === 2 && row === 2) || (reel === 3 && row === 4)}></i>
        {/each}
      </div>
    {/each}
    <span class="ex">1 × 2 × 1 × 1 = 2 {t.ways}</span>
  </div>
</section>

<section class="rules">
  <h3>{t.rules}</h3>
  <p>{t.rulesOutcome}</p>
  {#if !game.jurisdiction.disabledBuyBonus && RULES.buyBonus.rtp}
    <p>{fmt(t.buyRule, { x: RULES.buyBonus.cost, rtp: (RULES.buyBonus.rtp * 100).toFixed(2) })}</p>
  {/if}
  <p>{fmt(t.maxWinRule, { x: RULES.wincapX.toLocaleString(game.prefs.lang) })}</p>
  {#if stats && showRtp}
    <p data-testid="rtp">{fmt(t.rtpRule, { rtp: (stats.rtp * 100).toFixed(2) })}</p>
    <p>{fmt(t.hitRule, { hit: (1 / stats.hitFrequency).toFixed(2), bonus: Math.round(stats.bonusOneIn) })}</p>
    <p>{fmt(t.volatility, { sd: stats.stdDev.toFixed(1) })}</p>
  {/if}
  <p>{t.malfunction}</p>
  {#if game.isDemo}<p class="demo">{t.demoNotice}</p>{/if}
  <p class="ver">{t.version} : game 1.0.0 · math {RULES.mathVersion}</p>
</section>

<style>
  .note { color: var(--muted); margin-top: 0; }
  h3 { font-family: var(--font-title); color: var(--gold-hi); letter-spacing: .08em; font-size: 16px; margin: 18px 0 8px; }
  p { line-height: 1.55; margin: 6px 0; }
  .specials { display: grid; gap: 12px; }
  .special { display: flex; gap: 14px; align-items: center; background: rgba(255,255,255,.03); border: 1px solid rgba(227,181,82,.25); border-radius: 12px; padding: 10px; }
  .special img { width: 96px; height: 96px; flex: none; }
  .special h3 { margin-top: 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-top: 14px; }
  .sym { text-align: center; background: rgba(255,255,255,.03); border: 1px solid rgba(227,181,82,.2); border-radius: 12px; padding: 8px; }
  .sym img { width: 92px; height: 92px; }
  .nm { font-size: 13px; color: var(--muted); }
  table { margin: 4px auto 0; border-collapse: collapse; }
  td { padding: 2px 8px; font-size: 14px; }
  td:first-child { color: var(--muted); }
  td:last-child { color: var(--gold-hi); font-family: var(--font-title); }
  .ladder { display: flex; flex-wrap: wrap; gap: 6px; }
  .ladder span { padding: 6px 12px; border-radius: 999px; border: var(--chunky); font-family: var(--font-title); }
  .ladder .top { background: var(--gold-grad); color: #2a1c06; }
  .ways { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .col { display: grid; gap: 4px; }
  .col i { width: 22px; height: 22px; border-radius: 5px; background: rgba(0,0,0,.08); border: 2px solid var(--ink-line); }
  .col i.on { background: var(--accent); }
  .ex { margin-left: 10px; font-family: var(--font-title); color: var(--accent-2); }
  .demo { color: #eef6c4; }
  .ver { color: var(--muted); font-size: 12px; }
</style>
