# P0056H Function Design

## New Functions In `p0056h.py`

- `run_p0056h_36h_walk_forward(feature_db, evidence_dir)`: orchestrates schema, input loading, origin generation, model fitting, scoring, persistence and evidence.
- `create_schema(conn)`: creates compact P0056H forecast and metric tables.
- `origin_schedule(...)`: generates every-5th-day 06:00 local origins with complete 36h target/weather coverage.
- `build_modeling_rows(...)`: builds 36h rows for historical training origins and current forecast origins.
- `classify_lag(...)`: classifies each lag as origin-known, recursive, before-origin, or forbidden future actual.
- `apply_lag_mode_features(...)`: rewrites forecast lag features according to L1 or L2 protocol.
- `fit_hgb(...)`: trains deterministic no-price HGB on rows before the current origin.
- `predict_l1(...)`: predicts all 36h rows with unavailable short lags replaced by seasonal/fallback values.
- `predict_l2_recursive(...)`: predicts horizons sequentially and feeds earlier predictions back into short lag features.
- `score_origin(...)`: computes horizon slices, 36h MAE/RMSE/bias and energy metrics.
- `aggregate_area_mode_results(...)`: computes area/mode aggregate metrics.
- `compare_static(...)`: compares 36h results with P0056C/E/F full36 baselines.
- `compare_p0056g(...)`: compares 36h results with P0056G weekly MAE.
- `leakage_review(...)`: verifies lag safety, cutoff ordering and forbidden features.
- `write_evidence(...)`: writes required P0056H evidence and compact CSV/JSON.

## Side Effects

- Writes P0056H evidence under `requirements/package-runs/P0056H/`.
- Writes compact local DB P0056H forecast/metrics tables.
- No API calls, devices, runtime changes, production activation or large model artifacts.

## Tests

- `tests/mac/test_p0056h_lag_protocol.py` covers origin schedule, lag classification and metric calculation.
