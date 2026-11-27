# Conditions d'utilisation des données — état de la vérification

Ceci est un relevé de textes, pas un avis juridique. Aucune autorisation n'est supposée au-delà de ce qui est écrit.

## Binance Data Vision — texte lu intégralement

- Document : **Binance Vision Dataset Terms**, version 1.0, « Last Updated: August 26, 2026 ».
  - Source officielle : https://data.binance.vision/Binance_Vision-Terms_of_Use.pdf
  - Lu le 2026-11-27 ; SHA-256 du PDF : `0ec62cd26207f8be17f424d83240f671280ec4b17f7ef9a0026e7b6e0258121f`.
- Documents liés, **non lus** : les Binance Terms of Use, auxquels le PDF renvoie (§1.2), et la licence CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).
- Dépôt de documentation : https://github.com/binance/binance-public-data

| Usage | Ce que dit le texte | Statut pour NEXUS |
|---|---|---|
| Usage personnel | Accès gratuit sous conditions (§2.3) ; licence CC BY-NC-SA 4.0 (§3.1) | Autorisé dans ce cadre |
| Recherche quantitative / backtesting | §4.1 : « algorithmic historical backtesting for purely personal non-production research » fait partie des usages non commerciaux permis | **Autorisé** (usage actuel du projet) |
| Stockage local | §3.2 mentionne « downloading, caching, querying » comme formes d'utilisation soumises aux conditions | Permis comme usage soumis aux conditions |
| Stockage dans le cloud | Non traité explicitement. §4.3 interdit d'« host » les Datasets ; le contexte (licence, location, vente) vise la mise à disposition de tiers, mais ce n'est pas écrit | **À confirmer**. Mesure prise : données dans un conteneur privé et éphémère, **jamais versionnées dans git** (`.gitignore`), jamais partagées |
| Redistribution | §4.3 interdit la (sous-)licence, la vente, l'hébergement et l'exploitation commerciale ; §4.5 : tout travail dérivé redistribué doit citer Binance Vision et rester sous CC BY-NC-SA 4.0 | Aucune redistribution des données. Les rapports qui contiennent des résultats dérivés portent la mention d'attribution |
| Usage commercial | §3.4 : exclu ; licence écrite nécessaire. §4.4 : intégration interdite dans des « commercial trading bot platforms » | Exclu |
| **Trading réel** | §4.2 : « You shall not use the Datasets for live proprietary trading execution, automated commercial order generation… » | **Point bloquant pour l'objectif à long terme** : un bot qui négocierait avec de l'argent réel des stratégies développées sur ces données pourrait relever de cette interdiction. À faire examiner avant toute phase en argent réel. Le paper trading reposerait sur des données temps réel soumises à d'autres conditions, également à vérifier |
| Débit | §7.1–7.2 : respecter les limites, pas de contournement | Respecté (rythme lent, une seule passe, sommes de contrôle) |
| Marques | §8 : pas d'usage du nom Binance pour promouvoir un produit | Respecté |

Mention d'attribution à porter sur les rapports : *« Résultats dérivés de données Binance Vision (data.binance.vision), licence CC BY-NC-SA 4.0. Binance n'est pas associé à ce projet. »*

## Dukascopy — vérification EN ATTENTE

Les pages officielles sont inaccessibles depuis cet environnement : `www.dukascopy.com` n'est pas autorisé dans le réseau, et la lecture par l'outil web a échoué (DNS). **Aucune condition n'a été lue.** Le téléchargement EUR/USD reste suspendu côté cloud, et le script Windows ne devrait être lancé qu'après votre lecture de ces pages.

Liens officiels à consulter :

- Guide du flux historique : https://www.dukascopy.com/wiki/en/development/data-export
  - D'après un résumé de moteur de recherche, non vérifié : les fichiers seraient aussi proposés via un compartiment S3 « Requester Pays », c'est-à-dire avec un transfert payant. Je ne l'utiliserai pas sans votre autorisation.
- Outil d'export historique : https://www.dukascopy.com/swiss/english/marketwatch/historical/
- Conditions et avertissements légaux : https://www.dukascopy.com/swiss/english/legal-pages/ (rubriques « Terms of Use » et « Important Disclaimer »)

| Usage | Statut |
|---|---|
| Personnel / recherche / backtesting | En attente |
| Stockage local / cloud | En attente |
| Redistribution / commercial | En attente ; par défaut aucune redistribution |

Si vous le souhaitez, je peux demander l'ajout de `www.dukascopy.com` à la liste réseau de l'environnement afin de lire ces pages moi-même. Cela nécessite votre approbation.
