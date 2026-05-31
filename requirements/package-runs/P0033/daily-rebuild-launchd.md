# P0033 daily rebuild LaunchAgent

## Purpose

Rebuild the P0033 temperature-normalized feature DB daily after the existing input ingests:

```text
14:00 P0030 spotprice-history daily ingest
15:30 P0031/P0032 weather-history daily ingest
16:00 P0033 spotprice-temperature-normalization daily rebuild
```

## Installed LaunchAgent

```text
label = se.mlovholm.smart-home.spotprice-temperature-normalization-daily
plist = /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-temperature-normalization-daily.plist
loaded = true
state = not running
```

Schedule:

```text
Hour = 16
Minute = 0
```

Program arguments:

```text
/Library/Developer/CommandLineTools/usr/bin/python3
-m
src.mac.services.spotprice_temperature_normalization
build
--price-db
/Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
--weather-db
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
--feature-db
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
--start-date
2022-05-30
```

Logs:

```text
/Users/marcus.lovenstad/.smart-home/logs/spotprice-temperature-normalization-daily.out.log
/Users/marcus.lovenstad/.smart-home/logs/spotprice-temperature-normalization-daily.err.log
```

## Step ordering control

The daily job runs one synchronous `build` process.

Inside `build_training_foundation(...)`:

```text
1. load joined P0030/P0031/P0032 input rows
2. compute M1 normal prices
3. compute M2 climate normals
4. compute M2 climate anomalies
5. compute M3 statistical temperature deltas
6. write normalized training series and manifest
```

M3 is not called until M1 and M2 computations have returned successfully. If M1 or M2 raises an error, the process exits non-zero and launchd records the failure in the error log.

## Verification

Commands run:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization install-daily-job --price-db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3 --weather-db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3 --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
plutil -p /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-temperature-normalization-daily.plist
launchctl print gui/501/se.mlovholm.smart-home.spotprice-temperature-normalization-daily
python3 -m src.mac.services.spotprice_temperature_normalization validate --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

Result:

```text
install-daily-job loaded = true
launchctl state = not running
validate ok = true
```
