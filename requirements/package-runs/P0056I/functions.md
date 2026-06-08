# P0056I Function Design

## New Functions

### `run_p0056i_train_window_sensitivity`

Purpose: Execute the SE2 train-window sensitivity experiment and write package evidence.

Inputs: optional feature DB path and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes P0056I package-owned DB rows and evidence files.

Tests: exercised by package run; supporting pure helpers covered by unit tests.

### `train_window_start_utc`

Purpose: Compute the train-start timestamp for `TW2`, `TW3` and `TWX`.

Inputs: variant id and forecast origin UTC timestamp.

Outputs: UTC timestamp string.

Side effects: none.

Tests: direct unit coverage.

### `filter_train_rows_for_window`

Purpose: Select rows with `train_start <= target_timestamp_utc < forecast_origin_timestamp_utc`.

Inputs: base modeling rows, origin UTC timestamp and variant definition.

Outputs: filtered list of row copies.

Side effects: none.

Tests: direct unit coverage.

### `aggregate_window_results`

Purpose: Aggregate origin-level scores by training-window variant.

Inputs: origin result rows.

Outputs: summary rows including MAE, energy error, bias, weekday split and monthly split.

Side effects: none.

Tests: exercised by package run.

### `write_evidence`

Purpose: Create the required P0056I Markdown/CSV/JSON evidence files.

Inputs: evidence directory and summary object.

Outputs: mapping of evidence file names to paths.

Side effects: writes package-run files.

Tests: exercised by package run.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

No update to `docs/functions/` is planned because P0056I adds package-local diagnostics rather than a reusable runtime contract.
