# P0048 dataset contract

local_table = `se3_se1_bottleneck_training_dataset_v1`

row_counts = {'modeling_rows': 34968, 'source_rows': 69936}

split_counts = {'holdout': 3480, 'train': 22728, 'validate': 8760}

window = {'start': '2022-05-30', 'end': '2026-05-25', 'latest_timestamp_utc': '2026-05-25T22:00:00+00:00'}

`se3_minus_se1 = se3_price - se1_price` is reconstructed from corrected P0042 AI2 v2 rows. `timestamp_utc` remains primary identity and fixed-CET fields remain model calendar fields.
