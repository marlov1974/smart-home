# P0054H Downstream Contract For P0054F/P0054I Retry

Use table:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
```

Join keys:

```text
forecast_origin_timestamp_utc
target_timestamp_utc
```

Primary feature:

```text
predicted_price
```

Required filters:

```text
area = SE1
prediction_kind = anchored_absolute_price
quality_flag = forecast_safe_origin_local_baseline_not_m4
training_protocol = origin_local_no_fit_pre_origin_history
```

Important label:

```text
This is not M4. It is a forecast-safe origin-local historical price baseline.
```
