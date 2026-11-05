"""Calcul de l'economie unitaire a partir de UNIT_ECONOMICS.csv.

Usage : python3 tools/unit_economics.py
Ecrit UNIT_ECONOMICS_RESULTATS.csv et affiche un resume.

Hypotheses fiscales (a valider par un expert-comptable) :
- Micro-entreprise en franchise en base de TVA : aucune TVA collectee sur la vente,
  la TVA a l'import n'est pas recuperable -> c'est un cout.
- TVA a l'import calculee sur (cout fournisseur + livraison + droit de douane).
- Droit de douane UE forfaitaire : 3 EUR par categorie d'article (depuis le 1er juillet 2026).
- Frais de traitement UE ("handling fee") : montant non confirme, teste de 0 a 2 EUR.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "UNIT_ECONOMICS.csv"
OUT = ROOT / "UNIT_ECONOMICS_RESULTATS.csv"

# Cotisations sociales micro-entrepreneur (achat-revente), calculees sur le chiffre d'affaires,
# meme si la publicite absorbe le benefice. 12,3 % + 0,1 % formation professionnelle (taux 2026 a confirmer, hors ACRE).
TAUX_COTISATIONS_CA = 0.124

# Part de la marge contributive qu'on accepte de depenser en acquisition.
# Le reste couvre les frais fixes, les imprevus et le resultat.
PART_MARGE_POUR_CPA_CIBLE = 0.60

# Frais fixes mensuels de travail (EUR), detail dans PROJECT.md
FRAIS_FIXES_MENSUELS = {
    "shopify_basic_mensuel": 36.0,
    "domaine": 1.25,
    "rep_eco_organisme_minimum": 6.25,  # 75 EUR HT/an minimum Ecologic si filiere ASL
    "banque_divers": 5.0,
}


def f(row, key):
    return float(row[key])


def calc(row):
    prix = f(row, "prix_ttc")
    base_import = f(row, "cout_fournisseur") + f(row, "livraison") + f(row, "droit_douane_ue")
    tva_import = base_import * f(row, "tva_import_taux")
    cout_rendu = base_import + tva_import + f(row, "frais_traitement_ue") + f(row, "emballage_insert")
    frais_paiement = prix * f(row, "frais_paiement_pct") + f(row, "frais_paiement_fixe")
    provision = prix * f(row, "provision_retours_pct")
    cotisations = prix * TAUX_COTISATIONS_CA
    marge = prix - cout_rendu - frais_paiement - provision - cotisations
    cpa_max = marge
    roas_eq = prix / marge if marge > 0 else float("inf")
    # CPA cible : on garde au moins 3 EUR par commande (ou 40 % de la marge si c'est plus)
    cpa_cible = max(0.0, marge - max(3.0, marge * (1 - PART_MARGE_POUR_CPA_CIBLE)))
    roas_cible = prix / cpa_cible if cpa_cible > 0 else float("inf")
    fixes = sum(FRAIS_FIXES_MENSUELS.values())
    reste_par_cmd = marge - cpa_cible
    cmd_pour_fixes = fixes / reste_par_cmd if reste_par_cmd > 0 else float("inf")
    cmd_10k = 10000 / prix
    resultat_10k = cmd_10k * reste_par_cmd - fixes
    return {
        "produit": row["produit"],
        "scenario": row["scenario"],
        "prix_ttc": round(prix, 2),
        "tva_import": round(tva_import, 2),
        "cout_rendu_client": round(cout_rendu, 2),
        "frais_paiement": round(frais_paiement, 2),
        "provision_retours_sav": round(provision, 2),
        "cotisations_micro": round(cotisations, 2),
        "marge_contributive_avant_pub": round(marge, 2),
        "taux_marge_contributive": round(marge / prix, 3),
        "cpa_max_equilibre": round(cpa_max, 2),
        "roas_equilibre": round(roas_eq, 2),
        "cpa_cible": round(cpa_cible, 2),
        "roas_cible": round(roas_cible, 2),
        "commandes_mois_pour_couvrir_fixes": round(cmd_pour_fixes, 1),
        "commandes_mois_pour_10k_CA": round(cmd_10k, 0),
        "resultat_mois_a_10k_CA_si_cpa_cible": round(resultat_10k, 0),
    }


def main():
    with SRC.open(newline="", encoding="utf-8") as fh:
        rows = [calc(r) for r in csv.DictReader(fh)]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Frais fixes mensuels retenus : {sum(FRAIS_FIXES_MENSUELS.values()):.2f} EUR")
    for r in rows:
        print(
            f"{r['produit']:<22}{r['scenario']:<11} prix {r['prix_ttc']:>6} | marge {r['marge_contributive_avant_pub']:>6}"
            f" ({r['taux_marge_contributive']:.0%}) | CPA max {r['cpa_max_equilibre']:>6} | ROAS eq {r['roas_equilibre']:>5}"
            f" | CPA cible {r['cpa_cible']:>6} | resultat a 10k {r['resultat_mois_a_10k_CA_si_cpa_cible']:>6}"
        )


if __name__ == "__main__":
    main()
