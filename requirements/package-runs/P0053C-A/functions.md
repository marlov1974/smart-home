# P0053C-A Function Design

## New Functions

### `run_p0053ca_rebuild(...)`

- Purpose: orchestrate P0053C-A rebuild, metrics, forecast-origin log and evidence.
- Inputs: feature DB path, evidence dir.
- Outputs: result dataclass with status, metrics and evidence paths.
- Side effects: writes package evidence and local SQLite forecast-origin log.
- Tests: smoke/rebuild unit tests use small synthetic rows for helper functions.

### `assign_policy_splits(rows, timestamp_field)`

- Purpose: assign canonical P0053C splits to hourly target rows.
- Inputs: rows and timestamp field name.
- Outputs: split counts.
- Side effects: mutates row `split`.
- Tests: split-boundary tests.

### `filter_ai2_policy_rows(rows)`

- Purpose: exclude AI-2 scored target rows before the global modeling start.
- Inputs: AI-2 rows.
- Outputs: filtered rows.
- Side effects: none.
- Tests: no pre-start target rows test.

### `assign_ai1_policy_splits(rows)`

- Purpose: classify AI-1 daily rows using the first UTC hour represented by the fixed-CET model date.
- Inputs: AI-1 rows.
- Outputs: split counts.
- Side effects: mutates row `split`.
- Tests: helper covered through rebuild fixtures.

### `build_policy_forecast_windows(ai1_rows, ai2_rows)`

- Purpose: create exact 168h windows with all target timestamps in one canonical split.
- Inputs: policy-filtered AI-1/AI-2 rows.
- Outputs: window dictionaries.
- Side effects: none.
- Tests: boundary-crossing windows are excluded.

### `build_forecast_origin_log_rows(...)`

- Purpose: emit holdout selected-formula prediction rows with forecast-origin metadata.
- Inputs: windows, selected formulas, regenerated predictions.
- Outputs: log rows.
- Side effects: none.
- Tests: required columns and timestamp ordering.

### `persist_forecast_origin_log(...)`

- Purpose: write compact local SQLite forecast-origin log table.
- Inputs: feature DB path and log rows.
- Outputs: persisted row count.
- Side effects: replaces P0053C-A local table.
- Tests: covered indirectly by rebuild verification.

## Changed Functions

None in P0043/P0044/P0045. P0053C-A wraps existing functions instead of modifying historical package modules.

## Function Catalog

Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation because the P0053C-A forecast-origin log becomes a durable cross-package interface for future consumption response tests.
