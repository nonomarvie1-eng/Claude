# Phase 2D — Audit technique indépendant du moteur

| Point audité | Constat | Action | Test |
|---|---|---|---|
| Calculs de rendement | Courbe de capital limitée à [premier signal, dernière sortie]. **Défaut 1** : Sharpe, CAGR et alpha des stratégies calculés sur une fenêtre plus courte que celle des références | `run_backtest(period=…)` : courbe sur toute la période, jours en liquidités inclus | `test_equity_curve_covers_full_period_when_requested` |
| Comparaison aux références | **Défaut 2** : le Buy & Hold partait de la clôture du 1er jour, la stratégie de son ouverture | `passive_benchmarks(start_price=…)` | `test_full_investment_strategy_matches_passive_buy_and_hold` : une stratégie investie à 100 % égale le B&H à la friction près |
| Conversions monétaires | **Défaut 3** : valorisation quotidienne convertie au taux d'entrée | Taux du jour (dernier connu) | `test_mtm_uses_rate_of_each_day` |
| Frais stratégie / référence | Identiques : 0,10 % par côté sur le notionnel | — | `test_fees_are_identical_between_strategy_and_reference` |
| Valorisation quotidienne | Correcte hors défaut 3 | — | `test_daily_mark_to_market_for_multi_day_position` |
| Coûts, ordres non exécutés, arrondis, gaps, stops suiveurs | Conformes | — | Tests existants (15 scénarios d'exécution, équivalence vectorisé/naïf sur 3 000 trades, stops suiveurs) |
| Calculs d'exposition | Conformes | — | `test_exposure_stats` |
| Limites de risque | Conformes (limite journalière, arrêt, anti-martingale) | — | Tests existants |
| Verrouillage des périodes | **Défaut 4** : la validation n'était protégée que par le protocole, pas techniquement | Verrou technique de la validation, avec journal d'accès (`validation_access`) | `test_validation_period_is_technically_locked` |
| Rapport qualité des données | **Défaut 5** : en phase 2, des statistiques de prix (OHLC, pics) avaient été calculées sur 2020 → 2024, donc **y compris la validation**. Aucun résultat de stratégie n'en dépend | Statistiques limitées au développement ; couverture seule pour la validation et le test final | — |
| Reproductibilité | Résultats identiques à paramètres égaux | — | `test_backtest_is_deterministic` ; reproduction exacte des 12 essais d'audit |
| Persistance du registre | Le registre survit à la fermeture et à la réouverture ; migrations idempotentes | — | `test_registry_persists_across_connections` |
| Source de données non conforme | Téléchargeur Dukascopy automatique, alors que les conditions l'interdisent | Bloqué | `test_dukascopy_downloader_blocked_without_written_consent` |

## Effet des défauts 1 à 3 sur les candidats de la phase 2C

Les résultats enregistrés **ne sont pas modifiés**. Le recalcul est publié séparément : 6 répétitions techniques, famille TECH, `reports/phase2d_audit_technique.md`.

- E[R] : identique (ces défauts ne touchent pas les trades).
- Sharpe quotidien : de −0,09 à +0,05.
- Alpha : de −0,4 à +0,07 %/an.
- CAGR au profil équilibré : de −0,4 à −0,05 point.
- Buy & Hold : +331,8 % → +332,1 %.
- **Aucun verdict ne change.**

## Concentration des profits (nuance demandée)

Comparaison avec la distribution sous entrées aléatoires à exposition comparable (300 réplications, mêmes durées et mêmes stops ; `results/tech_audit_2d/concentration.json`) :

| Candidat 2C | Part des 5 meilleurs trades | Aléatoire : médiane [5 % ; 95 %] | Part des tirages plus concentrés |
|---|---|---|---|
| NXF-01 L = 20 | 65 % | 63 % [50 ; 77] | 40 % |
| NXF-01 L = 60 | 99,6 % | 93 % [80 ; 99,7] | 6 % |
| NXF-02 H4 | 94 % | 99 % [89 ; 100] | 86 % |
| NXF-03 L = 20 | 81 % | 69 % [57 ; 84] | 12 % |
| REF-SMA-01 | 97 % | 89 % [74 ; 98] | 9 % |
| NXD-02 H4 | 30 % | 35 % [28 ; 43] | 87 % |

Avec peu de trades et des détentions longues, une forte concentration est **attendue même par hasard**. L'alerte « > 50 % du profit sur 5 trades » de la phase 2C n'était donc pas discriminante en soi. Les réserves déterminantes restent l'absence d'alpha significatif et le faible nombre d'épisodes de tendance indépendants.
