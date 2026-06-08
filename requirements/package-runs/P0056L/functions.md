# P0056L Function Design

## `run_p0056l_neural_dayahead_smoke`

Status: new

Purpose: Execute the SE2 neural DayAhead smoke test and write all required evidence.

Inputs: feature DB path and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes package-run evidence files only.

Test coverage: end-to-end module run plus unit tests around supporting helpers.

## `select_representative_origins`

Status: new

Purpose: Select a deterministic reduced origin subset from P0056K-valid SE2 origins.

Inputs: ordered origins, step size.

Outputs: selected origins.

Side effects: none.

Test coverage: unit test verifies deterministic count and ordering.

## `add_sequence_window_features`

Status: new

Purpose: Add 168 known-at-origin load history values to each row for `N2_SequenceMLP_168h`.

Inputs: row list and timestamp-to-consumption mapping.

Outputs: enriched copied rows.

Side effects: none.

Test coverage: unit test verifies generated feature names and no forbidden leakage names.

## `fit_predict_mlp`

Status: new

Purpose: Train a small scikit-learn MLPRegressor on forecast-safe rows and predict a 24h DayAhead block.

Inputs: model id, train rows, forecast rows and feature list.

Outputs: predictions and training metadata.

Side effects: none.

Test coverage: smoke-tested by package module run.

## Evidence writers

Status: new

Purpose: Produce required Markdown/CSV/JSON evidence files for P0056L.

Inputs: summary dictionaries and result rows.

Outputs: evidence path mapping.

Side effects: writes under `requirements/package-runs/P0056L/`.

Test coverage: package verification checks generated files.
