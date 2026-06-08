# P0056F Function Design

## New Functions

### `run_p0056f_weather_ablation`

- Purpose: orchestrate input loading, W0-W12 execution, metrics, persistence and evidence.
- Inputs: feature DB path, evidence dir.
- Outputs: `P0056FResult`.
- Side effects: writes P0056F SQLite tables and package-run evidence.
- Test coverage: package execution and unit tests for pure helpers.

### `weather_stacks`

- Purpose: define cumulative W0-W12 weather stack contract.
- Inputs: none.
- Outputs: ordered stack definitions.
- Side effects: none.
- Test coverage: exact stack ids/order and cumulative behavior.

### `fixed_non_weather_features`

- Purpose: return calendar/load-history features held constant across stacks.
- Inputs: none.
- Outputs: feature name list.
- Side effects: none.
- Test coverage: identical fixed feature list across stacks; forbidden terms absent.

### `feature_names_for_stack`

- Purpose: combine fixed features with a stack's weather features.
- Inputs: stack id.
- Outputs: feature names.
- Side effects: none.
- Test coverage: W0 has no weather; W12 has full ordered weather stack.

### `fit_stack_model`

- Purpose: fit HBC weighted ensemble for one area/stack and attach P0056F prediction column.
- Inputs: rows, stack, specs.
- Outputs: training summary and prediction column.
- Side effects: mutates copied rows with prediction column.
- Test coverage: package execution.

### `marginal_gain_rows`

- Purpose: compute previous-stack, W0 and current-best deltas plus marginal gain.
- Inputs: result rows.
- Outputs: marginal-gain evidence rows.
- Side effects: none.
- Test coverage: marginal delta unit test.

### `peak_efficiency_decision`

- Purpose: choose best holdout stack, smallest within 0.5%, first negative gain and candidate recommendation.
- Inputs: result rows and marginal rows.
- Outputs: per-area decision summary.
- Side effects: none.
- Test coverage: candidate/smallest-within-threshold unit test.

## Changed Functions

None planned outside P0056F.

## Removed Functions

None.

## Cross-Package Function Catalog

No durable function catalog update planned; P0056F remains package-local LABB diagnostics.
