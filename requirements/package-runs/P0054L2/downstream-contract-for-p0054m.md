# P0054L2 Downstream Contract For P0054M

A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption training. P0054M must use holdout-only evaluation or create rolling/out-of-fold train forecasts if it needs train_fit consumption features.

Decision: `advanced_holdout_source_recommended`.
