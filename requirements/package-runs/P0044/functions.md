# P0044 function design

New module: `src.mac.services.spotprice_model_diagnostics.p0044`

Planned functions and classes:

- `run_p0044_training(feature_db, evidence_dir)`: orchestrates loading, validation, split assignment, model/baseline evaluation and evidence writing.
- `load_ai1_rows(feature_db)`: reads only `ai1_day_to_local_week_training_targets_v2`; raises if missing.
- `validate_dataset_contract(rows)`: verifies corrected AI-1 target columns, fixed-CET date field and target series coverage.
- `assign_splits(rows)`: assigns train/validate/holdout from `model_cet_date`.
- `split_counts(rows)`: summarizes split counts globally and per target series.
- `feature_names_for_group(group)`: returns feature names for F0-F5.
- `Encoder`: stores deterministic categorical category lists.
- `build_feature_matrix(rows, group, encoder)`: converts feature rows to numeric matrices without stochastic category ordering.
- `hgb_params()`: returns bounded HGB hyperparameters.
- `train_hgb_model(train_rows, group, target_name)`: fits a target-specific gradient boosting model.
- `predict_model(model, encoder, rows, group)`: returns finite numeric predictions.
- `fit_baselines(train_rows, target_name)`: fits target-specific train-only baselines.
- `predict_baseline(rows, baseline)`: applies a baseline to non-train rows without using their targets.
- `evaluate_predictions(rows, predicted, target_name)`: computes MAE, RMSE, mean signed error and target-specific ranking/correlation metrics.
- `local_window_rank_metrics(rows, predicted, target_name)`: evaluates D-2..D+4 windows over `model_cet_date`, including windows crossing calendar years.
- `subset_metrics(rows, predicted, target_name)`: reports special/normal/bridge/holiday/summer/winter/weather subset metrics.
- `train_evaluate_target(rows, target_series, target_name)`: evaluates baselines and feature groups for one of six target models.
- `select_feature_group(results)`: chooses simplest near-best validation MAE group.
- `best_worst_days(rows, predicted, target_name)`: lists best/worst holdout center dates.
- `write_p0044_evidence(evidence_dir, summary)`: writes required markdown and JSON evidence.
- Report helpers: build markdown reports and JSON-safe summaries.

Changed functions:

- `docs/functions/mac/spotprice-ml-normal-model.md` documentation is updated with the P0044 AI-1 diagnostic model.

Removed functions:

- None.

Side effects:

- Reads local SQLite feature DB.
- Writes package-run evidence under `requirements/package-runs/P0044/`.
- Does not write devices, KVS, Home Assistant, API configs or model binaries.
