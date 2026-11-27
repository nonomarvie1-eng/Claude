# 03 — Stratégies candidates

Chaque stratégie est décrite par une spécification figée **avant** tout test (pré-enregistrement). Les valeurs par défaut viennent des documents quand elles existent ; les grilles de sensibilité sont volontairement petites.

Règles communes à toutes les stratégies (sauf mention) :

- Un trade maximum par stratégie, par actif et par jour (référence) ; variante « re-entrée » testée séparément.
- Signal sur clôture de bougie, exécution à l'ouverture suivante ou par ordre limite/stop placé à l'avance.
- Exclusion news [DOC sans indicateur] : pas de nouvelle entrée de T−30 min à T+30 min autour des publications à fort impact (NFP, CPI, FOMC/BCE/BoJ, PIB) de la devise concernée. Testé **avec et sans**.
- Risque par trade : 0,5 % du capital courant, plafonné par la taille minimale (voir `06`). Trade ignoré si le lot minimal dépasse 1 % de risque.

---

## Références (« baselines » des documents)

### S1 — SBA Référence

| Paramètre | Valeur | Source |
|---|---|---|
| Range | 00:00–09:00, fuseau inconnu : hypothèses `paris`, `london`, `utc` testées comme essais distincts (révision phase 2) | DOC (fuseau PROP) |
| Fenêtre d'entrée | 09:00–13:00 | DOC |
| Déclencheur | Clôture au-delà du range, entrée à l'ouverture suivante | DOC |
| SL | EMA 50 (TF d'exécution) − `0,1·ATR` (achat) ; trade ignoré si EMA du mauvais côté ou distance < `0,5·ATR` | DOC + PROP |
| TP | 2R (grille 1,5 / 2 / 3 / 4) | DOC |
| BE | Aucun (variante : BE à 2R confirmé en clôture) | DOC |
| Sortie temps | 20:00 Europe/Paris | DOC |
| TF | M5, M15 | DOC |
| Sens | Les deux (variante : sens unique documenté par actif) | PROP / DOC |
| Filtres jour/mois | **Désactivés en référence**, testés uniquement comme hypothèse isolée sur données OOS | PROP |

### S2 — ICT Référence (version minimale formalisée)

1. Sweep H4 clôturé d'un swing H4 fractal (L=R=1) [DOC].
2. Dans les 24 h suivantes, MSS sur M5 (CHoCH clôture + displacement `d = 1,0`).
3. Premier FVG M5 dans le sens du MSS formé par la jambe du MSS, taille `≥ 0,3·ATR`.
4. Ordre limite au bord proximal du FVG [DOC « à l'entrée du SIBI »] ; variante CE.
5. SL au-delà de l'extrême du sweep M5 + `0,1·ATR`.
6. TP : swing opposé M15 le plus proche si RR ≥ 2, sinon 2R fixe ; sortie forcée 21:00 Europe/Paris.
7. Ordre annulé s'il n'est pas déclenché en 12 bougies M5.

L'Order Block et l'OTE sont **retirés** de la référence et testés en ablation (ajout).

### S3 — Sans indicateur Référence (H4)

1. Structure H4 haussière (dernier événement = BOS haussier), swings L=R=2.
2. Fibonacci `A → B` sur le swing low d'origine et le swing high du BOS.
3. Ordre limite d'achat à `F(0,786)` [DOC], variante `F(0,705)`.
4. SL `F(1) − 0,1·ATR_H4` ; TP `F(0)` [DOC]. Le RR est donc fixé par construction (≈ 3,7 à 0,786 hors coûts).
5. Ordre annulé si `C < A` ou nouveau BOS avant déclenchement.
6. Durée maximale de position : 5 jours (PROP : le document n'en fixe pas ; le libellé « day trading » est incompatible avec la TF H4).

Pas de timeframes de repli (H3, H2…) : elles constitueraient autant de tests supplémentaires.

### S4 — New York M1 Référence

Instruments : NASDAQ 100 (CFD/indice) en priorité, EUR/USD et XAU/USD en second (le document ne précise pas l'instrument).

1. Fenêtre 09:30–11:30 America/New_York (fin PROP).
2. Structure M1 (swings L=R=2), CHoCH en clôture [DOC].
3. FVG M1 formé par la jambe du CHoCH, taille `≥ 0,5·ATR_M1`.
4. Ordre limite au CE du FVG, uniquement si CE ∈ `[F(0,5), F(0,618)]` de la jambe [DOC].
5. SL au-delà du bas de la bougie 1 du FVG [DOC] avec distance minimale `max(1,5 × coût aller-retour, 0,5·ATR)` (PROP — sans ce plancher, les coûts dominent).
6. TP 4R [DOC]. BE après clôture au-delà du sommet de référence [DOC] (testé avec/sans).
7. Sortie forcée 15:55 New York.

### S5 — EMA 100 + Fibonacci (règles entièrement PROP)

Le document ne contient pas de règles de trading complètes ; cette version est **notre** traduction, à interpréter comme telle.

1. TF H1 (variante M15). Biais long si `C > EMA100` et pente EMA100 > 0.
2. Impulsion = dernier couple swing low → swing high (L=R=3) au-dessus de l'EMA.
3. Ordre limite à `F(0,705)` (milieu de 0,618–0,786).
4. SL `F(1)` ; TP `F(0)` (variante extension `F(−0,272)`).
5. Annulation si clôture sous l'EMA100.

---

## Hybrides

### A — NEXUS Breakout

Hypothèse économique : la compression nocturne précède une expansion de volatilité à l'ouverture d'une session liquide ; la direction de cassure contient un peu d'information si elle va dans le sens d'un filtre de tendance de plus haut niveau.

Pipeline (chaque bloc est activable/désactivable) :

| Bloc | Définition | Ablation |
|---|---|---|
| B0 Niveau | Range asiatique (FX, or, DAX) ou range d'ouverture 30 min (NASDAQ) | Toujours actif |
| B1 Compression | `W_A / ATR_D ≤` tercile bas des 60 jours précédents | on/off |
| B2 Filtre directionnel | Pente EMA100 journalière **ou** structure H4 (comparés entre eux) | off / EMA / structure |
| B3 Confirmation | Clôture au-delà + `b·ATR`, `b ∈ {0; 0,1; 0,25}` | b = 0 vs > 0 |
| B4 Retest | Ordre limite sur le niveau cassé (variante A, §6 de `02`) | entrée cassure vs retest |
| B5 Sortie | SL au-delà du milieu du range ou `1·ATR` ; TP 2R **ou** sortie temps seule (pas de TP) | comparaison |

### B — NEXUS Liquidity Reversal

Hypothèse : les fausses cassures de niveaux très visibles (extrêmes de range asiatique, plus haut/bas de la veille, swings H4) produisent un retour vers l'intérieur du range plus souvent que le hasard.

| Bloc | Définition | Ablation |
|---|---|---|
| L0 Sweep | Fausse cassure d'un niveau (range asiatique / veille / swing H4) avec réintégration en clôture sur M5 | Toujours actif |
| L1 Changement de structure | MSS M5 dans les `W = 12` bougies | on/off |
| L2 Entrée FVG | Limite au CE du premier FVG post-MSS | vs entrée au marché à la réintégration |
| L3 Zone premium/discount | Entrée uniquement dans la moitié du range opposée au sweep | on/off |
| L4 Cible | Milieu du range puis extrême opposé (deux variantes) vs RR fixe | comparaison |

**Point clé** : L0 seul (« fade the failed breakout », entrée au marché) est la version la plus simple. Si L1 + L2 n'améliorent pas significativement L0 en OOS, la complexité SMC est rejetée.

---

## Hypothèses alternatives NEXUS (justifiées par la littérature ou par la microstructure)

| Code | Hypothèse | Justification | Statut |
|---|---|---|---|
| H1 | **Momentum intraday** : le rendement de la première demi-heure (et de la séance de la veille au soir) prédit le signe de la dernière demi-heure sur les indices US | Effet documenté dans la littérature académique (Gao, Han, Li & Zhou, *Market Intraday Momentum*, JFE 2018) ; sa persistance récente reste à vérifier | À tester sur NASDAQ 100 |
| H2 | **Saisonnalité horaire de la volatilité** : la cassure n'apporte rien au-delà du fait que la volatilité augmente à l'ouverture ; une stratégie non directionnelle (straddle synthétique) capterait le même effet | Test de contrôle : sépare « direction » et « volatilité » | Contrôle |
| H3 | **Continuation vs fausse cassure conditionnelles au régime** : Breakout en régime de tendance, Reversal en consolidation | Rend A et B complémentaires plutôt que concurrents | Après validation séparée de A et B |
| H4 | **Filtres calendaires (jour/mois)** = bruit | Nulle par défaut ; un filtre n'est accepté que s'il survit à une correction de comparaisons multiples **et** a une justification (ex. NFP le vendredi) | Test de rejet |
| H5 | **Crypto — effet heure UTC / funding** : comportement autour des fixings de funding (00:00, 08:00, 16:00 UTC) | Mécanisme identifiable (flux de rebalancement) | Exploratoire, priorité basse |

## Modèles de référence simples (benchmarks obligatoires)

1. **Entrées aléatoires appariées** : même nombre de trades, mêmes heures de la journée, même distribution de distances de stop, même RR. 1 000 tirages → distribution nulle de l'espérance.
2. **Cassure naïve** : achat/vente à la première cassure du range sans aucun filtre, sortie 20:00.
3. **Toujours long / toujours court à heure fixe** (ex. 09:00 → 20:00) : isole la dérive.
4. **Buy & hold** de l'actif sur la période (pour BTC, NASDAQ, or : dérive positive forte sur 2020–2025, à ne pas confondre avec un avantage).
5. **Croisement EMA 50/200** journalier : stratégie de tendance de référence.

## Plan d'ablation

Pour chaque hybride : partir du bloc de base, ajouter **un seul bloc à la fois**, mesurer la variation d'espérance nette (en R) et son intervalle de confiance bootstrap. Un bloc n'est conservé que si :

- il améliore l'espérance nette **et** ne réduit pas le nombre de trades au point de rendre le test non significatif ;
- l'amélioration est visible sur au moins 2 des 3 périodes de validation et sur au moins la moitié des actifs ;
- il ne dégrade pas le drawdown médian Monte-Carlo.

Les combinaisons de blocs (2⁵ = 32 pour A, 2⁴ = 16 pour B) sont **toutes** journalisées et comptées dans la correction des comparaisons multiples, même celles abandonnées.
