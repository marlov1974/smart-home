# P0033 implementation design

## Input DBs and overlap

Input price DB:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
```

Input weather DB:

```text
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
```

The build joins P0032 price and weather contracts by `utc_hour_start`. Verified overlap is:

```text
2022-05-30..2026-05-24
34944 hourly rows
```

## Actual P0032 Level 1 weights

The local `weather_locations` rows are captured in `p0032-weather-location-weights.md`. P0033 does not recalculate location-level weather proxies from raw location observations; it consumes the P0032 `weather_area_hourly` proxy outputs and gradient table.

## Selected P0033 Level 2 weights

SE1 system climate signal:

```text
0.70 * se1_core_weather
0.25 * nordic_connected_weather
0.05 * south_connected_weather
```

Applied independently to:

- weighted temperature
- weighted apparent temperature
- heating degree hours
- cooling degree hours

Area-diff climate signal keeps P0032 gradients as separate signals:

- `temp_gradient_se3_load_minus_se1_core`
- `apparent_temp_gradient_se3_load_minus_se1_core`
- `heating_degree_gradient_se3_load_minus_se1_core`
- `south_temp_gradient_minus_se1_core`

Wind is not used by M3 in P0033. The existing P0032 wind gradient remains available for future packages.

## M1 calm normal price algorithm

M1 builds a weather-blind calendar baseline separately for:

- `system_proxy_se1`: actual SE1 system proxy price
- `area_diff_proxy_se3`: actual SE3 minus SE1 area-diff proxy

For every joined input hour, M1 computes a robust baseline from historical prices with:

- same local hour
- same weekday
- ISO week circular neighborhood of +/- 2 weeks
- median value
- all available years pooled in the bucket
- `bucket_year_count` stored only as diagnostics
- fallback to same local hour if the bucket is unexpectedly empty

Allowed M1 inputs are local calendar fields and target price history. M1 does not read weather, temperature, wind, cloud, precipitation, lagged price features or rolling current-event price features.

M1 does not condition on year. Year/regime is not a normal-price key in P0033, which avoids memorizing one year's price shocks.

## M2 climate normal algorithm

M2 creates normal climate and anomaly rows for all selected signals. For each signal and input hour:

- actual value is read from the selected P0032 proxy composition or gradient.
- normal value is the median for the same local hour and day-of-year circular neighborhood of +/- 7 days.
- all available years are pooled in the bucket.
- `bucket_year_count` is stored only as diagnostics.
- anomaly is `actual - normal`.

This captures broad climate seasonality while smoothing acute events.

M2 does not condition on year. Year is not a normal-climate key in P0033, which avoids memorizing one year's weather events.

## M3 statistical delta algorithm

M3 estimates conservative temperature deltas from M1 residuals:

```text
residual = actual_target - m1_normal_price
```

Targets:

- `system_proxy_se1`
- `area_diff_proxy_se3`

Primary anomaly feature:

- SE1: `se1_system_temperature_anomaly`
- area-diff: `temp_gradient_se3_load_minus_se1_core_anomaly`

Buckets:

- `extreme_cold`: anomaly <= -8
- `cold`: -8 < anomaly <= -3
- `normal`: -3 < anomaly < 3
- `warm`: 3 <= anomaly < 8
- `extreme_warm`: anomaly >= 8

Delta policy:

- median residual per bucket is compared with the `normal` bucket median.
- `normal` bucket delta is forced to `0.0`.
- non-normal buckets use `0.50 * (bucket_median - normal_median)`.
- absolute delta is capped at `0.50` SEK/kWh for SE1 and `0.35` SEK/kWh for area-diff.

This is deliberately conservative and statistical. It is not a full ML model.

## Storage schema and path

Generated feature DB:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

Required tables:

- `model_runs`
- `m1_normal_price_v1`
- `m2_climate_normals`
- `m2_climate_anomalies`
- `m2_climate_weights`
- `m3_temperature_delta_v1`
- `m3_temperature_delta_buckets`
- `m3_temp_normalized_prices_v1`
- `training_foundation_manifest`

## CLI commands

Build:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization build --price-db ~/.smart-home/data/spotprice_history.sqlite3 --weather-db ~/.smart-home/data/weather_history.sqlite3 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --start-date 2022-05-30
```

Validate:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization validate --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
```

Diagnostics:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization diagnostics --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
```

## Test strategy

Unit tests cover:

- P0032 weight extraction from SQLite.
- M1 weather-blind inputs and output formula.
- M2 normals/anomalies.
- Level 2 climate weight storage.
- M3 target residuals and dead-zone behavior.
- normalized series recomposition.
- schema initialization and validation summaries.

Local verification builds the real feature DB from local P0030/P0031/P0032 SQLite DBs and runs validation/diagnostics.

## Deferred work

M4/M5/M6/M7, full ML model training, forecast API, wind normalization, external ML dependencies and production deployment are deferred because P0033 is only the training-foundation package.

## Risks and uncertainties

The historical range has roughly four years of hourly data. Calendar medians are intentionally robust and conservative, but the foundation is not yet a forecast-quality model. P0033 stores diagnostics so later packages can evaluate whether M4 should use richer model classes.
