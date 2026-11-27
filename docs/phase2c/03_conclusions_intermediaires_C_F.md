# Conclusions intermédiaires — familles C, F, REF et REG (lot 2C-01)

Enregistré **avant** l'exécution de la famille D. BTC/USDT spot, période de développement 2020-01 → 2023-06. Résultats dérivés de données Binance Vision (CC BY-NC-SA 4.0).

## C — Trend Pullback (12 essais)

- Aucun « prometteur ». H1 : tous négatifs nets ; 3 variantes sont « incompatibles » (IC95 < 0).
- H4 : espérances positives pour les sorties sans objectif fixe (NXC-05 stop suiveur +0,61R ; NXC-06 invalidation +0,74R ; 74 trades), mais :
  - l'IC95 inclut 0 ([−0,05 ; 1,70] et [−0,16 ; 1,97]) ;
  - 70 à 77 % du profit brut vient de 5 trades ;
  - le résultat est porté par le premier semestre 2023 (≈ +5R en moyenne) ;
  - l'alpha quotidien n'est pas distinguable de 0.
- Ablations (différence avec C minimal, IC95) : **aucune contribution démontrée**, ni structure, ni confirmation, ni stop structurel, ni stop suiveur, ni sortie sur invalidation, ni filtre de régime.
- Walk-forward de la sélection au sein de C : E[R] hors échantillon −0,08 sur 258 trades.

## F — Momentum (11 essais) et référence moyenne mobile (1 essai)

- Verdict pré-enregistré « prometteur mais preuves insuffisantes » pour NXF-01 (L = 20 et 60), NXF-02 H4 (N = 120), NXF-03 L = 20 et REF-SMA-01. Les autres variantes ont moins de 20 trades.
- Réserves majeures, qui empêchent toute sélection :
  1. **Concentration** : 74 à 100 % du profit brut provient de 5 trades, essentiellement dans la tendance haussière de 2021.
  2. **Exposition au marché** : l'alpha quotidien n'est distinguable de 0 pour aucune variante (bornes basses de −0,1 à −4,6 %/an).
  3. **Pas de valeur ajoutée sur la simple moyenne mobile** : NXF-01 et NXF-02 ne battent pas REF-SMA-01 (différences dont l'IC inclut 0).
  4. **Échantillon** : 8 à 51 trades ; en pratique un seul grand cycle haussier (2020-2021), un cycle baissier (2022) et une reprise (2023). Le nombre d'épisodes de tendance indépendants est minime.
- Ce que montrent les données, de façon descriptive :
  - à exposition moyenne égale (≈ 2 % du capital), ces règles de suivi de tendance ont un drawdown plus faible qu'une détention passive à la même exposition (ex. REF-SMA équilibré : DD 4,8 % contre 11,5 %) ;
  - le Sharpe quotidien est d'environ 1,0 à 1,3, contre 0,95 pour l'achat-conservation de BTC sur la période ; les IC95 se recouvrent largement.
  - La réduction du risque n'est donc **pas démontrée** statistiquement, seulement suggérée.
- Le filtre de volatilité n'a pas de contribution démontrée.

## REG — filtre de régime journalier (2 essais)

Pas d'amélioration indépendante : Δ = −0,04R en H1 et +0,08R en H4, IC incluant 0.

## Décision pour la suite

- La famille D est maintenue, comme prévu au protocole et pour une raison précise : C et F montrent que les résultats positifs sur BTC s'expliquent surtout par l'exposition à la tendance. D est conçue avec un **contrôle sans compression**, qui permet justement de tester si la compression apporte quelque chose au-delà de cette exposition. Budget : 4 essais sur 8.
- Aucune variante n'est gelée comme candidate à la validation à ce stade.
