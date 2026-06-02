# P0048 component attribution summary

Status: PASS
1. Built `se3_se1_bottleneck_training_dataset_v1` with 34968 rows and splits {'holdout': 3480, 'train': 22728, 'validate': 8760}.
2. Regime thresholds used: {'near_zero_abs': 0.05, 'positive': 0.201919, 'negative': -0.201919, 'spike_positive': 0.807675, 'spike_negative': -0.807675}.
3. Gradient features created: 10; missing requested features: [].
4. Stage-1 gradient F1 delta over system weather: -0.012512.
5. Stage-1 lagged diagnostic F1 delta over gradients: 0.606417.
6. Stage-2 and continuous baseline metrics are reported in dedicated evidence files.
7. Recommendation: P0049 should compare direct SE3 AI-1/AI-2 against the best bottleneck path.
8. Confirmed: no SE1-to-SE3 anchoring, no API, no production model, no M5/M6/M7 and no device actions.
