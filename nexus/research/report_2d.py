"""Rapports Markdown de la phase 2D (générés depuis les résultats).

    python -m nexus.research.report_2d
"""
from __future__ import annotations

import json

from ..config import RESULTS_DIR, ROOT
from .report_2c import ATTR, batch_report, ci, f


def g_report() -> str:
    s = json.loads((RESULTS_DIR / "batch_2d_01" / "g_summary.json").read_text())
    bh = s["buy_hold"]
    o = ["## NEXUS G — Allocation dynamique BTC / liquidités (lot 2D-01)\n", ATTR, "",
         f"Fenêtre d'évaluation commune : {s['eval_window'][0][:10]} → {s['eval_window'][1][:10]} ; code `{s['code_version']}` ; "
         f"essais au registre : {s['registry_trials_total']}.\n",
         f"Buy & Hold BTC (même fenêtre, mêmes coûts) : {f(bh['net_return_pct'], 1)} %, CAGR {f(bh['cagr_pct'], 1)} %, volatilité "
         f"{f(bh['ann_vol_pct'], 1, False)} %, drawdown {f(bh['max_dd_pct'], 1, False)} %, Sharpe {f(bh['sharpe'], 2)}. Liquidités : 0 %, drawdown 0 %.\n",
         "### 1. Résultats nets sur 1 000 €\n",
         "| Hypothèse | Plafond | Final € | Rendement % | CAGR % | Vol. % | Max DD % (clôture / séance) | Sharpe | Sortino | Calmar | Temps sur marché % | Expo. moy. % | Turnover/an | Frais € | Rendement brut % | Coûts ×2 % | Verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        n = r["net"]
        o.append(f"| {r['hypothesis']} | {r['w_max']:.0%} | {f(n['final_eur'], 0, False)} | {f(n['net_return_pct'], 1)} | {f(n['cagr_pct'], 1)} | "
                 f"{f(n['ann_vol_pct'], 1, False)} | {f(n['max_dd_pct'], 1, False)} / {f(n['intraday_worst_dd_pct'], 1, False)} | {f(n['sharpe'], 2)} | "
                 f"{f(n['sortino'], 2)} | {f(n['calmar'], 2)} | {f(n['time_in_market_pct'], 1, False)} | {f(n['avg_exposure_pct'], 1, False)} | "
                 f"{f(n['turnover_per_year'], 2, False)} | {f(n['fees_eur'], 1, False)} | {f(r['gross']['net_return_pct'], 1)} | "
                 f"{f(r['cost_x2']['net_return_pct'], 1)} | {r['verdict']} |")
    o += ["\n### 2. Comparaisons aux références (différence de rendement annualisée, IC95 bootstrap par blocs de 20 jours)\n",
          "| Hypothèse | Plafond | Passif même expo. (poids) : rend. / DD / Sharpe | **Δ vs passif même expo.** [IC95] p (brut / BH) | Δ coûts ×2 | Passif même vol. (poids) : rend. | Δ vs même vol. [IC95] | Poids fixe = plafond : rend. / DD | Δ vs poids fixe | Alpha %/an [IC95] ; bêta |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        pe, pv = r["ref"]["passive_same_expo"], r["ref"]["passive_same_vol"]
        fx = r["ref"]["fixed_10pct" if r["w_max"] == 0.10 else "fixed_25pct"]
        t, tv, tf = r["vs_passive_same_expo"], r["vs_passive_same_vol"], r["vs_fixed_same_cap"]
        a = r["attribution"]
        o.append(f"| {r['hypothesis']} | {r['w_max']:.0%} | ({r['passive_same_expo_weight']:.1%}) {f(pe['net_return_pct'], 1)} / {f(pe['max_dd_pct'], 1, False)} / {f(pe['sharpe'], 2)} | "
                 f"**{f(t['diff_ann_pct'], 2)}** {ci(t['ci95_ann_pct'], 2)} p = {f(t['p'], 3, False)} / {f(r['p_bh'], 3, False)} | "
                 f"{f(r['vs_passive_same_expo_x2']['diff_ann_pct'], 2)} | ({r['passive_same_vol_weight']:.1%}) {f(pv['net_return_pct'], 1)} | "
                 f"{f(tv['diff_ann_pct'], 2)} {ci(tv['ci95_ann_pct'], 2)} | {f(fx['net_return_pct'], 1)} / {f(fx['max_dd_pct'], 1, False)} | "
                 f"{f(tf['diff_ann_pct'], 2)} {ci(tf['ci95_ann_pct'], 2)} | {f(a.get('alpha_ann_pct'), 2)} {ci(a.get('alpha_ci95_ann_pct'), 2)} ; {f(a.get('beta'), 3, False)} |")
    o += ["\n### 3. Décomposition (points de rendement sur la fenêtre)\n",
          "| Hypothèse | Plafond | Exposition à BTC (passif même expo.) | Timing + dimensionnement (stratégie − passif) | Frais (brut − net) | Réduction mécanique du DD par les liquidités (B&H − passif, points) |",
          "|---|---|---|---|---|---|"]
    for r in s["rows"]:
        dcp = list(r["decomposition_pct"].values())
        o.append(f"| {r['hypothesis']} | {r['w_max']:.0%} | " + " | ".join(f(x, 1) for x in dcp) + " |")
    o += ["\nLecture : NXG-03 (ajustement à la volatilité, toujours investi) isole le **dimensionnement dynamique** ; NXG-02 → NXG-05 mesure "
          "l'effet de l'ajout de ce dimensionnement au timing ; NXG-01, NXG-02 et NXG-04 mesurent le **timing**.\n",
          "### 4. Risque global, épisodes de baisse et arrêt global à 10 % (diagnostic)\n",
          "| Hypothèse | Plafond | Pire jour % | Pire semaine % | CVaR 5 % quotidienne % | Durée max sous l'eau (j) | Mai 2021 % (passif) | Mai–juin 2022 % (passif) | Nov. 2022 % (passif) | Marché baissier nov. 2021 → nov. 2022 % (passif) | Avec arrêt global : rend. % / DD % / date |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        n, e, ep, h = r["net"], r["episodes_pct"], r["episodes_passive_same_expo_pct"], r["with_global_halt"]
        o.append(f"| {r['hypothesis']} | {r['w_max']:.0%} | {f(n['worst_day_pct'], 2)} | {f(n['worst_week_pct'], 2)} | {f(n['cvar5_daily_pct'], 2)} | "
                 f"{n['longest_underwater_days']} | {f(e['mai_2021'], 1)} ({f(ep['mai_2021'], 1)}) | {f(e['juin_2022_luna_celsius'], 1)} ({f(ep['juin_2022_luna_celsius'], 1)}) | "
                 f"{f(e['nov_2022_ftx'], 1)} ({f(ep['nov_2022_ftx'], 1)}) | {f(e['bear_2022'], 1)} ({f(ep['bear_2022'], 1)}) | "
                 f"{f(h['net_return_pct'], 1)} / {f(h['max_dd_pct'], 1, False)} / {(h['halted_on'] or 'non')[:10]} |")
    o.append("\nLe krach de mars 2020 est antérieur à la fenêtre d'évaluation (période d'amorçage des indicateurs) : il n'est pas mesuré.")
    o += ["\n### 5. Rendement annuel %\n", "| Hypothèse | Plafond | " + " | ".join(sorted(s["rows"][0]["annual_return_pct"])) + " |",
          "|---|---|" + "---|" * len(s["rows"][0]["annual_return_pct"])]
    for r in s["rows"]:
        o.append(f"| {r['hypothesis']} | {r['w_max']:.0%} | " + " | ".join(f(r["annual_return_pct"][k], 1) for k in sorted(r["annual_return_pct"])) + " |")
    return "\n".join(o)


def main():
    (ROOT / "reports" / "phase2d_G_allocation.md").write_text(g_report())
    (ROOT / "reports" / "phase2d_E_mean_reversion.md").write_text(batch_report("batch_2d_01"))
    tech = json.loads((RESULTS_DIR / "tech_audit_2d" / "tech_audit.json").read_text())
    o = ["## Audit technique 2D — effet des défauts corrigés sur les candidats 2C\n", ATTR, "",
         f"Buy & Hold : {f(tech['buy_hold']['avant']['net_return_pct'], 1)} % → {f(tech['buy_hold']['apres']['net_return_pct'], 1)} %.\n",
         "| Hypothèse | Variante | E[R] avant → après | Sharpe quotidien avant → après [IC95] | Alpha %/an avant → après [IC95] | CAGR équilibré % avant → après |",
         "|---|---|---|---|---|---|"]
    for r in tech["rows"]:
        o.append(f"| {r['hypothesis']} | `{json.dumps(r['variant'], sort_keys=True)}` | {f(r['mean_r_avant'], 4)} → {f(r['mean_r_apres'], 4)} | "
                 f"{f(r['sharpe_quot_avant']['sharpe'], 2)} → {f(r['sharpe_quot_apres']['sharpe'], 2)} {ci(r['sharpe_quot_apres']['sharpe_ci95'], 2)} | "
                 f"{f(r['alpha_avant']['alpha_ann_pct'], 2)} → {f(r['alpha_apres']['alpha_ann_pct'], 2)} {ci(r['alpha_apres']['alpha_ci95_ann_pct'], 2)} | "
                 f"{f(r['equilibre_avant']['cagr_pct'], 2)} → {f(r['equilibre_apres']['cagr_pct'], 2)} |")
    (ROOT / "reports" / "phase2d_audit_technique.md").write_text("\n".join(o))
    print("rapports 2D écrits")


if __name__ == "__main__":
    main()
