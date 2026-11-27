"""Rapport Markdown du lot 4-01 (généré depuis results/batch_4_01_cubrik/results.json).

    python -m nexus.research.report_4
"""
from __future__ import annotations

import json

from ..config import RESULTS_DIR, ROOT

ATTR = "*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0 ; Binance n'est pas associé à ce projet.*"


def f(x, n=2, sign=True):
    if x is None:
        return "—"
    return f"{x:+.{n}f}" if sign else f"{x:.{n}f}"


def main():
    d = json.loads((RESULTS_DIR / "batch_4_01_cubrik" / "results.json").read_text())
    o = ["## Lot 4-01 — stratégies compatibles Cubrik (période de développement 2020-01 → 2023-06)\n", ATTR, "",
         f"Univers (figé sur le volume d'oct.–déc. 2019) : {', '.join(d['universe'])}. "
         f"Perpétuels disponibles : {', '.join(d['perp_universe'])}. Essais au registre : {d['registry_trials_total']}.\n",
         "### Stops % par actif (3 × médiane ATR14/clôture D1, S2 2019)\n",
         "| Actif | ATR médian % | Stop % |", "|---|---|---|"]
    for s, v in d["stops"].items():
        o.append(f"| {s} | {v['median_atr_pct']:.2f} | {v['stop_pct']} |")
    o += ["\n### Résultats principaux (USDT, risque 0,5 %/trade, sans arrêts globaux)\n",
          "| Hypothèse | Trades | R moyen net [IC95] | Rendement total | CAGR | Max DD | Sharpe | PF | Réussite | Expo. moy. | Bêta | Δ vs référence %/an [IC95] | p | p BH | Verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, e in d["results"].items():
        p, tr, pr = e["perf_usdt"], e.get("trade_R") or {}, e["primary"]
        ci = tr.get("ci95") or [None, None]
        o.append(f"| {k} | {p['n_trades']} | {f(tr.get('mean'), 3)} [{f(ci[0], 3)} ; {f(ci[1], 3)}] | {f(p['total_return_pct'], 1)} % | "
                 f"{f(p['cagr_pct'], 1)} % | {f(p['max_dd_pct'], 1, False)} % | {f(p['sharpe'])} | {f(p['profit_factor'], 2, False)} | "
                 f"{f(100 * p['win_rate'], 1, False) if p['win_rate'] is not None else '—'} % | {f(100 * e['avg_exposure'], 1, False)} % | "
                 f"{f(e['beta_vs_basket'], 3)} | {f(pr['diff_ann_pct'])} [{f(pr['ci95_ann_pct'][0])} ; {f(pr['ci95_ann_pct'][1])}] | "
                 f"{f(pr['p'], 3, False)} | {f(e['p_bh'], 3, False)} | **{e['verdict']}** |")
    o.append("\nRéférence : panier équipondéré passif ramené à la même exposition moyenne (achat seulement) ; trésorerie pour P4-03.")
    o += ["\n### Critères\n", "| Hypothèse | C1 alpha (p BH < 0,05) | C2 R > 0 (IC) | C3 coûts × 2 | C4 voisins | C5 sous-périodes | C6 DD < 10 % |",
          "|---|---|---|---|---|---|---|"]
    for k, e in d["results"].items():
        c = e["criteria"]
        o.append(f"| {k} | " + " | ".join("oui" if c[x] else "non" for x in ("C1", "C2", "C3", "C4", "C5", "C6")) + " |")
    o += ["\n### Stabilité temporelle (écart annualisé à la référence, %/an)\n", "| Hypothèse | 2020 | 2021 | 2022 | 2023 S1 |", "|---|---|---|---|---|"]
    for k, e in d["results"].items():
        sp = e["subperiods"]
        o.append(f"| {k} | " + " | ".join(f(sp[x], 1) for x in ("2020", "2021", "2022", "2023S1")) + " |")
    o += ["\n### Sensibilité (voisins pré-déclarés) et coûts × 2\n", "| Hypothèse | Variante | Trades | R moyen | Δ vs référence %/an | p |", "|---|---|---|---|---|---|"]
    for k, e in d["results"].items():
        for s in e["sensitivity"]:
            o.append(f"| {k} | {json.dumps(s['variant'])} | {s['perf_usdt']['n_trades']} | {f((s['trade_R'] or {}).get('mean'), 3)} | "
                     f"{f(s['primary']['diff_ann_pct'])} | {f(s['primary']['p'], 3, False)} |")
        c = e["cost_x2"]
        o.append(f"| {k} | coûts × 2 | {c['perf_usdt']['n_trades']} | {f((c['trade_R'] or {}).get('mean'), 3)} | {f(c['primary']['diff_ann_pct'])} | {f(c['primary']['p'], 3, False)} |")
    o += ["\n### Résultats en euros (1 000 €)\n", "| Hypothèse | Équilibré 0,5 % : final € | Rendement | Max DD | Avec règles (2 %/jour, arrêt 10 %) : final € | Max DD | Événements 2 % | Arrêt | Prudent 0,25 % : final € | Max DD |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, e in d["results"].items():
        a, r, p = e["perf_eur"], e["perf_eur_rules"], e["perf_eur_prudent"]
        o.append(f"| {k} | {a['final']:.0f} | {f(a['total_return_pct'], 1)} % | {f(a['max_dd_pct'], 1, False)} % | {r['final']:.0f} | "
                 f"{f(r['max_dd_pct'], 1, False)} % | {r['info']['daily_loss_events']} | {r['info']['halt_time'] or 'non'} | {p['final']:.0f} | {f(p['max_dd_pct'], 1, False)} % |")
    b, be = d["benchmark_basket"], d["benchmark_basket_eur"]
    o.append(f"\nPanier passif équipondéré, 100 % investi : {f(b['total_return_pct'], 1)} % (USDT), {f(be['total_return_pct'], 1)} % en euros, drawdown maximal {f(b['max_dd_pct'], 1, False)} %.")
    o += ["\n### Détail par sens et par actif (R moyen net)\n"]
    for k, e in d["results"].items():
        bs = " ; ".join(f"{s} : n = {v['n']}, R = {f(v['mean_R'], 3)}" for s, v in e.get("by_side", {}).items())
        sy = " ; ".join(f"{s.replace('USDT', '')} {f(v['mean_R'], 2)} (n = {v['n']})" for s, v in e.get("by_symbol", {}).items())
        rs = ", ".join(f"{a} {b}" for a, b in e.get("by_reason", {}).items())
        o.append(f"- **{k}** — {bs}. Sorties : {rs}. Frais {e.get('fees_total', 0):.1f} USDT, financement {e.get('funding_total', 0):+.1f} USDT. Par actif : {sy}.")
    if "random_baseline" in d:
        o += ["\n### Entrées aléatoires (même nombre, durée et sens ; 200 tirages ; R hors financement)\n",
              "| Hypothèse | R moyen réel | R moyen aléatoire | 95e centile aléatoire | Centile du réel |", "|---|---|---|---|---|"]
        for k, v in d["random_baseline"].items():
            o.append(f"| {k} | {f(v['actual_mean_R_ex_funding'], 3)} | {f(v['random_mean'], 3)} | {f(v['random_p95'], 3)} | {v['percentile_of_actual']:.0f} |")
    (ROOT / "reports" / "phase4_cubrik_lot_4_01.md").write_text("\n".join(o) + "\n")
    print("rapport écrit")


if __name__ == "__main__":
    main()
