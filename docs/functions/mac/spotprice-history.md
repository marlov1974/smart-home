# Spot Price History

Last changed: P0030

## Module

```text
src.mac.services.spotprice_history
```

## Purpose

Mac-only historical SE3 spot price store used by DB-backed spot forecast services.

Canonical mutable local DB:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

The repo commits code, tests and docs, not the mutable DB.

## CLI

```bash
python3 -m src.mac.services.spotprice_history init-db --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history backfill --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3 --start-date 2022-05-30 --end-date 2026-05-29
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history validate --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3 --start-date 2022-05-30
python3 -m src.mac.services.spotprice_history install-daily-job --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
```

## Important Functions

`default_db_path()` returns the canonical local SQLite path.

`init_db(path)` creates the P0030 SQLite schema.

`fetch_source_day(area, target_date, timeout)` performs one read-only HTTPS fetch from Elprisetjustnu.

`fetch_source_day_with_retry(area, target_date, timeout, attempts)` retries the read-only source fetch for transient source/network failures.

`parse_price_day(payload, area, source)` parses Elprisetjustnu object-list payloads or compact `p` payloads into hourly rows. Quarter-hour payloads are aggregated to hourly means.

`expected_utc_hours_for_local_date(local_date)` returns the Europe/Stockholm UTC hour sequence for one local date, including 23/25-hour DST days.

`upsert_prices(conn, rows)` idempotently inserts or updates hourly price rows.

`validate_range(conn, area, start_date, end_date, db_path)` validates continuity, duplicate count, expected hour count, gaps, negative-price count and summary statistics.

`latest_complete_local_date(conn, area)` finds the latest stored date whose expected local hours are complete.

`backfill(conn, area, start_date, end_date, db_path, fetcher, command)` fetches and stores an inclusive date range. Each day is committed independently so interrupted backfills can be rerun safely.

`ingest_daily(conn, area, db_path, today, fetcher)` fetches missing complete days through yesterday and is a no-op when the local DB tail is complete.

`render_launch_agent_plist(db_path, python_executable)` renders the user LaunchAgent.

`install_daily_job(db_path, plist_path, python_executable, run_launchctl)` writes and loads the user LaunchAgent.

## Daily LaunchAgent

Label:

```text
se.mlovholm.smart-home.spotprice-history-daily
```

Plist:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
```

Schedule:

```text
14:00 local time daily
```

Logs:

```text
~/.smart-home/logs/spotprice-history-daily.out.log
~/.smart-home/logs/spotprice-history-daily.err.log
```

Rollback:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
rm ~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
```

## Safety

This module performs read-only HTTP and local SQLite writes only. It does not call Shelly, Home Assistant, KVS writes, scripts or actuators.
