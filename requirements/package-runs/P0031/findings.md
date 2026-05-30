# P0031 findings

## Result

PASS

P0031 implemented a Mac-side Open-Meteo weather history dataset and daily ingest service.

## Database

```text
path = /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
size = 49696768 bytes
```

## Dataset

```text
source = Open-Meteo Historical Weather API
source_model = era5_seamless
area_proxy = SE3
start_date = 2022-05-30
end_date = 2026-05-24
first_utc_hour_start = 2022-05-29T22:00Z
last_utc_hour_start = 2026-05-24T21:00Z
location_row_count = 139776
area_row_count = 34944
complete = true
gaps = 0
duplicates = 0
nulls = 0
```

`2026-05-24` is the latest safely available complete ERA5-Seamless day observed on 2026-05-30. `2026-05-25` was partially null and `2026-05-29` was all null.

## Daily job

```text
label = se.mlovholm.smart-home.weather-history-daily
plist = /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
schedule = 15:30 local time daily
status = loaded
```

Manual daily ingest returned `no_new_complete_day_available` because the DB is current through the safe day.

## Live actions

No Shelly, Home Assistant, KVS, Script, Switch, Light, Cover, relay, dimmer or actuator actions were performed.

Local Mac writes performed by package scope:

- created/updated `/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3`
- created `/Users/marcus.lovenstad/.smart-home/logs/`
- wrote `/Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist`
- loaded the user LaunchAgent with launchctl

## Uncertainty

The launchd job is loaded and scheduled but has not naturally fired at 15:30 after installation. Manual `ingest-daily` verified the command path and no-op behavior.

No ML, climatology normals or weather-normalized price prediction were implemented.
