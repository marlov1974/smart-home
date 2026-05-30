# P0031 attempts

## Attempt 1

Implemented `src.mac.services.weather_history` with:

- Open-Meteo Historical Weather API source client.
- SQLite schema for locations, observations, weighted area proxy rows and ingest runs.
- Four-location weighted SE3 proxy.
- Validation for expected hours, gaps, duplicates, null counts, yearly counts and variable stats.
- Daily ingest with `today - 6 days` safe-complete-day rule.
- User LaunchAgent renderer/installer.

Read-only Open-Meteo checks showed:

```text
2026-05-20: complete values
2026-05-29: all null values
2026-05-25: partial values, then nulls
2026-05-24: complete values
```

Short live backfill:

```text
python3 -m src.mac.services.weather_history backfill --db /private/tmp/p0031-weather-test.sqlite3 --start-date 2026-05-24 --end-date 2026-05-24
result: complete=true, location_row_count=96, area_row_count=24, gaps=0, nulls=0
```

Full live backfill:

```text
python3 -m src.mac.services.weather_history backfill --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-24
result: complete=true, location_row_count=139776, area_row_count=34944, gaps=0, nulls=0
```

Install service:

```text
python3 -m src.mac.services.weather_history install-daily-job --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
result: loaded=true
```

Daily ingest:

```text
python3 -m src.mac.services.weather_history ingest-daily --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
result: no_new_complete_day_available
```

Launchd:

```text
launchctl print gui/501/se.mlovholm.smart-home.weather-history-daily
result: loaded LaunchAgent, 15:30 calendar trigger
```
