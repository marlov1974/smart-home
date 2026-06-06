# P0054S Function Design

Status: `planned-before-code`

## New Module

`src.mac.services.spotprice_model_diagnostics.p0054s`

## Intended New Functions

`run_p0054s_analysis(...)`

- Purpose: orchestrate the advanced SE3 spot-price LABB experiment.
- Inputs: feature DB path and evidence directory.
- Outputs: `P0054SResult` with status, row counts, evidence paths.
- Side effects: writes package-run evidence; may create a holdout-safe forecast log only if threshold is met.

`assign_internal_validation_splits(rows)`

- Purpose: annotate examples as internal train, internal validation, or not train_fit.
- Inputs: examples with `split` and `target_timestamp_utc`.
- Outputs: split counts.
- Side effects: mutates row dictionaries.
- Tests: boundary unit test.

`fit_model_on_rows(spec, feature_names, train_rows, predict_rows)`

- Purpose: train a cloned model spec on explicit rows and predict explicit rows.
- Inputs: model spec, feature names, training rows, prediction rows.
- Outputs: model, standardizer, predictions and training metadata.
- Side effects: in-memory model training only.

`learn_inverse_mae_weights(validation_rows, model_names)`

- Purpose: fit ensemble weights using only internal-validation prediction errors.
- Inputs: validation rows and model names.
- Outputs: weights and evidence.
- Side effects: none.
- Tests: weight sum and best-model preference.

`apply_weighted_ensemble(rows, weights, output_column)`

- Purpose: attach weighted ensemble predictions.
- Inputs: rows, weights keyed by model name, output column.
- Outputs: count of predictions attached.
- Side effects: mutates rows.
- Tests: explicit unit test.

`apply_median_ensemble(rows, model_names, output_column)`

- Purpose: attach median ensemble predictions.
- Inputs: rows, model names, output column.
- Outputs: count of predictions attached.
- Side effects: mutates rows.

`fit_linear_stack(validation_rows, model_names)`

- Purpose: fit a deterministic linear blend on internal-validation predictions only.
- Inputs: validation rows and model names.
- Outputs: stack coefficients and evidence.
- Side effects: none.

`apply_linear_stack(rows, coefficients, output_column)`

- Purpose: attach stacked blend predictions.
- Inputs: rows, coefficient payload, output column.
- Outputs: count of predictions attached.
- Side effects: mutates rows.

`fit_and_apply_residual_correction(...)`

- Purpose: fit residual correction on internal-validation residuals and apply to holdout predictions.
- Inputs: model spec, feature names, validation rows, target rows, base model name, output column.
- Outputs: correction evidence.
- Side effects: mutates target rows.

`fit_and_apply_horizon_bucket_specialized(...)`

- Purpose: train one model per horizon bucket and predict holdout rows.
- Inputs: model spec, feature names, train rows, target rows, output column.
- Outputs: bucket evidence.
- Side effects: mutates target rows.

`fit_and_apply_horizon_bias_correction(...)`

- Purpose: learn per-horizon mean bias from internal validation and apply to predictions.
- Inputs: validation rows, target rows, base model name, output column.
- Outputs: correction evidence.
- Side effects: mutates target rows.

`select_dayahead_rows_by_split(rows, split)`

- Purpose: select complete 12:00 Europe/Stockholm D-1 delivery-day price rows.
- Inputs: examples and split.
- Outputs: selected rows.
- Side effects: none.

`evaluate_dayahead_price_metrics(rows, prediction_columns)`

- Purpose: compute DayAhead price metrics for completed models.
- Inputs: selected rows and prediction columns.
- Outputs: metrics dictionary.
- Side effects: none.

`forecast_log_decision(...)`

- Purpose: decide whether P0054S creates/recommends a holdout-safe forecast log.
- Inputs: model comparison and scored rows.
- Outputs: forecast log summary.
- Side effects: optional local SQLite write if threshold is met.

`validate_p0054s_leakage(...)`

- Purpose: combine P0054L2 matrix safety with P0054S tuning/evidence checks.
- Inputs: matrix review, target contract and method evidence.
- Outputs: leakage review.
- Side effects: none.
- Tests: forbidden feature/tuning flags.

`write_p0054s_evidence(...)`

- Purpose: write required Markdown/JSON/CSV evidence.
- Inputs: summary and compact metric rows.
- Outputs: path map.
- Side effects: writes package-run evidence.

## Changed Functions

`docs/functions/mac/spotprice-model-diagnostics.md`

- Add P0054S current function catalog after implementation.

## Removed Functions

None.
