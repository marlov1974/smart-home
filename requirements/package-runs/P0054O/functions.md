# P0054O Function Design

## New Functions

`run_p0054o_analysis(...)`

- Purpose: orchestrate the weather-noise ablation and evidence writing.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: `P0054OResult`.
- Side effects: writes package-run evidence only.
- Tests: package command plus helper unit tests.

`build_base_rows(...)`

- Purpose: build P0054N-compatible exact-origin rows before profile features.
- Inputs: feature DB and weather DB paths.
- Outputs: source contracts, direct rows, exact price contract.
- Side effects: none.
- Tests: package command verifies row counts.

`temperature_feature_columns(...)`

- Purpose: discover temperature-like weather feature columns used by P0054N and classify which are directly perturbed.
- Inputs: P0054N feature contract.
- Outputs: discovery metadata.
- Side effects: none.
- Tests: unit coverage for selected source columns.

`apply_temperature_noise(...)`

- Purpose: deterministically add uniform temperature noise to selected columns.
- Inputs: rows, selected columns, seed, amplitude.
- Outputs: copy of rows plus noise audit.
- Side effects: none.
- Tests: deterministic and range unit tests.

`prepare_rows_for_training(...)`

- Purpose: assign splits, apply optional noise, recompute train profiles and return direct/path rows.
- Inputs: base rows and optional noise scenario.
- Outputs: prepared rows and audit.
- Side effects: none.
- Tests: package command verifies split and profile behavior.

`fit_selected_models(...)`

- Purpose: train the selected P0054O model variants and attach holdout/path predictions.
- Inputs: prepared rows, feature contract, model specs, selected variant list.
- Outputs: model results and scored rows.
- Side effects: none.
- Tests: package command verifies model training evidence.

`evaluate_weather_noise_run(...)`

- Purpose: calculate full_36h, DayAhead, percent and daily-energy metrics for one seed/scenario.
- Inputs: scored rows and model keys.
- Outputs: compact metrics rows.
- Side effects: none.
- Tests: percent helper unit tests.

`summarize_seed_metrics(...)`

- Purpose: aggregate mean/std/min/max and deltas versus no-noise baseline.
- Inputs: per-seed metrics and baseline metrics.
- Outputs: evidence summaries.
- Side effects: none.
- Tests: unit coverage via percent helpers.

`write_p0054o_evidence(...)`

- Purpose: write required Markdown/JSON/CSV evidence.
- Inputs: summary and compact metrics.
- Outputs: map of evidence paths.
- Side effects: package-run file writes.
- Tests: package command verifies output.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` with P0054O after implementation.
