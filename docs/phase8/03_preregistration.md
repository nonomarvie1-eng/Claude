# Phase 8 — Pré-enregistrement définitif (lot 8-01)

Fichier machine : `experiments/preregistration/batch_8_01_intraday.toml`. Il a été commité **avant** le téléchargement des perpétuels et toute exécution. Le brouillon reste conservé dans `experiments/drafts/`.

Précisions qui ne figuraient pas dans l'audit :

| Sujet | Règle fixée |
|---|---|
| Données | Klines perpétuelles USDT-M 1h (Binance Vision) et financement réel ; stops calibrés sur le comptant du S2 2019 |
| Disponibilité | Un actif n'est négociable qu'à partir de sa première bougie perpétuelle ; EMA 200 amorcée sur l'historique perpétuel |
| Signal et exécution | Bougies H1 **clôturées** ; ordre au marché à l'**ouverture suivante** |
| Canaux | Extrêmes des N bougies **précédentes** : la bougie de signal est exclue |
| VWAP | Ancré à 00:00 UTC : somme du prix typique × volume des bougies clôturées depuis minuit UTC (bougie de signal incluse, connue à sa clôture). Aucune donnée future |
| Stop | k × ATR H1 médian du S2 2019 (k = 2), en % fixe par actif, borné à [0,5 % ; 10 %]. Vérifié sur le plus haut et le plus bas H1 dès la bougie d'entrée. Exécution au stop, ou à l'ouverture en cas de gap |
| Objectif | Aucun : sorties sur signal, donc aucune ambiguïté stop/objectif dans une bougie |
| Retournement | Signal opposé en position : sortie, puis entrée inverse à la même ouverture si la capacité le permet |
| Coûts | Taker 0,05 % + demi-écart et glissement 0,05 % par côté ; financement réel à chaque échéance ; stress : × 2, plus une bougie de retard |
| Positions simultanées | 2 au maximum ; risque cumulé au stop ≤ 1 % ; notionnel total ≤ capital (levier 1). Signaux simultanés départagés par l'ordre fixe de l'univers (BTC, ETH, puis volume du T4 2019), jamais par le résultat |
| Perte journalière | Valeur liquidative horaire ≤ 98 % de celle de 00:00 UTC : **plus d'entrée** jusqu'au lendemain. Les positions ouvertes restent gérées par leurs stops |
| Drawdown | Cible de 10 %, rapportée ; une variante « arrêt à 10 % » est rapportée à part |
| Univers | Figé sur le volume du T4 2019 : pas de biais de survie |
| Test principal | R moyen net du **portefeuille de 10 actifs** ; bootstrap de semaines ; correction de Holm sur les 4 hypothèses. L'ordre de priorité de l'utilisateur **n'intervient pas** |
| Sharpe déflaté | N = nombre **total** d'essais du registre |
| Fréquence | Trades par jour au niveau du portefeuille, journées sans trade incluses ; aucune entrée forcée |

Les critères C1 à C8, le budget (4 + 16 + 4) et les conditions de l'analyse du levier figurent dans le TOML.
