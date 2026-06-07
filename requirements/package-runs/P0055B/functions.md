# P0055B function design

## New functions

`run_p0055b_analysis(...)`

- Purpose: orchestrate migration analysis, normalization, DB writes, forecasts, metrics and evidence.
- Inputs: feature DB path, evidence directory.
- Outputs: result object with status, row counts and evidence paths.
- Side effects: writes P0055B DB tables and evidence.
- Tests: full verification.

`load_aligned_decomposition_rows(feature_db)`

- Purpose: load direct SE3, P0054Y2 clusters and residual on common timestamps.
- Inputs: feature DB path.
- Outputs: aligned hourly rows with component MW and total MW.
- Side effects: none.

`monthly_allocation_rows(aligned_rows)`

- Purpose: compute observed monthly shares per component.
- Inputs: aligned hourly rows.
- Outputs: monthly allocation rows.
- Side effects: none.

`monotonicity_metrics(monthly_rows)`

- Purpose: assess one-way settlement migration readability.
- Inputs: monthly component share rows.
- Outputs: direction, slope, reversal and score metrics.
- Side effects: none.

`fit_train_share_models(monthly_rows)`

- Purpose: fit simple train-fit-only monthly linear share models.
- Inputs: monthly observed shares.
- Outputs: fitted monthly smoothed shares and reference allocation.
- Side effects: none.

`normalize_hourly_components(aligned_rows, allocation_model)`

- Purpose: create normalized components preserving total SE3 load.
- Inputs: aligned hourly rows and allocation model.
- Outputs: normalized hourly component rows and validation summary.
- Side effects: none.

`persist_p0055b_tables(feature_db, ...)`

- Purpose: write P0055B local DB tables.
- Inputs: allocation rows, normalized rows and validation rows.
- Outputs: persisted row counts.
- Side effects: writes SQLite tables.

`build_normalized_component_targets(normalized_rows)`

- Purpose: convert normalized rows to target dictionaries for forecasting.
- Inputs: normalized hourly component rows.
- Outputs: component target mapping and metadata.
- Side effects: none.

`forecast_normalized_components(...)`

- Purpose: run P0055A/P0054R-style direct, normalized component, residual and total forecasts.
- Inputs: target rows, weather rows, feature names and model specs.
- Outputs: component results, decomposition rows and metrics.
- Side effects: none.

`validate_p0055b_leakage(...)`

- Purpose: prove no forbidden features or holdout-derived migration/reference/reconciliation fitting.
- Inputs: summary structures.
- Outputs: leakage review.
- Side effects: none.

`write_p0055b_evidence(...)`

- Purpose: write required markdown/CSV/JSON evidence.
- Inputs: evidence directory and summary.
- Outputs: path mapping.
- Side effects: writes package-run evidence.

## Changed functions

None intended.

## Removed functions

None.
