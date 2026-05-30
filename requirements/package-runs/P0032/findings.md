# P0032 findings

## Result

PASS

P0032 added SE1 system-proxy price history, SE3-SE1 derived proxy view, weather proxy groups and weather gradient features. No ML, optimizer, Home Assistant, Shelly, KVS, MCP or device actions were performed.

## Local databases

```text
spotprice_db = /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
weather_db = /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
```

## Key results

```text
SE1 rows = 35064 / 35064
SE1 gaps = 0
SE3/SE1 aligned rows = 35064 / 35064
area_ratio_null_count = 191

weather proxy groups = complete
weather gradient rows = 34944 / 34944
weather gradient nulls = 0
weather DB size = 476868608 bytes
```

## Launchd

Spotprice daily job now uses:

```text
--areas SE3,SE1
```

Weather daily job remains loaded and uses implementation-level active proxy groups.

## Uncertainty

The launchd jobs were verified loaded and manual ingest commands were run. They have not naturally fired after the P0032 update.
