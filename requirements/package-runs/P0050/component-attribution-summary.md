# P0050 component attribution summary

Status: PASS
1. Input dataset/table used: `se3_se1_bottleneck_training_dataset_v1` with P0049 reservoir join from `se3_se1_bottleneck_reservoir_analysis_v1`.
2. Selected expected-spread baseline: `B2_smoothed_hour_daytype_dayofyear` because validation MAE was best or within the simpler-baseline tie tolerance.
3. Weekend/holiday effects are reported on raw and residual spread in `daytype-baseline-corrected-results.md`; residual lift is the only baseline-corrected conclusion.
4. Friday residual lift vs all: 0.001661; not treated as proven without sample/context review.
5. SE3 top4/top8 same-hour damping/rebound evidence is in `topN-response-and-rebound.csv`; top8 6h residual lift=-0.047458.
6. Bottom4 recovery after top8 6h residual lift=0.082056.
7. p70/p80/top8 features are included alongside top4/top2-style p90 diagnostics; the summary favors feature families by validation/holdout diagnostics, not assumptions.
8. Cheap recovery fields are split into backward-looking counters and explicitly `_oracle` next-window fields.
9. Heat debt pressure 24h correlation with future 6h residual=-0.025547.
10. Heat debt is compared against simple cold and price-rank groups in `exploratory-model-results.md`.
11. Weekday/weekend/holiday strength is summarized by residual lift; weekend residual lift vs all=-0.056817.
12. Best MAE groups by horizon: {'1h': 'G1_raw_spread_lagged', '6h': 'G1_raw_spread_lagged', '24h': 'G1_raw_spread_lagged', '48h': 'G1_raw_spread_lagged'}; best F1 groups by horizon: {'1h': 'G1_raw_spread_lagged', '6h': 'G1_raw_spread_lagged', '24h': 'G1_raw_spread_lagged', '48h': 'G2_local_se3_rank_topN'}.
13. Recommendation: P0051 should compare direct SE3 AI-1/AI-2 with a bottleneck/demand-response residual model, not deploy production yet.
14. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.
