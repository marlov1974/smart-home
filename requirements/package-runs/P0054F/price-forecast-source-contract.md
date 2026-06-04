# P0054F Price Forecast Source Contract

## Candidate Source

```text
source package = P0053C-B
source table = m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
area = SE1
prediction_kind = anchored_absolute_price
prediction_unit = source_hour_price_unit
rows = 82656
distinct forecast origins = 492
```

## Forecast-Origin Semantics

From P0053C-B:

```text
forecast_origin_timestamp_utc = first target timestamp in each 168h rolling path
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
target_window = [forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]
anchor_history_window = [forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)
```

P0053C-B leakage review reports:

```text
anchor_price_timestamps_strictly_before_origin = true
no_target_window_actual_price_used_for_anchor = true
input_cutoff_not_after_origin = true
forecast_origin_not_after_target = true
holdout_used_for_selection = false
```

## Coverage

By target timestamp:

| split | rows | origins | target range |
|---|---:|---:|---|
| train | 0 | 0 | none |
| validation | 24192 | 144 | 2025-01-01T23:00:00Z .. 2025-05-31T22:00:00Z |
| holdout | 58464 | 348 | 2025-06-01T23:00:00Z .. 2026-05-21T22:00:00Z |

By forecast origin:

| split | rows | origins | origin range |
|---|---:|---:|---|
| train | 0 | 0 | none |
| validation | 24192 | 144 | 2025-01-01T23:00:00Z .. 2025-05-24T23:00:00Z |
| holdout | 58464 | 348 | 2025-06-01T23:00:00Z .. 2026-05-14T23:00:00Z |

## Contract Decision

Forecast-origin semantics are acceptable, but training coverage is not.

P0054F cannot build a train/validation/holdout with-price SE1 consumption model from this source because train rows are absent.
