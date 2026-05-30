# P0030 changelog

## Added

- Added `src.mac.services.spotprice_history`, a standard-library Mac service for SE3 historical spot price ingestion, SQLite storage, validation and launchd installation.
- Added SQLite schema for `spot_prices`, `ingest_runs` and `schema_meta`.
- Added object-list and compact spot price source parsing, including quarter-hour-to-hour aggregation.
- Added continuity validation with DST-aware expected local hour counts.
- Added daily idempotent ingest and full historical backfill CLI commands.
- Added user LaunchAgent rendering/install support for `se.mlovholm.smart-home.spotprice-history-daily`.
- Added function documentation for spot price history.
- Added tests for source parsing, storage validation, daily ingest and launchd plist rendering.

## Changed

- Changed `src.mac.services.spot_forecast` CLI/server default source to the P0030 SQLite DB.
- Added `--db` and `--area` options to `spot_forecast`.
- Added `/spot/period-index/meta?week=WW`.
- Kept `/spot/period-index?week=WW` as a compact 21-number JSON array.
- Changed the weekly home optimizer POC to inject the legacy P0017 fixture explicitly so its existing deterministic lab contract remains separate from the P0030 service default.
- Updated `docs/functions/mac/spot-forecast.md` for DB-backed behavior.

## Verified local state

- Full DB exists at `~/.smart-home/data/spotprice_history.sqlite3`.
- Coverage: 2022-05-30 through 2026-05-29.
- Rows: 35064 expected and stored.
- Gaps: 0.
- Duplicates: 0.
- Negative prices: 1504.
- Daily LaunchAgent is loaded for 14:00 local time.
