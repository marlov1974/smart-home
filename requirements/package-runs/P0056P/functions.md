# P0056P Function Design

## New Module

```text
src/mac/services/spotprice_model_diagnostics/p0056p.py
```

## New Functions

### `build_p0056p_entsoe_request(area, start_utc, end_utc)`

- Status: new
- Purpose: build token-bearing and sanitized ENTSO-E Actual Total Load request parameters.
- Inputs: area code, UTC start, UTC end.
- Outputs: `(params, safe_metadata)`.
- Side effects: none.
- Reason: enforce package request contract and prevent forbidden source parameters.
- Tests: request contract test verifies `A65/A16`, SE2 EIC and absence of A09/A11/A61/flow/capacity parameters.

### `parse_entsoe_actual_load_xml(xml_bytes, request_meta)`

- Status: new
- Purpose: parse ENTSO-E Actual Total Load XML into native interval rows.
- Inputs: XML bytes and sanitized request metadata.
- Outputs: native row list plus response metadata.
- Side effects: none.
- Reason: package needs fresh/original rows without writing raw XML.
- Tests: parser fixture verifies interval timestamps, MW values, resolution minutes and response row counts.

### `load_fresh_entsoe_actual_load_rows(token, area, start_utc, end_utc, local_dates)`

- Status: new
- Purpose: perform the narrow fresh ENTSO-E fetch and parse rows.
- Inputs: token, area, UTC start/end and local date filter.
- Outputs: fresh native rows and sanitized response metadata.
- Side effects: network request to ENTSO-E only.
- Reason: source verification requires fresh/original source data.
- Tests: request construction is unit-tested; live fetch is verified by package command, not unit test.

### `load_local_native_area_rows(conn, area, start_utc, end_utc, local_dates)`

- Status: new
- Purpose: read package-scoped local native rows from `area_consumption_native_v1`.
- Inputs: SQLite connection, area, UTC window, local date set.
- Outputs: local native rows with local metadata.
- Side effects: read-only DB query.
- Reason: compare fresh source against local P0056A native ingestion.
- Tests: can be tested with in-memory fixture table.

### `load_local_hourly_area_rows(conn, area, start_utc, end_utc, local_dates)`

- Status: new
- Purpose: read package-scoped local hourly rows from `area_consumption_hourly_v1`.
- Inputs: SQLite connection, area, UTC window, local date set.
- Outputs: local hourly rows with local metadata.
- Side effects: read-only DB query.
- Reason: compare fresh source aggregation against local P0056A hourly truth table.
- Tests: can be tested with in-memory fixture table.

### `load_reference_hourly_area_rows(conn, area, start_utc, end_utc, local_dates)`

- Status: new
- Purpose: read optional local reference hourly rows from `entsoe_consumption_area_hourly_v1`.
- Inputs: SQLite connection, area, UTC window, local date set.
- Outputs: reference hourly rows with local metadata, or an empty list when the table is absent.
- Side effects: read-only DB query.
- Reason: compare P0056A hourly rows against the older corrected ENTSO-E hourly target path without using it as replacement truth.
- Tests: covered indirectly by package command evidence.

### `aggregate_native_to_hourly_for_audit(native_rows)`

- Status: new
- Purpose: aggregate native rows into UTC-hour mean MW rows for audit comparison.
- Inputs: native rows with interval start and value.
- Outputs: hourly rows with mean MW and input row count.
- Side effects: none.
- Reason: P0056P compares fresh source native rows to local hourly rows.
- Tests: fixture verifies 4 quarter-hour values average correctly.

### `summarize_native_rows(rows, local_dates, source_label)`

- Status: new
- Purpose: compute row counts, expected counts, missing/duplicate timestamps and value stats.
- Inputs: native rows, local dates and source label.
- Outputs: summary dictionary and compact comparison rows.
- Side effects: none.
- Reason: evidence must report native missing/duplicate/malformed/spike facts.
- Tests: fixture verifies missing timestamp and duplicate detection.

### `compare_native_rows(fresh_rows, local_rows, local_day)`

- Status: new
- Purpose: compare fresh and local native rows by interval start for the anomaly day.
- Inputs: compact fresh rows, compact local rows and local delivery day.
- Outputs: compact CSV-ready rows with fresh/local values and deltas.
- Side effects: none.
- Reason: evidence must show whether the anomalous source intervals are present in both layers.
- Tests: covered indirectly by parser/classification tests and package command evidence.

### `compare_hourly_rows(fresh_hourly, local_hourly, local_dates)`

- Status: new
- Purpose: compare fresh aggregated hourly rows against local hourly rows.
- Inputs: fresh hourly rows, local hourly rows and local date filter.
- Outputs: comparison rows plus summary metrics.
- Side effects: none.
- Reason: evidence must determine whether local hourly aggregation matches source rows.
- Tests: fixture verifies tolerance and differing-hour count.

### `classify_2026_03_28_anomaly(area, fresh_summary, local_native_summary, hourly_summary)`

- Status: new
- Purpose: apply the package decision table.
- Inputs: area, source/local summaries and hourly comparison summary.
- Outputs: classification object.
- Side effects: none.
- Reason: package must emit exactly one primary classification and model-selection action.
- Tests: classification table is unit-tested.

### `write_p0056p_evidence(evidence_dir, summary, native_rows, hourly_rows)`

- Status: new
- Purpose: write Markdown, JSON and compact CSV evidence under package-run directory.
- Inputs: evidence directory, summary dictionaries, compact row lists.
- Outputs: map of evidence file names to paths.
- Side effects: writes package-run evidence only.
- Reason: package requires durable evidence for ChatGPT review and follow-up decisions.
- Tests: unit test verifies no token-like fields are written in generated evidence.

### `run_p0056p_source_verification(...)`

- Status: new
- Purpose: orchestrate the full P0056P source verification.
- Inputs: area, local date window, feature DB, evidence directory, fetch mode.
- Outputs: result object/status and row counts.
- Side effects: optional ENTSO-E fetch; read-only local DB queries; package evidence writes.
- Reason: CLI and tests need one deterministic entry point.
- Tests: unit tests cover subfunctions; package command verifies end-to-end behavior.

## Shared Function Changes

No shared helper changes are planned. P0056P reuses existing P0052A/P0056A/P0054P2 constants and parsing style where practical, but keeps package-specific audit logic local to avoid broad ingestion changes.

## Durable Function Catalog

Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation with a short P0056P section because the new module is a reusable source-audit pattern for future anomaly checks.
