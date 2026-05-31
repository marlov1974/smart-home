# P0038 function design

## Changed functions

### `weather_history.storage.initialize_schema`

Adds deterministic P0038 wind/solar proxy location definitions.

## New functions

### `run_p0038_analysis`

Runs the full P0038 diagnostic and writes evidence.

### `solar_generation_proxy`

Builds a conservative radiation/cloud solar production proxy.

### `wind_power_proxy`

Builds a capped nonlinear wind power proxy from `wind_speed_100m`.

### `fit_apply_m3c_m3d`

Fits train-only M3C/M3D anomaly deltas and applies them to all splits.

### `fit_apply_m4_area_only`

Trains diagnostic M4 area_diff only and keeps SE1 zero-gated.

### `persist_feature_db_outputs`

Writes local generated `m3c_solar_delta`, `m3d_wind_delta` and `m3abcd_normalized_prices` tables.
