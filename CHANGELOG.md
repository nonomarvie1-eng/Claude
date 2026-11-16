# Changelog

## v5 — game 2.0.0 / math 3.0.0 (2026-11-16)

### Mathématiques (refonte complète, recalculée)
- 11 symboles (W, S, H1–H4, L1–L5) : suppression de l'ancien H5 ; nouvelle table de gains et nouvelle composition des rouleaux.
- Symboles empilés (blocs de 1 à 3) : fréquence de gain 67 % → 27,9 %.
- Deux niveaux de bonus : TIE-BREAK (3 scatters, 9 tours, ×1) et SUPER TIE-BREAK (4/5/6 scatters, 12/15/20 tours, ×2).
- Quatre modes Stake : `base` 1×, `bonus_chance` 1,4×, `buy_tiebreak` 49,4×, `buy_super` 105× ; RTP 96,41–96,52 % après plafond.
- Le calcul exact intègre désormais l'effet du plafond 5 000× (mesuré par simulation ciblée, erreur standard publiée). Sans cette correction, l'achat Super aurait été annoncé à 97,4 % au lieu de 96,4 %.
- Correction : probabilité « atteindre ×20 » (le dernier tour n'était pas compté).
- Export Stake généralisé aux 4 modes ; vérificateur officiel : 0 problème.
- Ancien achat unique 100× (tirage 3/4 scatters) supprimé.

### Jeu
- Nouveau pack de 11 symboles colorés (originaux conservés), taille uniforme, sans cadre commun.
- Connexions gagnantes lisibles : cadres colorés, tracé du rouleau 1 au dernier rouleau, comptes par rouleau, étiquette détaillée, présentation successive puis globale, bouton « Revoir les gains ».
- Fenêtre « Modes de jeu et achats » : 4 cartes (Normal, Bonus Chance, Achat Tie-Break, Achat Super Tie-Break), confirmation avec le montant exact ; prix du prochain tour affiché dans le HUD.
- Super Tie-Break : introduction dédiée, ambiance bleu électrique / or blanc, cadre lumineux bleu, panneau dédié, entrée spécifique d'Ace, récapitulatif.
- Ace : le symbole H1 du pack sert aussi de mascotte animée.
- Page d'informations refaite : 11 symboles, connexions, bonus, achats, Bonus Chance, RTP par mode.

### Tests
- pytest 29/29, vitest 24/24, svelte-check 0 erreur, e2e 161/161 (9 formats d'écran).

## v4 — refonte premium (2026-11-16)
Pack de 15 symboles, palette nuit, HUD sans chevauchement, écran d'accueil, Ace, Tie-Break distinct. Voir l'historique Git.
