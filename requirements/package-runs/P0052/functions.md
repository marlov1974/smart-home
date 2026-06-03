# P0052 function design

## New functions

`run_p0052_ingestion(feature_db=..., evidence_dir=..., start=None, end=None, workers=...)`

- Purpose: orchestrate source discovery, fetch, parse, aggregate, persist, validate, diagnose and evidence writing.
- Inputs: feature database path, evidence directory, optional UTC range and worker count.
- Outputs: result dataclass with status, ranges, row counts and evidence paths.
- Side effects: writes local SQLite tables and package-run evidence.
- Test coverage: integration-style unit test with fake rows plus persistence/idempotency tests.

`load_p0052_ranges(conn)`

- Purpose: read P0051/modeling overlap and decide P0052 requested/final source range.
- Inputs: SQLite connection.
- Outputs: range dictionary.
- Side effects: none.
- Test coverage: implicit through join/range tests.

`fetch_svk_flow_snapshot(timestamp_utc, timeout=...)`

- Purpose: fetch one SvK/Statnett flow-map snapshot for a UTC quarter-hour.
- Inputs: UTC datetime and timeout.
- Outputs: parsed JSON object.
- Side effects: HTTPS read only.
- Test coverage: parser tests use static payload; live verification exercises fetch.

`fetch_svk_flow_period(start, end, workers=...)`

- Purpose: fetch all quarter-hour snapshots in a range and return normalized observations.
- Inputs: UTC start/end datetimes and worker count.
- Outputs: list of quarter-hour observation dictionaries.
- Side effects: HTTPS read only.
- Test coverage: parser/aggregation tests; live verification for real fetch.

`parse_svk_flow_payload(payload, requested_timestamp)`

- Purpose: convert SvK flow-map JSON to raw directed border and SE1-SE4 import/export observations.
- Inputs: JSON payload and requested UTC timestamp.
- Outputs: raw observations.
- Side effects: none.
- Test coverage: source contract parser test.

`directed_border_values(border_id, signed_value)`

- Purpose: normalize SvK signed `A_B` flow into directed A->B and B->A values.
- Inputs: border id and signed MW value.
- Outputs: one or two long-format flow rows with non-negative directional value where applicable.
- Side effects: none.
- Test coverage: Swedish bidding-zone border mapping test.

`aggregate_hourly(observations)`

- Purpose: aggregate quarter-hour MW observations to hourly mean MW by natural key.
- Inputs: raw observations.
- Outputs: canonical hourly rows.
- Side effects: none.
- Test coverage: deterministic aggregation and uniqueness tests.

`build_wide_hourly(hourly_rows, physical_rows=None)`

- Purpose: create SE1-SE4 wide modeling rows with flows, import/export, net import, pressure and balance residual features.
- Inputs: hourly rows and optional P0051 physical rows.
- Outputs: wide row dictionaries.
- Side effects: none.
- Test coverage: import/export, net import, balance residual and utilization tests.

`capacity_utilization(flow, capacity)`

- Purpose: calculate utilization only when a valid positive capacity exists.
- Inputs: flow MW and capacity MW.
- Outputs: float or null.
- Side effects: none.
- Test coverage: zero/null capacity test.

`flow_based_market_coupling_flag(timestamp_utc)`

- Purpose: classify whether a timestamp is before or after Nordic flow-based market coupling go-live.
- Inputs: UTC timestamp.
- Outputs: integer 0/1.
- Side effects: none.
- Test coverage: deterministic flag test.

`persist_transfer_flow(conn, raw_rows, hourly_rows, wide_rows)`

- Purpose: replace P0052 tables deterministically and enforce canonical uniqueness.
- Inputs: SQLite connection and row lists.
- Outputs: none.
- Side effects: writes local SQLite tables.
- Test coverage: idempotent persistence test.

`validate_transfer_flow(conn, hourly_rows, wide_rows, ranges)`

- Purpose: validate numeric values, duplicates, missingness, joins to P0051 and forbidden path absence.
- Inputs: connection, row lists and range dictionary.
- Outputs: validation dictionary.
- Side effects: none.
- Test coverage: validation and join tests.

`run_initial_diagnostics(conn, wide_rows)`

- Purpose: calculate non-model correlations/event summaries against SE3 price and SE3-SE1 where joined rows exist.
- Inputs: SQLite connection and wide rows.
- Outputs: diagnostics dictionary.
- Side effects: none.
- Test coverage: basic no-crash/shape test.

`write_p0052_evidence(evidence_dir, summary)`

- Purpose: write all required P0052 Markdown and JSON evidence files.
- Inputs: evidence directory and summary dictionary.
- Outputs: mapping of evidence names to paths.
- Side effects: writes package-run evidence.
- Test coverage: live/package verification.

## Changed functions

None planned.

## Removed functions

None planned.
