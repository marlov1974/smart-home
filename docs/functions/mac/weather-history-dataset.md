# Weather History Dataset

Last changed: P0033

## Module

```text
src.mac.services.weather_history
```

## Purpose

Mac-only historical weather data service for future spotprice V2 feature-store and weather-normalization packages.

Canonical mutable local DB:

```text
~/.smart-home/data/weather_history.sqlite3
```

The repo commits code, tests and docs, not the generated full SQLite DB.

## Source

Open-Meteo Historical Weather API:

```text
https://archive-api.open-meteo.com/v1/archive
```

Model:

```text
era5_seamless
```

Hourly variables:

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
```

Requests use `timezone=GMT`; the service derives Europe/Stockholm local date/hour metadata from UTC timestamps.

## SE3 Proxy Locations

```text
stockholm  59.3293  18.0686  0.35
goteborg   57.7089  11.9746  0.25
orebro     59.2753  15.2134  0.20
linkoping  58.4108  15.6214  0.20
```

## CLI

```bash
python3 -m src.mac.services.weather_history init-db --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history backfill --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.weather_history validate --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.weather_history ingest-daily --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history install-daily-job --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history compute-proxy-groups --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.weather_history validate-proxy-groups --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
```

## Important Functions

`default_db_path()` returns the canonical weather SQLite path.

`initialize_schema(path)` creates schema and default SE3 proxy locations.

`configured_locations(conn, area_proxy)` returns active weather locations and weights.

`expected_utc_hours_for_local_date(local_date)` returns the expected Europe/Stockholm local-day UTC hours, including DST 23/25-hour days.

`fetch_open_meteo_range(location, start_utc_date, end_utc_date, timeout)` fetches one read-only Open-Meteo range.

`parse_open_meteo_response(payload, location, expected_hours)` validates required hourly arrays and produces normalized observations.

`upsert_weather_observations(conn, observations, ingest_run_id)` idempotently stores location-hour rows.

`compute_area_proxy_hourly(conn, area_proxy, start_date, end_date, ingest_run_id)` writes weighted SE3 hourly rows.

`latest_safe_complete_day(today)` returns `today - 6 days`, matching observed ERA5-Seamless publication delay.

`backfill(conn, start_date, end_date, db_path, fetcher, run_type)` fetches, stores, computes SE3 proxy rows and validates an inclusive range.

`ingest_daily(conn, db_path, today, fetcher)` ingests missing days through the latest safe complete day, or exits cleanly with `no_new_complete_day_available`.

`validate_weather_continuity(conn, start_date, end_date, area_proxy, db_path)` reports row counts, gaps, duplicates, null counts, yearly counts and variable stats.

`render_launchd_plist(db_path, python_executable)` renders the user LaunchAgent.

`install_launchd_plist(db_path, plist_path, python_executable, run_launchctl)` writes and loads the LaunchAgent.

## P0032 Proxy Groups

P0032 adds these queryable proxy groups in `weather_area_hourly` plus stable views:

```text
se1_core_weather                 weather_proxy_se1_core_hourly
nordic_connected_weather         weather_proxy_nordic_connected_hourly
south_connected_weather          weather_proxy_south_connected_hourly
se3_load_weather                 weather_proxy_se3_load_hourly
```

P0032 also adds `weather_proxy_gradients_hourly` with:

```text
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
wind_100m_gradient_nordic_connected_minus_se3_load
south_temp_gradient_minus_se1_core
```

## P0033 Consumer

`src.mac.services.spotprice_temperature_normalization` reads the P0032 proxy groups and gradients to create local normal climate, anomaly and conservative temperature-normalization feature rows. P0033 uses the SE1 climate weighting:

```text
0.70 * se1_core_weather
0.25 * nordic_connected_weather
0.05 * south_connected_weather
```

P0033 uses temperature, apparent temperature and heating/cooling degree signals. Wind, cloud, radiation and precipitation normalization are deferred.

## LaunchAgent

Label:

```text
se.mlovholm.smart-home.weather-history-daily
```

Plist:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

Schedule:

```text
15:30 local time daily
```

Logs:

```text
~/.smart-home/logs/weather-history-daily.out.log
~/.smart-home/logs/weather-history-daily.err.log
```

Rollback:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
rm ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

The DB is preserved by default. Remove it manually only if the operator intends to rebuild:

```bash
rm ~/.smart-home/data/weather_history.sqlite3
```

## Safety

This module performs read-only HTTP and local SQLite writes only. It does not call Shelly, Home Assistant, KVS writes, scripts or actuators.
