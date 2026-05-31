# Spotprice Temperature Normalization

Last changed: P0035

## Module

```text
src.mac.services.spotprice_temperature_normalization
```

## Purpose

Mac-only local feature-store builder for the spotprice V2 temperature-normalized training foundation.

Generated mutable local DB:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

The repo commits code, tests and docs, not the generated feature DB.

## Inputs

Price input:

```text
~/.smart-home/data/spotprice_history.sqlite3
spotprice_system_proxy_hourly
```

Weather input:

```text
~/.smart-home/data/weather_history.sqlite3
weather_proxy_se1_core_hourly
weather_proxy_nordic_connected_hourly
weather_proxy_south_connected_hourly
weather_proxy_se3_load_hourly
weather_proxy_gradients_hourly
```

## CLI

```bash
python3 -m src.mac.services.spotprice_temperature_normalization build --price-db ~/.smart-home/data/spotprice_history.sqlite3 --weather-db ~/.smart-home/data/weather_history.sqlite3 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.spotprice_temperature_normalization validate --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
python3 -m src.mac.services.spotprice_temperature_normalization diagnostics --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
python3 -m src.mac.services.spotprice_temperature_normalization dump-weights --weather-db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.spotprice_temperature_normalization install-daily-job --price-db ~/.smart-home/data/spotprice_history.sqlite3 --weather-db ~/.smart-home/data/weather_history.sqlite3 --feature-db ~/.smart-home/data/spotprice_model_features.sqlite3
```

## Feature DB Tables

```text
model_runs
m1_normal_price_v1
m2_climate_normals
m2_climate_anomalies
m2_climate_weights
m3a_temperature_delta
m3a_temperature_delta_buckets
m3_temperature_delta_v1
m3_temperature_delta_buckets
m3b_special_day_delta
m3b_special_day_delta_buckets
m3ab_normalized_prices
calendar_special_days
m3_temp_normalized_prices_v1
training_foundation_manifest
```

## Model Stages

M1 creates a calm weather-blind normal price baseline for:

```text
system_proxy_se1
area_diff_proxy_se3
```

M1 uses local calendar structure and broad robust medians only. It does not use weather, forecast, wind, cloud, precipitation, lags or rolling current-event price features.

M1 bucket definition:

```text
target + local_hour + weekday + ISO week distance <= 2
```

The normal value is the median over all available years in that bucket. Year is not part of the model key. `bucket_year_count` is stored only as diagnostic coverage.

M2 creates normal climate and anomaly rows for:

```text
se1_system_temperature
se1_system_apparent_temperature
se1_system_heating_degree
se1_system_cooling_degree
se3_load_temperature
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
south_temp_gradient_minus_se1_core
```

SE1 system climate signals use:

```text
0.70 * se1_core_weather
0.25 * nordic_connected_weather
0.05 * south_connected_weather
```

M2 P0035 smooth cyclic normal:

```text
normal = 0.70 * median(signal + local_hour + day-of-year distance <= 7)
       + 0.30 * mean(signal + local_hour + day-of-year distance <= 21)
```

Year is not part of the model key. `bucket_year_count` is stored only as diagnostic coverage.

M3A primary temperature anomaly signals:

```text
system_proxy_se1      -> se1_system_temperature
area_diff_proxy_se3   -> temp_gradient_se3_load_minus_se1_core
```

`se3_load_temperature` remains an M2 normal/anomaly signal for local context. M3 uses the gradient for `area_diff_proxy_se3` because the price target is the SE3-SE1 spread.

M3A creates conservative bucketed temperature deltas from M1 residuals. Compatibility tables with old M3 names remain populated. It writes:

```text
temp_delta_v1_se1
temp_delta_v1_area_diff
temp_normalized_price_v1_se1
temp_normalized_area_diff_v1
temp_normalized_price_v1_se3
```

M3B uses the committed Swedish special-day calendar to estimate conservative holiday/bridge-day deltas from residuals after M1 and M3A. It writes:

```text
m3b_special_day_delta_se1
m3b_special_day_delta_area_diff
m3ab_normalized_price_se1
m3ab_normalized_area_diff
m3ab_normalized_se3
```

SE3 remains recomposed as:

```text
temp_normalized_price_v1_se3 = temp_normalized_price_v1_se1 + temp_normalized_area_diff_v1
```

## Important Functions

`default_feature_db_path()` returns the generated local feature DB path.

`open_feature_database(path)` opens the local SQLite feature DB with row factory and foreign keys enabled.

`initialize_schema(conn)` creates P0033 feature tables.

`dump_p0032_location_weights(weather_db)` reads actual P0032 proxy location weights from `weather_locations`.

`load_price_targets(conn, price_db, weather_db, start_date, end_date)` loads joined P0032 price targets and weather overlap rows.

`load_weather_proxy_features(conn, price_db, weather_db, start_date, end_date)` returns the same joined P0032 weather feature rows for callers that want weather-focused semantics.

`select_m2_target_weights()` returns P0033 Level 2 climate weights.

`compute_m1_calm_normal_price(rows)` builds weather-blind robust calendar baseline rows.

`compute_m2_climate_normals(rows)` computes P0035 smooth cyclic normal climate rows.

`compute_m2_climate_anomalies(rows, normals)` computes `actual - normal` anomaly rows.

`compute_m3_statistical_temperature_delta(rows, m1_rows, anomaly_rows)` computes conservative bucketed deltas.

`compute_m3a_statistical_temperature_delta(rows, m1_rows, anomaly_rows)` is the P0035 name for the temperature-delta model.

`compute_m3b_special_day_delta(rows, m1_rows, m3a_rows, calendar_rows)` computes conservative special-day deltas.

`build_m3ab_normalized_training_series(...)` creates the M3A+M3B normalized series for residual M4.

`build_temp_normalized_training_series(rows, m1_rows, delta_rows)` creates normalized SE1, area-diff and recomposed SE3 rows.

`build_training_foundation(...)` orchestrates the full local feature DB build.

Build sequencing is synchronous in one process: M1 normal prices are computed first, M2 normals/anomalies second, and M3 temperature deltas only after M1/M2 have returned successfully. A failure before M3 exits the build and leaves the daily LaunchAgent run failed in its error log.

`validate_training_foundation(conn)` validates required table presence, row counts and date coverage.

`summarize_temperature_normalization(conn)` reports residual, anomaly, delta and before/after temperature-association diagnostics.

## Safety

This module reads local SQLite source DBs and writes one generated local SQLite feature DB. It does not call Shelly, Home Assistant, KVS writes, scripts, actuators, forecast APIs or external ML dependencies.

P0033 does not implement M4/M5/M6/M7 and does not expose a production forecast service.

## Daily LaunchAgent

Label:

```text
se.mlovholm.smart-home.spotprice-temperature-normalization-daily
```

Plist:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-temperature-normalization-daily.plist
```

Schedule:

```text
16:00 local time daily
```

Logs:

```text
~/.smart-home/logs/spotprice-temperature-normalization-daily.out.log
~/.smart-home/logs/spotprice-temperature-normalization-daily.err.log
```
