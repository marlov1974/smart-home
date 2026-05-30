# P0030 findings

## Result

PASS

P0030 implemented a Mac-side historical SE3 spot price dataset foundation, stored in SQLite at:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
```

The existing `src.mac.services.spot_forecast` CLI and HTTP service now default to the P0030 SQLite DB through `--db`, fail clearly when the DB is missing or incomplete, and keep the compact `/spot/period-index?week=WW` array response.

The new metadata endpoint is:

```text
GET /spot/period-index/meta?week=WW
```

## Dataset evidence

Validated local DB:

```text
area = SE3
start_date = 2022-05-30
end_date = 2026-05-29
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
per_year_counts = {"2022":5185,"2023":8760,"2024":8784,"2025":8760,"2026":3575}
```

The 2024 count includes leap year hours. DST day shape is validated by expected Europe/Stockholm local day duration.

## Daily service

Installed and loaded user LaunchAgent:

```text
label = se.mlovholm.smart-home.spotprice-history-daily
plist = /Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
schedule = 14:00 local time daily
stdout = /Users/marcus.lovenstad/.smart-home/logs/spotprice-history-daily.out.log
stderr = /Users/marcus.lovenstad/.smart-home/logs/spotprice-history-daily.err.log
```

`launchctl print gui/501/se.mlovholm.smart-home.spotprice-history-daily` confirmed the job is loaded and not running, with the expected command and calendar trigger.

Manual `ingest-daily` after backfill was a successful no-op:

```text
fetched_days = 0
upserted_rows = 0
validated tail date = 2026-05-29
```

## Verification

```text
python3 -m unittest discover tests/mac/spotprice_history
Ran 6 tests
OK

python3 -m unittest discover tests/mac/spot_forecast
Ran 18 tests
OK

python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
Ran 62 tests
OK

python3 -m unittest discover tests/mac
Ran 183 tests
OK

python3 -m compileall -q src/mac/services/spotprice_history src/mac/services/spot_forecast src/mac/labs/weekly_home_optimizer_poc
exit 0

git diff --check
exit 0
```

CLI verification:

```text
python3 -m src.mac.services.spot_forecast --once --week 2 --db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3
result = [0.72,1.29,1.1,0.66,1.27,1.09,0.7,1.24,1.03,0.61,1.36,1.33,0.81,1.34,1.18,0.63,1.0,1.03,0.68,0.89,1.05]
```

HTTP verification:

```text
GET /spot/period-index?week=2
result = compact 21-number array

GET /spot/period-index/meta?week=2
result = source sqlite, row_count 35064, expected_count 35064, gap_count 0
```

## Live actions

No Shelly, Home Assistant, KVS, Script, Switch, Light, Cover, relay, dimmer or actuator actions were performed.

Local Mac writes performed by package scope:

- created/updated `/Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3`
- created `/Users/marcus.lovenstad/.smart-home/logs/`
- wrote `/Users/marcus.lovenstad/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist`
- loaded the user LaunchAgent with launchctl

## Knowhow promotion

Created `memory/knowhow/spotprice.md` and updated `memory/knowhow/00-index.md`.

Promoted lessons:

- `se.elpris.eu?avg24` was not sufficient for full 2022 historical backfill.
- direct Elprisetjustnu history supports old hourly and newer quarter-hour payloads.
- Python urllib source fetch needs a project User-Agent.
- long source backfills should commit per day and be rerunnable.

## Uncertainty

The launchd job is loaded and scheduled but has not naturally fired at 14:00 after installation. Manual `ingest-daily` verified the command path and no-op behavior.

Spot forecast server startup validates the full DB before binding, so startup is slower than the old fixture-backed service.
