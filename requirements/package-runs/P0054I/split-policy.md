# P0054I LABB Split Policy

Policy name:

```text
LABB_P0054_TRAIN_THROUGH_MAY_2025
```

Timestamp interpretation:

```text
train_fit_start_utc = 2022-06-01T00:00:00Z
train_fit_end_utc   = 2025-06-01T00:00:00Z exclusive
holdout_start_utc   = 2025-06-01T00:00:00Z
holdout_end_utc     = latest_available_timestamp_utc
```

SQL-style rule:

```sql
CASE
  WHEN target_timestamp_utc >= '2022-06-01T00:00:00Z'
   AND target_timestamp_utc <  '2025-06-01T00:00:00Z'
  THEN 'train_fit'
  WHEN target_timestamp_utc >= '2025-06-01T00:00:00Z'
  THEN 'holdout'
END
```

There is no separate validation split for final reporting in this LABB comparison policy. If a model requires internal early stopping or hyperparameter selection, that split must be carved strictly from `train_fit` and must not use holdout.

## Scope

This policy applies to the P0054 experiment chain and follow-up packages that explicitly name it. It does not retroactively rewrite older package evidence and does not replace the global P0053C canonical split memory.
