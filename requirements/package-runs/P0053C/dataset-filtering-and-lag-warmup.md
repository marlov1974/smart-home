# P0053C Dataset Filtering And Lag Warmup

## Rule

Training/evaluation target rows must satisfy:

```text
target_timestamp_utc >= 2022-06-01T00:00:00Z
```

Pre-start rows may be read only as lag/rolling context.

## P0053B Rebuild Evidence

SQLite validation after rebuild:

```text
train    count=247477 min_target=2022-06-06T00:00:00Z max_target=2024-12-31T23:00:00Z
validate count=39864  min_target=2025-01-01T00:00:00Z max_target=2025-05-31T23:00:00Z
holdout  count=94765  min_target=2025-06-01T00:00:00Z max_target=2026-05-25T22:00:00Z
pre_start_target_rows=0
```

The first train target starts after the policy start because direct-horizon rows require origin-side lag/rolling context. This is expected and respects the context-only warmup rule.
