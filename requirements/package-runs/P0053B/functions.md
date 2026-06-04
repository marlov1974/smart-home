# P0053B function design

New functions in `p0053b.py`:

- `run_p0053b_analysis(...)`
  - Purpose: package entry point for loading data, building features, fitting baselines/models, evaluating paths and writing evidence.
  - Inputs: feature DB, weather DB, evidence directory.
  - Outputs: `P0053BResult`.
  - Side effects: writes local feature DB analysis table and package evidence.
  - Tests: smoke via deterministic helper tests and package run.

- `load_consumption_source_rows(...)`
  - Purpose: read `physical_balance_se1_se4_hourly_v1` target rows.
  - Inputs: feature DB path.
  - Outputs: source row dictionaries.
  - Side effects: reads SQLite.
  - Tests: target contract validation.

- `validate_target_contract(...)`
  - Purpose: verify unique normalized timestamps, finite positive target, fixed-CET fields and range.
  - Inputs: source rows.
  - Outputs: validation dictionary.
  - Side effects: none.
  - Tests: synthetic duplicates/missing fields.

- `load_weather_rows(...)`
  - Purpose: read SE1 core historical weather rows if available.
  - Inputs: weather DB path.
  - Outputs: weather rows keyed by normalized timestamp plus contract metadata.
  - Side effects: reads SQLite.
  - Tests: feature classification tests.

- `build_direct_horizon_rows(...)`
  - Purpose: create forecast-origin/target rows for required horizons with no future-origin leakage.
  - Inputs: source rows, weather rows, horizons.
  - Outputs: modeling rows.
  - Side effects: none.
  - Tests: lag and rolling leakage tests.

- `attach_calendar_features(...)`
  - Purpose: attach known-in-advance target timestamp calendar and Swedish special-day fields.
  - Inputs: modeling row.
  - Outputs: mutates row.
  - Side effects: none.
  - Tests: split/feature checks.

- `lag_features_at_origin(...)`
  - Purpose: compute lag features from consumption values at timestamps before or equal to origin-lag.
  - Inputs: timestamp index and origin index.
  - Outputs: lag feature dictionary or null marker.
  - Side effects: none.
  - Tests: no peek past origin.

- `rolling_features_at_origin(...)`
  - Purpose: compute rolling statistics from history ending before forecast origin.
  - Inputs: source rows and origin index.
  - Outputs: rolling feature dictionary or null marker.
  - Side effects: none.
  - Tests: no target/future inclusion.

- `assign_chronological_splits(...)`
  - Purpose: assign train/validate/holdout from target fixed-CET dates.
  - Inputs: modeling rows.
  - Outputs: split count dictionary.
  - Side effects: mutates rows.
  - Tests: non-overlap and ordering.

- `fit_train_profiles(...)`
  - Purpose: fit train-only mean profiles for baselines and weather normals.
  - Inputs: train rows.
  - Outputs: profile dictionary.
  - Side effects: none.
  - Tests: validation/holdout values do not affect profiles.

- `apply_baseline_predictions(...)`
  - Purpose: compute required baseline predictions for each modeling row.
  - Inputs: rows, profiles and source timestamp map.
  - Outputs: mutates rows with baseline columns.
  - Side effects: none.
  - Tests: previous-day/week formulas.

- `feature_group_contract(...)`
  - Purpose: declare forecast safety and feature columns for G0-G6.
  - Inputs: none.
  - Outputs: contract dictionary.
  - Side effects: none.
  - Tests: no forbidden features in forecast-safe groups.

- `build_feature_matrix(...)`
  - Purpose: convert rows and a feature group into numeric matrices with deterministic one-hot encoding.
  - Inputs: rows, group and optional encoder.
  - Outputs: matrix and encoder.
  - Side effects: none.
  - Tests: reproducibility.

- `evaluate_models(...)`
  - Purpose: fit Ridge/HGB models by horizon and feature group and compute validate/holdout metrics.
  - Inputs: rows and feature groups.
  - Outputs: nested result dictionary.
  - Side effects: fits in-memory models only.
  - Tests: metrics reproducibility.

- `evaluate_baselines(...)`
  - Purpose: compute required metric tables for baseline predictions by horizon and split.
  - Inputs: rows.
  - Outputs: metrics dictionary.
  - Side effects: none.
  - Tests: metric helper tests.

- `build_path_origins(...)` and `evaluate_168h_paths(...)`
  - Purpose: build daily-origin exact 168h baseline paths and report path metrics.
  - Inputs: source rows and profiles.
  - Outputs: path summary and CSV rows.
  - Side effects: none.
  - Tests: exactly 168 hourly predictions per full origin.

- `write_p0053b_evidence(...)`
  - Purpose: write required Markdown/JSON/CSV evidence.
  - Inputs: evidence dir and summary.
  - Outputs: evidence path map.
  - Side effects: writes files.
  - Tests: package verification.

Changed functions:

- None.

Removed functions:

- None.

Durable function catalog:

- Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation because P0053B creates reusable SE1 consumption forecasting diagnostics.
