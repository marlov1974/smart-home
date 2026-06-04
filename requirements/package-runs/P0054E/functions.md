# P0054E Function Design

Package: P0054E
Label: LABB

## New Functions

`run_p0054e_analysis(feature_db, weather_db, evidence_dir)`

- Purpose: orchestrate the P0054E dependency-aware boosted-model experiment and evidence writing.
- Inputs: local feature DB path, local weather DB path, package evidence directory.
- Outputs: result object/dict with status, row counts, dependency status and evidence paths.
- Side effects: writes package-run evidence files only.
- Test coverage: model-contract and evidence-shape tests.

`capture_environment_status()`

- Purpose: record Python, pip, platform and package import/version status after installation.
- Inputs: none.
- Outputs: serializable environment dict.
- Side effects: imports optional packages if present.
- Test coverage: import-status shape test.

`optional_model_specs(import_status)`

- Purpose: build the same-run model list using ExtraTrees plus LightGBM/XGBoost when importable.
- Inputs: dependency import status.
- Outputs: model spec list with names, classes and hyperparameters.
- Side effects: imports model classes only when available.
- Test coverage: optional dependency handling test.

`fit_p0054e_model(rows, features, spec)`

- Purpose: train one P0054E model on train rows and evaluate validation/holdout rows.
- Inputs: direct-horizon rows, feature list, model spec.
- Outputs: metrics, predictions and training metadata.
- Side effects: CPU-only local training; no persisted model artifact.
- Test coverage: row-set and prediction contract tests through small fixtures or module helpers.

`attach_named_predictions(rows, model_results)`

- Purpose: attach each model prediction to direct rows using stable prediction columns.
- Inputs: direct rows and per-model prediction arrays.
- Outputs: copied/scored rows.
- Side effects: none.
- Test coverage: identical row-set test.

`attach_weekly_predictions(path_rows, model_results, features)`

- Purpose: score weekly 168h candidate rows for each fitted same-run model.
- Inputs: weekly candidate rows, fitted model results, feature list.
- Outputs: scored weekly path rows.
- Side effects: none.
- Test coverage: complete weekly-path test.

`compare_p0054e_models(model_results, weekly_summary, p0054d_summary)`

- Purpose: identify best direct/weekly model and compare LightGBM/XGBoost to P0054D and same-run ExtraTrees.
- Inputs: same-run model metrics, weekly metrics, P0054D summary evidence.
- Outputs: comparison dict.
- Side effects: none.
- Test coverage: comparison threshold unit test.

`write_p0054e_evidence(evidence_dir, scored_rows, scored_path_rows, weekly_rows, summary)`

- Purpose: write required P0054E Markdown/JSON/CSV evidence.
- Inputs: evidence directory, scored rows, weekly rows, summary dict.
- Outputs: map of evidence file paths.
- Side effects: creates/updates package-run files.
- Test coverage: evidence file presence after runner verification.

## Changed Functions

None planned in existing modules.

## Removed Functions

None.

## Unchanged But Reused Functions

P0054D helpers for SE4 target loading, weather proxy loading, P0053C split assignment, feature contract validation, feature matrix encoding, metrics, direct horizon evaluation, weekly path evaluation and conditional regime evaluation will be reused where possible.

## Durable Function Catalog

Update `docs/functions/mac/spotprice-model-diagnostics.md` if P0054E adds durable diagnostic module documentation.
