# P0053B-A Feature Groups

## Status

`G7_forecast_price_signal` was not created.

## Reason

The G7 group requires forecast-safe old price forecasts. No qualifying historical SE1 price forecast source with forecast-origin timestamps was found.

## Candidate Features Not Created

```text
forecast_se1_price_target_hour
forecast_se1_price_horizon_h
forecast_se1_price_relative_to_forecast_24h_mean
forecast_se1_price_relative_to_forecast_168h_mean
forecast_se1_price_rank_in_forecast_day
forecast_se1_price_top4_forecast_day_flag
forecast_se1_price_top8_forecast_day_flag
forecast_se1_price_bottom4_forecast_day_flag
forecast_se1_price_daily_spread_forecast
forecast_se1_price_rolling_mean_next_24h_forecast
forecast_se1_price_rolling_max_next_24h_forecast
forecast_se1_price_volatility_next_24h_forecast
```

Creating any of these from actual spot prices would be leakage. Creating them from originless predictions would be non-forecast-safe.
