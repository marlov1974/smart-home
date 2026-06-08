# P0056E Function Design

## New Functions

### `run_p0056e_variant_test`

- Purpose: orchestrate P0056E input loading, variant execution, metrics, persistence and evidence.
- Inputs: feature DB path, evidence dir.
- Outputs: `P0056EResult`.
- Side effects: writes P0056E SQLite tables and package-run evidence.
- Test coverage: runner-level smoke through package execution and unit tests for pure helpers.

### `variant_specs`

- Purpose: define deterministic P0056E variant metadata.
- Inputs: none.
- Outputs: ordered list of variant definitions.
- Side effects: none.
- Test coverage: required variant ids and forbidden feature terms.

### `p0056d_weather_rows`

- Purpose: load SE1/SE2 P0056D Open-Meteo weather features in P0056C-compatible shape.
- Inputs: SQLite connection.
- Outputs: area-to-timestamp weather row map plus contract.
- Side effects: none.
- Test coverage: contract and label checks.

### `feature_groups`

- Purpose: map package feature-group names to P0056C-compatible feature name subsets.
- Inputs: none.
- Outputs: feature-group dictionary.
- Side effects: none.
- Test coverage: no forbidden market features; groups include required lag/weather families.

### `fit_variant`

- Purpose: train one variant using only train_fit/internal validation and attach predictions.
- Inputs: area, rows, variant, available model specs.
- Outputs: training result and prediction column.
- Side effects: mutates copied variant rows with prediction columns.
- Test coverage: split/leakage tests and package execution.

### `apply_internal_validation_regime_correction`

- Purpose: implement V8 segmented correction from internal validation residuals only.
- Inputs: rows, base prediction column.
- Outputs: correction evidence.
- Side effects: writes corrected prediction column to rows.
- Test coverage: unit test confirms holdout rows are not used to learn correction.

### `compare_against_baselines`

- Purpose: compare variants against best current P0056C/P0056D baseline per area.
- Inputs: variant metric rows.
- Outputs: comparison rows and decision summary.
- Side effects: none.
- Test coverage: decision threshold unit test.

### `write_evidence`

- Purpose: produce all required P0056E package-run evidence files.
- Inputs: evidence dir and summary.
- Outputs: path map.
- Side effects: writes markdown, CSV and JSON evidence.
- Test coverage: package execution and required-file verification.

## Changed Functions

None planned outside new P0056E module.

## Removed Functions

None.

## Cross-Package Function Catalog

No durable function catalog update is planned unless P0056E helpers are later promoted for reuse beyond package-local diagnostics.
