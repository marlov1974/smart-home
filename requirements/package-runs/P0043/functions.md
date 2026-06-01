# P0043 function design

## New module

`src/mac/services/spotprice_model_diagnostics/p0043.py`

## New functions

`run_p0043_training(...) -> P0043Result`

- End-to-end AI-2 training/evaluation/evidence runner.

`load_ai2_rows(feature_db) -> list[dict]`

- Loads only `ai2_hour_to_day_training_targets_v2`.
- Fails if the corrected P0042 table is missing.

`validate_dataset_contract(rows) -> dict`

- Verifies fixed-CET fields, timestamp uniqueness per target, and target field usage.

`assign_splits(rows) -> dict`

- Applies chronological train/validate/holdout split by `model_cet_date`.

`build_feature_matrix(rows, feature_group, encoder=None) -> tuple`

- Builds numeric feature matrices with deterministic categorical encoding.

`fit_baselines(train_rows) -> dict`

- Fits B0/B1/B2/B3 from train rows only.

`predict_baseline(rows, baseline) -> list[float]`

- Applies baseline predictions to any split.

`train_hgb_model(train_rows, feature_group) -> object`

- Trains bounded `HistGradientBoostingRegressor`.

`evaluate_predictions(rows, predicted) -> dict`

- Computes shape, rank, top/bottom and subset metrics.

`center_predictions_by_day(rows, predicted) -> list[float]`

- Applies deterministic per-day centering.

`write_p0043_evidence(...) -> dict`

- Writes required P0043 evidence and JSON summaries.

## Changed functions

None in existing modules. P0043 is additive.

## Removed functions

None.
