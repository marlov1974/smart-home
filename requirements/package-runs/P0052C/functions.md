# P0052C function design

## New functions

`run_p0052c_analysis(feature_db=..., evidence_dir=...)`

- Purpose: orchestrate token safety, local data loading, ratio analysis, classification and evidence writing.
- Inputs: feature DB path and evidence directory.
- Outputs: result dataclass with status, row counts and evidence paths.
- Side effects: writes package-run evidence only.
- Test coverage: unit tests and live local verification.

`load_entsoe_hourly_rows(conn, windows)`

- Purpose: read P0052B ENTSO-E A09/A11/A61 rows for sanity-check windows.
- Inputs: SQLite connection and window definitions.
- Outputs: normalized row dictionaries.
- Side effects: none.
- Test coverage: exercised through analysis tests.

`build_ratio_observations(rows, windows)`

- Purpose: join capacity to scheduled exchange and physical flow by timestamp/from/to/border/contract.
- Inputs: row dictionaries and windows.
- Outputs: ratio observations and missing-count records.
- Side effects: none.
- Test coverage: ratio grouping and missing-value tests.

`ratio_metrics(observations, missing_counts)`

- Purpose: summarize ratios per contract/border/direction/comparison/window/era.
- Inputs: ratio observations and missing counts.
- Outputs: metric rows.
- Side effects: none.
- Test coverage: percentile and violation tests.

`classify_contract_types(metric_rows)`

- Purpose: classify A61 A02/A03/A04 suitability as market/physical capacity proxies.
- Inputs: metric rows.
- Outputs: classification dictionary.
- Side effects: none.
- Test coverage: deterministic classification tests.

`flow_based_era(timestamp_utc)`

- Purpose: split timestamps into pre/post Nordic flow-based go-live.
- Inputs: UTC timestamp string/datetime.
- Outputs: `pre_flow_based` or `post_flow_based`.
- Side effects: none.
- Test coverage: boundary test.

`safe_ratio(flow_or_exchange, capacity)`

- Purpose: compute `abs(flow_or_exchange) / capacity` or return null reason.
- Inputs: flow/exchange and capacity.
- Outputs: ratio plus reason.
- Side effects: none.
- Test coverage: null/zero/negative tests.

`write_p0052c_evidence(evidence_dir, summary)`

- Purpose: write required Markdown/JSON/CSV evidence without secrets.
- Inputs: evidence directory and summary.
- Outputs: file path mapping.
- Side effects: writes evidence.
- Test coverage: no-token scan after verification.

## Changed functions

None planned. P0052C should not alter P0052B ingestion behavior.

## Removed functions

None.
