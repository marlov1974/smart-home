# P0036 function design

## New functions

### `load_m3ab_source_rows`

Purpose: Load M3AB normalized rows plus raw actuals and compatibility full-period M1 columns.

Inputs: feature DB path.

Outputs: list of source row dictionaries.

Side effects: reads local SQLite only.

Tests: fixture DB end-to-end tests.

### `compute_train_only_m1_predictions`

Purpose: Fit M1-like normal surfaces from training rows only and apply to all splits.

Inputs: source rows, target field names.

Outputs: mapping by UTC hour and target.

Side effects: none.

Tests: validate/holdout row changes must not change fitted training-only predictions.

### `build_train_only_m1_surface`

Purpose: Internal robust median bucket builder using iso-week +/- 2, same weekday/hour, fallback same hour.

Inputs: training rows, target field.

Outputs: callable/mapping for predictions.

Side effects: none.

Tests: direct fixture checks for holdout prediction availability.

### `train_hgb_candidate_grid`

Purpose: Train bounded HGB candidates per target and select by validation MAE.

Inputs: feature rows, target column, feature matrix, candidate parameter grid.

Outputs: selected model metadata and candidate timing rows.

Side effects: imports scikit-learn.

Tests: HGB trains on fixture data with bounded parameters.

### `evaluate_p0036_quality_gate`

Purpose: Classify PASS/WARN/STOP and decide whether promotion is allowed.

Inputs: predictions and baseline metrics.

Outputs: quality gate dictionary.

Side effects: none.

Tests: failed/WARN candidate does not promote active.

### `write_p0036_evidence`

Purpose: Persist concise holdout, baseline, timing, selection and promotion evidence.

Inputs: training/evaluation result dictionary.

Outputs: evidence file paths.

Side effects: writes `requirements/package-runs/P0036/*.md`.

Tests: validation checks evidence file existence.

## Changed functions

### `build_calendar_features`

Change: remove unsafe `days_since_start_scaled` and emit the P0036 safe feature schema.

Reason: P0035 failure mode was polynomial extrapolation over squared time.

### `build_feature_store`

Change: build fair train-only M1 baselines and residual targets.

Reason: P0036 holdout comparison must be strict out-of-sample for M1.

### `train_m4_target_model`

Change: primary estimator becomes bounded HGB. Polynomial/Ridge is not selected as primary.

Reason: P0036 forbids unbounded polynomial time extrapolation.

### `train_m4`

Change: train/evaluate in staging and promote active only if quality gate passes.

Reason: P0036 must not silently replace active with worse artifacts.

### `validate_m4_outputs`

Change: validate P0036 feature schema, evidence files and artifact state.

Reason: holdout evidence policy applies to P0036.
