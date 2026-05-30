# P0031 launchd service

## Installed service

```text
label = se.mlovholm.smart-home.weather-history-daily
plist_path = /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
schedule = 15:30 local time daily
stdout = /Users/marcus.lovenstad/.smart-home/logs/weather-history-daily.out.log
stderr = /Users/marcus.lovenstad/.smart-home/logs/weather-history-daily.err.log
```

## Command

```text
/Library/Developer/CommandLineTools/usr/bin/python3 -m src.mac.services.weather_history ingest-daily --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
```

## Verification

`launchctl print gui/501/se.mlovholm.smart-home.weather-history-daily` returned:

```text
type = LaunchAgent
state = not running
path = /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
Hour = 15
Minute = 30
```

Manual ingest verification:

```text
status = no_new_complete_day_available
fetched_location_ranges = 0
observations_upserted = 0
area_rows_upserted = 0
validated tail date = 2026-05-24
```

## Rollback

Unload and remove the LaunchAgent:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
rm ~/Library/LaunchAgents/se.mlovholm.smart-home.weather-history-daily.plist
```

Preserve the local DB by default:

```text
~/.smart-home/data/weather_history.sqlite3
```

Optional manual DB removal if a later package decides to rebuild from scratch:

```bash
rm ~/.smart-home/data/weather_history.sqlite3
```
