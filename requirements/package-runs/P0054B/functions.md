# P0054B Function Design

Package: P0054B
Label: LABB

## New Module Functions

`run_p0054b_analysis(feature_db, weather_db, evidence_dir)`

- Purpose: orchestrate the offline LABB experiment.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: result object with status, row counts and evidence paths.
- Side effects: writes package evidence and package-scoped CSV/JSON outputs.
- Tests: indirectly by module run and targeted helper tests.

`load_se3_consumption_rows(feature_db)`

- Purpose: read SE3 consumption target rows from the local feature DB.
- Inputs: SQLite path.
- Outputs: normalized list of hourly source rows.
- Side effects: none.
- Tests: covered by end-to-end run.

`normalize_source_row(row)`

- Purpose: normalize timestamps and fixed-CET calendar fields.
- Inputs: SQLite row dictionary.
- Outputs: normalized row dictionary.
- Side effects: none.
- Tests: covered by helper and end-to-end behavior.

`validate_target_contract(rows)`

- Purpose: verify target availability, unit, uniqueness and finite positive values.
- Inputs: normalized source rows.
- Outputs: contract dictionary.
- Side effects: none.
- Tests: end-to-end evidence.

`load_weather_proxy_rows(weather_db)`

- Purpose: read SE3 weather proxy rows from local weather DB.
- Inputs: SQLite path.
- Outputs: timestamp-indexed weather feature dictionary plus contract.
- Side effects: none.
- Tests: end-to-end evidence.

`build_direct_horizon_rows(source_rows, weather_rows, horizons)`

- Purpose: build forecast-origin rows for direct horizon modeling.
- Inputs: source rows, weather proxy rows, horizons.
- Outputs: modeling row dictionaries.
- Side effects: none.
- Tests: helper test validates origin-strict lag behavior.

`attach_calendar_features(row, target_model_dt)`

- Purpose: add deterministic target-time calendar features.
- Inputs: row dictionary and target fixed-CET datetime.
- Outputs: mutates row.
- Side effects: row mutation only.
- Tests: end-to-end evidence.

`lag_features_at_origin(values, origin_index)`

- Purpose: compute historical load lags strictly before forecast origin.
- Inputs: ordered target values and origin index.
- Outputs: lag feature dictionary.
- Side effects: none.
- Tests: unit test.

`rolling_features_at_origin(values, origin_index)`

- Purpose: compute historical load rollups and ramps strictly before forecast origin.
- Inputs: ordered target values and origin index.
- Outputs: rollup feature dictionary.
- Side effects: none.
- Tests: unit test.

`assign_global_splits(rows)`

- Purpose: assign train/validation/holdout by target timestamp using global split policy.
- Inputs: modeling rows.
- Outputs: split counts; mutates row split field.
- Side effects: row mutation only.
- Tests: end-to-end evidence.

`fit_train_profiles(train_rows)`

- Purpose: fit train-only calendar and seasonal profiles.
- Inputs: train rows only.
- Outputs: profile dictionaries.
- Side effects: none.
- Tests: end-to-end evidence.

`apply_baseline_predictions(rows, profiles, source_by_ts)`

- Purpose: add B0-B4 baseline predictions without future target leakage.
- Inputs: modeling rows, train-only profiles, source row lookup.
- Outputs: mutates rows with prediction columns.
- Side effects: row mutation only.
- Tests: end-to-end metrics and leakage evidence.

`feature_group_contract()`

- Purpose: return P0054B allowed feature groups and input classifications.
- Inputs: none.
- Outputs: feature group dictionary.
- Side effects: none.
- Tests: forbidden feature unit test.

`evaluate_baselines(rows)`

- Purpose: score required baselines by horizon and split.
- Inputs: modeled rows.
- Outputs: metrics dictionary.
- Side effects: none.
- Tests: end-to-end evidence.

`fit_hgb_benchmark(rows, features)`

- Purpose: train deterministic HGB benchmark on train split and score validation/holdout.
- Inputs: rows and features.
- Outputs: model result, predictions and feature importance.
- Side effects: none.
- Tests: end-to-end evidence.

`fit_advanced_mlp(rows, features)`

- Purpose: train deterministic small MLP advanced AI on the same row set and features as HGB.
- Inputs: rows and features.
- Outputs: model result and predictions.
- Side effects: none.
- Tests: end-to-end evidence.

`build_feature_matrix(rows, features, encoder=None)`

- Purpose: encode/scalewise numeric and categorical model features.
- Inputs: rows, feature names, optional existing encoder.
- Outputs: NumPy matrix, encoder, feature names.
- Side effects: none.
- Tests: end-to-end model run.

`regression_metric_from_predictions(rows, pred)`

- Purpose: compute regression metrics.
- Inputs: rows and predictions.
- Outputs: metric dictionary.
- Side effects: none.
- Tests: end-to-end evidence.

`select_weekly_holdout_origins(scored_rows)`

- Purpose: select every seventh complete 168h holdout forecast path from forecast origins on or after `2025-06-01T00:00Z`.
- Inputs: scored direct horizon rows.
- Outputs: weekly origin selection metadata.
- Side effects: none.
- Tests: unit test.

`evaluate_weekly_168h_paths(scored_rows, model_names)`

- Purpose: compute weekly path metrics for HGB and MLP.
- Inputs: scored rows and model prediction columns.
- Outputs: path metrics and path-level rows.
- Side effects: none.
- Tests: unit test for origin selection and end-to-end evidence.

`evaluate_conditional_regimes(scored_rows, model_names)`

- Purpose: score validation/holdout subsets by conditional regimes.
- Inputs: scored rows and prediction columns.
- Outputs: conditional metrics.
- Side effects: none.
- Tests: end-to-end evidence.

`write_p0054b_evidence(evidence_dir, rows, summary, scored_rows, path_rows)`

- Purpose: write all required P0054B evidence artifacts.
- Inputs: evidence path, datasets and summary.
- Outputs: file map.
- Side effects: writes Markdown, CSV and JSON evidence.
- Tests: module run verifies artifacts exist.

## Removed Functions

None.

## Durable Function Catalog

No durable cross-package function catalog entry is planned. P0054B is LABB-only and does not introduce a shared API contract.
