# P0049 component attribution summary

Status: PASS
1. Dataset used: `se3_se1_bottleneck_training_dataset_v1`; derived `se3_se1_bottleneck_reservoir_analysis_v1` with 34968 rows.
2. Reservoir formulas tested: ['base_pressure', 'learned_pressure_score']; EMA half-lives=(6, 12, 24, 48, 72, 168).
3. Rolling weather gradients were only a small correlation improvement over instantaneous weather gradients at longer horizons, but not a MAE/F1 winner.
4. Explicit reservoir pressure did not beat rolling features or lagged spread in this deterministic diagnostic.
5. SE1 price level weakly decreased future 6h spread risk in validation correlation (-0.052984).
6. SE3 price level behaved differently and had a positive future 6h spread correlation (0.279996).
7. Price-threshold tables are suggestive only; high SE3 prices were followed by higher 6h spread than high SE1 prices, so P0049 does not prove industrial demand-response drainage.
8. Lag/decay differs by day type: weekends retain stronger short lag correlation, while holiday/weekend 48h correlations are lower than Monday-Thursday/Friday.
9. Friday is not clearly less persistent after price spikes; Friday sample sizes are smaller and the evidence remains WARN-level.
10. Weekends look more direct at 1h-6h lag response, but less smoothed at long horizon is suggestive rather than proven.
11. Current observed SE3-SE1 remains useful for classification through 168h in this split; best-F1 groups by horizon: {'h1': 'G5_lagged_spread_only', 'h3': 'G5_lagged_spread_only', 'h6': 'G5_lagged_spread_only', 'h12': 'G5_lagged_spread_only', 'h24': 'G5_lagged_spread_only', 'h48': 'G5_lagged_spread_only', 'h72': 'G5_lagged_spread_only', 'h168': 'G5_lagged_spread_only'}.
12. Calendar features beat lagged spread by MAE at some longer horizons, but lagged spread stays best for classification; best-MAE groups: {'h1': 'G5_lagged_spread_only', 'h3': 'G5_lagged_spread_only', 'h6': 'G0_time_calendar', 'h12': 'G0_time_calendar', 'h24': 'G5_lagged_spread_only', 'h48': 'G0_time_calendar', 'h72': 'G0_time_calendar', 'h168': 'G0_time_calendar'}.
13. The bottleneck-reservoir path is worth comparing, but the explicit reservoir feature alone is not strong enough to become the only P0050 path.
14. Recommendation: P0050 should compare direct SE3 AI-1/AI-2 with a non-deployable reservoir/bottleneck prototype under forecast-origin validation.
15. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.
Raw attribution: {'h1': {'best_group_by_MAE': 'G5_lagged_spread_only', 'best_MAE': 0.1333327232617047}, 'h6': {'best_group_by_MAE': 'G0_time_calendar', 'best_MAE': 0.24821622098250798}, 'h24': {'best_group_by_MAE': 'G5_lagged_spread_only', 'best_MAE': 0.23781576989194586}, 'h72': {'best_group_by_MAE': 'G0_time_calendar', 'best_MAE': 0.24639398524819325}, 'h168': {'best_group_by_MAE': 'G0_time_calendar', 'best_MAE': 0.24506620216202893}, 'se1_price_corr_future_6h': -0.052984095043525116, 'se3_price_corr_future_6h': 0.2799962684227441}.
