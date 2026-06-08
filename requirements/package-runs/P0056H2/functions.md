# P0056H2 Function Design

## New Functions

### `run_p0056h2_static_style_lag_comparison`

- Purpose: run the full P0056H2 workflow and write DB/evidence outputs.
- Inputs: feature DB path and evidence directory.
- Outputs: result status, row counts and evidence map.
- Side effects: writes P0056H2 DB rows and package-run evidence.
- Test coverage: package execution and DB row-count verification.

### `build_static_style_modeling_rows`

- Purpose: build 36h modeling rows whose lag and rolling features are anchored at forecast origin.
- Inputs: area code, target rows, weather rows, origins and weather source.
- Outputs: modeling rows for train and forecast origins.
- Side effects: none.
- Test coverage: unit test confirms all horizons for one origin share origin-anchored lag values.

### `static_style_lag_features_at_origin`

- Purpose: compute required load lag and rolling/ramp features from origin history, matching P0056C static-style construction.
- Inputs: ordered consumption values and origin index.
- Outputs: lag/rolling feature dictionary.
- Side effects: none.
- Test coverage: unit test verifies lag values are origin-index based.

### `write_evidence`

- Purpose: write required P0056H2 Markdown/CSV/JSON evidence files.
- Inputs: summary payload.
- Outputs: path map.
- Side effects: writes files under `requirements/package-runs/P0056H2/`.
- Test coverage: package execution.

## Reused Functions

P0056H helpers reused without change:

- `origin_schedule`
- `anchored_historical_origin_schedule`
- `make_origin`
- `format_dt_utc`
- `fit_hgb`
- `predict_rows`
- `score_origin`
- `metric_scope`

P0056C helpers used as behavioral reference:

- `area_lag_features_at_origin`
- `area_rolling_features_at_origin`

## Removed Functions

None.
