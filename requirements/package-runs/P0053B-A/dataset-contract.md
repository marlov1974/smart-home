# P0053B-A Dataset Contract

## Status

No P0053B-A modeling dataset was created.

## Reason

The required price forecast source contract cannot be satisfied because no historical SE1 price forecast source with forecast-origin timestamps was found.

## Existing Input

P0053B created `se1_consumption_forecast_warmup_v1`, which includes consumption forecast examples with:

```text
origin_timestamp_utc
target_timestamp_utc
horizon_h
```

This is sufficient for consumption target modeling, but it does not include a forecast-safe price signal.

## Required Join Contract If Unblocked

A future source must support a join that enforces:

```text
price_forecast.area = 'SE1'
price_forecast.target_timestamp_utc = example.target_timestamp_utc
price_forecast.forecast_origin_timestamp_utc <= example.origin_timestamp_utc
```

When multiple forecasts qualify, the selected forecast must be the latest available forecast at or before the example origin.
