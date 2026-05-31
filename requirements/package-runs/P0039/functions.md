# P0039 Function Design

## New Functions

### `is_m1b_clean_training_row(row)`

- Purpose: classify rows eligible for M1B and M3A_m1b training.
- Inputs: diagnostic row dictionary.
- Outputs: boolean.
- Side effects: none.
- Reason: P0039 requires normal weekdays, Saturdays, and Sundays to remain while excluding special-day contaminated rows.
- Test coverage: normal weekday/weekend included; fixed holiday and Midsummer Day excluded.

### `fit_m1b_components(rows)`

- Purpose: fit M1B, M2A, M3A_m1b, and M3B_m1b under strict train-only leakage controls.
- Inputs: diagnostic rows.
- Outputs: mutates rows with P0039 component columns.
- Side effects: row dictionaries only.
- Reason: implement the sequential M1B residual contract.
- Test coverage: M3A target and M3B target math, holdout rows not used for fitting.

### `fit_m3a_m1b_deltas(clean_train)`

- Purpose: learn temperature anomaly deltas from `actual - M1B`.
- Inputs: clean train rows.
- Outputs: target/bucket delta mapping.
- Side effects: none.
- Reason: M3A must learn from holiday-clean residuals.
- Test coverage: target formula and clean-row policy.

### `fit_m3b_m1b_deltas(train)`

- Purpose: learn special-day deltas from `actual - M1B - M3A_m1b`.
- Inputs: train rows.
- Outputs: delta and sample-stat mappings.
- Side effects: none.
- Reason: M3B must be sequentially after temperature normalization.
- Test coverage: target formula and special-day-only training rows.

### `build_p0039_matrix(rows)`

- Purpose: compute strict full-year 2025 holdout metrics.
- Inputs: diagnostic rows with P0037 and P0039 components.
- Outputs: list of metric dictionaries.
- Side effects: none.
- Reason: P0039 requires M1/M1B/chain comparisons across SE1, area diff, and recomposed SE3.
- Test coverage: variants, targets, and 8760 holdout row count.

### `persist_p0039_feature_outputs(rows, feature_db)`

- Purpose: write P0039 diagnostic tables to the local feature DB.
- Inputs: rows and SQLite DB path.
- Outputs: none.
- Side effects: creates/replaces P0039-named tables in local SQLite DB.
- Reason: package asks for named outputs without committing generated databases.
- Test coverage: not unit-tested against user DB; exercised by module run.

### `write_p0039_evidence(...)`

- Purpose: write required markdown and JSON evidence.
- Inputs: evidence directory, rows, metric matrix.
- Outputs: mapping of evidence names to paths.
- Side effects: writes package-run files.
- Reason: package workflow and P0039 evidence requirements.
- Test coverage: module run plus file existence through final verification.

## Changed Functions

None planned in existing modules. P0039 should add a new diagnostics module and tests.

## Removed Functions

None.
