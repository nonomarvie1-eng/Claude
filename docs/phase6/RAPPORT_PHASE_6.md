# NEXUS QUANT — Rapport de phase 6 : confirmation des signaux et dimensionnement

Date : 2026-11-27. **Développement seulement**, rien après le 2023-06-30.

- Validation et test final : 0 accès.
- Aucun compte Cubrik, aucun agent, aucun ordre, aucun achat.
- Pré-enregistrement commité avant toute nouvelle donnée (`58b12eb`).

## 1. Conclusion

1. **Le signal japonais vient bien du marché japonais, pas du change.**
   - Décomposition de 151 trades avec les taux BCE : composante locale **+1,02 % par trade** [IC95 +0,68 ; +1,34] ; composante change **−0,34 %** [−0,49 ; −0,17].
   - Le change **réduit** l'avantage.
   - Sur un indice japonais reconstruit en yens, la règle figée reste significative : +0,55 % par trade, p = 0,0003 contre les entrées aléatoires.
   - Le yen seul ne donne rien.
   - **Question ouverte** : le portefeuille French (toutes les actions, proche du TOPIX) contre le Nikkei 225. Aucune source légale et automatisable n'a été trouvée.
2. **Le signal américain dépend du régime de marché.**
   - RSI 30/50 est significatif sur 1993-2009 (p = 0,002) et sur 2010-2023 (p = 0,001).
   - Il était **perdant pendant cinq décennies** (1940-1989 ; −1,0 % par trade dans les années 1960).
   - L'avantage existe depuis environ 30 ans et peut disparaître.
3. **Le stop simulé n'est pas un vrai stop.** C'est une sortie à la clôture.
   - Japon : aucune sortie sur stop, mais une clôture à −10,5 % pour un stop de 11 %. Un stop réel aurait probablement été touché au moins une fois.
   - US : 5 sorties, entre −6,1 % et −8,2 % pour un stop de 6 % (gaps).
   - Notre simulation est **légèrement optimiste** ; il faut des données OHLC pour la corriger.
4. **Le dimensionnement ne peut pas rendre ces stratégies économiquement intéressantes.**
   - Sharpe constant : 0,42 au Japon, 0,60 aux US. Calmar autour de 0,2.
   - Même investies à **100 %** à chaque signal, sans levier : **+2,6 %/an** (Japon) et **+3,9 %/an** (US), avec 67 à 79 % de probabilité simulée de dépasser 10 % de drawdown.
   - Sous votre seuil de 10 % (drawdown au 95e percentile), le rendement plafonne vers **1 à 1,4 %/an**.
5. **Cubrik payant n'est pas rentable avec 1 000 €.**
   - Beginner coûte **22,8 % du capital par an**, Intermediate 70,8 %.
   - Seule l'offre **Demo** gratuite (1 agent) est compatible.
   - Il faudrait environ **5 800 €** de capital pour que la meilleure stratégie, investie à 100 %, couvre l'offre Beginner.

**Réponse directe à votre question** : je n'ai trouvé **aucune stratégie présentant un avantage économique suffisant** pour justifier un agent Cubrik avec 1 000 € et vos contraintes de risque.

- Les deux signaux sont **statistiquement réels sur leur période récente**, mais leur rendement est trop faible.
- Rien ne permet d'atteindre 10 à 20 %/an sans levier, ni sans dépasser votre seuil de drawdown.

## 2. Livrables

| Document | Contenu |
|---|---|
| `01_audit_signal_japonais.md` | Reproduction, décomposition change et marché, indice en JPY, audit du stop |
| `02_audit_signal_americain.md` | Stabilité par décennie, transfert vers SPY, Nasdaq et CFD, audit du stop |
| `03_sources_donnees.md` | Sources examinées, conditions, ce qui manque, ce que je vous demande |
| `04_protocole_dimensionnement.md` | Protocole pré-enregistré |
| `05_resultats_developpement.md` | 8 profils × 2 stratégies : CAGR, drawdown, Sharpe, Calmar, exposition, gap, frais, financement, Monte Carlo |
| `06_frontiere_rendement_risque.md` | Frontière de Pareto |
| `07_rentabilite_cubrik.md` | Coûts fixes, rendement nécessaire, capital minimum |
| `08_compatibilite_strategies.md` | Traduction en règles Cubrik, utilisation du capital, combinaison, **manipulations Cubrik Demo** |
| `09_protocole_validation.md` | Protocole de validation 2023-07 → 2024-12, **non exécuté** |
| `10_hypotheses_complementaires.md` | 3 hypothèses présentées, non testées |

## 3. Utilisation du capital

- Le Japon est investi **7,9 %** des jours, les US **12,6 %**.
- Combinées, les deux stratégies le sont **17,9 %** des jours, avec peu de chevauchement et des rendements quotidiens non corrélés (−0,001).
- La combinaison double donc l'utilisation du capital, **sans changer l'ordre de grandeur** : +0,4 %/an au profil 0,5 %.
- En stress mondial, les deux sont des positions acheteuses sur des indices actions, et leurs pertes peuvent coïncider.

## 4. Discipline

- **Registre : 194 essais** (184 avant cette phase).
  - P6-DIAG : 8 sur 8, dont **1 en échec** journalisé : bug de fuseau horaire dans un utilitaire de date, corrigé, sans résultat produit.
  - P6-SIZE : 2 sur 2.
  - Aucun nouvel essai de sélection.
- **Tests : 103 réussis.**
- **Aucune règle d'entrée ou de sortie modifiée** ; les deux stratégies sont reproduites à l'identique (D0).
- **Données** :
  - taux de référence BCE (« Source : ECB statistics »), coupés au 2023-06-30 ;
  - Kenneth French (CRSP) ;
  - non versionnées.
- **Réseau** :
  - `www.ecb.europa.eu` ajouté à l'environnement ;
  - FRED et Stooq refusent les clients automatisés ; aucun contournement (un en-tête de navigateur imité a été refusé par le contrôle de sécurité de la session, et je ne l'ai pas réessayé).

## 5. Décisions qui vous reviennent

1. **Continuer ou arrêter.**
   - Ma recommandation honnête : avec 1 000 €, sans levier et avec un drawdown inférieur à 10 %, **aucune stratégie étudiée n'a d'intérêt économique**.
   - Les deux signaux méritent d'être **conservés comme résultats de recherche**, pas déployés.
2. **Si vous continuez** :
   - (a) faire les relevés **Cubrik Demo et MT5 démo** (`08` §4) et exporter l'historique D1 des CFD JP225 et US500 jusqu'au 2023-06-30 ;
   - (b) je refais alors l'audit sur l'**instrument réel**, avec plus hauts et plus bas : vrai stop, bougie du courtier, swap réel ;
   - (c) vous fixez le dimensionnement ;
   - (d) vous autorisez éventuellement la validation (`09`).
3. **Recherche** : autoriser ou non **H6-A** (momentum 12 mois, achat ou liquidités, sur indices). C'est une stratégie d'allocation qui utiliserait 60 à 75 % du capital. Son intérêt serait de réduire le drawdown de l'indice, pas un alpha élevé.
4. **Votre objectif de 10 à 20 %/an avec moins de 10 % de drawdown** n'est atteint par **aucun** des 194 essais. Il faudrait soit plus de capital (pour amortir les coûts fixes), soit accepter plus de risque. **Ces deux choix vous appartiennent.**

*Sources : ECB statistics (taux de référence) ; Kenneth R. French Data Library (CRSP) ; Binance Vision (CC BY-NC-SA 4.0) pour les phases antérieures.*
