# P0032 attempts

## Attempt 1

Implemented SE1 system-proxy storage and P0032 weather proxy groups.

SE1 source checks:

```text
2022-05-30 SE1: source returned 24 hourly rows
2026-05-29 SE1: source returned 96 quarter-hour rows
```

SE1 backfill:

```text
python3 -m src.mac.services.spotprice_history backfill --area SE1 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-29
result: 35064 rows, 0 gaps
```

System proxy validation:

```text
python3 -m src.mac.services.spotprice_history validate-system-proxy --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-29
result: complete=true, aligned_count=35064
```

Weather proxy backfill first hit Open-Meteo HTTP 429 after partial progress. Added complete-location skip logic and resumed.

Weather proxy validation:

```text
python3 -m src.mac.services.weather_history validate-proxy-groups --db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-24
result: complete=true, gradient_row_count=34944, gradient_null_count=0
```
