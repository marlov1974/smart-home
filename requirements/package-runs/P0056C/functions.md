# Package P0056C Function Design

## Package

`P0056C`

## Scope

Multi-area LABB consumption forecast construction and evaluation.

## New functions

### `run_p0056c_multi_area_forecast()`

Purpose: Execute the full P0056C pipeline.

Inputs: Feature DB path and evidence directory.

Outputs: `P0056CResult`.

Side effects: Writes DB forecast/metrics rows and evidence files.

Reason: Package entry point.

Tests: Package execution and unit tests for sub-functions.

### `create_schema()`

Purpose: Create P0056C forecast-log and metrics tables.

Inputs: SQLite connection.

Outputs: None.

Side effects: Local feature DB schema changes for P0056C-owned tables.

Reason: Required output tables.

Tests: Package execution.

### `load_area_targets()`

Purpose: Load corrected P0056A targets per area.

Inputs: SQLite connection.

Outputs: Area to target-row mapping and source contract.

Side effects: None.

Reason: P0056C must not use old physical_balance targets.

Tests: Input contract tests/package execution.

### `load_area_weather_rows()`

Purpose: Load P0056B weather actual-proxy rows per area.

Inputs: SQLite connection.

Outputs: Area/timestamp weather mapping and weather contract.

Side effects: None.

Reason: P0056C must use area weather proxies, not SE3-only weather.

Tests: Input contract tests/package execution.

### `build_area_modeling_rows()`

Purpose: Construct 36-horizon origin-target rows for one area.

Inputs: Area code, target rows, weather rows, horizon set.

Outputs: Modeling rows with target, calendar, lag/rolling, weather, split, and internal split fields.

Side effects: None.

Reason: Area-general equivalent of the SE3 modeling matrix.

Tests: Unit tests for split/leakage and feature availability.

### `learn_area_model()`

Purpose: Fit the default area model or documented fallback.

Inputs: Area code, modeling rows, feature list, model specs.

Outputs: Area model result with predictions attached to rows.

Side effects: Appends progress evidence.

Reason: Per-area learn job.

Tests: Package execution and fallback tests.

### `evaluate_area_model()`

Purpose: Compute DayAhead, full_36h, daily energy, horizon, weekday/weekend and regime metrics.

Inputs: Area code, scored rows, prediction column.

Outputs: Area metrics and selected rows for aggregate evaluation.

Side effects: Appends progress evidence.

Reason: Per-area test job.

Tests: Unit tests for aggregate and metric helpers.

### `persist_outputs()`

Purpose: Write compact forecast-log and metrics rows.

Inputs: SQLite connection, scored rows, metrics.

Outputs: Row counts.

Side effects: Replaces P0056C-generated DB rows.

Reason: Required local DB output.

Tests: Package execution.

### `write_evidence()`

Purpose: Write all required P0056C evidence files.

Inputs: Evidence directory and summary.

Outputs: Evidence path mapping.

Side effects: Writes package-run evidence.

Reason: Package workflow requirement.

Tests: Package execution.

## Changed functions

None planned.

## Removed functions

None planned.

## Important unchanged functions

### `p0054r.fit_and_apply_horizon_bias_correction()`

Reason for no change: P0056C reuses its internal-validation-only bias correction rather than changing SE3 package behavior.

### `p0055a.fit_horizon_bias_weighted_ensemble()`

Reason for no change: P0056C will follow this pattern but own area-specific feature names and evidence.

## Design deviations during implementation

None yet.
