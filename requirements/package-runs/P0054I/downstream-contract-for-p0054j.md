# P0054I Downstream Contract For P0054J

Recommended package:

```text
P0054J LABB SE1 consumption price forecast ablation train-through-May-2025
```

Split policy:

```text
LABB_P0054_TRAIN_THROUGH_MAY_2025
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z and target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Price forecast source:

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

Required label:

```text
This is not M4. It is a forecast-safe origin-local historical price baseline.
```

Model comparison:

```text
no_price
vs
with_p0054h_price_forecast
```

Suggested model families:

```text
HGB, ExtraTrees, LightGBM, XGBoost, MLP if practical
```

Holdout must not be used for fitting, selection, early stopping or normalization.
