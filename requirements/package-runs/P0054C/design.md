# P0054C Implementation Design

Package: P0054C
Label: LABB

## Interpretation

P0054C repeats P0054B for SE4 consumption. It asks whether the P0054B pattern, where small MLP beat HGB without price input, generalizes to SE4.

The result is LABB learning only. It creates no deployable model artifact and no runtime behavior.

## Implementation Structure

Add a package module:

`src/mac/services/spotprice_model_diagnostics/p0054c.py`

Add package tests:

`tests/mac/services/spotprice_model_diagnostics/test_p0054c.py`

Write evidence under:

`requirements/package-runs/P0054C/`

## Dataset Construction

The source target is `physical_balance_se1_se4_hourly_v1.consumption_se4`.

For each forecast origin and direct horizon, create rows when:

- target timestamp is at or after `2022-06-01T00:00Z`;
- enough pre-origin history exists for all SE4 lags and rollups;
- target timestamp exists locally.

Warmup rows before `2022-06-01` may feed lags but are never train/validation/holdout targets.

## Feature Groups

Implement:

- `G0_calendar_only`
- `G1_calendar_plus_load_lags`
- `G2_calendar_plus_load_lags_rollups`
- `G3_calendar_weather_proxy`
- `G4_calendar_load_lags_rollups_weather_proxy`

Load features are strictly pre-origin. Calendar features are deterministic from target timestamp. Weather features are archive proxy features from `weather_area_hourly` where `area_proxy = south_connected_weather`, labeled `weather_actual_as_forecast_proxy`.

## Models

Benchmark:

- `HistGradientBoostingRegressor`

Advanced model:

- deterministic `MLPRegressor`, same family as P0054B.

Both use G4 features and identical validation/holdout row sets. Holdout is not used for model selection.

## Weekly Paths

Weekly 168h paths use complete holdout origins from `2025-06-01T00:00Z`, every 168 hours, where all horizons 1..168 exist.

## Evidence

The module writes all required markdown files, a compact summary JSON, direct-row sample CSV, weekly path CSV and a forecast-origin log with the required columns:

- `forecast_origin_timestamp_utc`
- `input_data_cutoff_utc`
- `target_timestamp_utc`
- `horizon_hours`
- `area_or_target`
- `predicted_price_or_index`
- `prediction_kind`

Because P0054C predicts consumption, `prediction_kind` explicitly says the value is LABB consumption MW, not price or index.

## Test Strategy

Tests cover:

- SE4 lag/rollup features are pre-origin only.
- Feature contract excludes forbidden price/grid/production inputs.
- Weekly origin selection requires complete paths.
- HGB/MLP identical row-set validation.

Verification runs:

- unit tests;
- syntax compile with pycache redirected to `/private/tmp`;
- end-to-end module run;
- `git diff --check`.

## Risks

- Weather proxy is broad south-connected weather, not SE4-specific forecast weather.
- MLP is not sequence-aware, but sequence runtimes are unavailable and the package requests comparable P0054B MLP.
- Results are LABB-only and must not be promoted to G2-KANDIDAT.
