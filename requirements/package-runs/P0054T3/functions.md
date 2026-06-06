# P0054T3 Function Design

## New Functions

### `run_p0054t3_analysis`

- Purpose: orchestrate baseline gate, corrected matrix execution and evidence writing.
- Inputs: optional feature DB, weather DB and evidence directory.
- Outputs: `P0054T3Result`.
- Side effects: writes P0054T3 evidence.

### `run_baseline_gate`

- Purpose: reproduce P0054R and enforce the <=1 MW DayAhead MAE gate.
- Inputs: feature DB and weather DB.
- Outputs: compact gate evidence.
- Side effects: temporary evidence under `/private/tmp`.

### `build_p0_full_rows`

- Purpose: build P0054R no-price full-coverage rows with profiles and internal split.
- Inputs: feature DB and weather DB.
- Outputs: source rows, modeling rows, path rows and contracts.
- Side effects: none.

### `build_p1_price_rows`

- Purpose: build safe P0054N/P0054L2-compatible price rows and consumption rows.
- Inputs: feature DB, weather DB.
- Outputs: rows and price contract.
- Side effects: trains temporary in-memory price forecast models.

### `run_matrix_branch`

- Purpose: run one weather/price branch and score M1/M2/M3.
- Inputs: rows, features, selected model specs, weather mode, price mode and seed.
- Outputs: seed-level metrics and diagnostics.
- Side effects: none.

### `m1_m2_diagnostic`

- Purpose: report horizon-bias and prediction-difference diagnostics for M1 versus M2.
- Inputs: scored rows, M1/M2 columns and bias evidence.
- Outputs: compact diagnostic dictionary.
- Side effects: none.

### `aggregate_matrix_results`

- Purpose: aggregate W0 single run and W1 seed means.
- Inputs: seed-level rows.
- Outputs: 12 matrix summary rows.
- Side effects: none.

### `write_p0054t3_evidence`

- Purpose: write Markdown, JSON and CSV evidence.
- Inputs: summary dictionary.
- Outputs: path map.
- Side effects: writes files under `requirements/package-runs/P0054T3/`.

## Changed Functions

None planned.

## Removed Functions

None.
