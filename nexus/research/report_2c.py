"""Rapports Markdown de la phase 2C, générés depuis les résultats (aucun chiffre saisi à la main).

    python -m nexus.research.report_2c
"""
from __future__ import annotations

import json

from ..config import ROOT, RESULTS_DIR

ATTR = "*Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet.*"


def f(x, nd=3, sign=True):
    if x is None:
        return "—"
    try:
        return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def ci(v, nd=3):
    return f"[{f(v[0], nd)} ; {f(v[1], nd)}]" if v and v[0] is not None else "—"


def batch_report(name: str) -> str:
    rows = json.loads((RESULTS_DIR / name / "summary.json").read_text())
    o = [f"## Lot {name}\n", ATTR, "", f"Version du code : `{rows[0].get('code_version')}` ; essais au registre après le lot : {rows[0].get('registry_trials_total')}.\n"]
    o += ["### 1. Qualité intrinsèque des signaux (R par trade, profil statistique 0,5 %, sans arrêt)\n",
          "| Hypothèse | Variante | Trades | E[R] net | IC95 net | E[R] sans frottement | IC95 sans frott. | E[R] avant commissions | Coûts ×1,5 | Coûts ×2 | Frais BNB (sensib.) | Aléatoire expo. comparable | p(>0) BH | p(>aléa) BH | Verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("mean_r") is None:
            o.append(f"| {r['hypothesis']} | `{r['variant']}` | {r['n_trades']} | — | — | — | — | — | — | — | — | — | — | — | {r['verdict']} |")
            continue
        o.append(f"| {r['hypothesis']} | `{r['variant']}` | {r['n_trades']} | {f(r['mean_r'])} | {ci([r['ci_lo'], r['ci_hi']])} | "
                 f"{f(r['mean_r_frictionless'])} | {ci(r['ci_frictionless'])} | {f(r['mean_r_before_commission'])} | {f(r['mean_r_x1.5'])} | "
                 f"{f(r['mean_r_x2'])} | {f(r['mean_r_bnb_fee_sensitivity'])} | {f(r['random_mean'])} | {f(r.get('p_zero_bh'), 3, False)} | "
                 f"{f(r.get('p_random_bh'), 3, False)} | {r['verdict']} |")
    o += ["\n### 2. Exposition, références et attribution au marché\n",
          "| Hypothèse | Variante | Temps sur le marché % | Expo. moyenne % | Turnover/an | Durée moy. (h) | Rendement moyen/trade % | Aléatoire expo. comparable %/trade | Bêta | Alpha %/an [IC95] | Sharpe quotidien [IC95] | Alertes |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("mean_r") is None:
            continue
        e, a, s = r["exposure"], r.get("attribution") or {}, r.get("daily_sharpe") or {}
        o.append(f"| {r['hypothesis']} | `{r['variant']}` | {f(e['time_in_market_pct'], 1, False)} | {f(e['avg_exposure_pct'], 2, False)} | "
                 f"{f(e['turnover_per_year'], 1, False)} | {f(e['avg_duration_h'], 0, False)} | {f(r['strategy_ret_mean_pct'], 2)} | "
                 f"{f(r['random_ret_mean_pct'], 2)} | {f(a.get('beta'), 3, False)} | {f(a.get('alpha_ann_pct'), 2)} {ci(a.get('alpha_ci95_ann_pct'), 2)} | "
                 f"{f(s.get('sharpe'), 2)} {ci(s.get('sharpe_ci95'), 2)} | {'; '.join(r.get('overfit_flags') or [])} |")
    bh = next((r["passive"]["buy_hold"] for r in rows if r.get("passive")), None)
    if bh:
        o.append(f"\nRéférences passives (même période) : **Buy & Hold** BTC {f(bh['net_return_pct'], 1)} %, CAGR {f(bh['cagr_pct'], 1)} %, "
                 f"drawdown max {f(bh['max_dd_pct'], 1, False)} %, temps sur le marché 100 % ; **liquidités** 0 %, drawdown 0 %. "
                 "La colonne « passif même exposition » du tableau 3 donne la détention constante à l'exposition moyenne de chaque stratégie.\n")
    o += ["\n### 3. Capital simulé (1 000 €) : règles de risque, avec et sans arrêt à 10 %\n",
          "Les lignes « sans arrêt » sont purement analytiques et ne modifient pas les règles du futur bot.\n",
          "| Hypothèse | Variante | Profil | Trades | Capital final € | Rendement % | CAGR % | Max DD % (valorisé) | PF | Sharpe | Sortino | Calmar | Frais € | Série pertes | Arrêt (date) | Passif même expo. % / DD % |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("mean_r") is None:
            continue
        ps = r["passive"]["passive_same_exposure"]
        for pn, p in r["profiles"].items():
            o.append(f"| {r['hypothesis']} | `{r['variant']}` | {pn} | {p.get('n_trades')} | {f(p.get('final_capital_eur'), 0, False)} | "
                     f"{f(p.get('net_return_pct'), 1)} | {f(p.get('cagr_pct'), 1)} | {f(100 * p.get('max_dd_pct', 0), 1, False)} | "
                     f"{f(p.get('profit_factor'), 2, False)} | {f(p.get('sharpe'), 2)} | {f(p.get('sortino'), 2)} | {f(p.get('calmar'), 2)} | "
                     f"{f(p.get('total_fees_eur'), 1, False)} | {p.get('longest_losing_streak')} | {(p.get('halt_time') or 'non')[:10]} | "
                     f"{f(ps['net_return_pct'], 1)} / {f(ps['max_dd_pct'], 1, False)} |")
    o += ["\n### 4. Stabilité : E[R] net par année et par régime (régime causal à l'entrée)\n",
          "| Hypothèse | Variante | Par année | Par tendance (n, E[R]) | Par volatilité (n, E[R]) | Part des 5 meilleurs trades % |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("mean_r") is None:
            continue
        yrs = ", ".join(f"{k[:4]} {f(v, 2)}" for k, v in r["annual_mean_r"].items())
        tr = ", ".join(f"{k} ({v['n']}, {f(v['mean_r'], 2)})" for k, v in r["by_trend_regime"].items())
        vo = ", ".join(f"{k} ({v['n']}, {f(v['mean_r'], 2)})" for k, v in r["by_vol_regime"].items())
        o.append(f"| {r['hypothesis']} | `{r['variant']}` | {yrs} | {tr} | {vo} | {f(r.get('top5_share'), 0, False)} |")
    wf = json.loads((RESULTS_DIR / name / "walk_forward.json").read_text())
    o.append("\n### 5. Walk-forward du processus de sélection (choix sur le passé, mesure sur le semestre suivant)\n")
    for fam, w in wf.items():
        o.append(f"- Famille {fam} : {w['oos_n']} trades hors échantillon, E[R] = {f(w['oos_mean_r'])} — "
                 + "; ".join(f"{x['fold'][:7]} → {x.get('choice') or 'aucun choix'}" for x in w["folds"]))
    ab = RESULTS_DIR / name / "ablations.json"
    if ab.exists():
        o.append("\n### 6. Ablations (différence d'E[R], IC95 bootstrap hebdomadaire)\n")
        for x in json.loads(ab.read_text()):
            o.append(f"- {x['variant']} vs {x['vs']} : Δ = {f(x['delta'])} [{f(x['lo'])} ; {f(x['hi'])}] (n = {x['n_a']}/{x['n_b']})"
                     f" → {'contribution non démontrée' if x['lo'] <= 0 else 'contribution positive (à valider)'}")
    return "\n".join(o)


def audit_report() -> str:
    a = json.loads((RESULTS_DIR / "audit_2b_01" / "audit.json").read_text())
    o = ["## Audit du lot 2B-01 (NEXUS A et référence SBA, BTC/USDT spot, M5)\n", ATTR, "",
         f"Prix BTC : {a['bh']['start_price']:.0f} → {a['bh']['end_price']:.0f} USDT sur la période de développement.\n",
         "| Session | Hypothèse | Variante | Trades | Reproduction (enregistré → recalculé) | E[R] sans frottement [IC95] | E[R] avant commissions [IC95] | E[R] net [IC95] | Coût moyen (R) | Frais BNB (sensib.) | Aléatoire expo. comparable (p) | Rendement/trade % : stratégie / aléatoire / détention même fenêtre | Alpha %/an [IC95] |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in a["rows"]:
        at = r["attribution"]
        o.append(f"| {r['session']} | {r['hypothesis']} | `{r['variant']}` | {r['n_trades']} | {f(r['repro_stored_mean_r'], 4)} → {f(r['repro_now_mean_r'], 4)} | "
                 f"{f(r['mean_r_frictionless'])} {ci(r['ci_frictionless'])} | {f(r['mean_r_before_commission'])} {ci(r['ci_before_commission'])} | "
                 f"{f(r['mean_r_net'])} {ci(r['ci_net'])} | {f(r['mean_cost_r'], 3, False)} | {f(r['mean_r_bnb_fee'])} | "
                 f"{f(r['expo_random_mean_r'])} ({f(r['p_vs_expo_random'], 3, False)}) | {f(r['strategy_mean_ret_pct'], 3)} / "
                 f"{f(r['expo_random_mean_ret_pct'], 3)} / {f(r['window_hold_mean_ret_pct'], 3)} | {f(at.get('alpha_ann_pct'), 2)} {ci(at.get('alpha_ci95_ann_pct'), 2)} |")
    o += ["\n### Sensibilité aux coûts (E[R] net ; multiplicateur de tous les coûts — le nombre de trades varie car le filtre de faisabilité s'applique)\n",
          "| Session | Hypothèse | Variante | ×0 | ×0,25 | ×0,5 | ×0,75 | ×1 | ×1,5 | ×2 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in a["rows"]:
        c = r["cost_curve"]; n = r["cost_curve_n"]
        o.append(f"| {r['session']} | {r['hypothesis']} | `{r['variant']}` | " + " | ".join(f"{f(c[k], 3)} (n={n[k]})" for k in c) + " |")
    o += ["\n### Par année et par régime de tendance (E[R] net)\n",
          "| Session | Hypothèse | Variante | Années | Tendance (n, E[R]) |", "|---|---|---|---|---|"]
    for r in a["rows"]:
        o.append(f"| {r['session']} | {r['hypothesis']} | `{r['variant']}` | " + ", ".join(f"{k} {f(v, 2)}" for k, v in r["annual_mean_r"].items())
                 + " | " + ", ".join(f"{k} ({v['n']}, {f(v['mean_r'], 2)})" for k, v in r["by_trend_regime"].items()) + " |")
    o += ["\n### Biais de l'arrêt à 10 % : capital avec et sans arrêt (analytique)\n",
          "| Session | Hypothèse | Variante | Profil | Avec arrêt : rendement % / DD % / date d'arrêt | Sans arrêt : rendement % / DD % |", "|---|---|---|---|---|---|"]
    for r in a["rows"]:
        p = r["profiles"]
        for pn in ("prudent", "equilibre", "dynamique"):
            w, wo = p[pn], p[pn + "_sans_arret"]
            o.append(f"| {r['session']} | {r['hypothesis']} | `{r['variant']}` | {pn} | {f(w['net_return_pct'], 1)} / {f(w['max_dd_pct'], 1, False)} / "
                     f"{(w['halt_time'] or 'non')[:10]} | {f(wo['net_return_pct'], 1)} / {f(wo['max_dd_pct'], 1, False)} |")
    return "\n".join(o)


def main():
    out = ROOT / "reports"
    (out / "phase2c_audit_2b_01.md").write_text(audit_report())
    for b in ("batch_2c_01", "batch_2c_02"):
        if (RESULTS_DIR / b / "summary.json").exists():
            (out / f"phase2c_{b}.md").write_text(batch_report(b))
    print("rapports écrits dans", out)


if __name__ == "__main__":
    main()
