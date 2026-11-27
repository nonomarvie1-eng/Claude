# Phase 6 — Trois hypothèses complémentaires (présentées, NON testées)

Critères de sélection :

- distinctes des 184 essais ;
- documentées dans la littérature ;
- exprimables dans Cubrik (D1) ;
- simples ;
- justification économique ;
- potentiel après frais ;
- surtout, **capables d'augmenter l'utilisation du capital**, problème central de la phase 6.

| Clé | Hypothèse | Littérature | Règle Cubrik (D1) | Pourquoi elle est distincte | Données nécessaires | Utilisation du capital attendue |
|---|---|---|---|---|---|---|
| **H6-A** | **Momentum de série temporelle sur indices actions, achat ou liquidités** : investi tant que le rendement sur 12 mois est positif | Moskowitz, Ooi & Pedersen (2012) ; Hurst, Ooi & Pedersen (2017) ; Faber (2007) | Entrée `roc(252) crossesAbove 0` ; sortie `roc(252) crossesBelow 0` ; stop catastrophe | Jamais testée sur des indices actions : P4-02 et P4-03 portaient sur les cryptos | French US et Japon (déjà disponibles) ; CFD ensuite | **Élevée** : environ 60 à 75 % du temps |
| **H6-B** | **Ancrage sur le plus haut de 52 semaines** : investi quand l'indice est à moins de X % de son plus haut sur 252 jours | Li & Yu (2012), JFE : la proximité du plus haut de 52 semaines prédit positivement les rendements agrégés futurs | Entrée `price > highest(252) × (1 − X)` : un **multiplicateur d'opérande n'est pas documenté** dans Cubrik. Approximation `price crossesAbove highest(252)` (nouveau plus haut), à vérifier | Mécanisme comportemental (ancrage), différent du momentum de rendement | French US et Japon | Moyenne à élevée |
| **H6-C** | **Tendance diversifiée multi-classes** (indices, or, devises), une règle unique par actif | Hurst, Ooi & Pedersen (2017) ; Moskowitz et al. (2012) | SMA 200 ou ROC 252 par actif ; un agent par actif ou un agent multi-marchés | Diversification réelle entre classes d'actifs, ce qui répond à la concentration observée en phase 4 | **Indisponibles** : or, devises, indices en CFD (export MT5 démo) | Élevée, diversifiée |

**Avertissements** :

- **H6-A et H6-B gardent un rendement de marché** : leur intérêt serait de **réduire le drawdown** du marché (comme NXG-01 en phase 2D), pas de produire un alpha élevé. Avec 1 000 € et sans levier, leur rendement attendu est proche de celui de l'indice, environ 5 à 9 %/an à long terme, avec des drawdowns de 15 à 25 % [H]. Elles relèvent davantage de l'**allocation** que du trading.
- **H6-B** dépend d'une capacité de Cubrik non vérifiée (multiplicateur d'opérande).
- **H6-C** demande des données que nous n'avons pas.

**Je ne lance aucun backtest de ces hypothèses sans votre accord.** Si vous l'autorisez, je recommande H6-A seule, en pré-enregistrement :

- périodes : US 1928-2023 S1 et Japon 1991-2023 S1 ;
- critère principal : drawdown et rendement contre achat-conservation, avec le test de différence par blocs.
