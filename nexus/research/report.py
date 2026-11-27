"""Rapport Markdown à partir du résumé d'un lot (aucun chiffre n'est saisi à la main)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def fmt(x, nd=3, pct=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{nd}f}{' %' if pct else ''}"


def render(summary_path: str) -> str:
    rows = json.loads(Path(summary_path).read_text())
    out = []
    out.append(f"Source : `{summary_path}` — version du code `{rows[0].get('code_version')}` — "
               f"essais totaux dans le registre au moment du lot : {rows[0].get('registry_trials_total')}.\n")
    out.append("### Statistique de l'avantage (R nets, profil statistique 0,5 %, sans disjoncteur)\n")
    out.append("| Actif | Session | Hypothèse | Variante | Trades | E[R] net | IC95 bloc-hebdo | E[R] brut | E[R] coûts ×1,5 | E[R] coûts ×2 | Aléatoire E[R] | p(>0) BH | p(>aléa) BH | Verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        ci = f"[{fmt(r.get('ci_lo'))} ; {fmt(r.get('ci_hi'))}]" if r.get("ci_lo") is not None else "—"
        out.append(f"| {r['symbol']} | {r['session']} | {r['hypothesis']} | `{r['variant']}` | {r['n_trades']} | "
                   f"{fmt(r.get('mean_r'))} | {ci} | {fmt(r.get('mean_r_gross'))} | {fmt(r.get('mean_r_x1.5'))} | "
                   f"{fmt(r.get('mean_r_x2'))} | {fmt(r.get('random_mean'))} | {fmt(r.get('p_zero_bh'))} | "
                   f"{fmt(r.get('p_random_bh'))} | {r['verdict']} |")
    out.append("\n### Refus du gestionnaire de risque (profil statistique)\n")
    out.append("| Actif | Session | Hypothèse | Variante | Signaux | Trades | Motifs de refus |")
    out.append("|---|---|---|---|---|---|---|")
    for r in rows:
        rj = "; ".join(f"{k} : {v}" for k, v in sorted(r.get("rejections", {}).items(), key=lambda kv: -kv[1]))
        out.append(f"| {r['symbol']} | {r['session']} | {r['hypothesis']} | `{r['variant']}` | {r['n_signals']} | {r['n_trades']} | {rj or '—'} |")
    out.append("\n### Profils de risque (capital initial 1 000 €, limites actives)\n")
    out.append("| Actif | Session | Hypothèse | Variante | Profil | Trades | Capital final € | Profit net € | Rendement % | PF | Max DD % (observé) | Durée DD (j) | Win % | Gain moy. € | Perte moy. € | E[€] | Sharpe | Sortino | Calmar | Frais € | Série pertes max | Disjoncteur | P(DD≥10 %) MC | P(DD≥20 %) MC |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        for pname, p in (r.get("profiles") or {}).items():
            mc = p.get("mc", {})
            out.append(
                f"| {r['symbol']} | {r['session']} | {r['hypothesis']} | `{r['variant']}` | {pname} | {p.get('n_trades')} | "
                f"{fmt(p.get('final_capital_eur'), 2)} | {fmt(p.get('net_profit_eur'), 2)} | {fmt(p.get('net_return_pct'), 2)} | "
                f"{fmt(p.get('profit_factor'), 2)} | {fmt(100 * p.get('max_dd_pct', 0), 2)} | {p.get('max_dd_duration_days', '—')} | "
                f"{fmt(p.get('win_rate_pct'), 1)} | {fmt(p.get('avg_win_eur'), 2)} | {fmt(p.get('avg_loss_eur'), 2)} | "
                f"{fmt(p.get('expectancy_eur'), 3)} | {fmt(p.get('sharpe'), 2)} | {fmt(p.get('sortino'), 2)} | {fmt(p.get('calmar'), 2)} | "
                f"{fmt(p.get('total_fees_eur'), 2)} | {p.get('longest_losing_streak', '—')} | "
                f"{'oui : ' + p['halt_reason'] if p.get('halted') else 'non'} | {fmt(mc.get('p_dd_ge_10pct'), 2)} | {fmt(mc.get('p_dd_ge_20pct'), 2)} |")
    out.append("\n### Stabilité temporelle (E[R] net par semestre)\n")
    for r in rows:
        if r.get("folds"):
            f = ", ".join(f"{k[:7]} : {fmt(v['mean_r'], 2)} (n={v['n']})" for k, v in r["folds"].items())
            out.append(f"- {r['symbol']} {r['session']} {r['hypothesis']} `{r['variant']}` — {f}")
    out.append("\n### Ablations (différence d'E[R] vs modèle de base, IC95 bootstrap hebdomadaire)\n")
    for r in rows:
        if r.get("ablation_vs_base"):
            d, lo, hi = r["ablation_vs_base"]
            out.append(f"- {r['symbol']} {r['session']} {r['hypothesis']} `{r['variant']}` : Δ = {fmt(d)} [{fmt(lo)} ; {fmt(hi)}]"
                       f" → {'contribution non démontrée' if lo <= 0 else 'contribution positive (à valider)'}")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(sys.argv[1]))
