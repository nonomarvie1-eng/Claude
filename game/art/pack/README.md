# Golden Rally: Match Point — Pack de 15 symboles

Ce dossier contient les 15 symboles de la nouvelle direction artistique, exportés séparément en **PNG transparent 512 × 512** et en **WebP transparent 512 × 512**.

## Intégration

1. Ouvrir le projet Golden Rally dans Claude Code.
2. Déposer le dossier `png` ou `webp` dans `public/assets/golden-rally/symbols/` (adapter au framework).
3. Associer chaque fichier aux identifiants de symboles qui existent **réellement** dans le moteur du jeu. Inspecter d'abord le registre, les rouleaux, les poids et la paytable.
4. `love` remplace visuellement l'ancien symbole `0` **uniquement sur l'affichage** si celui-ci représente bien le score tennis « 0 » ; conserver l'ID logique existant.
5. `wild`, `scatter`, et `tiebreak_bonus` ne doivent être utilisés pour ces rôles que s'ils existent et ont été définis dans la logique. Sinon les laisser inutilisés.
6. Les objets supplémentaires peuvent être retenus pour de futures évolutions, sans modifier maintenant la distribution des symboles.
7. Vérifier le rendu à taille réelle sur smartphone : lisibilité, contraste, cadrage, stabilité de la grille 6×5 de la version actuelle.
8. Conserver les anciens assets dans un dossier de sauvegarde et prévoir le retour arrière.

## Attention

Les assets ont été isolés par cellules d'une illustration source. Vérifier l'absence de halos et de rognage sur vos fonds, puis ajuster l'alpha ou les marges au besoin. Ne modifier ni RTP, ni rouleaux, ni résultats du RGS, ni multiplicateurs lors du remplacement de sprites. Les noms de fichiers ne définissent pas la logique mathématique.

Le projet de démo affiché ici utilise des crédits fictifs. Avant un lancement commercial, vérifier les licences, les droits d'utilisation commerciale et les règles de l'opérateur et du marché visé.
