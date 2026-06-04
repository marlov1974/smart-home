# P0054H Coverage For P0054I Split

Source table:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
```

Required filters:

```text
area = SE1
prediction_kind = anchored_absolute_price
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

## By Target Timestamp

| split | rows | origins | min target timestamp | max target timestamp |
|---|---:|---:|---|---|
| train_fit | 181776 | 1082 | 2022-06-01T23:00:00Z | 2025-05-31T22:00:00Z |
| holdout | 59136 | 352 | 2025-06-01T23:00:00Z | 2026-05-25T22:00:00Z |

## By Forecast Origin

| split | rows | origins | min forecast origin | max forecast origin |
|---|---:|---:|---|---|
| train_fit | 181776 | 1082 | 2022-06-01T23:00:00Z | 2025-05-24T23:00:00Z |
| holdout | 59136 | 352 | 2025-06-01T23:00:00Z | 2026-05-18T23:00:00Z |

## Decision

Coverage is sufficient for P0054J.

Warmup/hour-boundary caveat: the first covered target hour is `2022-06-01T23:00:00Z`, not `2022-06-01T00:00:00Z`. This follows from the available complete 168h forecast-origin paths and is acceptable for downstream modeling when documented.

P0054H leakage review is acceptable: no cutoff/origin/history/training/source timestamp violations, no target-window actual price as input and no holdout fitting/selection.
