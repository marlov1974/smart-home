# P0047 function design

## New functions

`run_p0047_analysis(feature_db, evidence_dir, start_date, end_date)`

- Purpose: orchestrate P0047 loading, export, analysis and evidence writing.
- Inputs: feature DB path, evidence directory path, fixed-CET date range.
- Outputs: `P0047Result` with status, export window, row count and evidence paths.
- Side effects: reads local SQLite feature DB and writes P0047 package-run evidence.
- Test coverage: package verification plus targeted unit tests for helpers.

`load_p0047_source_rows(feature_db)`

- Purpose: load corrected P0042 AI2 v2 rows for `system_proxy_se1` and `area_diff_proxy_se3`.
- Inputs: SQLite feature DB path.
- Outputs: list of row dictionaries.
- Side effects: reads local SQLite only.
- Test coverage: validation helper tests and package verification.

`validate_p0047_contract(rows)`

- Purpose: validate fixed-CET fields and required target rows.
- Inputs: loaded row dictionaries.
- Outputs: contract dictionary.
- Side effects: none.
- Test coverage: missing-field test.

`join_spread_rows(rows, start_date, end_date)`

- Purpose: join SE1 and area-diff rows by UTC timestamp and build export rows.
- Inputs: loaded rows and fixed-CET date range.
- Outputs: ordered export rows.
- Side effects: none.
- Test coverage: arithmetic and fixed-CET date filtering tests.

`threshold_candidates(spreads)`

- Purpose: compute fixed, quantile and robust-sigma candidate threshold definitions.
- Inputs: spread values.
- Outputs: threshold dictionary.
- Side effects: none.
- Test coverage: reproducibility tests.

`assign_spread_regime(spread, thresholds)`

- Purpose: assign sign and recommended regime label for one spread.
- Inputs: spread value and selected threshold strategy.
- Outputs: sign/regime strings.
- Side effects: none.
- Test coverage: near-zero, positive/negative and spike tests.

`analyze_distribution(rows)`

- Purpose: compute overall and grouped spread distribution summaries.
- Inputs: export rows.
- Outputs: summary dictionaries.
- Side effects: none.
- Test coverage: package verification.

`analyze_persistence(rows)`

- Purpose: compute run lengths and transition matrix for regime labels.
- Inputs: export rows.
- Outputs: run-length rows and transition matrix.
- Side effects: none.
- Test coverage: deterministic run/transition test.

`analyze_signal_attribution(rows)`

- Purpose: summarize spread relation to available weather, calendar and price-level signals.
- Inputs: export rows.
- Outputs: attribution dictionaries.
- Side effects: none.
- Test coverage: package verification.

`write_p0047_evidence(evidence_dir, summary)`

- Purpose: write required P0047 Markdown, CSV and JSON evidence.
- Inputs: evidence directory and summary dictionary.
- Outputs: mapping of evidence labels to paths.
- Side effects: creates/updates P0047 evidence files.
- Test coverage: package verification.

## Changed functions

None planned.

## Removed functions

None planned.

## Unchanged but relevant functions

`p0041.percentile`, `p0041.robust_scale`, `p0041.write`

- Purpose: existing deterministic statistics and evidence helpers.
- Reason relevant: P0047 uses them to match previous package style.

`p0045.load_corrected_inputs`

- Purpose: existing loader for P0042 corrected AI1/AI2 datasets.
- Reason relevant: P0047 follows the same corrected-table contract but reads only AI2 rows.
