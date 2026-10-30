# Robot Tendance

Robot de suivi de tendance sur 7 marchés (actions US, obligations US, or, pétrole, euro, yen, livre).
Version 2, règles figées le 30 octobre 2026. **Argent fictif uniquement.**

- `robot.py` : télécharge les données publiques, note la décision du mois dans `journal.json`, calcule le portefeuille fictif de 1 000 € du robot et un plan ETF fictif de 150 € par mois, puis reconstruit `page.html`.
- `journal.json` : une ligne par mois, écrite au moment de la décision. On ne la modifie jamais après coup.
- `template.html` : la page de résultats.

Lancer : `python3 robot-tendance/robot.py`

Les réglages en haut de `robot.py` ne doivent pas changer pendant le suivi, sinon ce n'est plus un vrai test.
