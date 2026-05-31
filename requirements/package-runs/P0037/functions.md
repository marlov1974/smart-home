# P0037 function design

## New module

`src/mac/services/spotprice_model_diagnostics/p0037.py`

## Functions

### `run_p0037_analysis`

Runs the full analysis and writes package-run evidence.

### `load_diagnostic_rows`

Loads joined price/weather rows from local SQLite sources.

### `fit_m1_surface` / `predict_m1`

Fits and applies train-only M1 median surfaces.

### `fit_m2_signal_normals` / `predict_m2_normal`

Fits train-only climate normals for required M3A anomaly signals and applies them to all rows.

### `fit_m3a_deltas` / `fit_m3b_deltas`

Fits train-only component deltas and applies them to all rows.

### `train_m4_models`

Trains bounded HGB residual candidates per target with 2024 validation selection.

### `build_component_matrix`

Builds Mode A and Mode B ablation metrics for SE1, area_diff and recomposed SE3.

### `write_evidence`

Persists required P0037 Markdown/JSON evidence files.

## Tests

Fixture tests cover full-year row counting, strict holdout exclusion, ablation row consistency, SE3 recomposition, matrix shape and subset metrics.
