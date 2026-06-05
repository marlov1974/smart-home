# P0054L2 Function Design

## New Functions

`run_p0054l2_analysis(...)`

- Purpose: orchestrate source loading, baseline evaluation, serial model training, checkpoint writing, comparison, optional forecast-log persistence and evidence output.
- Inputs: local feature DB path and evidence directory.
- Outputs: result object with status, row counts and evidence paths.
- Side effects: writes package-run evidence and may write a local SQLite forecast log if learning threshold is met.
- Test coverage: exercised by the module command and helper unit tests.

`load_se3_price_rows(...)`

- Purpose: load reconstructed SE3 absolute price rows from the canonical P0054K source.
- Inputs: feature DB path.
- Outputs: ordered row dictionaries with normalized timestamps and price fields.
- Side effects: none.
- Test coverage: source contract verified during package command.

`build_price_forecast_examples(...)`

- Purpose: build direct 168h forecast-origin examples with strict pre-origin historical price features.
- Inputs: reconstructed price rows and horizon set.
- Outputs: modeling rows with features, target price and split fields.
- Side effects: none.
- Test coverage: unit test verifies feature source timestamps are before origin.

`price_history_features_at_origin(...)`

- Purpose: derive lag, rolling and recent-ramp price features using only timestamps before `forecast_origin_timestamp_utc`.
- Inputs: origin timestamp, target timestamp, price lookup.
- Outputs: feature dictionary plus source timestamp audit.
- Side effects: none.
- Test coverage: unit test verifies source timestamp ordering and no target-window feature use.

`validate_feature_matrix_safety(...)`

- Purpose: reject forbidden feature names and source timestamps that violate forecast-origin ordering.
- Inputs: modeling rows and feature names.
- Outputs: leakage/safety review dictionary.
- Side effects: none.
- Test coverage: unit test verifies forbidden terms are caught.

`fit_serial_model(...)`

- Purpose: train one model family and evaluate internal validation/holdout predictions.
- Inputs: model spec, rows and feature list.
- Outputs: model result with metrics, predictions and training metadata.
- Side effects: none.
- Test coverage: runtime package command.

`write_model_checkpoint(...)`

- Purpose: persist compact evidence immediately after a model completes, fails or is skipped.
- Inputs: evidence directory, model name and checkpoint dictionary.
- Outputs: paths written.
- Side effects: writes Markdown and JSON checkpoint files.
- Test coverage: unit test verifies files are created.

`evaluate_direct_metrics(...)`, `evaluate_weekly_path_metrics(...)`, `evaluate_ranking_spike_ramp_metrics(...)`

- Purpose: compute broad, path and ranking/extreme price forecast metrics.
- Inputs: scored rows and prediction column.
- Outputs: metric dictionaries.
- Side effects: none.
- Test coverage: unit tests cover small deterministic ranking/spike behavior.

`persist_advanced_forecast_log(...)`

- Purpose: write the recommended holdout-safe advanced forecast log when learning threshold is met.
- Inputs: feature DB path, model result rows and model metadata.
- Outputs: row count.
- Side effects: writes SQLite table `advanced_spotprice_forecast_log_p0054l2_se3_v1`.
- Test coverage: runtime verification when a recommended model exists.

`write_p0054l2_evidence(...)`

- Purpose: write required package-run Markdown/JSON summaries.
- Inputs: evidence directory and summary dictionary.
- Outputs: map of evidence paths.
- Side effects: writes package-run evidence files.
- Test coverage: runtime package command.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

Update `docs/functions/mac/spotprice-model-diagnostics.md` with a P0054L2 section after implementation.
