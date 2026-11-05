# Catalogue Gâté Pourri — plan d'extension (2026-11-05)

## Principe
Un modèle = animal + décor, avec **deux zones vides** (bandeau de phrase + cartouche du prénom).
L'outil écrit la phrase et le prénom → nombre de combinaisons = modèles × phrases, sans regénérer d'images.

## Priorités
1. Modèle golden « bandeau de phrase vide » (test de l'outil à deux zones)
2. Décor **Noël** (saisonnier, à prêt avant fin novembre)
3. **Chats** : européen tigré, roux, noir, gris (type british), maine coon
4. Chiens, lot 2 : berger allemand, cavalier King Charles, jack russell, chihuahua, border collie, berger belge malinois, teckel, yorkshire, beagle, shih tzu/bichon
5. Décor « salon cosy » (intérieur, toute l'année)

## Phrases (en majuscules, idéalement ≤ 22 caractères, maximum 26 — au-delà le texte devient trop petit)
Outil : `python3 tools/generer_plaque.py <modèle> "<prénom>" "<phrase>" <sortie>` — modèles à deux zones vides dans `designs/modeles2/`.
Chiens : UN CHIEN GÂTÉ VIT ICI · LE CHIEN COMMANDE ICI · CHIEN GENTIL MAIS TRÈS BAVARD · VOLEUR DE CHAUSSETTES À BORD · GARDIEN OFFICIEL DU CANAPÉ
Chats : UN CHAT GÂTÉ VIT ICI · ICI LE CHAT EST LE PATRON · CHAT DE GARDE INEFFICACE · LES HUMAINS SONT TOLÉRÉS
Noël : UN CHIEN SAGE (OU PRESQUE) · UN CHAT SAGE (OU PRESQUE)

## Règle de lancement
Boutique : au départ 10–15 combinaisons mises en avant ; le reste via le choix « race / phrase » sur la fiche produit. Ne pas multiplier les modèles avant la validation de l'échantillon.
