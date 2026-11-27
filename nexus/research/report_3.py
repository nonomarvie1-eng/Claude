"""Rapport Markdown des études événementielles de la phase 3 (généré depuis les résultats).

    python -m nexus.research.report_3
"""
from __future__ import annotations

import json

from ..config import RESULTS_DIR, ROOT
from .report_2c import ATTR, ci, f


def main():
    d = RESULTS_DIR / "batch_3_01_events"
    btc = json.loads((d / "events_BTCUSDT.json").read_text())
    o = ["## Études événementielles Liquidity Intelligence — lot 3-01 (période de développement)\n", ATTR, "",
         f"Code `{btc['code_version']}` ; essais au registre après le lot BTC : {btc['registry_trials_total']}.\n",
         "Δ = métrique(niveaux réels) − métrique(contrôles) ; IC95 bootstrap par semaines ; p unilatéral ; BH sur les 14 tests BTC.\n",
         "| Test | Métrique principale | n réel / contrôle | Réel | Contrôle | Δ [IC95] | p | p BH | Information | P(contact) réel | P(retournement) réel | Seuil de rentabilité | Exploitable |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in btc["results"].items():
        dl, real = r["delta"], r.get("real", {})
        o.append(f"| {k} | {r['primary']} | {dl.get('n_real')} / {dl.get('n_ctrl')} | {f(dl.get('real'), 3, False)} | {f(dl.get('ctrl'), 3, False)} | "
                 f"{f(dl.get('delta'), 3)} {ci(dl.get('ci95'), 3)} | {f(dl.get('p'), 4, False)} | {f(r.get('p_bh'), 4, False)} | "
                 f"{'oui' if r.get('information') else 'non'} | {f(real.get('p_touch'), 3, False)} | {f(real.get('p_reversal'), 3, False)} | "
                 f"{f(real.get('p_breakeven_reversal'), 3, False)} | {'—' if r.get('exploitable') is None else ('oui' if r['exploitable'] else 'non')} |")
    o.append("\n### Mesures complémentaires (niveaux réels)\n")
    o.append("| Test | Niveaux | Déjà franchis à la disponibilité | Délai médian de contact (h) | P(clôture M5 au-delà) | P(réintégration \\| franchissement) | MFE médiane (ATR) | MAE médiane (ATR) | Distance médiane (ATR) | Coût moyen (ATR) |")
    o.append("|---|---|---|---|---|---|---|---|---|---|")
    for k, r in btc["results"].items():
        s = r.get("real")
        if not s or "n_levels" not in s:
            continue
        o.append(f"| {k} | {s['n_levels']} | {s['n_deja_atteint']} | {f(s.get('median_time_to_touch_h'), 1, False)} | {f(s.get('p_cross_close'), 3, False)} | "
                 f"{f(s.get('p_reintegration_given_cross'), 3, False)} | {f(s.get('median_mfe_atr'), 2, False)} | {f(s.get('median_mae_atr'), 2, False)} | "
                 f"{f(s.get('median_dist_atr'), 2, False)} | {f(s.get('mean_cost_atr'), 3, False)} |")
    orb = btc["results"]["EV-12-ORB"]
    o.append(f"\n**ORB (EV-12)** : continuation {f(orb['delta']['real'], 3, False)} contre {f(orb['delta']['ctrl'], 3, False)} pour le range de contrôle. "
             f"Avec retest dans les 6 bougies : {f(orb['p_cont_with_retest'], 3, False)} (n = {orb['n_with_retest']}) ; sans retest : "
             f"{f(orb['p_cont_without_retest'], 3, False)} (n = {orb['n_without_retest']}). Ce conditionnement utilise l'information des 30 minutes "
             f"suivantes : il est **descriptif** (confirme le biais de sélection décrit par le document ORB), pas un signal. Grande cassure : "
             f"{f(orb['p_cont_big_break'], 3, False)} ; petite : {f(orb['p_cont_small_break'], 3, False)}.")
    lrl = btc["results"]["EV-07-LRL"]["lrl_vs_hrl_touch"]
    o.append(f"\n**LRL vs HRL (EV-07, comparaison brute)** : P(contact) {f(lrl['real'], 3, False)} contre {f(lrl['ctrl'], 3, False)}, Δ = {f(lrl['delta'], 3)} "
             f"{ci(lrl['ci95'], 3)}. Contre des contrôles à même distance normalisée, l'effet disparaît : l'écart brut s'explique par la distance.")
    sb = btc["results"]["EV-13-SILVERBULLET"]["by_window"]
    o.append("\n**Silver Bullet (EV-13), P(retournement) par heure de formation du FVG (NY)** : "
             + " ; ".join(f"{h} h : {f(v.get('p_reversal'), 3, False)} (n = {v.get('n_race')})" for h, v in sb.items()))
    smt = btc["results"]["EV-14-SMT"]
    o.append(f"\n**SMT BTC/ETH (EV-14)** : P(retournement) avec SMT {f(smt['p_rev_smt'], 3, False)} (n = {smt['n_smt']}) ; sans SMT "
             f"{f(smt['p_rev_no_smt'], 3, False)} (n = {smt['n_no_smt']}).")
    eth = d / "events_ETHUSDT.json"
    if eth.exists():
        e = json.loads(eth.read_text())["results"]["EV-12-ORB"]["delta"]
        o.append(f"\n**Réplication ETH (EV-12-ORB)** : Δ = {f(e['delta'], 3)} {ci(e['ci95'], 3)}, p = {f(e['p'], 3, False)} → **non répliqué**.")
    dg = d / "diagnostics.json"
    if dg.exists():
        g = json.loads(dg.read_text())
        c, of = g["cointegration"], g["ofi"]
        o.append(f"\n**Diagnostic cointégration BTC/ETH** : fenêtres cointégrées à 5 % : {f(100 * c['share_windows_cointegrated_5pct'], 1, False)} % ; "
                 f"β roulant de {f(c['beta_min'], 2, False)} à {f(c['beta_max'], 2, False)} ; corrélation des rendements quotidiens {f(c['corr_daily_returns'], 2, False)} ; "
                 f"CUSUM p = {c['cusum_full_period_p']:.1e}.")
        o.append(f"\n**Diagnostic OFI (minute)** : Spearman h = 1 min : {f(of['h1']['spearman_nonoverlap'], 3)} ; h = 5 min : {f(of['h5']['spearman_nonoverlap'], 3)} ; "
                 f"écart entre déciles extrêmes {f(of['h1']['spread_top_bottom_bp'], 2)} pb (1 min), {f(of['h5']['spread_top_bottom_bp'], 2)} pb (5 min), "
                 f"contre {of['round_trip_cost_bp']} pb de coût aller-retour.")
    (ROOT / "reports" / "phase3_liquidity_events.md").write_text("\n".join(o))
    print("rapport écrit")


if __name__ == "__main__":
    main()
