# P0049 dataset contract

source_table = `se3_se1_bottleneck_training_dataset_v1`
derived_table = `se3_se1_bottleneck_reservoir_analysis_v1`
row_counts = {'source_rows': 34968, 'persisted_rows': 34968}
split_counts = {'holdout': 3480, 'train': 22728, 'validate': 8760}
contract = {'ok': True, 'missing_fields': [], 'spread_reconstruction_errors': 0, 'split_check': {'ok': True, 'errors': 0, 'split_ranges': {'train': {'first': '2022-05-29T23:00:00+00:00', 'last': '2024-12-31T22:00:00+00:00'}, 'validate': {'first': '2024-12-31T23:00:00+00:00', 'last': '2025-12-31T22:00:00+00:00'}, 'holdout': {'first': '2025-12-31T23:00:00+00:00', 'last': '2026-05-25T22:00:00+00:00'}}}, 'source_table': 'se3_se1_bottleneck_training_dataset_v1'}

All horizon and rolling features use fixed-CET rows ordered by `timestamp_utc`.
