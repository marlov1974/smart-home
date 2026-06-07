# P0056A function design

## New functions

`run_p0056a_ingestion`

- Purpose: orchestrate P0056A source access, fetching, parsing, aggregation, DB persistence, validation and evidence.
- Inputs: feature DB path, evidence directory, optional start/end.
- Outputs: package result dataclass.
- Side effects: writes local SQLite tables and compact package evidence.
- Tests: package run and helper unit tests.

`area_catalog`

- Purpose: define requested bidding-zone scope and EIC mapping.
- Inputs: none.
- Outputs: list of catalog rows.
- Side effects: none.
- Tests: required areas present.

`fetch_actual_load_native_rows`

- Purpose: request ENTSO-E A65/A16 actual total load by area/year chunk.
- Inputs: token, start/end.
- Outputs: native rows and sanitized response metadata.
- Side effects: ENTSO-E HTTPS requests.
- Tests: parser/params helpers; full package run covers live access.

`parse_actual_load_document` / `parse_actual_load_period`

- Purpose: parse ENTSO-E XML into native interval rows.
- Inputs: XML bytes and request metadata.
- Outputs: native interval rows with start/end, value, unit and native resolution.
- Side effects: none.
- Tests: parser-adjacent aggregation tests.

`aggregate_native_to_hourly`

- Purpose: convert native average-MW interval rows to hourly average MW by time-weighted overlap.
- Inputs: native rows.
- Outputs: hourly rows with resolution mix and input row counts.
- Side effects: none.
- Tests: 15m/60m aggregation.

`persist_p0056a_tables`

- Purpose: create and rerun P0056A DB tables.
- Inputs: sqlite connection, catalog/native/hourly rows.
- Outputs: row counts.
- Side effects: local SQLite writes for P0056A tables only.
- Tests: schema/DDL expectations by package run.

`validation_summary`

- Purpose: build coverage, missingness, volume sanity and SE3 consistency evidence.
- Inputs: sqlite connection and request range.
- Outputs: evidence-ready dict.
- Side effects: none.
- Tests: package run.

`write_p0056a_evidence`

- Purpose: write required package evidence and compact CSV/JSON.
- Inputs: summary.
- Outputs: evidence path map.
- Side effects: writes files under `requirements/package-runs/P0056A`.
- Tests: package run.

## Changed functions

None planned in existing modules.

## Removed functions

None.
