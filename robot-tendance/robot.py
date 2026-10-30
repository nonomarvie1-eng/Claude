"""Robot Tendance, version 2 (règles figées le 30 octobre 2026).

Chaque mois, pour 7 marchés : on regarde si le prix a monté sur 1, 3 et 12 mois.
On mise dans le sens de la tendance, moins sur les marchés qui bougent beaucoup.
Levier total plafonné à 2.

Utilisation : python3 robot.py
  1. télécharge les dernières données publiques
  2. note la décision du mois en cours dans journal.json (si pas déjà fait)
  3. calcule le portefeuille fictif de 1 000 € du robot, et à côté un plan ETF fictif
     de 150 € par mois (ce que donnerait un PEA investi chaque mois)
  4. reconstruit page.html
"""
import csv, io, json, math, os, sys, urllib.request
from datetime import date

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCES = {
    "sp": "datasets/s-and-p-500/main/data/data.csv",
    "bond": "datasets/bond-yields-us-10y/main/data/monthly.csv",
    "gold": "datasets/gold-prices/main/data/monthly.csv",
    "oil": "datasets/oil-prices/main/data/wti-daily.csv",
    "fx": "datasets/exchange-rates/main/data/daily.csv",
}
MARCHES = ["Actions US", "Obligations US", "Or", "Pétrole", "Euro", "Yen", "Livre sterling"]
# Réglages figés : ne pas les modifier, sinon le suivi n'est plus un vrai test.
DUREES = (1, 3, 12)
FENETRE_VOL = 36
CIBLE_VOL = 0.12
LEVIER_MAX = 2.0
FRAIS = 0.001
DEBUT_SUIVI = "2026-11"
CAPITAL_FICTIF = 1000.0
VERSEMENT_ETF = 150.0  # plan ETF : versement mensuel fictif


def telecharger(chemin):
    url = "https://raw.githubusercontent.com/" + chemin
    with urllib.request.urlopen(url, timeout=120) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))


def nombre(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def rendements(niveaux):
    """{mois: niveau} -> {mois: rendement du mois}"""
    ks = sorted(k for k, v in niveaux.items() if v and v > 0)
    return {b: niveaux[b] / niveaux[a] - 1 for a, b in zip(ks, ks[1:])}


def fin_de_mois_complets(lignes):
    """Prix quotidiens -> dernier prix de chaque mois terminé (le mois en cours est ignoré)."""
    out, dernier = {}, ""
    for d, v in lignes:
        out[d[:7]] = v
        dernier = max(dernier, d[:7])
    out.pop(dernier, None)
    return out


def charger():
    R = {}
    # Actions US : S&P 500 dividendes compris
    rend, prec, dernier_rdt = {}, None, None
    for r in telecharger(SOURCES["sp"]):
        p, dv = nombre(r["SP500"]), nombre(r["Dividend"])
        if not p:
            continue
        if dv and dv > 0:
            dernier_rdt = dv / p
        rdt = dv / p if dv and dv > 0 else dernier_rdt
        if prec:
            rend[r["Date"][:7]] = p / prec - 1 + (rdt or 0) / 12
        prec = p
    R["Actions US"] = rend
    # Obligations US 10 ans : variation de prix d'une obligation + intérêts
    taux = [(r["Date"][:7], nombre(r["Rate"]) / 100) for r in telecharger(SOURCES["bond"]) if nombre(r["Rate"])]
    obl = {}
    for (_, y0), (m1, y1) in zip(taux, taux[1:]):
        c, yy, N = y0 / 2, y1 / 2, 20
        prix = sum(c / (1 + yy) ** k for k in range(1, N + 1)) + 1 / (1 + yy) ** N
        obl[m1] = prix - 1 + y0 / 12
    R["Obligations US"] = obl
    R["Or"] = rendements({r["Date"][:7]: nombre(r["Price"]) for r in telecharger(SOURCES["gold"])})
    R["Pétrole"] = rendements(fin_de_mois_complets(
        (r["Date"], nombre(r["Price"])) for r in telecharger(SOURCES["oil"]) if nombre(r["Price"])))
    fx = {}
    for r in telecharger(SOURCES["fx"]):
        v = nombre(r["Exchange rate"])
        if v:
            fx.setdefault(r["Country"], []).append((r["Date"], v))
    for pays, nom in [("Euro", "Euro"), ("Japan", "Yen"), ("United Kingdom", "Livre sterling")]:
        R[nom] = rendements({k: 1 / v for k, v in fin_de_mois_complets(fx[pays]).items()})
    return R


def passe(R, n, mois, k):
    """Les k derniers rendements connus avant `mois`."""
    ks = [x for x in sorted(R[n]) if x < mois][-k:]
    return [R[n][x] for x in ks] if len(ks) == k else None


def decision(R, mois):
    """Poids de chaque marché pour `mois` (0,25 = 25 % du capital, négatif = pari à la baisse)."""
    w = {}
    for n in MARCHES:
        pv = passe(R, n, mois, FENETRE_VOL)
        if not pv:
            w[n] = 0.0
            continue
        signal = sum(1 if math.prod(1 + x for x in passe(R, n, mois, L)) > 1 else -1 for L in DUREES) / len(DUREES)
        moy = sum(pv) / len(pv)
        vol = math.sqrt(sum((x - moy) ** 2 for x in pv) / (len(pv) - 1) * 12)
        w[n] = signal * (CIBLE_VOL / math.sqrt(len(MARCHES))) / vol
    total = sum(abs(x) for x in w.values())
    if total > LEVIER_MAX:
        w = {n: x * LEVIER_MAX / total for n, x in w.items()}
    return w


def filet(R, mois):
    """Filet de sécurité : "ETF" si l'indice (dividendes compris) est au-dessus
    de sa moyenne des 10 derniers mois connus, sinon "cash"."""
    ks = [x for x in sorted(R["Actions US"]) if x < mois]
    niveau, niveaux = 1.0, []
    for k in ks:
        niveau *= 1 + R["Actions US"][k]
        niveaux.append(niveau)
    dix = niveaux[-10:]
    return "ETF" if dix[-1] > sum(dix) / len(dix) else "cash"


def resultat_mois(R, w, w_avant, mois):
    if not all(mois in R[n] for n in MARCHES):
        return None
    rotation = sum(abs(w[n] - w_avant.get(n, 0)) for n in MARCHES)
    return sum(w[n] * R[n][mois] for n in MARCHES) - rotation * FRAIS


def historique(R):
    fin = min(max(R[n]) for n in MARCHES)
    mois = [m for m in sorted(R["Actions US"]) if "2000-01" <= m <= fin]
    robot, avant = [], {}
    for m in mois:
        w = decision(R, m)
        robot.append(resultat_mois(R, w, avant, m))
        avant = w
    actions = [R["Actions US"][m] for m in mois]
    return mois, robot, actions


def courbe(rs):
    e, out = 1.0, []
    for x in rs:
        e *= 1 + x
        out.append(round(e * 1000))
    return out


def main():
    R = charger()
    aujourd_hui = date.today()
    mois_courant = aujourd_hui.strftime("%Y-%m")
    if aujourd_hui.day >= 25:  # fin de mois : on prépare le mois suivant
        a, m = aujourd_hui.year, aujourd_hui.month + 1
        if m == 13:
            a, m = a + 1, 1
        mois_courant = f"{a}-{m:02d}"
    mois_courant = max(mois_courant, DEBUT_SUIVI)

    chemin_journal = os.path.join(ICI, "journal.json")
    journal = json.load(open(chemin_journal)) if os.path.exists(chemin_journal) else []
    if not any(e["mois"] == mois_courant for e in journal):
        w = decision(R, mois_courant)
        journal.append({
            "mois": mois_courant,
            "decide_le": aujourd_hui.isoformat(),
            "donnees_jusqu_a": {n: max(R[n]) for n in MARCHES},
            "poids": {n: round(x, 4) for n, x in w.items()},
            "filet": filet(R, mois_courant),
        })
        journal.sort(key=lambda e: e["mois"])
        json.dump(journal, open(chemin_journal, "w"), ensure_ascii=False, indent=1)

    # Portefeuille fictif
    valeur, avant, lignes = CAPITAL_FICTIF, {}, []
    for e in journal:
        r = resultat_mois(R, e["poids"], avant, e["mois"])
        if r is not None:
            valeur *= 1 + r
        lignes.append({"mois": e["mois"], "decide_le": e["decide_le"], "resultat": r,
                       "valeur": round(valeur, 2) if r is not None else None})
        avant = e["poids"]

    # Plan ETF fictif : 150 € investis chaque début de mois.
    # Simulé avec le S&P 500 (dividendes compris) converti en euros,
    # car il n'existe pas de données publiques gratuites de l'indice monde.
    def mois_suivant(m):
        a, mm = int(m[:4]), int(m[5:]) + 1
        return f"{a + (mm == 13)}-{1 if mm == 13 else mm:02d}"
    # Plan avec filet de sécurité : mêmes 150 € par mois, mais tout passe en cash
    # quand l'indice est sous sa moyenne des 10 derniers mois (décision notée dans le journal).
    def rendement_etf(m):
        if m in R["Actions US"] and m in R["Euro"]:
            return (1 + R["Actions US"][m]) / (1 + R["Euro"][m]) - 1
        return None
    choix_filet = {e["mois"]: e.get("filet", "ETF") for e in journal}
    etf_lignes, etf_val, fil_val, verse, fini, m = [], 0.0, 0.0, 0.0, 0.0, DEBUT_SUIVI
    pos = "ETF"
    while m <= mois_courant:
        verse += VERSEMENT_ETF
        pos = choix_filet.get(m, pos)
        r_etf = rendement_etf(m)
        r_fil = None
        if r_etf is not None:
            r_fil = r_etf if pos == "ETF" else 0.0
            etf_val = (etf_val + VERSEMENT_ETF) * (1 + r_etf)
            fil_val = (fil_val + VERSEMENT_ETF) * (1 + r_fil)
            fini += VERSEMENT_ETF
        etf_lignes.append({"mois": m, "resultat": r_etf, "filet": r_fil, "pos": pos})
        m = mois_suivant(m)
    etf_valeur = etf_val + (verse - fini)  # les mois en attente comptent à leur prix d'achat
    fil_valeur = fil_val + (verse - fini)
    par_mois = {l["mois"]: l for l in etf_lignes}
    for l in lignes:
        p = par_mois.get(l["mois"], {})
        l["etf"], l["filet"], l["pos"] = p.get("resultat"), p.get("filet"), p.get("pos")

    # Retour sur 2026 avant le début du suivi (même robot, appliqué aux mois déjà passés)
    retro, avant_r, rv, ev, dca, dca_verse = [], decision(R, "2025-12"), CAPITAL_FICTIF, CAPITAL_FICTIF, 0.0, 0.0
    fv, fdca = CAPITAL_FICTIF, 0.0
    m = "2026-01"
    while m < DEBUT_SUIVI:
        w = decision(R, m)
        r = resultat_mois(R, w, avant_r, m)
        avant_r = w
        e = rendement_etf(m)
        p = filet(R, m)
        f = None if e is None else (e if p == "ETF" else 0.0)
        if r is not None:
            rv *= 1 + r
        if e is not None:
            ev *= 1 + e
            fv *= 1 + f
            dca_verse += VERSEMENT_ETF
            dca = (dca + VERSEMENT_ETF) * (1 + e)
            fdca = (fdca + VERSEMENT_ETF) * (1 + f)
        retro.append({"mois": m, "robot": r, "etf": e, "filet": f, "pos": p})
        m = mois_suivant(m)

    mois, robot, actions = historique(R)
    melange = [0.8 * a + 0.2 * b for a, b in zip(actions, robot)]
    D = {
        "m": mois, "sp": courbe(actions), "ro": courbe(robot), "mx": courbe(melange),
        "w": {n: round(x * 100) for n, x in journal[-1]["poids"].items()},
        "wMois": journal[-1]["mois"],
        "live": {"debut": DEBUT_SUIVI, "capital": CAPITAL_FICTIF, "valeur": round(valeur, 2),
                 "lignes": lignes, "maj": aujourd_hui.isoformat(),
                 "etf": {"versement": VERSEMENT_ETF, "verse": verse, "valeur": round(etf_valeur, 2)},
                 "filet": {"valeur": round(fil_valeur, 2), "pos": journal[-1].get("filet", "ETF")}},
        "retro": {"lignes": retro, "robot": round(rv, 2), "etf": round(ev, 2), "dca": round(dca, 2), "dcaVerse": dca_verse,
                  "filet": round(fv, 2), "filetDca": round(fdca, 2)},
    }
    gabarit = open(os.path.join(ICI, "template.html"), encoding="utf-8").read()
    page = gabarit.replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":")))
    open(os.path.join(ICI, "page.html"), "w", encoding="utf-8").write(page)

    rs = [x for x in robot]
    an = (math.prod(1 + x for x in rs) ** (12 / len(rs)) - 1) * 100
    print(f"Historique {mois[0]} -> {mois[-1]} : {an:.1f} % par an")
    print(f"Décision {journal[-1]['mois']} : " + ", ".join(f"{n} {x*100:+.0f} %" for n, x in journal[-1]["poids"].items()))
    print(f"Portefeuille fictif : {valeur:.2f} € ({sum(1 for l in lignes if l['resultat'] is not None)} mois terminés)")
    print(f"Plan ETF fictif : {etf_valeur:.2f} € pour {verse:.0f} € versés")
    print(f"Plan avec filet : {fil_valeur:.2f} € pour {verse:.0f} € versés (ce mois : {journal[-1].get('filet')})")


if __name__ == "__main__":
    main()
