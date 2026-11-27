# Phase 5 — Hypothèses quantitatives (5 au maximum, plus l'essai de gestion de l'exposition)

## 1. Justification économique

- **Retour à la moyenne court terme sur indices actions.** Plusieurs mécanismes sont documentés :
  - la fourniture de liquidité : les vendeurs pressés paient une prime aux acheteurs (Nagel 2012, « Evaporating Liquidity », RFS : les rendements des stratégies de retournement court terme montent avec la volatilité, comme le dit le document 7) ;
  - les achats systématiques sur repli.
- **Limite connue** : l'autocorrélation des rendements courts de l'indice américain n'est pas stable dans le temps. Lo & MacKinlay (1988) mesuraient une autocorrélation hebdomadaire *positive* sur 1962-1985 ; le comportement de retour à la moyenne invoqué par les documents serait plus récent [H]. L'avantage étant connu et publié, il a pu être arbitré : c'est pourquoi la période **postérieure à 2010** sert de test principal, et la période **1928-1992** de contrôle.
- **Suivi de tendance (essai de gestion)** : momentum de série temporelle (Moskowitz, Ooi & Pedersen 2012), déjà motivé en phase 4. Le problème mesuré est la **concentration** et les **gains rendus**, pas l'absence d'information de timing.

## 2. Les hypothèses retenues

| Clé | Hypothèse | Marché | Pourquoi elle est distincte |
|---|---|---|---|
| **H5-01** | RSI 2 de Connors : (a) version d'origine, sans stop ; (b) même règle avec stop catastrophe pré-défini | Marché américain (CRSP), journalier | Référence la plus documentée ; reproduction des chiffres annoncés, puis test hors échantillon post-2010 |
| **H5-02** | RSI 30/50 (RSI 5 < 30 ; sortie au croisement de 50), avec stop catastrophe | Idem | Oscillateur plus lent, sortie sur l'oscillateur ; la règle la plus native dans Cubrik |
| **H5-03** | Double 5 (clôture au plus bas des 5 clôtures ; sortie au plus haut des 5 clôtures), avec stop catastrophe | Idem | Extrêmes de prix au lieu d'un oscillateur ; sortie plus tardive |
| **H5-04** | Réplication de H5-01b sur l'Europe, le Japon et l'Asie-Pacifique hors Japon | Marchés développés (French, USD), depuis 1990 | Leçon du document indien : un avantage sur un marché ne se transpose pas forcément |
| **H5-EXP** | Protection progressive des gains sur P4-01 (Donchian 55/20, 10 cryptos) avec les paliers `lock` de Cubrik | Crypto (Binance, période de développement) | **Essai unique autorisé** ; s'attaque à la concentration et au drawdown mesurés en phase 4 |

**Non retenues**, avec la raison :

- R3, %B, jours de baisse, trois jours bas : incompatibles avec Cubrik (décalages, calculs) ;
- plus bas de 5 jours, IBS, Williams %R : il faut le plus haut et le plus bas, absents des données ;
- XLP et FXI : règles non publiées ;
- Turtles en mode toujours en position : déjà couvert par P4-01 et P4-03 (rejetés).

## 3. Classement a priori

| Clé | Justification économique | Faisabilité Cubrik | Coût d'exécution | Rang |
|---|---|---|---|---|
| H5-01 | Forte (liquidité, retournements) | Native, sous réserve que la période 2 soit acceptée | Faible : ≈ 4 jours de détention, environ 10 trades par an | 1 |
| H5-02 | Forte (même famille) | La plus native | Faible | 2 |
| H5-04 | Test de généralité | Selon les CFD disponibles | Faible | 3 |
| H5-03 | Moyenne : construction moins standard | À vérifier (`lowest`) | Faible | 4 |
| H5-EXP | Forte (tendance), mais il s'agit d'une règle de gestion | Native (`lock`) | Nul : aucun trade supplémentaire | Essai distinct |

## 4. Le conflit entre la règle de risque et ces stratégies

Les stratégies Connors investissent **100 % du capital** pendant quelques jours, sans stop. Notre règle impose 0,25 à 0,5 % de risque au stop. Avec un stop catastrophe d'environ 8 %, la position engage seulement 0,5 / 8 ≈ **6 % du capital**, et le rendement annuel devient très faible, même si l'avantage est réel.

Je présente donc deux dimensionnements :

1. **Règle NEXUS** (risque 0,5 % au stop) : la seule conforme aux contraintes actuelles.
2. **Notionnel 100 %, sans levier**, comme dans les documents : à titre d'information. Le risque réel au stop vaut alors environ 8 % du capital par trade, ce qui **dépasse** la règle.

Choisir entre les deux serait **une décision de votre part**, pas un résultat de recherche.
