# P0043 training split

train: earliest..2024-12-31
validate: 2025-01-01..2025-12-31
holdout: 2026-01-01..latest complete fixed-CET model day

split_counts = {'holdout': 6960, 'train': 45456, 'validate': 17520}
No shuffle is used.
