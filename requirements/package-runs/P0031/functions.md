# P0031 function design

## New module: `src.mac.services.weather_history`

`default_db_path() -> Path`

- Returns `~/.smart-home/data/weather_history.sqlite3`.

`connect_db(path) -> sqlite3.Connection`

- Opens SQLite with row access.

`initialize_schema(path) -> None`

- Creates tables and default SE3 proxy locations.

`configured_locations(conn) -> list[WeatherLocation]`

- Reads active locations and weights.

`expected_utc_hours_for_local_date(local_date) -> tuple[datetime, ...]`

- Reuses the P0030 Europe/Stockholm DST policy.

`fetch_open_meteo_range(location, start_utc_date, end_utc_date, timeout) -> bytes`

- Performs one read-only Open-Meteo archive fetch.

`parse_open_meteo_response(payload, location, expected_hours) -> list[WeatherObservation]`

- Parses hourly arrays, validates required variables and normalizes UTC/local timestamp metadata.

`upsert_weather_observations(conn, observations, ingest_run_id) -> int`

- Idempotently stores location-hour weather rows.

`compute_area_proxy_hourly(conn, area_proxy, start_date, end_date, ingest_run_id) -> int`

- Computes weighted SE3 hourly rows from all active locations.

`record_weather_ingest_run(...) -> int`

- Stores backfill/daily/validate/install metadata.

`latest_complete_local_date(conn, area_proxy) -> date | None`

- Finds the latest complete stored area-proxy day.

`latest_safe_complete_day(today) -> date`

- Returns `today - 6 days`.

`backfill(conn, start_date, end_date, fetcher) -> IngestSummary`

- Fetches all configured locations, stores observations, computes SE3 proxy and validates.

`ingest_daily(conn, today, fetcher) -> IngestSummary`

- Fetches missing complete days through the latest safe day and no-ops cleanly when already current.

`validate_weather_continuity(conn, start_date, end_date) -> ValidationReport`

- Reports gaps, duplicates, null counts, first/last timestamp, counts and summary statistics.

`render_launchd_plist(db_path, python_executable) -> str`

- Renders the LaunchAgent XML.

`install_launchd_plist(db_path, run_launchctl) -> LaunchdInstallResult`

- Writes, bootstraps and enables the user LaunchAgent.

`main(argv=None) -> int`

- Implements the CLI.
