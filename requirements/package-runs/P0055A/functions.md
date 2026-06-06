# P0055A function design

## New functions

`run_p0055a_analysis(...)`

- Purpose: orchestrate P0055A loading, forecasting, aggregation, metrics, evidence and status.
- Inputs: feature DB path, evidence directory.
- Outputs: result object with status, row counts and evidence paths.
- Side effects: writes package-run evidence.
- Tests: smoke through helper unit tests and full module verification.

`load_direct_target_rows(feature_db)`

- Purpose: load corrected ENTSO-E SE3 target rows.
- Inputs: feature DB path.
- Outputs: normalized target rows keyed by UTC timestamp.
- Side effects: none.
- Tests: full module verification.

`load_component_target_rows(feature_db)`

- Purpose: load P0054Y2 cluster and residual targets, including zero cluster contract rows.
- Inputs: feature DB path.
- Outputs: component target mapping and component metadata.
- Side effects: none.
- Tests: zero-history cluster unit test.

`load_climate_zone_weather_rows(feature_db)`

- Purpose: read P0054Z long weather feature table into per-zone hourly feature dictionaries.
- Inputs: feature DB path.
- Outputs: `zone -> timestamp -> feature dict`.
- Side effects: none.
- Tests: mapping unit test and full module verification.

`build_component_modeling_rows(...)`

- Purpose: create 36h forecast-origin rows with calendar, historical component lag/rolling and mapped weather features.
- Inputs: target rows, component id, weather rows, horizons.
- Outputs: modeling rows.
- Side effects: none.
- Tests: leakage review and full module verification.

`fit_component_forecast(...)`

- Purpose: train/apply P0054R-style no-price component forecast or safe fallback.
- Inputs: component rows, component metadata, model specs.
- Outputs: forecast result with predictions, status and training evidence.
- Side effects: none.
- Tests: fallback behavior through helper tests.

`apply_zero_forecast(...)`

- Purpose: attach zero predictions for zero-history cluster rows.
- Inputs: rows and output column.
- Outputs: status/evidence.
- Side effects: mutates rows.
- Tests: zero-history unit test.

`apply_same_week_fallback(...)`

- Purpose: forecast sparse/failed components using previous-week same-hour values available before origin.
- Inputs: rows and output column.
- Outputs: status/evidence.
- Side effects: mutates rows.
- Tests: full module verification.

`aggregate_decomposition_rows(component_results)`

- Purpose: sum cluster and residual predictions into total SE3 decomposition forecast rows.
- Inputs: component forecast rows.
- Outputs: total rows with actual direct SE3 target and decomposition prediction.
- Side effects: none.
- Tests: aggregation equality unit test.

`learn_reconciliation_weights(validation_rows)`

- Purpose: learn direct/decomposition weights from internal validation only.
- Inputs: validation rows with direct/decomposition predictions and actuals.
- Outputs: weights and evidence.
- Side effects: none.
- Tests: holdout-exclusion unit test.

`compute_total_metrics(rows, prediction_column)`

- Purpose: compute required DayAhead/full_36h/daily-energy and regime metrics.
- Inputs: scored rows and prediction column.
- Outputs: metrics dictionaries.
- Side effects: none.
- Tests: full module verification.

`validate_p0055a_leakage(summary)`

- Purpose: enforce no forbidden target/features/holdout fitting.
- Inputs: summary/evidence structures.
- Outputs: review dict.
- Side effects: none.
- Tests: forbidden feature unit test.

`write_p0055a_evidence(evidence_dir, summary)`

- Purpose: write required markdown/CSV/JSON package evidence.
- Inputs: evidence directory and summary.
- Outputs: path mapping.
- Side effects: writes files under `requirements/package-runs/P0055A/`.
- Tests: full module verification.

## Changed functions

None intended.

## Removed functions

None.
