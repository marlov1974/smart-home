# P0054F Feature Groups

## Status

No P0054F feature groups were materialized.

## Intended Groups

```text
no_price = calendar + historical SE1 load lags/rollups + SE1 weather proxy/normals
with_se1_price_forecast = no_price + G7 price forecast path features
```

## Blocked G7 Features

The following features are ready in concept from P0053C-B G7 readiness, but were not created because the source lacks train coverage:

```text
forecast_se1_price_target_hour
forecast_se1_price_relative_to_forecast_24h_mean
forecast_se1_price_relative_to_forecast_168h_mean
forecast_se1_price_rank_in_forecast_day
forecast_se1_price_rank_in_168h
forecast_se1_price_top4_forecast_day_flag
forecast_se1_price_top8_forecast_day_flag
forecast_se1_price_bottom4_forecast_day_flag
forecast_se1_price_daily_spread_forecast
forecast_se1_price_volatility_next_24h_forecast
```

Creating these only for validation/holdout would not permit model training under the required split.
