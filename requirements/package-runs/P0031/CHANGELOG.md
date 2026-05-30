# P0031 changelog

## Added

- Added `src.mac.services.weather_history`.
- Added Open-Meteo ERA5-Seamless source client for required weather variables.
- Added local SQLite schema for weather locations, location observations, weighted SE3 hourly proxy rows and ingest runs.
- Added default four-location weighted SE3 proxy.
- Added backfill, validate, ingest-daily and install-daily-job CLI commands.
- Added user LaunchAgent `se.mlovholm.smart-home.weather-history-daily`.
- Added tests under `tests/mac/services/weather_history`.
- Added `docs/functions/mac/weather-history-dataset.md`.
- Added P0031 package-run review, design, functions, attempts, dataset manifest and launchd evidence.

## Local artifacts

```text
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
/Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
/Users/marcus.lovenstad/.smart-home/logs/weather-history-daily.out.log
/Users/marcus.lovenstad/.smart-home/logs/weather-history-daily.err.log
```

## Verified state

```text
coverage = 2022-05-30..2026-05-24
location_row_count = 139776
area_row_count = 34944
complete = true
gaps = 0
nulls = 0
launchd = loaded
```
