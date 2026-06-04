# P0053A function design

New functions in `p0053a.py`:

- `run_p0053a_backfill(...)`
  - Purpose: package entry point for token safety, fetch, persistence, wide update, analysis dataset, validation, diagnostics and evidence.
  - Inputs: feature DB path, evidence dir, start/end datetimes, worker count, fetch/skip-fetch mode.
  - Outputs: `P0053AResult`.
  - Side effects: reads local token, reads/writes local feature SQLite DB, writes evidence files.
  - Tests: smoke through focused helpers and live package command.

- `a09_a11_configs()`
  - Purpose: return only ENTSO-E A09/A11 document configs.
  - Inputs: none.
  - Outputs: tuple of config dictionaries.
  - Side effects: none.
  - Tests: excludes A61 and forbidden price documents.

- `monthly_chunks(start, end)`
  - Purpose: create UTC month-bound request chunks clipped to a requested range.
  - Inputs: UTC start/end datetimes.
  - Outputs: ordered list of `(start, end)` pairs.
  - Side effects: none.
  - Tests: expected clipping and hour-inclusive end.

- `plan_missing_fetch_tasks(conn, start, end)`
  - Purpose: skip already-covered A09/A11 monthly border/direction chunks and build safe ENTSO-E tasks only for missing data.
  - Inputs: SQLite connection and date range.
  - Outputs: task list and planning summary.
  - Side effects: reads canonical table.
  - Tests: in-memory DB coverage check.

- `fetch_task(token, task)`
  - Purpose: perform one ENTSO-E request and parse rows with safe metadata.
  - Inputs: token and task dictionary.
  - Outputs: rows, safe response metadata and optional safe failure metadata.
  - Side effects: network request.
  - Tests: scope checks around task metadata; live verification covers network behavior.

- `fetch_missing_entsoe_rows(token, tasks, workers)`
  - Purpose: execute fetch tasks concurrently and collect rows/responses/failures.
  - Inputs: token, tasks, worker count.
  - Outputs: raw rows, response summaries, failed chunk summaries.
  - Side effects: network requests and progress output without token.
  - Tests: not directly unit-tested beyond task construction.

- `ensure_p0053a_schema(conn)`
  - Purpose: ensure metadata, directional and derived wide columns exist.
  - Inputs: SQLite connection.
  - Outputs: added-column summary.
  - Side effects: ALTER TABLE on local feature DB.
  - Tests: in-memory DB schema check.

- `load_a09_a11_hourly_rows(conn, start, end)`
  - Purpose: load canonical A09/A11 rows for the target range after any backfill.
  - Inputs: SQLite connection and date range.
  - Outputs: list of row dictionaries.
  - Side effects: reads DB.
  - Tests: covered indirectly by wide/analysis tests.

- `derive_flow_exchange_features(values)`
  - Purpose: compute directed net scheduled exchange, net physical flow and southward pressure features.
  - Inputs: per-hour wide values.
  - Outputs: derived feature dictionary.
  - Side effects: none.
  - Tests: explicit formula tests.

- `update_wide_flow_exchange_features(conn, hourly_rows)`
  - Purpose: insert missing wide timestamps and update A09/A11 directional plus P0053A derived columns.
  - Inputs: SQLite connection and canonical hourly rows.
  - Outputs: inserted/updated counts.
  - Side effects: writes wide table.
  - Tests: in-memory update test.

- `create_joined_analysis_dataset(conn, start, end)`
  - Purpose: build `physical_balance_flow_exchange_analysis_v1` by normalized timestamp matching between wide, price and physical balance rows.
  - Inputs: SQLite connection and date range.
  - Outputs: row count and coverage summary.
  - Side effects: drops/recreates package analysis table.
  - Tests: mixed timestamp format join test.

- `validate_p0053a(conn, ...)`
  - Purpose: verify no A61 in package rows/tasks, finite values, no duplicate package keys, coverage threshold, one row per wide timestamp, joined rows and secret safety.
  - Inputs: SQLite connection plus fetch/evidence summaries.
  - Outputs: validation dictionary.
  - Side effects: reads DB.
  - Tests: formula/scope tests plus live verification.

- `run_p0053a_diagnostics(conn, start, end)`
  - Purpose: compute correlation and pre/post flow-based descriptive diagnostics for observed A09/A11 features.
  - Inputs: SQLite connection and range.
  - Outputs: diagnostics dictionary.
  - Side effects: reads analysis table.
  - Tests: smoke through analysis creation.

- `write_p0053a_evidence(evidence_dir, summary)`
  - Purpose: write required package evidence markdown/json without secrets.
  - Inputs: evidence dir and summary dictionary.
  - Outputs: evidence path map.
  - Side effects: writes evidence files.
  - Tests: token-safe content checked by live scan.

Changed functions:

- None. P0053A is additive and reuses previous package helpers without changing their contracts.

Removed functions:

- None.

Durable function catalog:

- Update `docs/functions/spotprice_model_diagnostics_p0053a.md` after implementation because P0053A creates reusable ENTSO-E A09/A11 backfill and normalized analysis dataset functions for later packages.
