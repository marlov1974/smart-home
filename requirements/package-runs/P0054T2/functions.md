# P0054T2 Function Design

## New Functions

### `run_p0054t2_analysis`

- Purpose: orchestrate evidence comparison, rowset diff, implementation diff, minimal reproduction and evidence writing.
- Inputs: optional feature DB, weather DB and evidence directory paths.
- Outputs: `P0054T2Result` with status, headline summary and evidence paths.
- Side effects: writes compact P0054T2 evidence under `requirements/package-runs/P0054T2/`.
- Test coverage: module-level run plus helper unit tests.

### `rowset_summary`

- Purpose: summarize target/origin counts and intersections between two modeling rowsets.
- Inputs: R-like rows and T-like rows.
- Outputs: dictionary of row/origin counts and overlap counts.
- Side effects: none.
- Test coverage: synthetic unit test.

### `model_alias_summary`

- Purpose: explain whether P0054T M1 equals M2 by bias evidence and prediction-column comparison.
- Inputs: T-like rows, weighted prediction column, bias-corrected prediction column and bias evidence.
- Outputs: dictionary with equality flags and non-zero bias count.
- Side effects: none.
- Test coverage: synthetic unit test.

### `prediction_diff_summary`

- Purpose: compute compact prediction-level diff metrics for overlapping R-like and T-like prediction rows.
- Inputs: R-like rows, T-like rows and prediction columns.
- Outputs: dictionary and top discrepancy rows.
- Side effects: none.
- Test coverage: synthetic unit test.

### `run_t_like_w0_p0`

- Purpose: execute the minimal P0054T W0/P0 no-price path without running the full 12-combination matrix.
- Inputs: base rows, feature contract and model specs.
- Outputs: metrics, rows, model evidence and M1/M2 alias evidence.
- Side effects: none.
- Test coverage: integration through package run.

### `write_p0054t2_evidence`

- Purpose: write required Markdown/JSON/CSV package-run evidence.
- Inputs: summary dictionary.
- Outputs: path map.
- Side effects: writes files under P0054T2 evidence directory.
- Test coverage: package run and diff inspection.

## Changed Functions

None planned.

## Removed Functions

None.
