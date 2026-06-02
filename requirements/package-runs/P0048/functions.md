# P0048 function design

## New functions

`run_p0048_analysis(feature_db, weather_db, evidence_dir)`

- Purpose: orchestrate P0048 dataset construction, exploratory modeling and evidence writing.
- Inputs: local feature DB path, local weather DB path, evidence directory.
- Outputs: `P0048Result` with status, row counts, selected conclusions and evidence paths.
- Side effects: reads local SQLite DBs, writes local feature DB table `se3_se1_bottleneck_training_dataset_v1`, writes package evidence.
- Test coverage: package verification plus helper unit tests.

`load_ai2_spread_source_rows(feature_db)`

- Purpose: load corrected fixed-CET AI2 v2 rows for SE1 and SE3-SE1.
- Inputs: feature DB path.
- Outputs: row dictionaries.
- Side effects: reads local SQLite only.
- Test coverage: package verification.

`build_base_spread_rows(rows)`

- Purpose: join SE1 and spread target rows and reconstruct SE3.
- Inputs: loaded AI2 rows.
- Outputs: ordered base spread rows.
- Side effects: none.
- Test coverage: arithmetic test.

`load_weather_feature_rows(weather_db)`

- Purpose: load required weather proxy source rows.
- Inputs: weather DB path.
- Outputs: mapping keyed by `timestamp_utc`.
- Side effects: reads local SQLite only.
- Test coverage: package verification.

`derive_weather_features(base_rows, weather_rows)`

- Purpose: attach weather actuals, normals, deltas and gradients.
- Inputs: spread rows and weather rows.
- Outputs: enriched modeling rows.
- Side effects: none.
- Test coverage: gradient formula test.

`fit_weather_normals(rows, feature_names)`

- Purpose: fit fixed-CET seasonal-hour medians for weather actual/gradient fields.
- Inputs: enriched rows and feature names.
- Outputs: normal maps.
- Side effects: none.
- Test coverage: package verification.

`add_regime_labels(rows, thresholds)`

- Purpose: attach binary and multiclass P0048 regime targets.
- Inputs: modeling rows and threshold dictionary.
- Outputs: rows with labels.
- Side effects: mutates rows in place.
- Test coverage: threshold label test.

`add_lagged_features(rows)`

- Purpose: add previous-hour and previous-day spread/regime diagnostics without leakage.
- Inputs: chronological rows.
- Outputs: rows with lagged fields.
- Side effects: mutates rows in place.
- Test coverage: lag test.

`assign_chronological_splits(rows)`

- Purpose: assign train/validate/holdout by fixed-CET model date.
- Inputs: modeling rows.
- Outputs: split count dictionary.
- Side effects: mutates rows in place.
- Test coverage: split non-overlap test.

`persist_modeling_dataset(feature_db, rows)`

- Purpose: write local SQLite table `se3_se1_bottleneck_training_dataset_v1`.
- Inputs: feature DB path and modeling rows.
- Outputs: persisted row count.
- Side effects: writes local feature DB.
- Test coverage: package verification.

`evaluate_stage1_classifiers(rows)`

- Purpose: train/evaluate exploratory Stage-1 classifiers by feature group and target.
- Inputs: modeling rows.
- Outputs: metric dictionaries and confusion matrices.
- Side effects: none.
- Test coverage: package verification.

`evaluate_stage2_regressors(rows)`

- Purpose: train/evaluate exploratory positive-regime severity regressors.
- Inputs: modeling rows.
- Outputs: metric dictionaries.
- Side effects: none.
- Test coverage: package verification.

`evaluate_continuous_spread_baselines(rows)`

- Purpose: train/evaluate constrained continuous spread regression baselines.
- Inputs: modeling rows.
- Outputs: metric dictionaries.
- Side effects: none.
- Test coverage: package verification.

`write_p0048_evidence(evidence_dir, summary)`

- Purpose: write required Markdown/JSON/CSV package evidence.
- Inputs: evidence directory and run summary.
- Outputs: mapping of evidence labels to paths.
- Side effects: creates/updates P0048 evidence files.
- Test coverage: package verification.

## Changed functions

None planned.

## Removed functions

None planned.

## Unchanged but relevant functions

`p0047.threshold_candidates` and `p0047.assign_spread_regime`

- Purpose: P0047 threshold/regime logic.
- Reason relevant: P0048 starts from P0047 robust-sigma thresholds and keeps labels comparable.

`p0043.assign_splits`

- Purpose: previous chronological split convention.
- Reason relevant: P0048 uses the same 2024/2025/2026 chronological split boundaries.
