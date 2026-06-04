# P0053C Global Period Policy

Canonical forecast modeling period:

```text
forecast_modeling_start_utc = 2022-06-01T00:00:00Z
forecast_modeling_end_utc = latest_available_timestamp_utc
```

Canonical split:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

Boundary membership is based on `timestamp_utc`.

Fixed-CET fields remain feature/calendar fields:

```text
model_cet_timestamp = timestamp_utc + 1h all year
```

Rows before `2022-06-01T00:00:00Z` may be used only as context-only lag warmup for target rows at or after the modeling start. They must not be trained, validated, held out, scored or used as targets.

Reusable implementation:

```text
src/mac/services/spotprice_model_diagnostics/forecast_period_policy.py
```

Durable memory:

```text
memory/spotprice-forecast-period-policy.md
```
