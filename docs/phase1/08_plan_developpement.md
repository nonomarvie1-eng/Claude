# 08 — Architecture cible et plan de développement

## 1. Architecture modulaire (cible, construite progressivement)

```
nexus/
  data/            collecteur : téléchargement, contrôle qualité, Parquet UTC (lecture seule vis-à-vis des marchés)
  features/        primitives causales : swings, structure, FVG, OB, ranges, sweeps, EMA, ATR, Fib, régimes
  strategies/      une classe par stratégie ; entrée = features disponibles à t ; sortie = intentions d'ordre
  risk/            gestionnaire de risque INDÉPENDANT : taille, plafonds jour/semaine, exposition corrélée, kill-switch
  execution/       simulateur : bid/ask, slippage, limites/stops, ambiguïté intrabar, lots, swaps, funding
  backtest/        orchestrateur, walk-forward, verrou du test final
  stats/           métriques, bootstrap, Monte-Carlo, DSR, PBO, SPA, BH, entrées aléatoires
  journal/         SQLite : runs, configs (hash), trades, accès au test final, erreurs
  dashboard/       Streamlit local, lecture seule sur le journal
  monitoring/      logs structurés, alertes, contrôles de santé
configs/           YAML pré-enregistrés et versionnés (git)
tests/             unitaires, troncature (look-ahead), scénarios d'exécution, DST
```

Principes de sécurité :

- **Aucun module de passage d'ordres réels** n'existe dans le dépôt. Un test automatique échoue si un fichier importe une API d'ordres (ex. `order_send` de MetaTrader5, endpoints d'ordres OANDA/Binance).
- Le gestionnaire de risque a le dernier mot : une stratégie émet des intentions, le risque peut les refuser ; il n'est jamais contourné.
- **Arrêt d'urgence** : fichier sentinelle `STOP` + commande CLI + seuils automatiques (perte journalière, drawdown, erreurs répétées, données périmées) qui figent toute nouvelle position simulée.
- **Versionnement** : chaque stratégie = code + config YAML + hash ; le mode « production » (paper trading) ne charge que des versions marquées `approved` dans le journal par une action manuelle de votre part. Aucune auto-optimisation en production.
- Pas de martingale, pas d'augmentation de taille après perte : vérifié par un test sur le gestionnaire de risque (taille fonction uniquement du capital et de la distance du stop).

## 2. Plan de développement

| Phase | Contenu | Livrable | Critère de sortie | Durée indicative |
|---|---|---|---|---|
| **P1** (terminée) | Audit, formalisation, protocole | Ce dossier | Votre validation | — |
| **P2 Socle** | Environnement Windows, structure du projet, collecteur Dukascopy/Binance pour **2 actifs** (EUR/USD, BTC/USDT), contrôles qualité | Données Parquet + rapport de qualité | Couverture ≥ 99 % hors fermetures, contrôle croisé HistData OK | 1 semaine |
| **P3 Features** | Primitives causales + tests de troncature | `features/` testé | 100 % des features passent le test de troncature | 1–2 semaines |
| **P4 Moteur** | Simulateur d'exécution, risque, journal SQLite | Moteur validé | Scénarios synthétiques exacts ; marche aléatoire ⇒ espérance ≈ −coûts | 1–2 semaines |
| **P5 Références** | S1–S5 + benchmarks sur Développement uniquement, 2 actifs | Rapport « références » | Rapport honnête, y compris négatif | 1 semaine |
| **P6 Extension** | 8 actifs, hybrides A et B, H1–H5, ablations, walk-forward | Rapport de recherche | Application des critères `05 §5` | 2–3 semaines |
| **P7 Validation** | Passe unique sur le bloc Validation, puis test final verrouillé pour ≤ 3 stratégies | Rapport final | Décision go / no-go | 1 semaine |
| **P8 Paper trading** | Uniquement si go : flux temps réel en lecture seule, simulation, tableau de bord, monitoring | Bot de simulation | ≥ 3 mois, résultats dans l'IC attendu | ≥ 3 mois |

**Points de décision** : je vous présente les résultats à la fin de P2, P5, P6 et P7 avant de continuer. Si à la fin de P6 aucune stratégie ne satisfait les critères, la conclusion sera « aucun avantage statistique démontré » et je vous proposerai soit d'arrêter, soit de nouvelles hypothèses pré-enregistrées (testées sur des données neuves), jamais un réajustement des mêmes.

## 3. Décisions nécessaires de votre part pour lancer la phase 2

1. Valider (ou modifier) le découpage temporel et les critères d'acceptation de `05`.
2. Confirmer le fuseau Europe/Paris pour le range asiatique (et ses variantes de robustesse).
3. Exécuter `scripts/check_env.py` sur votre PC et me transmettre la sortie.
4. Choisir où tourne la recherche : sur votre PC (Windows, accès réseau libre) ou dans un environnement cloud dont il faudrait ouvrir l'accès réseau aux hôtes de données (`datafeed.dukascopy.com`, `data.binance.vision`, `www.histdata.com`).
5. Accepter l'ordre de priorité des actifs : EUR/USD et BTC/USDT d'abord, puis GBP/USD, USD/JPY, XAU/USD, ETH/USDT, NASDAQ 100, DAX 40.
