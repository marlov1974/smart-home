# P0054T4 Function Design

## New Functions

### `run_p0054t4_analysis`

- Purpose: orchestrate baseline gate, clean M1 fit, inference-only weather noise scoring and evidence writing.
- Inputs: optional feature DB, weather DB and evidence directory.
- Outputs: `P0054T4Result`.
- Side effects: writes P0054T4 evidence.

### `fit_clean_m1`

- Purpose: fit P0054R-style base models, weights and horizon-bias correction on clean train/internal-validation rows.
- Inputs: clean P0054R rows, path rows, feature list and model specs.
- Outputs: fitted base results, model columns, weights, bias evidence and clean path predictions.
- Side effects: none.

### `apply_inference_temperature_noise`

- Purpose: apply deterministic temperature noise only to holdout/inference rows.
- Inputs: rows, seed, selected temperature columns and magnitude.
- Outputs: noise evidence.
- Side effects: mutates copied rows.

### `score_prediction_branch`

- Purpose: score W0 or one W1 seed with DayAhead, full36, daily-energy and extra metrics.
- Inputs: path rows, prediction column, weather mode and seed.
- Outputs: metric dictionary.
- Side effects: none.

### `summarize_seed_results`

- Purpose: aggregate W0 and W1 seed-level metrics and deltas.
- Inputs: seed results.
- Outputs: summary dictionaries.
- Side effects: none.

### `write_p0054t4_evidence`

- Purpose: write Markdown, JSON and CSV evidence.
- Inputs: summary dictionary.
- Outputs: evidence path map.
- Side effects: writes files under `requirements/package-runs/P0054T4/`.

## Changed Functions

None planned.

## Removed Functions

None.
