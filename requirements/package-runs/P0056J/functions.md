# P0056J Function Design

## New Functions

### `run_p0056j_static_vs_rolling_row_level_audit`

Purpose: Execute the SE2 row-level audit and write package evidence.

Inputs: optional feature DB and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes compact package evidence only.

Tests: exercised by package run.

### `row_key`

Purpose: Return the stable `(forecast_origin_timestamp_utc, target_timestamp_utc)` comparison key.

Inputs: row dict.

Outputs: tuple of strings.

Side effects: none.

Tests: direct unit coverage through intersection helper.

### `intersect_rows`

Purpose: Build paired static/rolling rows on common row keys.

Inputs: static rows and rolling rows.

Outputs: ordered pair rows.

Side effects: none.

Tests: direct unit coverage.

### `summarize_feature_diffs`

Purpose: Summarize numeric and categorical feature differences.

Inputs: paired feature rows and feature names.

Outputs: per-feature diff summary.

Side effects: none.

Tests: direct unit coverage.

### `select_origin_sample`

Purpose: Pick a compact representative origin set including high/low-error origins, multiple weekdays/months and late-period origins.

Inputs: rolling rows.

Outputs: selected origin ids/timestamps.

Side effects: none.

Tests: exercised by package run.

### `write_evidence`

Purpose: Create the required P0056J Markdown/CSV/JSON evidence files.

Inputs: evidence directory and summary.

Outputs: mapping of evidence file names to paths.

Side effects: writes package-run files.

Tests: exercised by package run.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

No `docs/functions/` update is planned because P0056J adds package-local audit helpers rather than a reusable runtime API.
