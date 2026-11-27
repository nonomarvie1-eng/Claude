# Phase 8 — Guide : exporter des données H1 depuis MetaTrader 5 (compte démo)

Objectif : récupérer l'historique **H1** de XAU/USD, EUR/USD, GBP/USD, NAS100, US500 et JP225 **jusqu'au 30 juin 2023 inclus**, pour l'hypothèse H8-5. **Aucun dépôt d'argent, aucune position.**

## 1. Avant de commencer

- Choisissez un courtier régulé, de préférence dans l'UE (AMF, CySEC, BaFin…), qui propose MetaTrader 5 et des CFD sur ces six instruments.
- **Lisez ses conditions sur l'usage des données de cotation.** Certaines interdisent la redistribution ; un usage de recherche personnelle est généralement admis, mais vérifiez-le. Si les conditions l'interdisent, arrêtez-vous là et dites-le-moi.
- Notez le nom exact du courtier et du serveur : les données diffèrent d'un courtier à l'autre.

## 2. Ouvrir un compte démo (gratuit)

1. Téléchargez **MetaTrader 5** depuis le site du courtier ou de MetaQuotes.
2. Menu **Fichier → Ouvrir un compte**, choisissez le serveur **démo** du courtier, puis « Ouvrir un compte de démonstration ».
3. Ne versez **aucun** argent. Ne cliquez jamais sur « Nouvel ordre », « Acheter » ou « Vendre ».

## 3. Afficher les symboles

1. **Affichage → Symboles** (ou Ctrl + U).
2. Cherchez chaque instrument. Les noms varient selon le courtier : `XAUUSD`, `EURUSD`, `GBPUSD`, `NAS100` / `US100` / `USTEC`, `US500` / `SPX500`, `JP225` / `JPN225`.
3. Sélectionnez-le, puis **Afficher le symbole**.

## 4. Relever les spécifications (pour des coûts réalistes)

Clic droit sur le symbole dans la fenêtre **Observation du marché** → **Spécification**. Notez :

- taille du contrat, valeur du point ou du tick ;
- volume minimal et pas de volume ;
- spread (flottant ou fixe) ;
- **swap acheteur et swap vendeur** (financement de nuit), en points ou en %, et le jour du swap triple ;
- commission éventuelle ;
- heures de cotation (pour connaître l'heure de la bougie journalière) ;
- fuseau du serveur (souvent GMT+2 ou GMT+3).

## 5. Exporter les barres H1

1. **Affichage → Symboles → onglet « Barres »**.
2. Choisissez le symbole, la période **H1**, puis les dates : du **2010-01-01** (ou le plus ancien disponible) au **2023-06-30**. **Ne dépassez pas le 30 juin 2023** : nos périodes de validation et de test final restent verrouillées.
3. Cliquez sur **Requête** : MT5 télécharge l'historique du serveur. La profondeur dépend du courtier ; notez la date de la première barre obtenue.
4. Cliquez sur **Exporter les barres** et enregistrez en CSV, par exemple `XAUUSD_H1_jusqu2023-06-30.csv`.
5. Recommencez pour les 6 instruments.

Le fichier contient `<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>`. Les heures sont celles du **serveur du courtier**. Mon chargeur écarte de toute façon toute ligne postérieure au 2023-06-30.

## 6. Ce qu'il faut m'envoyer

- Les 6 fichiers CSV.
- Le nom du courtier et du serveur, et le fuseau du serveur.
- Les relevés de spécifications (§4), en texte ou en capture.
- L'extrait des conditions du courtier sur l'usage des données.

## 7. Ce que je ferai

- Je vérifierai les trous de données, les doublons et les spreads aberrants.
- Je convertirai les horodatages en UTC.
- J'appliquerai **la meilleure hypothèse H8-1 à H8-4, figée** (H8-5), avec les coûts relevés : un essai par instrument, plafonné à 6.
- **Aucun paramètre ne sera ajusté** à ces nouveaux marchés.
