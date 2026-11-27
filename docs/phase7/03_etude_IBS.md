# Phase 7 — Étude de l'IBS et de ses équivalents

## 1. Équivalences mathématiques (vérifiées)

Pour une bougie de plus haut H, plus bas L et clôture C, avec H > L :

| Indicateur | Définition standard | Période 1 | Relation avec l'IBS |
|---|---|---|---|
| IBS | (C − L) / (H − L) | — | — |
| Williams %R(n) | −100 × (HHₙ − C) / (HHₙ − LLₙ) | −100 × (H − C) / (H − L) | **%R(1) = 100 × IBS − 100** |
| Stochastique %K brut (n) | 100 × (C − LLₙ) / (HHₙ − LLₙ) | 100 × (C − L) / (H − L) | **%K(1) = 100 × IBS** |

**Démonstration pour %R(1)** : −100 × (H − C)/(H − L) = −100 × [(H − L) − (C − L)]/(H − L) = −100 + 100 × IBS. ∎

**Correspondances** :

| Seuil IBS | Williams %R(1) | Stochastique %K(1) brut |
|---|---|---|
| IBS < 0,1 | %R(1) < −90 | %K(1) < 10 |
| IBS < 0,2 | %R(1) < −80 | %K(1) < 20 |
| IBS > 0,9 | %R(1) > −10 | %K(1) > 90 |

**Conditions de validité**, vérifiées par des tests automatisés (`tests/test_phase7.py`) :

1. **Mêmes données OHLC.** Un CFD dont la bougie journalière couvre environ 23 heures n'a pas le même H, L et C que QQQ sur sa séance au comptant (9:30-16:00 New York). L'IBS d'un CFD est donc **un autre signal** que celui du document.
2. **Pas de lissage.** Les plateformes appliquent souvent un lissage de 3 au %K (« slow stochastic ») ou une moyenne %D. Avec un lissage, l'équivalence **disparaît**.
3. **Bougie sans range (H = L).** L'IBS n'est pas défini ; selon les logiciels, %R vaut alors 0, −100, −50 ou une valeur manquante. Les conventions diffèrent, donc les signaux aussi, sur des cas rares.
4. **Période exacte de 1.** Certaines plateformes imposent une période minimale (souvent 2 ou 5).

**Statut Cubrik** :

- Williams %R est **absent** du format documenté (**✗**) ;
- `stochastic` existe, mais la période 1 et l'absence de lissage ne sont **pas documentées** (**?**).
- Les stratégies IBS sont donc de **classe D** tant que vous ne l'avez pas vérifié dans votre compte (`02_compatibilite_cubrik.md` §3).

## 2. Exécution causale

- Le document achète « à la clôture » quand l'IBS de cette même clôture est < 0,1. C'est **irréalisable tel quel** : l'IBS n'est connu qu'au moment où la séance est terminée.
- Deux versions réalistes :
  - (a) **ouverture suivante** : signal calculé sur la bougie terminée, exécution à l'ouverture suivante ;
  - (b) une estimation de l'IBS quelques minutes avant la clôture, qui exige des données intrajournalières.
- **Pré-enregistré** (`05_preregistration.md`) : **ouverture suivante pour la décision** ; la clôture du signal est calculée seulement pour comparaison avec les chiffres annoncés.
- **Cubrik** contrôle toutes les 60 minutes : l'ordre partirait dans l'heure qui suit la clôture de la bougie du courtier, donc **plus près de l'ouverture suivante** que de la clôture.

## 3. Données : le blocage

L'IBS exige les plus hauts et plus bas **journaliers** de QQQ, SPY ou d'un CFD :

- Kenneth French : clôtures seulement. **Insuffisant.**
- FRED, Stooq : refusent les clients automatisés (phases 5 et 6).
- Yahoo : exclu (conditions).
- Binance : OHLC disponible, mais pour des cryptos. L'IBS sur crypto serait une **autre hypothèse**, sans justification économique propre : marché 24 h/24, « clôture » arbitraire à 00:00 UTC. Je ne la lance pas.

**Il faut donc l'une des trois sources suivantes, à obtenir par vous et gratuitement** :

1. **Export MT5 démo** des CFD NAS100 et US500 en D1, **jusqu'au 2023-06-30** : l'instrument même que traderait l'agent ;
2. une **clé gratuite Alpha Vantage ou Tiingo** (QQQ, SPY), après lecture de leurs conditions ;
3. l'activation du **connecteur MCP Alpha Vantage** dans votre compte claude.ai.

Le code est **prêt** : `nexus/phase7/ibs.py` lit tout fichier OHLC journalier (CSV MT5 ou autre), applique le verrou des périodes, et exécute les hypothèses H7-A et H7-B pré-enregistrées dès que les données sont fournies.

## 4. Que peut-on attendre ? (sans résultat inventé)

- L'IBS sur les ETF actions américains est un effet **publié depuis une dizaine d'années** sur les blogs quantitatifs [H].
- Nos résultats de phase 6 montrent que l'achat de repli sur l'indice américain est **significatif depuis 1993, mais perdant de 1940 à 1989**. L'IBS hérite probablement de cette **dépendance au régime de marché** [H].
- Ses atouts possibles par rapport à RSI 30/50 :
  - une **exposition plus élevée** (38 % annoncés pour QQQ, contre 12 %) : c'était le problème central de la phase 6 ;
  - une **fréquence** plus forte.
- Ses risques :
  - pas de filtre de tendance ni de stop dans la règle d'origine ;
  - drawdown de 21 à 23 % annoncé, au-delà de votre seuil de 10 %.
