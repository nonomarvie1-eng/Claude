# Phase 6 — Compatibilité des stratégies, utilisation du capital, vérifications Cubrik

## 1. Les deux stratégies dans le format Cubrik

Format documenté : `docs/phase4/01_audit_cubrik.md`. Statuts : **V** vérifié dans la documentation publique ; **?** à vérifier dans votre compte.

| Élément | RSI 2 Japon | RSI 30/50 US | Statut |
|---|---|---|---|
| Instrument | CFD JP225 (ou équivalent) | CFD US500 | ? |
| Unité | `1D` | `1D` | V (forex, indices et métaux à partir de H1 en backtest) |
| Entrée | `rsi(2) < 10` ET `price > sma(200)` | `rsi(5) < 30` ET `price > sma(200)` | V (période du RSI : ?) |
| Sortie | `price crossesAbove sma(5)` | `rsi(5) crossesAbove 50` | V |
| Stop | `stopLossPct: 11` | `stopLossPct: 6` | V ; un vrai stop intrajournalier, contrairement à notre simulation à la clôture |
| Objectif | `takeProfitPct: null` | `takeProfitPct: null` | V |
| Sens | `long` | `long` | V |
| Taille | `risk.perTradePct` | idem | ? (sens exact du paramètre) |
| Exécution | Agent contrôlé toutes les 60 min (Demo ou Beginner) : il entre peu après la **clôture de la bougie journalière du courtier** | idem | ? (heure de clôture D1) |

## 2. Utilisation du capital : pourquoi on est si souvent hors du marché (D6)

| Mesure (1991-07 → 2023-06) | Japon | US |
|---|---|---|
| Jours où le filtre SMA 200 est satisfait | **54,7 %** | 76,2 % |
| Jours investis | **7,9 %** | **12,6 %** |
| Trades par an | 5,8 | 6,3 |

**Causes** :

1. Le filtre de tendance exclut 25 à 45 % des jours.
2. La condition de survente (RSI 2 < 10, RSI 5 < 30) ne se produit que quelques jours par an.
3. La sortie au premier rebond limite chaque trade à 4 à 6 jours.

Ce sont précisément les choix qui donnent l'avantage. Les assouplir reviendrait à **modifier les règles**, ce qui est hors du périmètre de cette phase.

## 3. Deux stratégies ensemble : faisabilité (pas d'optimisation)

| Mesure | Valeur | Lecture |
|---|---|---|
| Jours investis : l'une **ou** l'autre / les deux | 17,9 % / 2,7 % | Peu de chevauchement : la combinaison double l'utilisation du capital |
| Corrélation des rendements quotidiens des stratégies | **−0,001** | Indépendantes au jour le jour |
| Corrélation des P&L mensuels | 0,20 | Faible |
| Corrélation des P&L mensuels quand l'une perd | −0,04 | Les pertes ne coïncident pas |
| Corrélation quotidienne Japon-US (indices, même date) | 0,02 | Artefact des fuseaux horaires : Tokyo clôture avant l'ouverture de New York. La corrélation **décalée d'un jour** est nettement plus forte [H]. Dans un krach mondial, les deux stratégies achèteraient le même repli |
| Exposition commune | Deux positions acheteuses sur des indices actions | En stress mondial (2008, mars 2020), les deux peuvent être en position et perdre ensemble |
| P&L combiné au profil 0,5 % chacune (1991-2023 S1) | 1 000 € → ≈ 1 146 € | Environ +0,4 %/an : la combinaison ne change pas l'ordre de grandeur |

**Cubrik** :

- l'offre Demo n'autorise qu'**un** agent actif ; un agent unique portant les deux instructions et deux marchés est plausible, mais non vérifié ;
- Beginner : 2 agents, mais 228 €/an (§07) ;
- **aucun coût supplémentaire n'est justifiable avec 1 000 €.**

Cette étude ne constitue **pas** une autorisation de combinaison ; aucun portefeuille n'a été optimisé.

## 4. Manipulations à faire dans Cubrik Demo (sans backtest, sans agent démarré)

Ne connectez **aucun compte réel** et ne cliquez jamais sur « Start » ni « Run now ».

1. **Créer le compte** sur cubrik.ai : l'offre Demo est gratuite, sans carte.
2. **Instruments** :
   - dans l'application, ouvrez la création d'agent ou le module de backtest et tapez JP225, puis US500, puis NAS100 (essayez aussi « Japan 225 », « Nikkei », « US 500 », « S&P 500 », « US Tech 100 ») ;
   - notez **le nom exact** de chaque instrument et la plateforme qui le fournit ;
   - si la liste dépend d'un courtier connecté, connectez **uniquement le compte démo** d'un courtier MT5 qui propose ces CFD.
3. **RSI 2 et RSI 5** :
   - dans l'écran de règles d'un nouvel agent **en pause**, ou d'un brouillon de backtest **sans le lancer**, saisissez une condition « RSI période 2 inférieur à 10 », puis « RSI période 5 inférieur à 30 » ;
   - notez si la période 2 est refusée ou arrondie.
4. **Sortie sur indicateur** : vérifiez qu'une sortie « clôture croise au-dessus de la SMA 5 » et une sortie « RSI 5 croise au-dessus de 50 » sont acceptées, en plus d'un stop en %.
5. **Taille de position** : notez les options proposées (% de risque, montant fixe, % du capital) et le **texte d'aide** de `perTradePct`. S'agit-il du risque au stop ou du capital engagé ?
6. **Tailles minimales** : dans le compte démo du courtier, notez pour JP225 et US500 le lot minimal, le pas de lot, la valeur du point et la marge requise.
7. **Bougie journalière** : dans MT5 démo, ouvrez le graphique D1 de JP225 et US500 et notez l'heure d'ouverture et de clôture de la bougie (heure du serveur et fuseau).
8. **Frais et financement** : dans les spécifications du symbole (MT5 : clic droit → Spécification), notez le spread type, le **swap acheteur** (financement de nuit), le jour du triple swap et les commissions.
9. **Ne lancez aucun backtest** de ces règles : il couvrirait les 12 derniers mois, donc notre période de test final. Si vous souhaitez tester l'outil, lancez un backtest **sans rapport** avec nos stratégies, par exemple un achat régulier hebdomadaire de BTC sur 1 mois, et copiez le texte « methodology » (frais, glissement, prix d'exécution).
10. Envoyez-moi ces relevés, en texte ou en capture.
