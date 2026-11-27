"""Génère docs/phase5/06_resultats_backtests.md et 07_robustesse_monte_carlo.md depuis les résultats.

    python -m nexus.research.report_5
"""
from __future__ import annotations

import json

from ..config import RESULTS_DIR, ROOT

D = RESULTS_DIR / "batch_5_01_indices"
SRC = ("*Données : Kenneth R. French Data Library (dérivées de CRSP), usage de recherche, non redistribuées ; "
       "H5-EXP : Binance Vision (CC BY-NC-SA 4.0).*")
NAMES = {"H5-01a-RSI2-NOSTOP_US": "RSI 2 d'origine, sans stop (US)", "H5-01b-RSI2-STOP_US": "RSI 2 + stop (US)",
         "H5-02-RSI3050_US": "RSI 30/50 + stop (US)", "H5-03-DOUBLE5_US": "Double 5 + stop (US)",
         "H5-04-RSI2-INTL_Europe": "RSI 2 + stop (Europe)", "H5-04-RSI2-INTL_Japan": "RSI 2 + stop (Japon)",
         "H5-04-RSI2-INTL_AsiaPacExJapan": "RSI 2 + stop (Asie-Pacifique hors Japon)"}
CUBRIK = {"H5-01a-RSI2-NOSTOP_US": "Native (si RSI 2 accepté) ; sans stop : contraire à la règle NEXUS",
          "H5-01b-RSI2-STOP_US": "Native (si RSI 2 accepté)", "H5-02-RSI3050_US": "Native",
          "H5-03-DOUBLE5_US": "À vérifier (définition de `lowest`/`highest`)",
          "H5-04-RSI2-INTL_Europe": "Native ; CFD européen à vérifier", "H5-04-RSI2-INTL_Japan": "Native ; CFD JP225 à vérifier (en JPY, nos données sont en USD)",
          "H5-04-RSI2-INTL_AsiaPacExJapan": "Native ; instrument à vérifier"}


def f(x, n=2, s=True):
    if x is None:
        return "—"
    return f"{x:+.{n}f}" if s else f"{x:.{n}f}"


def main():
    r = json.loads((D / "results.json").read_text())
    rep = json.loads((D / "reproduction.json").read_text())
    stops = json.loads((D / "stops.json").read_text())
    exp = json.loads((D / "h5_exp.json").read_text()) if (D / "h5_exp.json").exists() else None
    mcj = json.loads((D / "montecarlo.json").read_text()) if (D / "montecarlo.json").exists() else {}
    keys = [k for k in r if not k.startswith("_")]
    o = ["# Phase 5 — Résultats des backtests (lot 5-01)\n", "*Généré par `python -m nexus.research.report_5` depuis `results/batch_5_01_indices/`.*\n", SRC, "",
         f"Essais au registre après le lot : {r.get('_registry_trials_total')} (avant Monte Carlo et H5-EXP).\n",
         "## 1. Reproduction des chiffres annoncés (RSI 2, US, 1993-2009, notionnel 100 %, sans stop)\n",
         "| | Trades | Gagnants | Rendement moyen par trade | Profit factor | Temps investi | Multiple du capital |", "|---|---|---|---|---|---|---|"]
    for lab, v in rep.items():
        if lab == "annonce_doc2":
            o.append(f"| Annoncé (SPY 1993 → ≈ 2026) | — | {v['win_rate']*100:.1f} % | +{v['mean_ret_pct']:.2f} % | {v['profit_factor']:.2f} | {v['exposure_pct']:.1f} % | 4,14 (sur ≈ 33 ans) |")
        else:
            o.append(f"| NEXUS, {lab} | {v['n_trades']} | {v['win_rate']*100:.1f} % | {f(v['mean_ret_pct'])} % | {v['profit_factor']:.2f} | {v['exposure_pct']:.1f} % | {v['growth_multiple']:.2f} (17 ans) |")
    o.append("\nÉcarts attendus : indice CRSP (pas SPY), exécution à la clôture, fenêtre plus courte. L'ordre de grandeur est reproduit ; le taux de réussite et le gain moyen sont un peu inférieurs.\n")
    o.append("Stops catastrophe (3 × écart-type sur 5 séances, avant 2010) : " + ", ".join(f"{m} {v['stop_pct']} %" for m, v in stops.items()) + ".\n")
    o += ["## 2. Statistiques par trade (fenêtre principale ; US 2010-2023 S1, international 1991-2023 S1)\n",
          "| Stratégie | Trades | Gagnants | Gain moyen | Perte moyenne | Rendement net moyen [IC95] | PF | Pire trade | Durée médiane (j) | Temps investi |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        t, v = r[k]["trades"], r[k]
        o.append(f"| {NAMES[k]} | {t['n']} | {t['win_rate']*100:.1f} % | {f(t['avg_win_pct'])} % | {f(t['avg_loss_pct'])} % | {f(t['mean_ret_pct'],3)} % "
                 f"[{f(t['ci95_pct'][0],3)} ; {f(t['ci95_pct'][1],3)}] | {f(t['profit_factor'],2,False)} | {f(t['worst_trade_pct'])} % | {t['median_days']:.0f} | {v['exposure_time_pct']:.1f} % |")
    o += ["\n## 3. Tests statistiques\n",
          "| Stratégie | Entrées aléatoires (même régime, mêmes durées) : moyenne | 95e centile | p | p BH | Aléatoire + même sortie : gagnants | Alpha vs passif même exposition %/an [IC95] |",
          "|---|---|---|---|---|---|---|"]
    for k in keys:
        v = r[k]
        re_, a = v["random_entries"], v["alpha_vs_passive_same_exposure"]
        o.append(f"| {NAMES[k]} | {f(re_['random_mean_pct'],3)} % | {f(re_['random_p95_pct'],3)} % | {re_['p']:.4f} | {v['p_bh']:.4f} | "
                 f"{v['random_same_exit']['win_rate']*100:.1f} % | {f(a['diff_ann_pct'],3)} [{f(a['ci95_ann_pct'][0],3)} ; {f(a['ci95_ann_pct'][1],3)}] |")
    o.append("\nLe taux de réussite des entrées **aléatoires** avec la même sortie dépasse 59 % partout : comme l'annonçait le document 2, le taux de réussite élevé vient **surtout de la règle de sortie**.\n")
    o += ["## 4. Coûts, délai, stabilité, sensibilité\n",
          "| Stratégie | Coûts × 2 | 0,20 %/côté | Exécution à t+1 | Sous-périodes | 1928-1992 (US) | Grille : part positive |", "|---|---|---|---|---|---|---|"]
    for k in keys:
        v = r[k]
        s = v["stress"]
        sub = " ; ".join(f"{a} {f(b['mean_ret_pct'],2)}" for a, b in v["subperiods"].items())
        o.append(f"| {NAMES[k]} | {f(s['couts_x2']['mean_ret_pct'],3)} % | {f(s['cout_0.20pct']['mean_ret_pct'],3)} % | {f(s['delai_t+1']['mean_ret_pct'],3)} % | {sub} | "
                 f"{f(v['hist']['mean_ret_pct'],3) + ' % (n = ' + str(v['hist']['n']) + ')' if 'hist' in v else '—'} | {v['grid']['share_positive']*100:.0f} % |")
    o += ["\n## 5. Résultats en euros (1 000 €, effet de change ignoré)\n",
          "| Stratégie | Taille | Capital final | Gain € | Rendement total | Annualisé | Max DD | Sharpe | Frais € | Financement € |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        v = r[k]
        for lab, e in (("NEXUS 0,5 %", v["eur_nexus"]), ("prudent 0,25 %", v["eur_prudent"]), ("notionnel 100 % (hors règle)", v["eur_full_notional"])):
            o.append(f"| {NAMES[k]} | {lab} | {e['final_eur']:.0f} € | {f(e['pnl_eur'],0)} | {f(e['total_return_pct'],1)} % | {f(e['cagr_pct'],2)} % | "
                     f"{e['max_dd_pct']:.1f} % | {f(e['sharpe'])} | {e['fees_eur']:.1f} | {e['financing_eur']:.1f} |")
        bh, tr = v["buy_hold_return_pct"], v["filter_only_sma_full"]
        o.append(f"| ↳ références | achat-conservation : {f(bh,1)} % ; filtre SMA seul (100 %) : {f(tr['total_return_pct'],1)} %, DD {tr['max_dd_pct']:.1f} % | | | | | | | | |")
    o += ["\n## 6. Critères et verdicts\n", "| Stratégie | C1 | C2 | C3 | C4 | C5 | C6 | Monte Carlo | Compatibilité Cubrik | Verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        v = r[k]
        c = v["criteria"]
        o.append(f"| {NAMES[k]} | " + " | ".join("oui" if c[x] else "non" for x in ("C1", "C2", "C3", "C4", "C5", "C6"))
                 + f" | {'—' if 'montecarlo_pass' not in v else ('oui' if v['montecarlo_pass'] else 'non')} | {CUBRIK[k]} | **{v['verdict']}** |")
    if exp:
        o += ["\n## 7. H5-EXP — gestion de l'exposition sur P4-01 (cryptos, 2020-2023 S1)\n",
              "| | Trades | Rendement | Max DD | Sharpe | PF | Expo. moy. | Alpha %/an [IC95] | p | Meilleur trade € | Part du meilleur trade | P&L sans meilleur trade | P&L sans 2021 | P&L sans MATIC | Rendu depuis le sommet |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for lab, v in exp.items():
            if lab.startswith("_"):
                continue
            p, c, a = v["perf_usdt"], v["concentration"], v["primary"]
            o.append(f"| {lab} | {p['n_trades']} | {f(p['total_return_pct'],1)} % | {p['max_dd_pct']:.1f} % | {f(p['sharpe'])} | {f(p['profit_factor'],2,False)} | "
                     f"{v['avg_exposure']*100:.1f} % | {f(a['diff_ann_pct'])} [{f(a['ci95_ann_pct'][0])} ; {f(a['ci95_ann_pct'][1])}] | {a['p']:.3f} | "
                     f"{c['best_trade_pnl']:.0f} | {f((c['best_trade_share'] or 0)*100,0,False)} % | {f(c['pnl_without_best_trade'],0)} | {f(c['pnl_without_2021'],0)} | "
                     f"{f(c['pnl_without_MATIC'],0)} | {v['giveback_from_peak_pct']:.1f} % |")
        lk = exp["P4-01 + lock 1/2"]
        o.append("\nSensibilité : " + " ; ".join(f"{k} : alpha {f(s['primary']['diff_ann_pct'])} %/an (p {s['primary']['p']:.3f}), DD {s['perf_usdt']['max_dd_pct']:.1f} %" for k, s in lk["sensitivity"].items()) + ".")
        o.append("\nCritères (phase 4) : " + ", ".join(f"{k} {'oui' if v else 'non'}" for k, v in lk["criteria"].items()) + f" → **{lk['verdict']}**.")
        o.append("\nP&L par année d'entrée (avec gestion) : " + ", ".join(f"{y} {f(x,0)} €" for y, x in lk["concentration"]["pnl_by_entry_year"].items()) + ".")
    (ROOT / "docs" / "phase5" / "06_resultats_backtests.md").write_text("\n".join(o) + "\n")

    # ---- 07 Monte Carlo
    m = ["# Phase 5 — Robustesse Monte Carlo\n", "*Généré par `python -m nexus.research.report_5`.*\n", SRC, "",
         "**Ces simulations ne donnent pas une probabilité de réussite future.** Elles mesurent la fragilité du résultat historique. "
         "Les drawdowns sont calculés sur un capital composé et solvable (≤ 100 %).\n",
         "## 1. Dimensionnement NEXUS (0,5 % de risque au stop), 10 000 simulations\n",
         "| Stratégie | Méthode | Rendement médian | 5e percentile | 95e percentile du DD | Simulations perdantes | P(DD > 10 %) |", "|---|---|---|---|---|---|---|"]
    for k, v in mcj.items():
        x = v["nexus_0.5pct"]
        rows = [("mélange de l'ordre", x["shuffle"]), ("bootstrap par blocs mensuels", x["block_bootstrap"])] + \
               [(f"suppression {int(float(p)*100)} %", y) for p, y in x["removal"].items()]
        for lab, y in rows:
            m.append(f"| {NAMES[k]} | {lab} | {f(y['median_return_pct'])} % | {f(y['p05_return_pct'])} % | {y['p95_drawdown_pct']:.2f} % | {y['share_losing']*100:.1f} % | {y['p_dd_over_limit']*100:.2f} % |")
    m += ["\n## 2. Notionnel 100 % sans levier (comme les documents ; hors règle de risque), bootstrap par blocs\n",
          "| Stratégie | Rendement médian | 5e percentile | 95e percentile du DD | Simulations perdantes | P(DD > 10 %) |", "|---|---|---|---|---|---|"]
    for k, v in mcj.items():
        y = v["notionnel_100pct"]["block_bootstrap"]
        m.append(f"| {NAMES[k]} | {f(y['median_return_pct'],1)} % | {f(y['p05_return_pct'],1)} % | {y['p95_drawdown_pct']:.1f} % | {y['share_losing']*100:.1f} % | {y['p_dd_over_limit']*100:.1f} % |")
    m += ["\n## 3. Concentration, bruit, régimes (notionnel 100 %, pour la lisibilité)\n",
          "| Stratégie | Total | Sans le meilleur trade | Meilleure année | Sans la meilleure année | Part des 5 meilleurs dans les gains bruts | Bruit ±0,1 % : part positive (5e pct) | Volatilité basse / moyenne / haute (rendement moyen) |",
          "|---|---|---|---|---|---|---|---|"]
    for k, v in mcj.items():
        c = v["notionnel_100pct"]["concentration"]
        n = v["noise_0.1pct"]
        rv = v["regimes_vol"]
        m.append(f"| {NAMES[k]} | {f(c['total_return_pct'],1)} % | {f(c['without_best_trade_pct'],1)} % | {c['best_year']} ({f(c['best_year_return_pct'],1)} %) | "
                 f"{f(c['without_best_year_pct'],1)} % | {(c['top5_share_of_gross_profit'] or 0)*100:.0f} % | {n['share_positive']*100:.0f} % ({f(n['p05_mean_ret_pct'],3)} %) | "
                 + " / ".join(f"{f(rv[g]['mean_ret_pct'],2)} % (n = {rv[g]['n']})" for g in ("basse", "moyenne", "haute") if g in rv) + " |")
    m.append("\nLecture : un rendement qui ne dépend ni du meilleur trade, ni de la meilleure année, et qui reste positif au 5e percentile, est moins fragile. "
             "Volatilité : le rendement moyen est le plus élevé en volatilité haute pour le Japon et l'Europe (cohérent avec Nagel 2012 et le document 7), "
             "mais pas pour les stratégies américaines, plus rentables en volatilité moyenne : l'effet n'est pas uniforme.")
    (ROOT / "docs" / "phase5" / "07_robustesse_monte_carlo.md").write_text("\n".join(m) + "\n")
    print("rapports écrits")


if __name__ == "__main__":
    main()
