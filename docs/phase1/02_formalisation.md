# 02 — Formalisation mathématique (causale)

Toutes les définitions sont **[PROP]** sauf mention [DOC]. Principe directeur : **toute grandeur porte un horodatage de disponibilité** `t_avail`, et un signal émis au temps `t` ne peut utiliser que des grandeurs avec `t_avail ≤ t`.

## Notations

- Bougie `i` d'une unité de temps `TF` : `O_i, H_i, L_i, C_i`, horodatage d'**ouverture** `t_i`, disponibilité à la **clôture** `t_i + Δ_TF`.
- Données bid/ask lorsque disponibles : les signaux sont calculés sur le **mid** (ou bid si seul disponible), l'exécution sur bid/ask.
- Multi-timeframe : une bougie H4 n'est utilisable par un signal M5 qu'après sa clôture. Jointure par `merge_asof(direction="backward")` sur `t_avail`, jamais sur `t_i`.
- `ATR_n` : défini ci-dessous ; sert à normaliser les seuils pour qu'ils soient comparables entre actifs.
- `ε` : tolérance en prix (par défaut 0, variante `κ·ATR`).

## 1. Swing High / Swing Low (fractals)

Paramètres `L` (bougies à gauche), `R` (à droite). [DOC ICT] `L = R = 1` sur les mèches.

- Swing High en `i` si `H_i > max(H_{i−L..i−1})` **et** `H_i ≥ max(H_{i+1..i+R})`.
- Swing Low en `i` si `L_i < min(L_{i−L..i−1})` **et** `L_i ≤ min(L_{i+1..i+R})`.
- Égalités : strict à gauche, large à droite (évite les doublons sur plateaux).
- **Disponibilité : `t_avail = clôture de la bougie i+R`.** C'est le point de look-ahead le plus fréquent dans les backtests SMC : un swing n'existe qu'après les `R` bougies qui le confirment.

Variante adaptative (zigzag ATR) : un sommet devient swing confirmé quand le prix a reculé d'au moins `m·ATR` depuis cet extrême. Disponible au moment du recul. Utilisée comme test de robustesse du choix `L, R`.

## 2. État de structure, BOS, CHoCH, MSS

Mémoire : dernier swing high confirmé `SH*`, dernier swing low confirmé `SL*`, et l'état `S ∈ {haussier, baissier, indéfini}`.

- **Swing protégé** en tendance haussière : `PL` = le swing low confirmé qui précède le plus haut ayant produit le dernier BOS haussier (« higher low pertinent » [DOC NY]). Symétrique `PH` en baisse.
- **BOS haussier** au temps `t` : `S = haussier` et `C_t > SH*` (mode clôture [DOC NY, SBA]) ; variante mèche `H_t > SH*`. Après un BOS, `SH*` est consommé (un niveau ne déclenche qu'un BOS).
- **CHoCH baissier** : `S = haussier` et `C_t < PL` → `S := baissier`. Symétrique.
- Initialisation : `S` devient haussier à la première séquence de 2 swing highs et 2 swing lows croissants (HH + HL), baissier pour décroissants.
- **MSS** (ICT) [PROP] = CHoCH satisfaisant en plus :
  1. il survient dans les `W` bougies suivant un **liquidity sweep** dans le sens opposé (§7) ;
  2. **displacement** : la jambe entre l'extrême du sweep et la bougie de cassure contient au moins une bougie de corps `|C−O| ≥ d·ATR` **ou** crée un FVG (§3).

## 3. Fair Value Gap

[DOC NY] sur trois bougies `t−2, t−1, t` :

- **FVG haussier** si `L_t > H_{t−2}`. Zone `[H_{t−2}, L_t]`.
- **FVG baissier** si `H_t < L_{t−2}`. Zone `[H_t, L_{t−2}]`.
- `t_avail` = clôture de `t`. Milieu (CE) = moyenne des bornes [DOC NY : entrée à 50 %].
- Filtre de taille [PROP] : hauteur `≥ g·ATR` (élimine les micro-gaps de bruit, qui sont innombrables en M1).
- **Mitigation** : première bougie ultérieure qui trade dans la zone. **Invalidation** : clôture au-delà de la borne opposée → le FVG devient **IFVG** (inversé) [DOC ICT].
- Durée de vie maximale `T_max` bougies (sinon les zones s'accumulent indéfiniment).

## 4. Order Block

[PROP] (aucun document ne le définit formellement) :

- **OB haussier** : au moment d'un BOS ou CHoCH haussier en `t`, on remonte depuis le début de la jambe d'impulsion (le swing low d'origine) et on prend **la dernière bougie baissière** (`C < O`) dans les `N` bougies précédant ou incluant ce swing low. Zone = `[L, H]` de cette bougie (variante corps `[C, O]`).
- `t_avail` = temps du BOS/CHoCH (pas avant : l'OB n'est qualifié qu'a posteriori par la cassure).
- Invalidation : clôture sous `L` de l'OB → candidat **Breaker Block** (zone inversée) [DOC sans indicateur].
- Symétrique pour l'OB baissier.

## 5. Range asiatique

[DOC SBA] fenêtre 00:00–09:00, fuseau non spécifié ; [PROP] **Europe/Paris** par défaut, avec variantes Asia/Tokyo 00:00–09:00 et UTC 23:00–07:00 en test de robustesse.

- Pour le jour de trading `D` : `A_H(D) = max H_i`, `A_L(D) = min L_i` sur les bougies dont l'intervalle `[t_i, t_i+Δ)` est entièrement dans la fenêtre convertie depuis le fuseau local (gestion DST automatique via `zoneinfo`).
- `t_avail` = fin de la fenêtre (09:00 local).
- Validité : couverture `≥ 95 %` des bougies attendues, sinon pas de trade ce jour.
- Grandeurs dérivées : largeur `W_A = A_H − A_L`, largeur normalisée `W_A / ATR_D` (ATR journalier de la veille) → mesure de compression.

## 6. Cassure confirmée, fausse cassure, retest

Pour un niveau `X` (range ou swing), fenêtre d'entrée `[T1, T2]` :

- **Cassure confirmée haussière** [DOC SBA] : première bougie `t ∈ [T1, T2]` telle que `C_t > X + b·ATR` (`b = 0` en référence). Ordre au marché à l'**ouverture de la bougie suivante** (jamais au prix de clôture de la bougie signal).
- **Cassure en mèche** : `H_t > X` sans clôture au-delà.
- **Fausse cassure** (sweep d'un niveau) : il existe `t0` avec `H_{t0} > X` et, dans les `m` bougies suivantes (`m = 0` = même bougie), une clôture `C_t < X`. Variante stricte : la cassure avait été confirmée en clôture puis invalidée.
- **Retest** après cassure confirmée en `t0` : première bougie `t ∈ (t0, t0+W]` telle que `L_t ≤ X + r·ATR` et `C_t > X`. Entrée : ordre limite à `X + r·ATR` placé dès `t0` (variante A) ou au marché après la clôture du retest (variante B). Si `C_t < X` avant retest valide → setup annulé.

## 7. Liquidity Sweep

Niveaux de liquidité candidats en `t` : swings confirmés non encore balayés, plus extrêmes de sessions (range asiatique, plus haut/bas de la veille), **Equal Highs/Lows** = au moins deux swings à moins de `δ·ATR` l'un de l'autre.

- **Sweep sell-side (signal haussier potentiel)** : niveau `Y` (âge `≥ a` bougies, `t_avail(Y) < t`), bougie `t` avec `L_t < Y − ε` et `C_t > Y` (rejet sur la même bougie), ou réintégration en clôture dans les `m` bougies.
- Sur H4 [DOC ICT], le sweep n'est connu qu'à la **clôture** de la bougie H4 : un MSS M5 survenu pendant cette bougie H4 ne peut pas être conditionné à un sweep H4 « clôturé » (sinon look-ahead). Variante [PROP] : sweep détecté en temps réel (« le prix est actuellement sous Y et revenu au-dessus ») sur la TF d'exécution.

## 8. EMA 50 / EMA 100

- `α = 2/(n+1)`, `EMA_t = α·C_t + (1−α)·EMA_{t−1}`, amorçage par la SMA des `n` premières clôtures.
- Période de chauffe : les `3n` premières bougies de chaque série sont exclues des signaux (l'influence de l'amorçage y est < 1 %).
- Calculée sur la TF de la stratégie, disponible à la clôture de la bougie.
- Attention : l'EMA doit être calculée sur l'**historique continu** et non recalculée par segment, sinon les valeurs diffèrent au début de chaque fenêtre de test (fuite par incohérence).

## 9. ATR

Wilder, `n = 14` : `TR_t = max(H_t − L_t, |H_t − C_{t−1}|, |L_t − C_{t−1}|)`, `ATR_t = ATR_{t−1} + (TR_t − ATR_{t−1})/n`. Deux versions : ATR de la TF d'exécution (seuils intraday) et ATR journalier de la veille (normalisation inter-actifs, connue dès l'ouverture du jour).

## 10. Retracements de Fibonacci

Ancrage sur une paire de swings **confirmés** : `A` (swing low) puis `B` (swing high postérieur ayant produit un BOS).

- Niveau `F(x) = B − x·(B − A)` ; `F(0) = B`, `F(1) = A` [DOC sans indicateur].
- Zones testées : 0,5–0,618 [DOC NY], 0,618–0,786 [DOC EMA100], 0,705–1 [DOC sans indicateur].
- L'ancrage est figé à `t_avail(B)`. Il est **abandonné** si `C < A` (invalidation [DOC]) ou si un nouveau swing high confirmé dépasse `B` (ré-ancrage).
- Piège : utiliser le « plus haut du mouvement » avant que le swing soit confirmé = look-ahead.

## 11. Régimes de marché

Toutes les classifications utilisent des **seuils calculés sur le passé uniquement** (fenêtre glissante ou expansive), jamais sur l'échantillon complet.

- **Tendance** : Efficiency Ratio `ER_n = |C_t − C_{t−n}| / Σ_{k=t−n+1..t} |C_k − C_{k−1}|` (n = 20 jours sur données journalières) et pente de l'EMA 100 normalisée `(EMA_t − EMA_{t−k}) / (k·ATR_t)`. Tendance si `ER > 0,35` et `|pente| > s`.
- **Consolidation** : `ER < 0,2` **et** amplitude des `n` dernières bougies `< c·ATR`.
- **Volatilité** : rang percentile de l'ATR journalier sur les 250 jours précédents → terciles basse/moyenne/haute.
- Les régimes servent d'**axe d'analyse** (performance par régime) avant d'être éventuellement utilisés comme filtres — et dans ce cas ils comptent comme des paramètres supplémentaires dans la correction des comparaisons multiples.

## 12. Tests unitaires de causalité prévus

Pour chaque fonction de feature : calculer la série sur `[0, T]` puis sur `[0, t]` pour plusieurs `t < T` et vérifier que les valeurs jusqu'à `t` sont **identiques** (test de « troncature »). Toute différence = look-ahead. Ce test sera obligatoire dans la CI du projet.
