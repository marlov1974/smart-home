# P0054R Function Design

Status: `planned-before-code`

## New Module

`src.mac.services.spotprice_model_diagnostics.p0054r`

## Intended New Functions

`run_p0054r_analysis(...)`

- Purpose: orchestrate the P0054R corrected-target LABB experiment and evidence writing.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: `P0054RResult` with status, row counts, and evidence paths.
- Side effects: writes package-run evidence only.
- Tests: smoke through package run where practical; unit coverage for key subcontracts.

`build_p0054r_modeling_rows(...)`

- Purpose: load corrected ENTSO-E target rows and build direct/path modeling rows with P0054Q/P0054N semantics.
- Inputs: feature DB and weather DB paths.
- Outputs: source rows, direct rows, path rows, and contracts.
- Side effects: none.
- Tests: covered through target/source/leakage tests and package run.

`assign_internal_validation_splits(rows)`

- Purpose: annotate train_fit rows as `internal_train`, `internal_validation`, or `not_train_fit`.
- Inputs: modeling rows with `target_timestamp_utc` and `split`.
- Outputs: split counts.
- Side effects: mutates row dictionaries by adding `p0054r_internal_split`.
- Tests: explicit boundary test.

`fit_model_on_rows(spec, features, train_rows, predict_rows)`

- Purpose: train a cloned model on an explicit train subset and predict an explicit predict subset.
- Inputs: model spec, feature list, training rows, prediction rows.
- Outputs: fitted model, encoder, feature names, predictions, and training metadata.
- Side effects: model training in memory only.
- Tests: indirect through ensemble tests/package run.

`learn_inverse_mae_weights(validation_rows, model_keys)`

- Purpose: learn non-negative ensemble weights using only internal-validation prediction errors.
- Inputs: validation rows and model keys with attached predictions.
- Outputs: model-key-to-weight mapping and validation MAE evidence.
- Side effects: none.
- Tests: explicit unit test confirming best validation model receives largest weight and weights sum to one.

`apply_weighted_ensemble(rows, weights, output_column)`

- Purpose: attach weighted ensemble predictions to rows.
- Inputs: rows, weights keyed by model key, output column.
- Outputs: count of rows with predictions.
- Side effects: mutates rows by adding output column.
- Tests: explicit unit test.

`apply_median_ensemble(rows, model_keys, output_column)`

- Purpose: attach median ensemble predictions to rows.
- Inputs: rows, model keys, output column.
- Outputs: count of rows with predictions.
- Side effects: mutates rows by adding output column.
- Tests: explicit unit test.

`fit_and_apply_residual_correction(...)`

- Purpose: fit a residual correction model on internal-validation residuals and apply it to rows with final baseline predictions.
- Inputs: model spec, feature list, validation rows, target rows, base model key, output column.
- Outputs: correction evidence.
- Side effects: mutates target rows by adding corrected predictions.
- Tests: package-run evidence and leakage review.

`fit_and_apply_horizon_specialized(...)`

- Purpose: train one no-price model per horizon from train_fit and apply to holdout/path rows.
- Inputs: base model spec, feature list, train rows, prediction rows, output column.
- Outputs: training/checkpoint evidence.
- Side effects: mutates prediction rows by adding output column.
- Tests: package-run evidence.

`fit_and_apply_dayahead_specialized(...)`

- Purpose: train a DayAhead-only no-price model using exact 12:00 Europe/Stockholm D-1 delivery-day rows.
- Inputs: base model spec, feature list, all path rows, output column.
- Outputs: training/checkpoint evidence and selected row counts.
- Side effects: mutates DayAhead rows by adding output column.
- Tests: DayAhead timing evidence in package run.

`select_dayahead_rows_by_split(rows, split)`

- Purpose: select complete exact-origin DayAhead delivery-day rows for train_fit or holdout.
- Inputs: path rows and split name.
- Outputs: selected rows.
- Side effects: none.
- Tests: boundary/timing coverage where practical.

`validate_p0054r_leakage(...)`

- Purpose: extend P0054Q leakage review with internal-validation-only selection evidence and P0054R feature set.
- Inputs: target, feature, matrix, fairness, and advanced-method evidence.
- Outputs: leakage review dictionary.
- Side effects: none.
- Tests: forbidden feature test.

`write_p0054r_evidence(...)`

- Purpose: write all required P0054R evidence files.
- Inputs: summary and compact metrics rows.
- Outputs: evidence path mapping.
- Side effects: writes Markdown, JSON, and CSV under package-run directory.
- Tests: package run.

## Changed Functions

`docs/functions/mac/spotprice-model-diagnostics.md`

- Add durable P0054R function catalog section after implementation.

## Removed Functions

None.
