# P0030 design

## Implementation structure

Add a new standard-library-only package:

```text
src/mac/services/spotprice_history/
```

The package owns source fetching, parsing, SQLite storage, validation, manifest reporting and launchd installation for spot price history. It is Mac-local and has no device integration.

## SQLite schema

Use one canonical mutable DB with these tables:

- `spot_prices`: one row per area and UTC hour start.
- `ingest_runs`: one row per CLI ingest/backfill/validate run.
- `schema_meta`: small key/value metadata including schema version.

`spot_prices` stores:

- `area`
- `utc_hour_start`
- `local_hour_start`
- `local_date`
- `local_hour`
- `utc_offset`
- `fold`
- `price_sek_per_kwh`
- `price_eur_per_kwh`
- `exchange_rate`
- `source`
- `source_resolution`
- `samples`
- `ingested_at`

The primary key is `(area, utc_hour_start)`. Upserts are idempotent.

## Source parsing

Fetcher behavior:

- Primary historical fetch: `https://www.elprisetjustnu.se/api/v1/prices/YYYY/MM-DD_AREA.json`.
- Optional compact fetch helper: `https://se.elpris.eu/api/v1/prices/YYYY/MM-DD_AREA.json?avg24`, used only when explicitly selected or for diagnostics because it did not cover 2022-05-30.
- Parse object-list payloads with either 24 hourly rows or 96 quarter-hour rows.
- For quarter-hour payloads, aggregate all samples with the same local hour start into one hourly value using arithmetic mean for price and exchange-rate fields.
- Preserve the canonical UTC hour start by parsing the local timestamp and converting to UTC.

No synthetic gap fill is allowed. Missing, duplicate or partial hours remain validation failures.

## Completeness rules

For a local date and area:

- Expected local hour count is derived from Europe/Stockholm midnight-to-midnight UTC duration, so DST days naturally validate as 23 or 25 hours.
- Actual rows must exactly match the expected UTC hour sequence for each local date.
- Duplicate UTC hour keys are failures.
- Negative prices are allowed and counted in manifest/statistics.

For full validation:

- First expected local date is `2022-05-30`.
- End date defaults to the latest stored local date.
- Every date in the inclusive range must pass per-day validation.
- Summary includes first/last timestamps, total rows, expected rows, per-year counts, gaps, duplicates, negative count, min/max/mean and DB path.

## CLI

Expose:

```text
python3 -m src.mac.services.spotprice_history init-db --db PATH
python3 -m src.mac.services.spotprice_history backfill --area SE3 --db PATH --start-date 2022-05-30
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db PATH
python3 -m src.mac.services.spotprice_history validate --area SE3 --db PATH --start-date 2022-05-30
python3 -m src.mac.services.spotprice_history install-daily-job --db PATH
```

`ingest-daily` determines the latest stored complete local date, fetches missing complete dates through yesterday local date, upserts, validates, and returns success as a no-op when nothing is missing.

## Launchd

Render a user LaunchAgent:

```text
~/Library/LaunchAgents/se.mlovholm.smart-home.spotprice-history-daily.plist
```

The job runs daily at 14:00 local time:

```text
python3 -m src.mac.services.spotprice_history ingest-daily --area SE3 --db ~/.smart-home/data/spotprice_history.sqlite3
```

Logs:

```text
~/.smart-home/logs/spotprice-history-daily.out.log
~/.smart-home/logs/spotprice-history-daily.err.log
```

The installer creates directories, writes the plist, bootstraps or reloads the user agent, and provides rollback commands. If sandbox restrictions prevent installation, package evidence records exact manual commands.

## Spot forecast API migration

Change `src.mac.services.spot_forecast` so its default source is:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

Add `--db` to CLI/server. The compact `/spot/period-index?week=WW` endpoint remains a 21-number array for compatibility. Add a metadata endpoint:

```text
GET /spot/period-index/meta?week=WW
```

`--once --week WW --db PATH` prints the compact array. A missing or incomplete DB returns a clear error and nonzero exit; there is no silent fallback to the old fixture.

The historical model still uses P0017 week-neighborhood weighting, but derives historical weekly 21-period indexes from all matching ISO weeks in the SQLite hourly actual dataset.

## Test strategy

Add package-scoped unit tests with compact fixtures:

- source parser accepts old 24-hour and new 96-quarter payload shapes;
- DST expected-hour validation handles 23/25-hour local dates;
- SQLite init/upsert/validate is idempotent and detects gaps;
- daily ingest no-op behavior is deterministic with an injected fetcher;
- launchd plist rendering contains the exact label, schedule, command and logs;
- spot forecast fails on missing DB and returns compact arrays from a fixture DB;
- metadata endpoint reports source DB and history coverage.

## Risks

- The full backfill is many daily HTTP requests. Implementation keeps the command resumable and idempotent so interruption is safe.
- Source availability/rate limits may make full live backfill fail during verification. This should be recorded as WARN with current DB state, not hidden.
- LaunchAgent installation writes outside the repo and requires sandbox escalation.
