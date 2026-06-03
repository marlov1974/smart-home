# P0052A function design

## New functions

`run_p0052a_ingestion(feature_db=..., evidence_dir=..., start=None, end=None)`

- Purpose: orchestrate token checks, ENTSO-E discovery/ingestion, persistence, wide feature update, validation, diagnostics and evidence.
- Inputs: feature database path, evidence directory and optional UTC range.
- Outputs: result dataclass with status, row counts, ranges and evidence paths.
- Side effects: writes local SQLite rows and package-run evidence.
- Test coverage: live verification plus focused unit tests.

`load_entsoe_token()`

- Purpose: read the token from environment or local secret file.
- Inputs: none.
- Outputs: token plus token source label.
- Side effects: none.
- Test coverage: token loader test with temporary file/environment.

`verify_secret_safety(token_source)`

- Purpose: confirm secret file is outside repo or otherwise not committable, and permissions are owner-only where available.
- Inputs: token source metadata.
- Outputs: sanitized safety dictionary.
- Side effects: reads filesystem metadata only.
- Test coverage: mocked/local path checks.

`build_entsoe_params(document_type, from_area, to_area, start, end, contract_type=None)`

- Purpose: build request parameters while keeping token separate from evidence-safe parameter records.
- Inputs: document type, areas, range and optional contract type.
- Outputs: request params and sanitized params.
- Side effects: none.
- Test coverage: request builder test ensures token is not in sanitized output.

`fetch_entsoe_document(token, params)`

- Purpose: perform one token-backed read-only ENTSO-E API call.
- Inputs: token and request params.
- Outputs: XML bytes and status metadata.
- Side effects: HTTPS read only.
- Test coverage: parser tests use fixture XML; live verification uses real API.

`parse_entsoe_document(xml_bytes, request_meta)`

- Purpose: parse ENTSO-E MarketDocument or Acknowledgement response into observations or failure evidence.
- Inputs: XML bytes and sanitized request metadata.
- Outputs: observations plus response summary.
- Side effects: none.
- Test coverage: success and acknowledgement XML tests.

`parse_entsoe_period_points(period, request_meta, series_meta)`

- Purpose: expand ENTSO-E `Point` positions into UTC timestamps based on period start and resolution.
- Inputs: XML period, request metadata and series metadata.
- Outputs: observation dictionaries.
- Side effects: none.
- Test coverage: deterministic timestamp expansion, including ENTSO-E `P1M` capacity periods expanded from actual period bounds.

`resolution_to_timedelta(resolution, period_start=None, period_end=None)`

- Purpose: map ENTSO-E ISO-like resolutions to timedeltas, including calendar-month `P1M` values when the source period gives explicit bounds.
- Inputs: resolution string and optional UTC period start/end.
- Outputs: timedelta.
- Side effects: none.
- Test coverage: PT/P1D fixture coverage plus P1M period-bound test added after live attempt 1 found monthly capacity resolution.

`persist_entsoe_rows(conn, raw_rows, hourly_rows)`

- Purpose: insert ENTSO-E rows into existing P0052 long tables without dropping SvK/Statnett rows.
- Inputs: SQLite connection and row lists.
- Outputs: none.
- Side effects: `INSERT OR REPLACE` into long tables.
- Test coverage: idempotent insert test.

`update_wide_entsoe_features(conn, hourly_rows)`

- Purpose: add missing wide columns and update matching internal-border feature values.
- Inputs: SQLite connection and hourly rows.
- Outputs: updated row count.
- Side effects: alters/updates wide table.
- Test coverage: wide update and utilization tests.

`capacity_utilization(flow_or_exchange, capacity)`

- Purpose: compute utilization only with positive capacity.
- Inputs: flow/exchange and capacity.
- Outputs: float or null.
- Side effects: none.
- Test coverage: null/zero capacity test.

`run_p0052a_diagnostics(conn)`

- Purpose: compute capacity/utilization/bottleneck diagnostics against SE3 price and SE3-SE1 when joined rows exist.
- Inputs: SQLite connection.
- Outputs: diagnostics dictionary.
- Side effects: none.
- Test coverage: shape/no-token test.

`write_p0052a_evidence(evidence_dir, summary)`

- Purpose: write required P0052A evidence without secrets.
- Inputs: evidence directory and summary dictionary.
- Outputs: path mapping.
- Side effects: writes package-run evidence.
- Test coverage: no-token evidence scan in live verification.

## Changed functions

None planned. P0052A will not modify `p0052.py`; it will preserve P0052 behavior and extend the database state through its own module.

## Removed functions

None planned.
