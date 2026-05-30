# P0030 function design

## New package: `src.mac.services.spotprice_history`

`default_db_path() -> Path`

- Purpose: return `~/.smart-home/data/spotprice_history.sqlite3`.
- Side effects: none.
- Tests: default path is stable.

`connect_db(path: Path | str) -> sqlite3.Connection`

- Purpose: open a SQLite connection with row access and foreign key support.
- Side effects: opens/creates a local DB file when callers initialize schema.
- Tests: schema init uses it with temporary DBs.

`init_db(path: Path | str) -> None`

- Purpose: create/upgrade P0030 schema.
- Side effects: creates parent directory and SQLite tables.
- Tests: creates required tables and is idempotent.

`fetch_source_day(area: str, date: date, timeout: float) -> bytes`

- Purpose: fetch one local-date source payload from Elprisetjustnu.
- Side effects: read-only HTTPS.
- Tests: not directly network-tested by unit tests; parser and ingest use injected fetchers.

`parse_price_day(payload: bytes | str, area: str, source_url: str) -> list[HourlySpotPrice]`

- Purpose: parse object-list or compact payloads and return canonical hourly rows.
- Side effects: none.
- Tests: 24-row and 96-row fixture payloads, duplicate/partial failures.

`expected_utc_hours_for_local_date(local_date: date) -> tuple[datetime, ...]`

- Purpose: derive Europe/Stockholm expected UTC hour sequence for one local date.
- Side effects: none.
- Tests: normal day 24, spring DST 23, autumn DST 25.

`upsert_prices(conn: sqlite3.Connection, rows: Sequence[HourlySpotPrice]) -> int`

- Purpose: insert/update canonical hourly rows idempotently.
- Side effects: writes SQLite rows.
- Tests: repeated upsert does not duplicate rows.

`validate_range(conn: sqlite3.Connection, area: str, start_date: date, end_date: date | None) -> ValidationReport`

- Purpose: validate continuity and compute manifest/statistics.
- Side effects: none.
- Tests: complete fixture passes; intentional gap fails.

`latest_complete_local_date(conn: sqlite3.Connection, area: str) -> date | None`

- Purpose: find the latest stored date whose expected local hours are complete.
- Side effects: none.
- Tests: ignores incomplete tail day.

`backfill(conn, area, start_date, end_date, fetcher) -> IngestSummary`

- Purpose: fetch, parse, upsert and validate an inclusive date range.
- Side effects: read-only HTTP through fetcher and SQLite writes.
- Tests: injected fetcher, idempotence, gap failure.

`ingest_daily(conn, area, today, fetcher) -> IngestSummary`

- Purpose: fetch missing complete days through yesterday local date.
- Side effects: read-only HTTP through fetcher and SQLite writes.
- Tests: no-op when complete; inserts only missing days.

`render_launch_agent_plist(...) -> str`

- Purpose: render the user LaunchAgent XML.
- Side effects: none.
- Tests: exact label, command args and log paths.

`install_daily_job(...) -> LaunchdInstallResult`

- Purpose: write LaunchAgent and load it with launchctl.
- Side effects: creates local dirs, writes plist, runs launchctl.
- Tests: rendering covered by unit tests; live install verified manually/package command.

## Changed package: `src.mac.services.spot_forecast`

`load_history_from_db(path, area) -> list[HistoricalWeek]`

- Purpose: build P0017-compatible 21-period weekly index records from SQLite hourly actual prices.
- Side effects: reads SQLite.
- Tests: fixture DB produces expected week records and fails clearly on missing/incomplete DB.

`forecast_period_indexes(target_week, history=None, db_path=None, area="SE3")`

- Purpose: keep existing history injection for tests, otherwise load from SQLite DB.
- Side effects: reads SQLite when history is omitted.
- Tests: existing model tests plus DB-backed tests.

`run_once(week_arg, db_path, area, out, err)`

- Purpose: print compact 21-number JSON from DB-backed history.
- Side effects: reads SQLite and writes stdout/stderr.
- Tests: valid fixture DB and missing DB error.

`serve(host, port, db_path, area, history=None)`

- Purpose: run HTTP service with DB-backed history.
- Side effects: binds local HTTP server and reads SQLite at startup.
- Tests: handler tests use injected history; CLI smoke may use temp DB.

`build_handler(history, metadata=None)`

- Purpose: preserve compact array endpoint and expose metadata endpoint.
- Side effects: none except HTTP response writes.
- Tests: compact endpoint remains array, metadata endpoint returns source/coverage.

## Documentation updates

`docs/functions/mac/spotprice-history.md`

- Purpose: durable function catalog for the new P0030 history service.

`docs/functions/mac/spot-forecast.md`

- Purpose: document DB-backed P0030 behavior, `--db`, failure semantics and metadata endpoint.
