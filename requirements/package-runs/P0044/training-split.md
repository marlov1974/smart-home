# P0044 training split

train: earliest..2024-12-31
validate: 2025-01-01..2025-12-31
holdout: 2026-01-01..latest complete fixed-CET model day

split_counts = {'global': {'holdout': 282, 'train': 1890, 'validate': 730}, 'per_target_series': {'system_proxy_se1': {'holdout': 141, 'train': 945, 'validate': 365}, 'area_diff_proxy_se3': {'holdout': 141, 'train': 945, 'validate': 365}}, 'split_definition': {'train': 'earliest..2024-12-31', 'validate': '2025-01-01..2025-12-31', 'holdout': '2026-01-01..latest'}}

No shuffle is used. Baselines and HGB models are fit on train rows only.
