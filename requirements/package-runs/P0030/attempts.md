# P0030 attempts

## Attempt 1

Implemented P0030 as a new Mac-only SQLite history service plus DB-backed spot forecast API.

Source diagnostics:

```text
curl https://se.elpris.eu/api/v1/prices/2026/05-29_SE3.json?avg24
result: compact 24-hour payload

curl https://se.elpris.eu/api/v1/prices/2022/05-30_SE3.json?avg24
result: HTTP 410

curl https://www.elprisetjustnu.se/api/v1/prices/2022/05-30_SE3.json
result: 24 hourly records

curl https://www.elprisetjustnu.se/api/v1/prices/2026/05-29_SE3.json
result: 96 quarter-hour records
```

Initial Python source fetch failed in the sandbox with DNS denial, then succeeded after command escalation but returned HTTP 403. Added a normal User-Agent to the read-only urllib request.

Short backfill verification:

```text
python3 -m src.mac.services.spotprice_history backfill --area SE3 --db /private/tmp/p0030-test.sqlite3 --start-date 2022-05-30 --end-date 2022-05-31
result: fetched_days=2, row_count=48, expected_count=48, gap_count=0, duplicate_count=0
```

Full backfill attempt initially stopped on a source read timeout. The implementation was updated so each day is committed independently, source fetches retry, and fetch errors include the target date.

Full backfill verification:

```text
python3 -m src.mac.services.spotprice_history backfill --area SE3 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-29
result:
  fetched_days = 1461
  row_count = 35064
  expected_count = 35064
  first_utc_hour_start = 2022-05-29T22:00Z
  last_utc_hour_start = 2026-05-29T21:00Z
  gap_count = 0
  duplicate_count = 0
  negative_price_count = 1504
  min_price_sek_per_kwh = -0.69112
  max_price_sek_per_kwh = 8.56048
  mean_price_sek_per_kwh = 0.7029750320841905
  per_year_counts = 2022:5185, 2023:8760, 2024:8784, 2025:8760, 2026:3575
```

Daily job install:

```text
python3 -m src.mac.services.spotprice_history install-daily-job --area SE3 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
result: loaded=true, label=se.mlovholm.smart-home.spotprice-history-daily
```

Launchd verification:

```text
launchctl print gui/501/se.mlovholm.smart-home.spotprice-history-daily
result:
  state = not running
  program = /Library/Developer/CommandLineTools/usr/bin/python3
  StartCalendarInterval Hour=14 Minute=0
  stdout path = /Users/marcus.lovenstad/.smart-home/logs/spotprice-history-daily.out.log
  stderr path = /Users/marcus.lovenstad/.smart-home/logs/spotprice-history-daily.err.log
```

Daily no-op verification:

```text
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
result: fetched_days=0, upserted_rows=0, validation ok for 2026-05-29
```

Spot forecast CLI verification:

```text
python3 -m src.mac.services.spot_forecast --once --week 2 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
result: [0.72,1.29,1.1,0.66,1.27,1.09,0.7,1.24,1.03,0.61,1.36,1.33,0.81,1.34,1.18,0.63,1.0,1.03,0.68,0.89,1.05]
```

HTTP verification:

```text
GET /spot/period-index?week=2
result: compact 21-number array

GET /spot/period-index/meta?week=2
result: source=sqlite, start_date=2022-05-30, end_date=2026-05-29, row_count=35064, expected_count=35064, gap_count=0
```

The HTTP server needed command escalation for local socket bind. The verification server was stopped with:

```text
pkill -f src.mac.services.spot_forecast
```
