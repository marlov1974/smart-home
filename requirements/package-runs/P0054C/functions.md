# P0054C Function Design

Package: P0054C
Label: LABB

P0054C intentionally mirrors the P0054B function shape with SE4 target semantics.

## New Functions

`run_p0054c_analysis(feature_db, weather_db, evidence_dir)`

- Orchestrates the offline LABB run and evidence writing.
- Side effects: writes P0054C evidence only.

`load_se4_consumption_rows(feature_db)`

- Reads and normalizes `consumption_se4` from `physical_balance_se1_se4_hourly_v1`.
- Side effects: none.

`normalize_source_row(row)`

- Normalizes timestamps and fixed-CET calendar fields.
- Side effects: none.

`validate_target_contract(rows)`

- Verifies target coverage, uniqueness, finite positive values and summary stats.
- Side effects: none.

`load_weather_proxy_rows(weather_db)`

- Reads `weather_area_hourly` for `south_connected_weather` and exposes broad LABB weather proxy features.
- Side effects: none.

`build_direct_horizon_rows(source_rows, weather_rows, horizons)`

- Builds direct horizon rows from forecast origins without target leakage.
- Side effects: none.

`build_weekly_path_candidate_rows(source_rows, weather_rows)`

- Builds complete weekly 168h holdout path rows from deterministic weekly origins.
- Side effects: none.

`attach_calendar_features(row, target_model_dt)`

- Adds deterministic target calendar fields.
- Side effects: mutates row.

`lag_features_at_origin(values, origin_index)`

- Adds SE4 lags strictly before forecast origin.
- Side effects: none.

`rolling_features_at_origin(values, origin_index)`

- Adds SE4 rollups and ramps strictly before forecast origin.
- Side effects: none.

`assign_global_splits(rows)`

- Assigns train/validation/holdout by target timestamp.
- Side effects: mutates rows.

`fit_train_profiles(train_rows)`

- Fits train-only profile baselines and weather normal proxy.
- Side effects: none.

`apply_profile_features(rows, profiles)`

- Adds profile-derived proxy features.
- Side effects: mutates rows.

`apply_baseline_predictions(rows, profiles, source_by_ts)`

- Adds B0-B4 forecast-safe baseline predictions.
- Side effects: mutates rows.

`feature_group_contract()`

- Returns P0054C feature groups and input classification.
- Side effects: none.

`validate_feature_contract(contract)`

- Rejects forbidden price, production, flow/export/import, A61 and related features.
- Side effects: none.

`fit_hgb_benchmark(rows, features)`

- Trains and scores deterministic HGB.
- Side effects: none.

`fit_advanced_mlp(rows, features)`

- Trains and scores deterministic sklearn MLP.
- Side effects: none.

`fit_model(rows, features, model, model_class)`

- Shared train/validate/holdout fitting helper.
- Side effects: none.

`build_feature_matrix(rows, features, encoder=None)`

- Encodes numeric and categorical features with train-fitted scaling.
- Side effects: none.

`evaluate_baselines`, `evaluate_direct_horizons`, `evaluate_weekly_168h_paths`, `evaluate_conditional_regimes`

- Produce package metrics.
- Side effects: none.

`write_p0054c_evidence(evidence_dir, rows, path_candidate_rows, weekly_path_rows, summary)`

- Writes required markdown, JSON and CSV evidence.
- Side effects: P0054C evidence files only.

## Changed Functions

None in existing modules.

## Removed Functions

None.

## Durable Function Catalog

No durable cross-package function catalog update is planned. This is a package-local LABB module with no shared runtime API.
