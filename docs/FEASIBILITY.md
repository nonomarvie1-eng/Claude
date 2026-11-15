# Phase 1 — Étude de distribution et faisabilité

*Date de l'étude : 15 novembre 2026.*

## Sources réellement consultées

| Source | Accès | Remarque |
|---|---|---|
| stake-engine.com/docs, /faq, /distribution, /approval-guidelines | **Bloqué** (domaine hors de la liste réseau autorisée de cet environnement) | À consulter directement avant toute décision ; ajouter `stake-engine.com` aux hôtes autorisés de l'environnement pour que je puisse le faire. |
| github.com/engineio/math-sdk (commit `141b4e8`, 2 nov. 2026) | ✅ cloné | Licence **MIT**. Contient la doc RGS (`docs/rgs_docs/RGS.md`), le format des fichiers (`data_format.md`) et le vérificateur `utils/rgs_verification.py`. |
| github.com/engineio/web-sdk (commit `1843d60`, 28 nov. 2025) | ✅ cloné | **Aucun fichier de licence** → tous droits réservés par défaut. Code non réutilisé ; seules les versions de la pile (Svelte 5, PixiJS 8, Vite 6) ont été suivies. |
| github.com/engineio/ts-client (commit `df9e126`) | ✅ cloné | **Aucun fichier de licence** → non réutilisé ; client RGS réécrit à partir de la documentation. |
| Recherche web (presse spécialisée, blog Stake) | ✅ | Sources **secondaires**, signalées comme telles. |

## Ce qui est vérifié (sources officielles accessibles)

- **Format mathématique** : `index.json` (modes, coût), table CSV `id,poids,payoutMultiplier` en entiers non signés, books JSON-lines compressés zstd avec `id`, `events`, `payoutMultiplier`. Les paiements doivent correspondre exactement entre books et table.
- **Contrôles automatiques du SDK (version de nov. 2026)** : RTP **96,0 %–96,7 %**, paiements par paliers de 10 (0,1× la mise), minimum non nul 0,1×, un mode de base à coût 1×, écart-type du jeu de base ≥ 0,6, gain max ≤ 1 000 000×, contrôles de risque (queue de distribution, volatilité).
- **API RGS** : `/wallet/authenticate`, `/wallet/balance`, `/wallet/play`, `/wallet/end-round`, `/bet/event` ; montants entiers à 6 décimales ; codes d'erreur `ERR_VAL`, `ERR_IPB`, `ERR_IS`, `ERR_ATE`, `ERR_GLE`, `ERR_LOC`, `ERR_GEN`, `ERR_MAINTENANCE` ; paramètres `sessionID`, `lang`, `device`, `rgs_url` ; drapeaux de juridiction (`socialCasino`, `disabledFullscreen`, `disabledTurbo`, …) ; 16 langues ; devises dont XGC/XSC (Stake.us, casino social).
- **Hébergement** : jeu servi en fichiers statiques sous `https://{team}.cdn.stake-engine.com/{game}/{version}/index.html`.

## Ce qui provient de sources secondaires (à confirmer)

- Rémunération : **10 % du GGR**, versée mensuellement (blog Stake, easygo.io, presse spécialisée). Calcul exact du GGR, reports de mois négatifs, seuils, fiscalité : **non vérifiés**.
- Fourchette RTP des nouvelles soumissions abaissée à **90,0 %–96,70 %** (presse, juin 2026) ; le SDK actuel applique 96,0–96,7 %. Nous sommes à 96,49 % : compatible avec les deux.
- Exigence d'afficher le RTP et le gain maximal **par mode** ; mathématiques figées après approbation (seules des retouches cosmétiques possibles).

## Inconnues

- Contrat développeur Stake Engine : exclusivité, propriété intellectuelle, durée, résiliation, droit applicable, responsabilité, KYC/KYB du studio, fiscalité.
- Coûts éventuels (inscription, hébergement, certification) : **aucun coût n'a été trouvé dans les sources accessibles** ; à confirmer.
- Marchés où Stake diffuse les jeux Engine et rôle exact du studio dans la conformité de chaque marché.
- Exigence ou non d'une certification par un laboratoire indépendant (GLI, BMM, eCOGRA, iTech Labs…) pour les jeux Engine.

## Obstacles

**Aucun obstacle n'empêche la démo** (gratuite, locale, sans argent réel).

**Obstacles potentiellement bloquants pour la commercialisation :**

1. Le contrat Stake Engine n'est pas lu (accès réseau bloqué ici) : il conditionne la rémunération, la propriété intellectuelle et l'exclusivité.
2. La vente à d'autres opérateurs, hors Stake, nécessite en général une licence de fournisseur (B2B) dans chaque juridiction : par exemple Malte (MGA), Royaume-Uni (UKGC), Ontario, et selon les cas Curaçao. Elle demande aussi une certification par laboratoire et un RGS agréé. **Utiliser Stake Engine ne rend pas le jeu légalement commercialisable ailleurs.**
3. Le nom « Golden Rally » doit faire l'objet d'une recherche d'antériorité de marque (EUIPO, USPTO, WIPO) avant toute diffusion publique.
4. Jeux d'argent en France : l'ANJ n'autorise pas les machines à sous en ligne. Le jeu ne peut donc pas être exploité en argent réel auprès des joueurs français.

## Positionnement concurrentiel (vérification du concept)

- Le format retenu en v2 (6×5 « ways ») est **standard et accepté** par le SDK : le SDK fournit un exemple officiel `0_0_ways`. Il est vérifié par l'outil officiel sur nos fichiers.
- Les machines à sous à thème tennis sont peu nombreuses. Celles qui existent se reposent surtout sur la licence de joueurs ou de tournois célèbres. Un univers « club privé » original, sans licence, se distingue et évite les coûts de licence.
- La mécanique Rally (multiplicateur persistant alimenté par les Wilds) est simple, lisible, et son RTP est **calculable exactement**, ce qui facilite la certification.
- v2 : passage à un style cartoon à personnages, demandé après comparaison avec les jeux du marché. Les jeux de référence ont inspiré des principes, aucun dessin n'a été repris.
