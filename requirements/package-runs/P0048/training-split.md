# P0048 training split

train: earliest available .. 2024-12-31
validate: 2025-01-01 .. 2025-12-31
holdout: 2026-01-01 .. latest complete timestamp

split_counts = {'holdout': 3480, 'train': 22728, 'validate': 8760}

No random shuffle is used as primary evaluation.
