# P0049 function design

## New functions

`run_p0049_analysis(feature_db, evidence_dir)`

- Purpose: orchestrate reservoir feature construction, horizon analysis and evidence writing.
- Inputs: feature DB path, evidence directory.
- Outputs: `P0049Result`.
- Side effects: reads/writes local SQLite; writes package evidence.
- Test coverage: package verification.

`load_p0049_source_rows(feature_db)`

- Purpose: load P0048 bottleneck training dataset.
- Inputs: feature DB path.
- Outputs: row dictionaries.
- Side effects: reads local SQLite.
- Test coverage: package verification.

`validate_p0049_contract(rows)`

- Purpose: verify required columns, fixed-CET fields and spread arithmetic.
- Inputs: rows.
- Outputs: contract dictionary.
- Side effects: none.
- Test coverage: arithmetic/fixed-CET tests.

`add_daytype_features(rows)`

- Purpose: add workday, Friday/weekend/holiday and peak-hour proxy fields.
- Inputs: chronological rows.
- Outputs: mutates rows.
- Side effects: none.
- Test coverage: deterministic day-type test.

`fit_price_thresholds(train_rows)`

- Purpose: fit train-only price medians/quantiles by hour.
- Inputs: train rows.
- Outputs: threshold dictionaries.
- Side effects: none.
- Test coverage: train-only test.

`add_price_response_features(rows, thresholds)`

- Purpose: add price deltas, rolling ranks, threshold flags and hours-since/last-window threshold features.
- Inputs: rows and train-only thresholds.
- Outputs: mutates rows.
- Side effects: none.
- Test coverage: package verification.

`add_rolling_features(rows, windows)`

- Purpose: add strictly backward-looking rolling features for spread, binary regimes, prices and gradients.
- Inputs: rows and lookback windows.
- Outputs: mutates rows.
- Side effects: none.
- Test coverage: backward-looking test.

`add_reservoir_features(rows)`

- Purpose: create explicit EMA reservoir pressure indices and learned pressure score.
- Inputs: rows.
- Outputs: formula metadata and mutated rows.
- Side effects: none.
- Test coverage: reproducibility test.

`add_horizon_targets(rows, horizons)`

- Purpose: add t+H classification and severity targets.
- Inputs: rows and horizon list.
- Outputs: mutates rows.
- Side effects: none.
- Test coverage: horizon-shift test.

`evaluate_horizon_groups(rows, horizons)`

- Purpose: evaluate classification/regression metrics by horizon and feature group.
- Inputs: analysis rows and horizons.
- Outputs: metrics summary.
- Side effects: none.
- Test coverage: package verification.

`write_p0049_evidence(evidence_dir, rows, summary)`

- Purpose: write required Markdown/JSON/CSV evidence.
- Inputs: evidence directory, dataset rows and summary.
- Outputs: path map.
- Side effects: writes evidence files.
- Test coverage: package verification.

## Changed functions

None.

## Removed functions

None.
