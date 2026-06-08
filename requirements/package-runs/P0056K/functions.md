# P0056K Function Design

## New Functions

### `run_p0056k_realistic_dayahead_restart`

Purpose: Execute the long-running realistic DayAhead model comparison.

Inputs: feature DB path and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes package evidence/progress files.

### `dayahead_origins`

Purpose: Build D-1 12:00 Europe/Stockholm forecast origins for complete delivery days.

Inputs: target/weather contracts.

Outputs: origin descriptors.

Side effects: none.

### `build_dayahead_rows`

Purpose: Build forecast-safe DayAhead target rows with DA-L3 seasonal-safe load features.

Inputs: area, target rows, weather rows, origins.

Outputs: modeling rows.

Side effects: none.

### `train_predict_origin_model`

Purpose: Fit one model family for one area/origin and predict the 24h delivery block.

Inputs: train rows, forecast rows, model specification and feature list.

Outputs: prediction rows and runtime metrics.

Side effects: none.

### `append_progress`

Purpose: Persist progress lines and job status so long runs are easy to poll.

Inputs: evidence directory, status payload.

Outputs: none.

Side effects: writes `progress-log.md`, `job-status.csv`, `job-status.md`.

### `status_report`

Purpose: Print current P0056K progress without running models.

Inputs: evidence directory.

Outputs: short text/JSON status.

Side effects: none.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

No `docs/functions/` update is planned for this package-local LABB runner.
