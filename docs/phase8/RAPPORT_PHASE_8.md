# NEXUS QUANT — Rapport de phase 8 : day trading H1 sur perpétuels crypto

Date : 2026-11-27. Période de développement seulement (2020-01 → 2023-06). Validation et test final verrouillés : 0 accès. Aucun argent réel, aucun ordre, aucun abonnement, aucune martingale.

## 1. Conclusion

**Les quatre hypothèses intrajournalières sont rejetées.**

- Aucune n'a d'espérance nette positive démontrée.
- Trois perdent de façon nette et significative.
- La simulation chronologique du portefeuille (10 cryptos, 2 positions maximum, 0,5 % de risque par trade) aboutit à :

| | Capital final | Espérance nette par trade | Trades par jour | Drawdown maximal |
|---|---|---|---|---|
| H8-3 Bollinger + ADX | 53 € | −0,155 R | 2,9 | 95 % |
| H8-4 RSI + EMA 50/200 | 201 € | −0,187 R | 1,3 | 80 % |
| H8-1 Cassure 24 h | 920 € | +0,015 R (non significatif) | 1,7 | 74 % |
| H8-2 VWAP + EMA | 52 € | −0,060 R | 7,2 | 96 % |

- **Rendement journalier réalisable** : de −0,22 % à +0,02 % en moyenne. La part de journées à +5 % (0 à 2 %) correspond à de la volatilité, pas à un avantage.

## 2. Pourquoi

1. **Les coûts.** Un trade H1 coûte environ **0,08 à 0,10 R** en frais, glissement et financement : c'est ce que perdent en moyenne des entrées tirées au hasard. Une stratégie doit d'abord gagner au moins cela.
2. **Le retour à la moyenne intrajournalier ne fonctionne pas sur les cryptos en H1.** H8-3 et H8-4 font **pire que des entrées aléatoires** (centile 0) : les excès se prolongent au lieu de se résorber.
3. **Le timing de tendance existe mais ne paie pas.**
   - La cassure H8-1 fait mieux que le hasard d'environ **+0,11 R**, mais les coûts absorbent ce gain.
   - Le résultat dépend du régime de marché : achats +0,21 R, ventes −0,22 R ; 2020-21 +0,17 R, 2022-23 −0,18 R.
   - Même lecture que pour P4-01 en D1 : **une exposition au marché haussier**.
4. **La fréquence augmente les coûts sans augmenter l'avantage.** H8-2, à 7 trades par jour, a payé **1 058 € de coûts pour 1 000 € de capital**.

Ces résultats confirment ceux des phases 2 et 3 (BTC M5) et les étendent à 10 actifs, en H1, à l'achat comme à la vente, en portefeuille.

## 3. Robustesse du constat négatif

- **Sensibilité** : 16 voisins pré-déclarés, **tous négatifs**.
- **Coûts × 2** et **retard d'une bougie** : tous négatifs.
- **Mono-actif** : aucun actif sur 10 n'est positif au-delà du bruit, quelle que soit l'hypothèse.
- **Sous-périodes** : seule H8-1 est positive, et seulement en 2020-21 (marché haussier).
- **Sharpe déflaté** : 0 pour les quatre (N = 217 essais au moment du calcul). **p Holm** : 1,00.
- **Biais de survie** : l'univers est figé sur le volume du T4 2019 ; les résultats ne dépendent pas de la sélection des gagnants d'aujourd'hui.

## 4. Cubrik

Voir `04_compatibilite_cubrik_portefeuille.md`.

- Les règles de portefeuille (2 positions, 1 % de risque cumulé, priorité entre actifs) **ne s'expriment pas** dans le backtest Cubrik, qui calcule un symbole à la fois. Elles seraient de simples consignes à l'IA, sans garantie.
- **Seules les règles mono-actif sont reproductibles**, et elles sont toutes négatives (§4 de `06`).
- Le contrôle toutes les 60 minutes (offres Demo et Beginner) équivaut au retard d'une bougie, qui **dégrade** encore les résultats.

## 5. Levier

**Non simulé.** Le pré-enregistrement le conditionnait à un avantage démontré sans levier.

- À risque égal, le levier ne change rien au rendement.
- Utilisé pour grossir les positions, il accélère la ruine d'une espérance négative.
- À ×20, la liquidation intervient vers −4,5 %, un mouvement courant en H1 sur les altcoins.

## 6. Discipline

| Élément | Détail |
|---|---|
| Pré-enregistrement | Commit `a212a23`, **avant** le téléchargement des perpétuels |
| Données | Archives perpétuelles 1h 2020-01 → 2023-06, sommes vérifiées ; financement réel ; rien après le 2023-06-30 |
| Registre | **218 essais** (194 avant cette phase) ; P8 4/4, P8-SENS 16/16, P8-DIAG 4/4. Le 4e diagnostic est journalisé avec la mention « aucune exécution » : le Monte Carlo et le levier n'ont pas été lancés faute de candidate. Le Sharpe déflaté utilise N = 217, le total au moment du calcul |
| Tests | 115 réussis (109 + 6 nouveaux : VWAP causal, canal sans la bougie de signal, ouverture suivante, stop, capacité et priorité, blocage journalier, financement) |
| Phase 7 | Suspendue, code conservé ; aucune hypothèse exécutée |
| Données conservées | Aucune donnée supprimée |

## 7. Ce que je recommande

1. **Ne pas déployer de stratégie de day trading crypto sur Cubrik.**
   - Les 4 hypothèses H1, les 16 variantes, les familles A, B, E et NLI des phases 2 et 3, et la cassure ORB convergent toutes : **après frais, aucune espérance positive**.
   - Elles ont pourtant été testées sur 10 actifs, à l'achat et à la vente, avec des règles simples.
2. **Ne pas tester d'unités plus courtes (M5, M15).**
   - Les coûts y valent 0,3 à 1,3 R par trade.
   - Il faudrait l'offre Pro ou Max de Cubrik, soit 20 à 40 % du capital par mois.
3. **H8-5 (or, forex, indices)** : c'est la seule piste intrajournalière non encore fermée, car ces marchés ont des coûts plus faibles en % du range (spread de l'or ou d'EUR/USD autour de 0,01 à 0,02 %).
   - Le pré-enregistrement prévoyait d'appliquer la « meilleure des quatre » : **aucune n'est positive**. Je recommande donc de **ne pas lancer H8-5 telle quelle**.
   - Si vous fournissez les exports MT5 (guide `05`), il faudrait d'abord **une nouvelle hypothèse pré-enregistrée**, propre à ces marchés.
4. **L'objectif de 5 % par jour n'est approché par aucun des 217 essais.**
   - Le meilleur résultat intrajournalier robuste mesuré est une espérance **nulle**.
   - Le meilleur résultat tout court reste celui des phases 5-6 (RSI 2 Japon, RSI 30/50 US) : environ **0,0005 à 0,001 % par jour** au profil 0,5 %, et **0,007 à 0,011 % par jour** (2,6 à 3,9 %/an) à 100 % d'exposition. **Il n'est pas intrajournalier.**

## 8. Décisions qui vous reviennent

1. **Arrêter la recherche intrajournalière sur les cryptos**, ce que je recommande.
2. Me fournir les **exports MT5** si vous souhaitez une dernière hypothèse intrajournalière sur l'or, le forex ou les indices (nouvelle hypothèse pré-enregistrée).
3. Réexaminer l'objectif.
   - Les données montrent qu'avec 1 000 €, sans levier et via Cubrik, un rendement positif robuste après frais est déjà **difficile à obtenir** à toutes les fréquences testées.
   - Les seuls signaux statistiquement réels (phases 5 et 6) sont lents et peu rémunérateurs.

*Données : Binance Vision (CC BY-NC-SA 4.0), recherche personnelle §4.1.*
