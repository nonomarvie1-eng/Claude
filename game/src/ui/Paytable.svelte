<script lang="ts">
  import { game } from '../game/state.svelte';
  import { RULES } from '../engine/rules';
  import { money } from '../game/format';
  import { fmt } from '../i18n/strings';
  import type { ModeName, SymbolName } from '../engine/types';
  import { RALLY_PATH_BUILD, GOLDEN_SERVE_BUILD, FINAL_SET_BUILD, DUEL_BUILD, RETURN_SPINS_BUILD, BUILD_ID } from '../engine/gameplay';
  import { RS } from '../engine/returnSpins';
  const RSS = RS.stats;
  const p2 = (x: number) => `${(x * 100).toLocaleString(game.prefs.lang, { maximumFractionDigits: 2 })} %`;
  import { DUEL } from '../engine/duel';
  const DX = DUEL.exact;
  const pct1 = (x: number) => `${(x * 100).toLocaleString(game.prefs.lang, { maximumFractionDigits: 1 })} %`;
  const outNames: Record<string, string> = { DOUBLE_FAULT: 'Double faute', ACE: 'Ace', LOST: 'Échange perdu', RALLY_WON: 'Point gagné (erreur adverse)', WINNER: 'Coup gagnant', GOLDEN: 'Golden Winner / Golden Smash' };
  import { GS } from '../engine/goldenServe';
  const GR = GS.rules;
  const pc = (x: number) => `${(x * 100).toLocaleString(game.prefs.lang, { maximumFractionDigits: 2 })} %`;
  import { PROTO } from '../engine/rallyPath';
  const RP = PROTO.rules;
  // in the Rally Path build the racket pays the prototype ways table (t-units -> payoutMultiplier x10)
  const payOf = (s: SymbolName, k: string) => (RALLY_PATH_BUILD && s === RP.racket ? RP.racketWaysPay[k] * 10 : RULES.paytable[s][k]);

  // Every value on this page comes from RULES (exported by the validated maths).
  const urls = import.meta.glob('../assets/img/sym_*.webp', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
  const img = (s: string) => Object.entries(urls).find(([k]) => k.endsWith(`sym_${s}.webp`))?.[1];
  const t = $derived(game.t);
  const pay = (pm: number) => money(Math.round((game.bet * pm) / 100), game.currency, game.prefs.lang);
  const premium: SymbolName[] = ['H1', 'H2', 'H3', 'H4'];
  const classic: SymbolName[] = ['L1', 'L2', 'L3', 'L4', 'L5'];
  const name = (s: SymbolName) => (game.prefs.lang === 'fr' ? RULES.symbolInfo[s].fr : RULES.symbolInfo[s].label);
  const showRtp = $derived(game.jurisdiction.displayRTP !== false);
  const M = RULES.modes;
  const oneIn = (x: number | null) => (x ? Math.round(x).toLocaleString(game.prefs.lang) : '—');
  const rtp = (m: ModeName) => (M[m].rtp ? (M[m].rtp! * 100).toFixed(2) : '—');
  const modeName = (m: ModeName) => ({ base: t.modeNormal, bonus_chance: t.modeChance, buy_rally: t.modeBuyTb, buy_final: t.modeBuyStb })[m];
  const modes: ModeName[] = ['base', 'bonus_chance', 'buy_rally', 'buy_final'];
  const triggers = Object.entries(RULES.fsAward).map(([k, n]) => ({ k: +k, n, level: +k === 3 ? 'rally' : 'final' }) as const);
  const FS = RULES.finalSet;
  const shots = ['RALLY', 'ACE', 'SMASH', 'PASSING', 'DROP', 'GOLDEN'] as const;
  const pct = (w: number) => `${((w / FS.SHOT_ROLL) * 100).toLocaleString(game.prefs.lang, { maximumFractionDigits: 1 })} %`;
</script>

<p class="note">{t.paysInCredits} : <strong>{money(game.bet, game.currency, game.prefs.lang)}</strong></p>

<h3>{t.special}</h3>
<section class="specials">
  <div class="special wild">
    <img src={img('W')} alt="WILD" />
    <div><h4>WILD</h4><p>{t.rulesWild}</p></div>
  </div>
  <div class="special scatter">
    <img src={img('S')} alt="SCATTER" />
    <div><h4>SCATTER</h4><p>{fmt(t.rulesScatter, { s3: pay(RULES.scatterPay['3']), s4: pay(RULES.scatterPay['4']), s5: pay(RULES.scatterPay['5']), s6: pay(RULES.scatterPay['6']) })}</p></div>
  </div>
</section>

{#each [{ title: t.premium, list: premium }, { title: t.classic, list: classic }] as grp}
  <h3>{grp.title}</h3>
  <section class="grid">
    {#each grp.list as s}
      <div class="sym" data-testid="pay-{s}">
        <img src={img(s)} alt={name(s)} />
        <div class="nm">{name(s)}</div>
        <table><tbody>
          {#each ['6', '5', '4', '3'] as k}<tr><td>{k}×</td><td>{pay(payOf(s, k))}</td></tr>{/each}
        </tbody></table>
      </div>
    {/each}
  </section>
{/each}

<section>
  <h3>{t.connectionsTitle}</h3>
  <p>{t.rulesLines}</p>
  <div class="ways" aria-hidden="true">
    {#each [0, 1, 2, 3, 4, 5] as reel}
      <div class="col">
        <b>{[2, 1, 3, 0, 0, 0][reel] || ''}</b>
        {#each [0, 1, 2, 3, 4] as row}
          <i class:on={(reel === 0 && (row === 1 || row === 3)) || (reel === 1 && row === 2) || (reel === 2 && (row === 0 || row === 2 || row === 4))}></i>
        {/each}
      </div>
    {/each}
    <span class="ex">2 × 1 × 3 = 6 {t.ways}</span>
  </div>
</section>

{#if RETURN_SPINS_BUILD}
<section data-testid="rs-rules">
  <h3>GOLDEN SERVE — RETURN SPINS</h3>
  <div class="special"><img src={img('G')} alt="Golden Ball" style="width:72px;height:72px" /><div><p>{t.rsRule1}</p></div></div>
  <p>{t.rsRule2}</p>
  <p>{t.rsRule3}</p>
  <p>{fmt(t.rsRule4, { b: RS.rules.MAX_RETURNS.base, r: RS.rules.MAX_RETURNS.rally, f: RS.rules.MAX_RETURNS.final })}</p>
  <p>{fmt(t.rsRule5, { a: RS.rules.BONUS.rally.spins, b: RS.rules.BONUS.final.spins })}</p>
  {#if showRtp}
    <p data-testid="rs-stats">{fmt(t.rsStats, { rtp: p2(RSS.game.rtp), lo: p2(RSS.game.ci95[0]), hi: p2(RSS.game.ci95[1]), n: (RSS.n / 1e6).toLocaleString(game.prefs.lang), serve: RSS.game.serve_1_in.toFixed(1), rc: RSS.bonus_rally.mean_x.toFixed(1), cn: RSS.bonus_final.mean_x.toFixed(1) })}</p>
  {/if}
  <p class="demo">{t.rsRuleProto}</p>
</section>
{:else if DUEL_BUILD}
<section data-testid="duel-rules">
  <h3>CHAMPIONSHIP DUEL</h3>
  <p>{t.duelRule1}</p>
  <p>{t.duelRule2}</p>
  <table class="modes" data-testid="duel-table">
    <thead><tr><th>{t.duelColEvent}</th><th>Tie-Break Duel</th><th>Grand Final</th></tr></thead>
    <tbody>
      {#each Object.keys(outNames) as o}
        <tr><td>{outNames[o]}</td><td>{pct1(DX.tiebreak.point.p_outcome[o])}</td><td>{pct1(DX.final.point.p_outcome[o])}</td></tr>
      {/each}
      <tr><td>Golden Match Point (par point)</td><td>—</td><td>{pct1(DX.final.point.p_gmp)}</td></tr>
    </tbody>
  </table>
  <p>{t.duelRule3}</p>
  {#if showRtp}
    <p data-testid="duel-stats">{fmt(t.duelStats, { rtp: (DX.rtp.total * 100).toFixed(2), tb: DX.tiebreak.bonus.mean_x.toFixed(1), gf: DX.final.bonus.mean_x.toFixed(1), tbm: DX.tiebreak.bonus.quantiles_x['0.5'], gfm: DX.final.bonus.quantiles_x['0.5'], max: DX.final.bonus.max_x })}</p>
  {/if}
  <p class="demo">{t.duelRuleProto}</p>
</section>
{:else if GOLDEN_SERVE_BUILD}
<section data-testid="golden-serve-rules">
  <h3>GOLDEN SERVE</h3>
  <div class="special"><img src={img('G')} alt="Golden Ball" style="width:72px;height:72px" /><div><p>{t.gsRule1}</p></div></div>
  <p>{t.gsRule2}</p>
  {#if game.concept === 'A'}<p><strong>{t.gsConceptA}</strong> — {t.gsRuleA}</p>{:else}<p><strong>{t.gsConceptB}</strong> — {t.gsRuleB}</p>{/if}
  <p>{fmt(t.gsRule3, { s: (GR.P_SMASH.base / 10).toLocaleString(game.prefs.lang), sr: (GR.P_SMASH.rally / 10).toLocaleString(game.prefs.lang), sf: (GR.P_SMASH.final / 10).toLocaleString(game.prefs.lang), dr: (GR.P_DOUBLE.rally / 10).toLocaleString(game.prefs.lang), df: (GR.P_DOUBLE.final / 10).toLocaleString(game.prefs.lang) })}</p>
  <p>{fmt(t.gsRule4, { a: GR.BONUS.rally.spins, b: GR.BONUS.final.spins })}</p>
  {#if showRtp}
    <p data-testid="gs-stats">{fmt(t.gsStats, { c: game.concept, rtp: pc(GS.stats[game.concept].game.rtp), lo: pc(GS.stats[game.concept].game.ci95[0]), hi: pc(GS.stats[game.concept].game.ci95[1]), n: (GS.stats[game.concept].n / 1e6).toLocaleString(game.prefs.lang), rc: GS.stats[game.concept].bonus_rally.mean_x.toFixed(1), gf: GS.stats[game.concept].bonus_final.mean_x.toFixed(1) })}</p>
  {/if}
  <p class="demo">{t.gsRuleProto}</p>
</section>
{:else if RALLY_PATH_BUILD}
<section data-testid="rally-path-rules">
  <h3>RALLY PATH</h3>
  <div class="special"><img src={img('G')} alt="Golden Ball" style="width:72px;height:72px" /><div><p>{t.rpRule1}</p></div></div>
  <p>{t.rpRule2}</p>
  <p>{fmt(t.rpRule3, { r2: pay(RP.reward['2'] * 10), r3: pay(RP.reward['3'] * 10), r4: pay(RP.reward['4'] * 10), r5: pay(RP.reward['5'] * 10) })}</p>
  <p>{fmt(t.rpRule4, { list: RP.csTable.map(([v, w]) => `${pay(v * 10)} (${(w / RP.csRoll * 100).toFixed(0)} %)`).join(' · ') })}</p>
  <p>{fmt(t.rpRule5, { a: RP.bonus.rally.spins, b: RP.bonus.final.spins })}</p>
  <p class="demo">{t.rpRuleProto}</p>
</section>
{:else}
<section data-testid="final-set-rules">
  <h3>THE FINAL SET</h3>
  <p>{t.fsRulesIntro}</p>
  <div class="court" aria-hidden="true">
    {#each ['DL', 'DC', 'DR', 'SL', 'SC', 'SR'] as z, i}<div class="z" class:short={i >= 3}>{t.zoneNames[i]}</div>{/each}
    <div class="net">{t.netLabel}</div>
  </div>
  <table class="modes">
    <thead><tr><th>SCATTERS</th><th>Bonus</th><th>{t.exchangesLabel}</th></tr></thead>
    <tbody>
      {#each triggers as tr}
        <tr class:sup={tr.level === 'final'}><td>{tr.k}</td><td>{tr.level === 'final' ? 'THE GRAND FINAL' : 'RALLY CHALLENGE'}</td><td>{tr.n}</td></tr>
      {/each}
    </tbody>
  </table>
  <h3>{t.shotsTitle}</h3>
  <table class="modes" data-testid="shot-table">
    <thead><tr><th>{t.colShot}</th><th>Rally Challenge</th><th>Grand Final</th><th>Championship Point</th></tr></thead>
    <tbody>
      {#each shots as sh}
        <tr><td><strong>{t.shotNames[sh]}</strong><br /><small>{t.shotDesc[sh]}</small></td>
          <td>{pct(FS.RALLY_TABLE[sh])}</td><td>{pct(FS.FINAL_TABLE[sh])}</td><td>{pct(FS.CP_TABLE[sh])}</td></tr>
      {/each}
    </tbody>
  </table>
  <h3>{t.courtValuesTitle}</h3>
  <div class="values">
    {#each RULES.symbols as s}
      <span><img src={img(s)} alt={s} />{pay(FS.COURT_VALUE[s] * 10)}</span>
    {/each}
  </div>
  <p>{fmt(t.fsRulesMarks, { ace: pay(FS.ACE_PRIZE * 10), mark: pay(FS.MARK_PRIZE * 10), am: FS.ACE_MARK, dm: FS.DROP_MARK, gm: FS.GOLDEN_MARK, gmin: FS.GR_MIN, gmax: FS.GR_MAX })}</p>
  <p>{fmt(t.fsRulesSlam, { slam: pay(FS.SLAM_PRIZE * 10) })}</p>
  <p>{fmt(t.fsRulesHawk, { line: (FS.P_LINE / 10).toFixed(0), inp: (FS.P_IN / 10).toFixed(0), hawk: pay(FS.HAWK_PRIZE * 10), hm: FS.HAWK_MARK })}</p>
  <p>{fmt(t.fsRulesCp, { max: FS.MAX_REMAINING })}</p>
  <p>{fmt(t.fsRulesCeremony, { a: RULES.ceremonyX.trophy, b: RULES.ceremonyX.grand })}</p>
</section>
{/if}

<section class="rules">
  {#if FINAL_SET_BUILD}
  <h3>{t.modesTable}</h3>
  <table class="modes" data-testid="modes-table">
    <thead><tr><th>{t.colMode}</th><th>{t.colCost}</th>{#if showRtp}<th>{t.colRtp}</th>{/if}<th>{t.colBonus}</th></tr></thead>
    <tbody>
      {#each modes as m}
        {#if !(M[m].kind === 'buy' && game.jurisdiction.disabledBuyBonus) && !(m === 'bonus_chance' && game.jurisdiction.disabledBonusChance)}
          <tr><td>{modeName(m)}</td><td>{M[m].cost}×</td>{#if showRtp}<td data-testid="rtp-{m}">{rtp(m)} %</td>{/if}<td>{M[m].kind === 'buy' ? t.everyRound : `1 / ${oneIn(M[m].bonusOneIn)}`}</td></tr>
        {/if}
      {/each}
    </tbody>
  </table>
  {#if !game.jurisdiction.disabledBuyBonus}
    <p>{fmt(t.buyRule, { xtb: M.buy_rally.cost, rtb: rtp('buy_rally'), xstb: M.buy_final.cost, rstb: rtp('buy_final') })}</p>
  {/if}
  {#if !game.jurisdiction.disabledBonusChance}
    <p>{fmt(t.chanceRule, { x: M.bonus_chance.cost, b: oneIn(M.bonus_chance.bonusOneIn), b0: oneIn(M.base.bonusOneIn), s: oneIn(M.bonus_chance.finalOneIn), s0: oneIn(M.base.finalOneIn), rtp: rtp('bonus_chance') })}</p>
  {/if}
  {/if}
  <h3>{t.rules}</h3>
  <p>{t.rulesOutcome}</p>
  <p>{fmt(t.maxWinRule, { x: RULES.wincapX.toLocaleString(game.prefs.lang) })}</p>
  {#if RULES.stats && showRtp && FINAL_SET_BUILD}
    <p data-testid="rtp">{fmt(t.rtpRule, { rtp: (RULES.stats.rtp * 100).toFixed(2) })}</p>
    {#if RULES.stats.hitFrequency}<p>{fmt(t.hitRule, { hit: (1 / RULES.stats.hitFrequency).toFixed(2), bonus: Math.round(RULES.stats.bonusOneIn) })}</p>{/if}
    {#if RULES.stats.stdDev}<p>{fmt(t.volatility, { sd: RULES.stats.stdDev.toFixed(1) })}</p>{/if}
  {/if}
  <p>{t.malfunction}</p>
  {#if game.isDemo}<p class="demo">{t.demoNotice}</p>{/if}
  <p class="ver">{t.version} : build {BUILD_ID} · math {RETURN_SPINS_BUILD ? 'return-spins proto' : DUEL_BUILD ? 'championship-duel proto' : GOLDEN_SERVE_BUILD ? 'golden-serve proto' : RALLY_PATH_BUILD ? 'rally-path proto' : RULES.mathVersion}</p>
</section>

<style>
  .note { color: var(--muted); margin-top: 0; }
  h3 { font-family: var(--font-title); font-weight: 700; color: var(--gold-hi); letter-spacing: .06em; font-size: 16px; margin: 18px 0 8px; }
  h4 { margin: 0 0 4px; font-family: var(--font-title); font-size: 15px; }
  p { line-height: 1.55; margin: 6px 0; }
  .specials { display: grid; gap: 10px; }
  .special { display: flex; gap: 14px; align-items: center; background: rgba(242,229,195,.04); border: 1px solid var(--line); border-radius: 14px; padding: 10px; }
  .special.wild { border-color: #ff3fb4; } .special.wild h4 { color: #ff8fd2; }
  .special.scatter { border-color: #37b6ff; } .special.scatter h4 { color: #8fd3ff; }
  .special img { width: 88px; height: 88px; flex: none; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(118px, 1fr)); gap: 8px; }
  .sym { text-align: center; background: rgba(242,229,195,.04); border: 1px solid var(--line-soft); border-radius: 14px; padding: 8px; }
  .sym img { width: 76px; height: 76px; }
  .nm { font-size: 13px; color: var(--cream); font-weight: 700; }
  table { margin: 4px auto 0; border-collapse: collapse; }
  td, th { padding: 3px 8px; font-size: 14px; font-variant-numeric: tabular-nums; }
  .sym td:first-child { color: var(--muted); }
  .sym td:last-child { color: var(--gold-hi); font-weight: 700; }
  .modes { width: 100%; margin: 8px 0; }
  .modes th { text-align: left; color: var(--gold); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; }
  .modes td { border-top: 1px solid var(--line-soft); }
  .modes tr.sup td { color: #9fdcff; }
  .ladder { display: flex; flex-wrap: wrap; gap: 6px; }
  .ladder span { padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); font-weight: 700; }
  .ladder .top { background: var(--gold-btn); color: var(--night); border-color: transparent; }
  .ways { display: flex; align-items: flex-end; gap: 6px; flex-wrap: wrap; }
  .col { display: grid; gap: 4px; justify-items: center; }
  .col b { height: 18px; font-size: 13px; color: var(--tennis); }
  .col i { width: 22px; height: 22px; border-radius: 6px; background: rgba(242,229,195,.05); border: 1px solid var(--line-soft); }
  .col i.on { background: var(--tennis); border-color: var(--tennis); }
  .ex { margin-left: 10px; font-weight: 700; color: var(--tennis); }
  .court { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; max-width: 360px; margin: 8px 0; background: #0f4a3d; padding: 4px; border-radius: 8px; border: 1px solid var(--line); }
  .court .z { height: 54px; display: grid; place-items: center; font-size: 11px; font-weight: 700; color: var(--cream); border: 1px solid rgba(242,229,195,.5); border-radius: 4px; text-align: center; }
  .court .z.short { height: 38px; }
  .court .net { grid-column: 1 / -1; text-align: center; font-size: 10px; letter-spacing: .2em; color: var(--night); background: var(--cream); border-radius: 3px; }
  .values { display: flex; flex-wrap: wrap; gap: 8px; }
  .values span { display: flex; align-items: center; gap: 4px; font-weight: 700; font-size: 13px; padding: 2px 8px 2px 2px; border: 1px solid var(--line-soft); border-radius: 999px; }
  .values img { width: 30px; height: 30px; }
  small { color: var(--muted); }
  .demo { color: var(--cream); }
  .ver { color: var(--muted); font-size: 12px; }
</style>
