# P0030 amendment: Daily ingest job and storage decision

## Status

planned amendment to P0030

## Applies to

```text
requirements/packages/P0030-historical-spotprice-dataset-foundation.md
```

This amendment is part of P0030 scope and must be read by Codex together with the main P0030 package file before P0030 review/design/implementation.

## User clarification

P0030 must not only backfill historical SE3 spotprice data. It must also establish how the Mac keeps the dataset current by fetching the next available actual spotprice day every day and storing it in the chosen database/storage layer.

The long-term direction is a full Mac-side ML algorithm with later weather normalization and feature engineering. P0030 must therefore make a deliberate storage decision instead of treating historical data as ad-hoc fixtures only.

## Added decision summary

P0030 must establish:

```text
1. historical backfill from 2022-05-30 through latest safely available actual 2026 data
2. validated durable local storage suitable for future ML feature extraction
3. a daily Mac-side ingest/update job that fetches the newest available actual spotprice day
4. manifest/evidence proving both backfill and incremental update semantics
```

P0030 still must not implement ML, weather normalization, optimizer changes, Shelly runtime changes, or control-policy changes.

## Storage policy to review and decide

Codex must explicitly evaluate whether the existing repo fixture/storage approach is sufficient for future ML.

The expected preferred outcome is:

```text
SQLite database for mutable local historical spotprice storage
```

Rationale:

- Python `sqlite3` is in the standard library.
- Hourly spotprice data for several years is small enough for SQLite.
- SQLite supports deterministic queries, unique constraints, upserts, incremental ingestion and future feature extraction.
- The database can live locally outside repo while schema, builder, validator and small test fixtures are versioned.
- Future ML packages can export training matrices from SQLite without changing ingestion.

Codex must review alternatives in `requirements/package-runs/P0030/design.md`:

```text
A. committed CSV/JSONL fixtures only
B. local SQLite database plus committed schema/manifest/test fixtures
C. other storage, only if justified without external dependencies
```

Default decision unless Codex finds a repository-policy blocker:

```text
Use local SQLite as canonical mutable store for spotprice history.
Do not commit the full generated SQLite database to repo unless design explicitly justifies repo-size and binary-artifact tradeoffs.
Commit schema, code, tests, docs and dataset manifest/evidence instead.
```

## Database requirements

If SQLite is chosen, P0030 must create a stable schema with at least:

```text
spot_prices
  area
  timestamp_utc or timestamp_local with explicit timezone policy
  local_date
  local_hour
  price
  currency
  unit
  source
  fetched_at
  dataset_build_id or ingest_run_id
  PRIMARY KEY or UNIQUE(area, timestamp_*)

ingest_runs or dataset_builds
  run_id
  run_type: backfill | daily
  started_at
  completed_at
  source
  area
  start_date
  end_date
  status
  records_inserted
  records_updated
  gaps_detected
  error_summary
```

Schema must preserve enough information for future ML/weather-normalization packages to join on time, local date/hour, weekday/weekend, season and future weather features.

## Daily ingest job requirements

P0030 must add a Mac-side daily ingest command. The command must be safe to run repeatedly and must be idempotent.

Expected command shape, exact CLI to be chosen in design:

```bash
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3
```

Daily ingest behavior:

1. Determine latest complete stored actual spotprice hour/day for the area.
2. Determine the newest safely available source day.
3. Fetch only missing complete days/hours, or the next missing day if the source works day-by-day.
4. Upsert into storage using a unique area+timestamp key.
5. Re-run validation for the affected tail range and overall completeness summary.
6. Record an ingest run row and concise evidence/log entry.
7. Exit cleanly with no changes if no new complete day is available.
8. Never synthesize missing values.
9. Never silently skip gaps.

The job must handle source timing explicitly: spotprice data for a new day may not be available at midnight. The design must choose a safe daily run time, likely after afternoon publication, or implement `no_new_complete_day_available` as a normal non-error status.

## Scheduling requirements

P0030 must provide a Mac-side job contract. Codex must decide whether P0030 should:

```text
A. implement only the ingest command and document launchd/manual scheduling for a later package
B. include a disabled/template launchd plist for daily local scheduling
C. install/enable a launchd job now
```

Default unless explicitly safer in repo policy:

```text
Implement the ingest command and provide a documented launchd template, but do not install/enable a persistent job automatically.
```

If Codex proposes installing/enabling a launchd job, it must `WARN` first and require explicit operator approval because this changes Mac runtime behavior.

## Repository/data placement requirements

Codex must choose and document locations for:

```text
schema file
local database default path
test fixtures
manifest/evidence
optional launchd template
```

Preferred local DB path unless repo policy says otherwise:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

Repo should contain:

```text
- schema/migration definition
- builder/ingest/validator code
- small deterministic test fixtures
- dataset manifest or summary evidence
- docs/functions/mac/spotprice-history-dataset.md
```

Repo should not contain:

```text
- large raw source dumps
- secrets
- local operator-specific database paths with private credentials
- generated full SQLite DB unless explicitly justified
```

## Main P0030 sections amended

### Problem

Add:

```text
Future ML work needs both historical backfill and ongoing daily updates. A one-time fixture is not sufficient if the model will learn from continuously arriving actual spotprice data.
```

### Target behavior

Add:

```text
Build a local durable storage layer and daily ingest command that keeps the historical spotprice dataset current after the initial backfill.
```

### Dataset schema requirements

Add storage-level requirements:

```text
- stable primary key per area/hour
- ingest/build metadata
- source and fetched_at
- queryable local date/hour fields for future feature engineering
```

### Design requirements

Add:

```text
- storage decision: CSV/JSONL vs SQLite vs other
- selected DB path
- schema/migration model
- daily ingest algorithm
- idempotent upsert model
- daily schedule recommendation
- whether launchd is implemented, templated or deferred
- how future ML/weather-normalization will read from storage
```

### Function design requirements

Add intended functions or equivalents:

```text
open_database(...)
initialize_schema(...)
get_latest_stored_hour(...)
fetch_missing_days(...)
upsert_hourly_prices(...)
record_ingest_run(...)
ingest_daily(...)
validate_database_continuity(...)
export_dataset_manifest(...)
```

### Test cases

Add:

```text
TC11: SQLite schema initialization
TC12: Idempotent daily ingest/upsert
TC13: No-op when no new complete day is available
TC14: Daily ingest detects source gap and marks incomplete
TC15: Ingest run metadata is recorded
TC16: Launchd template/docs do not auto-install persistent job
```

### Verification commands

Add equivalents of:

```bash
python3 -m src.mac.services.spotprice_history init-db --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history backfill --start 2022-05-30 --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spotprice_history validate --db ~/.smart-home/data/spotprice_history.sqlite3
```

If actual command names differ, document the equivalents.

## Safety and non-goals remain

This amendment does not permit:

- ML training
- weather normalization
- optimizer/control changes
- Shelly deploy
- Shelly RPC/KVS writes
- Home Assistant integration
- actuator/device access
- synthetic gap filling
- external Python dependencies without STOP/approval
- automatic installation of persistent launchd jobs without explicit approval

## Expected Codex output added

Codex output must include:

```text
- storage decision and rationale
- whether SQLite was chosen
- database schema path
- local DB path used for verification
- backfill result
- daily ingest result
- idempotency verification result
- launchd/manual scheduling decision
- whether a persistent job was installed; expected answer should be no unless explicitly approved
- how future ML packages should consume the storage
```
