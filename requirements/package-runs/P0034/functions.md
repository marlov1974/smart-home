# P0034 function design

## New module

```text
src.mac.services.spotprice_ml_model
```

## Responsibilities

`default_model_dir()`

- Returns `~/.smart-home/data/spotprice_ml_models/m4`.

`load_p0033_training_series(feature_db)`

- Loads timestamp-aligned P0033 normalized SE1 and area-diff training series.

`build_calendar_features(rows)`

- Builds deterministic allowed calendar and slow-trend features.
- Excludes weather and temperature columns by construction.

`build_level_targets(rows)`

- Computes weekly, monthly and yearly means per target.

`build_curve_targets(rows, level_targets)`

- Computes intra-week price indexes and target curve rows.

`build_week_of_year_indexes(rows, level_targets)`

- Computes week-vs-year and week-within-month indexes.

`build_clipped_month_curves(rows, level_targets)`

- Builds month-only clipped week curves and renormalizes month curves to mean `1.0`.

`train_m4_target_model(rows, target, feature_names, ridge_lambda)`

- Trains one scikit-learn `PolynomialFeatures(degree=2) + Ridge(alpha=1.0)` model for one target when sklearn is available.
- Falls back to pure-Python Ridge if sklearn cannot import.

`train_m4_level_model(...)`

- Stores level diagnostics used by validation.

`train_m4_curve_model(...)`

- Stores curve/index diagnostics used by validation.

`recompose_se3_predictions(predictions)`

- Computes SE3 as SE1 plus area-diff.

`run_walk_forward_backtest(...)`

- Runs time-based train/validate/holdout scoring.

`compare_against_baselines(...)`

- Compares M4 predictions against P0033 M1 normal baselines.

`write_model_artifact_manifest(...)`

- Writes JSON model metadata, joblib estimator artifacts when sklearn is used, and artifact manifest.

`validate_m4_outputs(...)`

- Validates DB tables, artifacts, split coverage and absence of weather features.

`main(argv=None)`

- CLI entry point for feature build, training, backtest and validation.
