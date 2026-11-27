# Phase 2D — Conditions d'utilisation des données : textes officiels consultés

Ceci est un relevé de textes, pas un avis juridique. Aucune autorisation n'est supposée au-delà de ce qui est écrit, et une autorisation de recherche historique n'implique **pas** une autorisation de trading réel.

## 1. Dukascopy — vérification effectuée le 2026-11-27

Accès obtenu avec votre autorisation : hôte `www.dukascopy.com` ajouté au réseau de l'environnement.

| Document | URL | Statut | SHA-256 de la page reçue |
|---|---|---|---|
| Terms of Use (TCU) | https://www.dukascopy.com/swiss/english/legal-pages/terms-of-use/ | Lu intégralement | `8bdec56d37875290789f4a4eb4ec0f35b797cb39f0e82aa4f714fe93480117bb` |
| Important Disclaimer | https://www.dukascopy.com/swiss/english/legal-pages/important-disclaimer/ | Lu | `99543af4023a181e3c931abf927ba12c62c68cdb661ad0f6e4891cd2a2e2a6e6` |
| Page « Historical data export » | https://www.dukascopy.com/swiss/english/marketwatch/historical/ | Lue : outil interactif, pas de conditions spécifiques dans le texte statique | `6ee758b5a3629e573e2d8c01097d7e2a8ce467479e0fbd96a9c03716dd2b20f2` |
| Wiki « data-export » | https://www.dukascopy.com/wiki/en/development/data-export | **Non lu** : la page redirige vers un hôte non autorisé (refus du proxy) | — |

Les TCU ne portent pas de date de version. Elles indiquent que les modifications sont « effective immediately ».

### Extraits déterminants (texte original)

- **Restrictions on Use** : « you agree to use the WEBSITE solely for your own non-commercial use and benefit, and not for resale or other transfer or disposition to, or use by or for the benefit of, any other person or entity. »
- « you may download material from the WEBSITE and/or make one print copy for your own personal, non-commercial use, provided that you retain all copyright and other proprietary notices. »
- « The WEBSITE and the information contained therein may not be used to construct a database of any kind. Nor may the WEBSITE be stored (in its entirety or in any part) in databases for access by you or any third party… »
- « You shall not use or attempt to use any "scraper," "robot," "bot," "spider," "data mining," "computer code," or any other automate device, program, tool, algorithm, process or methodology to access, acquire, copy, or monitor any portion of the WEBSITE, any data or content found on or accessed through the WEBSITE, or any other WEBSITE information without the prior express written consent of DUKASCOPY. »
- « You may neither take nor attempt any action that … imposes … an unreasonable or disproportionately large load… »
- **License (i)** : « Such download is licensed to you by DUKASCOPY ONLY for your own personal, non-commercial use… »
- Les TCU couvrent le site « or any service accessible via this website ». Je les applique donc par prudence au flux `datafeed.dukascopy.com`, utilisé par l'outil d'export du site.

### Grille d'usage

| Usage | Lecture stricte du texte | Décision NEXUS |
|---|---|---|
| Téléchargement manuel via le site | Permis pour un usage personnel non commercial | Possible, mais voir « base de données » |
| **Téléchargement automatisé (script)** | **Interdit sans accord écrit préalable** | **Bloqué dans le code** (`DukascopyTermsError`) et dans le script Windows |
| Stockage local | « may not … be stored … in databases » : un stockage structuré de séries pour backtesting relève vraisemblablement de cette interdiction | Non autorisé sans accord écrit |
| Stockage cloud | Même interdiction ; en outre, aucun accès pour des tiers | Non autorisé |
| Backtesting | Non mentionné ; il suppose une base de données | Non autorisé sans accord écrit |
| Usage personnel | Seul usage licencié | — |
| Usage commercial | Interdit | Exclu |
| Trading réel | Non traité ; « non-commercial » seulement | Non supposé autorisé |
| Redistribution | Interdite (« recirculate, redistribute or publish ») | Exclue |

### Mesures appliquées

1. En phase 2, **avant** d'avoir pu lire ces conditions, le téléchargeur automatique avait obtenu 16 fichiers journaliers (184 Ko), plus 2 fichiers d'essai. Ils ont été **supprimés** le 2026-11-27. Ils n'avaient jamais été convertis en Parquet, versionnés ou utilisés dans une expérience.
2. `nexus.data.dukascopy.download_range` lève `DukascopyTermsError` sans la variable `NEXUS_DUKASCOPY_WRITTEN_CONSENT`, qui doit contenir la référence d'un accord écrit (test `test_dukascopy_downloader_blocked_without_written_consent`).
3. Le script Windows `telecharger_eurusd.ps1` s'arrête immédiatement pour la même raison.
4. Les hôtes Dukascopy restent dans la liste réseau, mais ne sont plus utilisés. Vous pouvez les retirer dans les réglages de l'environnement.

## 2. Binance Vision — référence vérifiable

| Élément | Valeur |
|---|---|
| Document | « BINANCE VISION DATASET TERMS », Version 1.0, « Last Updated: August 26, 2026 » |
| URL officielle | https://data.binance.vision/Binance_Vision-Terms_of_Use.pdf |
| Consulté le | 2026-11-27 (téléchargement direct depuis l'hôte officiel) |
| SHA-256 du PDF | `0ec62cd26207f8be17f424d83240f671280ec4b17f7ef9a0026e7b6e0258121f` (144 891 octets) |
| Licence | CC BY-NC-SA 4.0 (§3.1) |

Texte des articles clés, cité littéralement :

- **§4.1** « Permitted non-commercial uses are limited to academic research, non-monetized open educational projects, algorithmic historical backtesting for purely personal non-production research, and non-commercial open-source data science evaluations. »
- **§4.2** « You shall not use the Datasets for live proprietary trading execution, automated commercial order generation, or signal distribution to third parties for direct or indirect compensation. »
- **§4.3** « You shall not license, sub-license, sell, rent, lease, host, or commercially exploit the Datasets or any derivative real-time or historical data feeds. »
- **§4.4** « You shall not integrate the Datasets into commercial financial products, hedge fund management tools, paid subscription newsletters, or commercial trading bot platforms. »

Conséquence : la recherche actuelle (backtesting personnel hors production) est couverte par le §4.1. Un bot négociant de l'argent réel à partir de stratégies développées sur ces données pourrait relever du §4.2. **Point juridique à trancher avant toute phase en argent réel.**

## 3. Sources alternatives pour EUR/USD (non vérifiées, à décider)

| Option | Qualité | Conditions | Statut |
|---|---|---|---|
| A. Demander un **accord écrit à Dukascopy** (usage personnel de backtesting, téléchargement à faible débit, stockage local privé) | Excellente (bid/ask M1) | À obtenir | **Action de votre part** (courriel au support Dukascopy) |
| B. HistData.com (téléchargement manuel mensuel, M1 bid) | Moyenne : bid seulement, fuseau EST fixe, spread à modéliser | Non lues (hôte non autorisé) | Je peux les lire si vous autorisez `www.histdata.com` |
| C. Historique d'un compte de démonstration MT5 d'un courtier | Variable : spread du courtier | Conditions du courtier à lire | Nécessite l'ouverture d'un compte démo par vous |
| D. Taux de référence BCE (journaliers, réutilisation libre) | **Insuffisante** pour le lot intraday M5 pré-enregistré | Libre | Non substituable : refusé |

Je ne substitue pas une source de qualité insuffisante pour débloquer les expériences. Le lot EUR/USD pré-enregistré reste **en attente**.
