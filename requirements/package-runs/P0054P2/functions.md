# P0054P2 Function Design

## New Functions

`run_p0054p2_ingestion(...)`

- Purpose: orchestrate ENTSO-E actual-load fetch, persistence, validation and evidence.
- Inputs: feature DB path, evidence directory, optional start/end.
- Outputs: `P0054P2Result`.
- Side effects: writes `entsoe_consumption_area_hourly_v1` and package-run evidence.
- Tests: package command plus helper tests.

`build_actual_load_params(...)`

- Purpose: build token-free safe request metadata and token-bearing ENTSO-E params for actual total load.
- Inputs: area, start, end.
- Outputs: params and safe metadata.
- Side effects: none.
- Tests: unit test verifies `A65/A16` and no flow/capacity parameters.

`fetch_actual_load_rows(...)`

- Purpose: fetch yearly actual-load chunks for SE1-SE4 through ENTSO-E.
- Inputs: token, start, end.
- Outputs: raw observations and sanitized response metadata.
- Side effects: network calls only.
- Tests: package command; parser unit tests cover XML shape.

`parse_actual_load_document(...)`

- Purpose: parse ENTSO-E XML into load observations or acknowledgement metadata.
- Inputs: XML bytes and safe request metadata.
- Outputs: observations and response summary.
- Side effects: none.
- Tests: XML fixture unit test.

`aggregate_hourly_load(...)`

- Purpose: normalize PT15M/PT30M/PT60M values to hourly mean MW.
- Inputs: raw observations.
- Outputs: canonical hourly rows.
- Side effects: none.
- Tests: subhourly aggregation unit test.

`persist_actual_load_rows(...)`

- Purpose: create/update `entsoe_consumption_area_hourly_v1` idempotently.
- Inputs: SQLite connection and hourly rows.
- Outputs: none.
- Side effects: local SQLite write.
- Tests: package command; schema helper tested.

`coverage_by_area(...)`

- Purpose: summarize train_fit/holdout coverage and missing hours.
- Inputs: canonical rows.
- Outputs: compact coverage summary.
- Side effects: none.
- Tests: helper behavior via validation tests.

`volume_sanity_by_area_season(...)`

- Purpose: compute seasonal load distributions and daily energy summaries.
- Inputs: canonical rows.
- Outputs: area-season summary.
- Side effects: none.
- Tests: package command evidence.

`old_source_comparison(...)`

- Purpose: compare ENTSO-E actual load with `physical_balance_se1_se4_hourly_v1`.
- Inputs: SQLite connection and canonical rows.
- Outputs: ratio/difference/correlation summary.
- Side effects: none.
- Tests: package command evidence and final SQLite/evidence inspection.

`write_p0054p2_evidence(...)`

- Purpose: write required compact Markdown/JSON/CSV evidence.
- Inputs: summary and compact rows.
- Outputs: evidence path map.
- Side effects: package-run file writes.
- Tests: package command.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation.
