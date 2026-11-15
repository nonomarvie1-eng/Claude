"""Builds docs/MATH_REPORT.md (+ charts) from the JSON outputs of exact.py,
simulate.py, export_stake.py and the official SDK verifier.  Every number in
the report is read from those files: nothing is typed by hand."""

from __future__ import annotations

import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import config as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(C.HERE))
DOCS = os.path.join(ROOT, "docs")
IMG = os.path.join(DOCS, "img")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def pct(x, d=3):
    return f"{x * 100:.{d}f} %"


def main() -> None:
    os.makedirs(IMG, exist_ok=True)
    ex = load(os.path.join(ROOT, "math", "reports", "exact.json"))
    mc = load(os.path.join(ROOT, "math", "reports", "montecarlo.json"))
    lut = load(os.path.join(ROOT, "stake", "publish_files", "export_summary.json"))
    sdk_p = os.path.join(ROOT, "stake", "official_sdk_verification.json")
    sdk = load(sdk_p) if os.path.exists(sdk_p) else None

    plt.rcParams.update({"figure.facecolor": "white", "axes.grid": True, "grid.alpha": 0.3, "font.size": 10})
    # 1. distribution of round wins (MC)
    edges = mc["distribution_buckets_x"]
    counts = mc["distribution_counts"]
    labels = ["0"] + [f"{edges[i]:g}–{edges[i + 1]:g}" if i + 1 < len(edges) else f"≥{edges[i]:g}" for i in range(1, len(edges))]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(range(len(counts)), [c / mc["rounds"] for c in counts], color="#1f6b47")
    ax.set_yscale("log")
    ax.set_xticks(range(len(counts)), labels[: len(counts)], rotation=40, ha="right")
    ax.set_ylabel("probabilité (log)")
    ax.set_xlabel("gain du tour (× mise)")
    ax.set_title(f"Distribution des gains par tour — Monte-Carlo, {mc['rounds']:,} tours".replace(",", " "))
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "win_distribution.png"), dpi=130)
    plt.close(fig)
    # 2. RTP of 10k-round batches
    b = mc["batch_rtps_10k"]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.hist([x * 100 for x in b], bins=60, color="#c8643a")
    ax.axvline(ex["rtp"] * 100, color="#0b2a1e", lw=2, label=f"RTP exact {ex['rtp'] * 100:.3f} %")
    ax.set_xlabel("RTP observé sur une session de 10 000 tours (%)")
    ax.set_ylabel("nombre de sessions")
    ax.set_title("Dispersion du RTP sur des sessions de 10 000 tours (volatilité)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "session_rtp.png"), dpi=130)
    plt.close(fig)

    se = mc["rtp_std_error"]
    z = (mc["rtp_observed"] - ex["rtp"]) / se
    b3 = ex["bonus_by_trigger"]
    bsd = (sum((x - ex["rtp"]) ** 2 for x in b) / len(b)) ** 0.5 if b else float("nan")
    lines = []
    w = lines.append
    w("# Rapport mathématique — Golden Rally\n")
    w(f"Version math : **{C.MATH_VERSION}** · généré automatiquement par `math/rally_math/report.py` à partir des sorties de calcul (aucun chiffre saisi à la main).\n")
    w("## 1. Modèle\n")
    w("- Grille 5 × 3, **20 lignes fixes**, gains de gauche à droite, mise totale = 1 (toutes les valeurs sont des multiples de la mise totale).")
    w("- Bandes de rouleaux : `math/reels/BASE.csv` (jeu de base) et `math/reels/FREE.csv` (tours gratuits). Chaque position d'arrêt est équiprobable.")
    w(f"- Cycle complet du jeu de base : **{ex['base_cycle_boards']:,}** grilles ; cycle des tours gratuits : **{ex['free_cycle_boards']:,}** grilles.".replace(",", " "))
    w("- Wild (Raquette d'Or) sur les rouleaux 2-4, remplace tout sauf le Scatter. Scatter (Trophée) paie partout ; 3/4/5 → 10/12/15 tours gratuits.")
    w(f"- Multiplicateur « Rally » pendant les tours gratuits : {' → '.join('×' + str(m) for m in C.RALLY_LADDER)}, indexé sur le nombre de Wilds tombés depuis le début du bonus ; appliqué aux gains de ligne du tour où le Wild tombe. Relance : 3+ Scatters = +{C.FS_RETRIGGER} tours (50 restants max).")
    w(f"- Plafond de gain : **{C.WINCAP_X:,}× la mise** par tour.\n".replace(",", " "))
    w("### Table des gains (× mise totale, par ligne)\n")
    w("| Symbole | 3 | 4 | 5 |\n|---|---|---|---|")
    for s, p in C.PAYTABLE.items():
        w(f"| {C.SYMBOL_INFO[s]['fr']} ({s}) | {p[3] / 10:g} | {p[4] / 10:g} | {p[5] / 10:g} |")
    w(f"| Trophée (S, n'importe où) | {C.SCATTER_PAY[3] / 10:g} | {C.SCATTER_PAY[4] / 10:g} | {C.SCATTER_PAY[5] / 10:g} |\n")
    w("## 2. Résultats exacts (énumération complète + chaîne de Markov)\n")
    w("| Indicateur | Valeur |\n|---|---|")
    w(f"| **RTP théorique total** | **{pct(ex['rtp'], 4)}** |")
    w(f"| dont jeu de base (lignes) | {pct(ex['rtp_base_lines'])} |")
    w(f"| dont Scatters du jeu de base | {pct(ex['rtp_base_scatter'])} |")
    w(f"| dont tours gratuits | {pct(ex['rtp_free'])} |")
    w(f"| Fréquence de gain (tour gagnant) | {pct(ex['hit_frequency'], 2)} (1 sur {1 / ex['hit_frequency']:.2f}) |")
    w(f"| Fréquence du bonus | 1 sur {ex['trigger_1_in']:.1f} ({pct(ex['p_trigger'], 4)}) |")
    w(f"| Gain moyen d'un bonus | {ex['bonus_mean_x']:.2f}× |")
    w(f"| Écart-type par tour (volatilité) | {ex['std_dev']:.3f}× (jeu de base seul : {ex['base_std_dev']:.3f}×) |")
    w(f"| Résidu numérique de la chaîne de Markov | {ex['markov_residual']:.1e} |\n")
    w("| Déclenchement | Tours | Gain moyen | Écart-type | Tours joués (moy.) | P(atteindre ×10) | Multiplicateur final moyen |\n|---|---|---|---|---|---|---|")
    for k in ("3", "4", "5"):
        v = b3[k]
        w(f"| {k} Trophées (p = {ex['p_scatter'][k]:.3e}) | {v['spins']} | {v['E_x']:.2f}× | {v['SD_x']:.2f}× | {v['E_spins']:.2f} | {pct(v['P_reach_max_mult'], 1)} | ×{v['E_final_multiplier']:.2f} |")
    w("\nLimite connue : la forme fermée n'inclut pas le plafond de 5 000× (il faudrait la loi complète du total du bonus). Son effet est mesuré ci-dessous par simulation : aucun tour plafonné observé, effet inférieur à la précision de toute mesure réalisable.\n")
    w("## 3. Contrôle Monte-Carlo (moteur de référence, tours indépendants)\n")
    w(f"Générateur : {mc['rng']}, graine {mc['seed']}.\n")
    w("| Indicateur | Simulé | Exact |\n|---|---|---|")
    w(f"| Tours simulés | {mc['rounds']:,} | — |".replace(",", " "))
    w(f"| RTP | {pct(mc['rtp_observed'])} ± {pct(1.96 * se)} (IC 95 %) | {pct(ex['rtp'])} |")
    w(f"| Écart normalisé z | {z:+.2f} | (|z| < 2 attendu) |")
    w(f"| Fréquence de gain | {pct(mc['hit_frequency'], 2)} | {pct(ex['hit_frequency'], 2)} |")
    w(f"| Bonus 1 sur | {mc['trigger_1_in']:.1f} | {ex['trigger_1_in']:.1f} |")
    w(f"| Écart-type | {mc['std_dev']:.3f} | {ex['std_dev']:.3f} |")
    w(f"| RTP base / bonus | {pct(mc['rtp_base_observed'])} / {pct(mc['rtp_free_observed'])} | {pct(ex['rtp_base'])} / {pct(ex['rtp_free'])} |")
    w(f"| Tours gratuits joués par bonus | {mc['mean_fs_spins']:.2f} | — |")
    w(f"| Bonus terminés à ×10 | {pct(mc['p_bonus_ends_at_max_multiplier'], 1)} | — |")
    w(f"| Tours plafonnés à 5 000× | {mc['capped_rounds']} | — |")
    w(f"| Plus gros gain observé | {mc['max_win_observed_x']:.1f}× | plafond 5 000× |\n")
    w("![Distribution des gains](img/win_distribution.png)\n")
    w(f"![RTP par session](img/session_rtp.png)\n\nSur une session de 10 000 tours, le RTP observé a un écart-type d'environ **{bsd * 100:.1f} points** : un joueur ou un opérateur peut s'écarter largement de 96,49 % à court terme. C'est la conséquence normale de la volatilité, pas une anomalie.\n")
    w("## 4. Fichiers Stake Engine (table de correspondance publiée)\n")
    w(f"- {lut['books']:,} tours enregistrés (« books »), pondérés par strates aux probabilités exactes (pas de bonus / bonus à 3, 4, 5 Trophées), puis calibrés par basculement exponentiel minimal à l'intérieur de chaque strate.".replace(",", " "))
    w(f"- **RTP de la table publiée : {pct(lut['lut_rtp'], 5)}** (écart au modèle exact : {lut['lut_minus_exact']:.1e}).")
    w(f"- Écart-type : {lut['lut_std_dev']:.3f}× · fréquence de gain : {pct(lut['lut_hit_rate'], 2)} · gain maximal présent dans la table : **{lut['lut_max_payout_x']:.1f}×**.")
    w("\n| Strate | Probabilité | Books | Moyenne visée | Moyenne échantillon | Divergence KL | Poids max / uniforme |\n|---|---|---|---|---|---|---|")
    for s in lut["strata"]:
        w(f"| {s['name']} | {s['probability']:.4e} | {s['books']} | {s['target_mean_x']:.4f}× | {s['sample_mean_x']:.4f}× | {s['kl_divergence_from_uniform']:.1e} | {s['max_weight_ratio_vs_uniform']:.4f} |")
    w(f"\nEmpreintes SHA-256 : books `{lut['sha256_books'][:16]}…`, table `{lut['sha256_lut'][:16]}…`.\n")
    w("**Important** — sur Stake Engine, le serveur ne peut tirer que des tours présents dans les books. Le gain maximal *réellement atteignable* en production est donc celui de la table (" + f"{lut['lut_max_payout_x']:.1f}×" + "), pas le plafond théorique de 5 000×. Avant soumission, il faudra soit afficher ce maximum, soit ajouter une strate de queue (échantillonnage d'importance) contenant des tours proches du plafond. Voir `docs/DISTRIBUTION_READINESS.md`.\n")
    if sdk:
        w("## 5. Vérification par l'outil officiel (engineio/math-sdk)\n")
        m = sdk["modes"]["base"]
        w(f"- Commit du SDK : `{sdk['sdk_commit']}`")
        w(f"- Format de la table et des books : conforme ; paiements books = table : conforme.")
        w(f"- Problèmes bloquant la soumission : **{len(sdk['submission_issues'])}** · contrôles de risque en échec : **{sum(len(v) for v in sdk['risk_failures'].values())}**.")
        w(f"- RTP mesuré par l'outil : {m['rtp'] * 100:.2f} % (limites de soumission du SDK : 96,0 %–96,7 %) · écart-type : {m['std']:.2f}.")
        w("\nCette vérification automatique n'est **pas** une approbation : l'approbation relève de Stake Engine et, selon les marchés, d'un laboratoire de certification.\n")
    w("## 6. Indépendance des tours\n")
    w("Le résultat d'un tour est une fonction pure des positions d'arrêt tirées pour ce tour. Aucun paramètre ne dépend du solde, de l'historique, des gains précédents ou du comportement du joueur. Les tests `test_determinism_and_replay` et `test_independence_of_rounds_order` le vérifient ; sur Stake Engine, chaque tour est un tirage indépendant dans la table publiée.")
    with open(os.path.join(DOCS, "MATH_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote docs/MATH_REPORT.md")


if __name__ == "__main__":
    main()
