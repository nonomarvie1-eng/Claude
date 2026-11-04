# PROJECT — Marque e-commerce mono-produit (France)

Dernière mise à jour : 2026-11-04

## Contexte
- Fondateur débutant en e-commerce, ~2 h/jour, ne montre pas son visage.
- Modèle : dropshipping sans stock au lancement, Shopify, marché France.
- Budget total : 500 à 1 000 € (dont pub ≤ 500 €). Aucune dépense supplémentaire supposée.
- Boutique mono-produit (+ variantes/accessoires cohérents). Pas d'abonnement obligatoire.
- Objectif long terme : 10 000 €/mois de CA **si** l'économie unitaire le permet. Rentabilité et trésorerie d'abord.

## Règles de travail
- Aucune action engageante sans accord explicite : paiement, achat, message à un tiers, compte externe, publication, pub.
- Chaque chiffre est marqué : **vérifié** (source + date), **estimation de travail**, ou **inconnu**.
- Jalons 1 → 8 (voir ROADMAP.md). On ne saute pas un jalon.

## Environnement de travail (audit du 2026-11-04)
| Élément | État |
|---|---|
| Dépôt git | Vide au départ (README seul). Branche `claude/dropshipping-market-research-2xgb7b`. |
| Recherche web (WebSearch) | **Disponible** — renvoie des résumés de résultats + URL. |
| Lecture directe de pages (curl) | Domaines autorisés le 2026-11-04 (soir). Résultat des tests : **AliExpress OK** (données relevées dans `data/`), **douane.gouv.fr OK**. **Amazon.fr** : protection anti-robot → non contournée (règle du projet). **CJ** : recherche réservée aux comptes connectés. **Google Trends** : page dynamique, non exploitable. **Meta Ad Library, legifrance, economie.gouv** : 403. **service-public** redirige vers `service-public.gouv.fr` (non autorisé). |
| Similarweb, TrendTrack, Meta Ad Library, TikTok Creative Center, outils SEO | **Non accessibles** (aucun connecteur, réseau bloqué). |
| Shopify, CJ, AliExpress (comptes) | **Aucun compte connecté.** |
| Python 3.13 | Disponible (calculs dans `tools/`). |

Conséquence : les données de prix fournisseurs, d'avis Amazon, de volume de recherche et de publicités actives n'ont **pas** pu être vérifiées en page directe. Elles sont marquées comme telles.

Pour lever la limite : dans les réglages de l'environnement cloud (menu de l'environnement dans la barre de titre → Edit → Network access), autoriser au minimum : `www.amazon.fr`, `fr.aliexpress.com`, `cjdropshipping.com`, `trends.google.com`, `www.facebook.com`, `www.douane.gouv.fr`, `entreprendre.service-public.fr`, `www.legifrance.gouv.fr`. Doc : https://code.claude.com/docs/en/cloud-environments#network-access

## Frais fixes mensuels de travail (estimation)
| Poste | €/mois | Statut |
|---|---|---|
| Shopify Basic (mensuel) | 36 | Vérifié via guides 2026, à confirmer sur shopify.com/fr/tarifs |
| Domaine | ~1,25 | Estimation (~15 €/an) |
| Éco-organisme REP (minimum Ecologic ASL si produit de sport) | 6,25 | Vérifié : minimum 75 € HT/an (barème Ecologic 2026) — seulement si filière ASL |
| Banque / divers | 5 | Estimation |
| **Total** | **~48,50** | |

## Fichiers
- `ROADMAP.md` — jalons et progression
- `RESEARCH.md` — recherche, sources, réglementation
- `RAPPORT_DECISION_01.md` — rapport de la session 1
- `OPPORTUNITIES.csv` — candidats analysés et verdict
- `COMPETITORS.md` — marques étrangères et concurrents français
- `SUPPLIERS.csv` — pistes fournisseurs (non contactés)
- `UNIT_ECONOMICS.csv` → `tools/unit_economics.py` → `UNIT_ECONOMICS_RESULTATS.csv`
- `DECISIONS.md` — décisions et justifications
- `NEXT_ACTIONS.md` — prochaines actions
