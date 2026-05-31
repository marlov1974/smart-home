# P0033 consistency review

Result: PASS

## Package interpretation

P0033 builds the first temperature-normalized spotprice V2 training foundation. Scope is limited to M1, M2 and M3:

- M1: calm, weather-blind normal spotprice baseline for `system_proxy_se1` and `area_diff_proxy_se3`.
- M2: normal climate and anomaly series from P0032 weather proxy groups and gradients.
- M3: conservative statistical temperature delta model from M1 residuals and M2 anomalies.

Explicitly out of scope: M4/M5/M6/M7, full ML, forecast APIs, wind normalization, solar/cloud/radiation normalization, Home Assistant, Shelly, KVS writes, actuators and deployment.

## Local input evidence

Spotprice DB:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
SE1: 2022-05-30..2026-05-29, 35064 rows
SE3: 2022-05-30..2026-05-29, 35064 rows
spotprice_system_proxy_hourly: 2022-05-30..2026-05-29, 35064 rows
```

Weather DB:

```text
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
nordic_connected_weather: 2022-05-30..2026-05-24, 34944 rows
se1_core_weather: 2022-05-30..2026-05-24, 34944 rows
se3_load_weather: 2022-05-30..2026-05-24, 34944 rows
south_connected_weather: 2022-05-30..2026-05-24, 34944 rows
se3_area_diff_weather gradients: 2022-05-30..2026-05-24, 34944 rows
```

Joined overlap:

```text
2022-05-30..2026-05-24
34944 joined hourly rows
```

## Required P0032 contracts

Available:

- `spotprice_system_proxy_hourly`
- `weather_proxy_se1_core_hourly`
- `weather_proxy_nordic_connected_hourly`
- `weather_proxy_south_connected_hourly`
- `weather_proxy_se3_load_hourly`
- `weather_proxy_gradients_hourly`

P0032 actual location weights were read from local SQLite and captured in `p0032-weather-location-weights.md`.

## Safety review

No device access is required. Implementation can be completed with local SQLite reads and a generated local feature DB write only:

```text
~/.smart-home/data/spotprice_model_features.sqlite3
```

No network, no Shelly, no Home Assistant, no KVS, no scripts and no actuator calls are required.

## Decision

PASS. P0033 is consistent with repository state and local data. Continue with design, function design, implementation, local feature DB build, tests, validation, evidence, commit and push.
