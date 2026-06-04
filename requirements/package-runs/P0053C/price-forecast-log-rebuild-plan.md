# P0053C Price Forecast Log Rebuild Plan

P0053C does not reuse old M1/M4 prediction artifacts as consumption features because they lack forecast-origin provenance.

## Required Synthetic Historical Price Forecast Log

Minimum schema:

```text
forecast_run_id
model_name
model_version
train_start_utc
train_end_utc
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hours
area
predicted_price_or_index
prediction_unit
created_at_utc
split_policy_version
```

## Safe First Rebuild

For a first diagnostic log:

```text
train price model only on 2022-06-01T00:00:00Z .. 2025-05-31T23:00:00Z
create predictions for 2025-06-01T00:00:00Z .. latest
store every prediction with forecast_origin and target timestamps
```

## Better Later Rebuild

Use rolling or weekly forecast origins. Each origin must apply or train only with data available before that origin.

## Recommendation

Run P0053C-A next to rebuild M4/price-shape artifacts under the global period policy and produce a forecast-origin-safe log for later consumption price-response testing.
