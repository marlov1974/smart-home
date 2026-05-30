# P0031 design

## Package interpretation

P0031 creates a Mac-only historical weather dataset service and daily ingest job. It does not build ML, weather-normalized price prediction, optimizer policy, Home Assistant integration, Shelly runtime code or device control.

## Source

Use Open-Meteo Historical Weather API:

```text
https://archive-api.open-meteo.com/v1/archive
```

Request settings:

```text
models=era5_seamless
timezone=GMT
hourly=temperature_2m,apparent_temperature,wind_speed_10m,wind_speed_100m,wind_gusts_10m,cloud_cover,shortwave_radiation,precipitation,snowfall,relative_humidity_2m,pressure_msl
```

`timezone=GMT` makes source timestamps unambiguous. The service derives Europe/Stockholm `local_date`, `local_hour`, UTC offset and fold from UTC timestamps so rows can join to P0030 spotprice hours.

## Date interval

Backfill starts at:

```text
2022-05-30
```

At build time on 2026-05-30, latest safe complete day is:

```text
2026-05-24
```

Daily ingest uses:

```text
latest_safe_complete_day = local_today - 6 days
```

This matches observed Open-Meteo ERA5-Seamless source delay on 2026-05-30: `2026-05-25` was partially null while `2026-05-24` was complete.

## Locations and weights

```text
stockholm  59.3293  18.0686  0.35
goteborg   57.7089  11.9746  0.25
orebro     59.2753  15.2134  0.20
linkoping  58.4108  15.6214  0.20
```

Weights sum to 1.0 and produce the `SE3` area proxy. The schema stores locations and weights so a future package can revise them with a forward migration.

## SQLite DB

Canonical path:

```text
~/.smart-home/data/weather_history.sqlite3
```

Tables:

- `weather_locations`
- `weather_observations`
- `weather_area_hourly`
- `weather_ingest_runs`
- `schema_meta`

`weather_observations` is wide, one row per location and UTC hour. `weather_area_hourly` is wide, one weighted `SE3` row per UTC hour.

No raw HTTP payloads are stored.

## Commands

```text
python3 -m src.mac.services.weather_history init-db --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history backfill --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.weather_history validate --db ~/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.weather_history ingest-daily --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history install-daily-job --db ~/.smart-home/data/weather_history.sqlite3
```

## Validation

Validation reports:

- first/last UTC timestamp
- row counts and expected counts
- per-year counts
- duplicate counts
- gap counts
- null counts per variable
- min/max/mean per variable
- DB file size
- completeness flag

Completeness is true only if every expected hour exists for all active locations and the `SE3` proxy, and required variables are non-null.

## Launchd

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

Reason: Open-Meteo ERA5-Seamless can lag and partially publish recent days. The job ingests `today - 6 days`, so 15:30 is a low-conflict daily local maintenance time, not an assumption that yesterday is complete.

Logs:

```text
~/.smart-home/logs/weather-history-daily.out.log
~/.smart-home/logs/weather-history-daily.err.log
```

Rollback:

```text
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
rm ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

The DB is preserved by default. Removing it is a manual operator decision:

```text
rm ~/.smart-home/data/weather_history.sqlite3
```

## Future consumption

Future P0032/P0033 feature-store/model packages should join weather to P0030 spot prices by `utc_hour_start`. P0031 prepares deterministic columns only; no ML, climatology normals or anomaly training are implemented.
