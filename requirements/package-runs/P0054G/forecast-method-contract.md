# P0054G Forecast Method Contract

## Existing P0053C-B Contract

```text
prediction_kind = anchored_absolute_price
area = SE1
prediction_unit = source_hour_price_unit
forecast_origin_timestamp_utc = first target timestamp in a 168h path
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
target_window = [forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]
anchor_history_window = [forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)
```

The selected P0053C-B anchor is:

```text
A1_median_iqr
```

It was selected using validation MAE, with holdout report-only.

## Safe Scope Of Existing Method

The existing P0053C-B method is safe for validation and holdout origins because the upstream P0045/P0053C AI1/AI2 shape model is trained under the canonical train split, which ends before validation and holdout origins.

## Unsafe Train Extension

For train-period origins, using the same globally trained shape model would mean early train-origin forecasts are produced by a model that already saw later train-period target rows.

That violates:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
no data after input_data_cutoff_utc for a given origin
```

## Safe Future Contract

A future implementation may generate train rows only if upstream shape predictions are produced using one of these forecast-origin-safe approaches:

- rolling-origin refit where model training rows end before each origin
- expanding-origin refit with the same cutoff rule
- blocked out-of-fold/cross-fitted train predictions where each fold's model is trained only on data before that fold's origins
- a deliberately simpler baseline that uses only pre-origin deterministic/calendar/history features and is labeled separately

The current package did not implement any of those protocols.
