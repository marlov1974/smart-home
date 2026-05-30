# P0032 launchd update

## Spotprice job

Existing label preserved:

```text
se.mlovholm.smart-home.spotprice-history-daily
```

P0032 updated the command to ingest both areas:

```text
python3 -m src.mac.services.spotprice_history ingest-daily --areas SE3,SE1 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
```

`launchctl print gui/501/se.mlovholm.smart-home.spotprice-history-daily` confirmed the loaded user LaunchAgent has `--areas SE3,SE1` and still runs at 14:00.

Manual daily ingest returned no-op validations for both SE3 and SE1 on `2026-05-29`.

## Weather job

Existing label preserved:

```text
se.mlovholm.smart-home.weather-history-daily
```

The command remains:

```text
python3 -m src.mac.services.weather_history ingest-daily --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
```

P0032 changed the service implementation so this command covers all active proxy groups and recomputes gradients.

`launchctl print gui/501/se.mlovholm.smart-home.weather-history-daily` confirmed the loaded user LaunchAgent still runs at 15:30.

Manual daily ingest returned `no_new_complete_day_available` with 38 configured locations and validated tail date `2026-05-24`.
