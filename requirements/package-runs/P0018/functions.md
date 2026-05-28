# Package P0018 Function Design

## Package

`P0018`

## Scope

New Mac lab module:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

## New functions

### `parse_args(argv)`

Purpose: parse CLI inputs and output format.

Inputs: optional argv sequence.

Outputs: argparse namespace.

Side effects: none.

Reason: enforce the public input contract.

Tests: CLI contract tests.

### `main(argv)`

Purpose: run the POC from CLI.

Inputs: optional argv sequence.

Outputs: process status code.

Side effects: writes table/JSON/CSV to stdout.

Reason: package-required executable entrypoint.

Tests: CLI execution tests.

### `build_input_profile(week_number)`

Purpose: create deterministic 168-hour weather and RH-policy inputs.

Inputs: ISO week number.

Outputs: `InputProfile`.

Side effects: none.

Reason: no-network weather provider for POC v1.

Tests: output shape and policy tests.

### `expand_period_indexes_to_hours(period_indexes)`

Purpose: convert P0017 21x8h spot indexes into 168 hourly values.

Inputs: 21 period indexes.

Outputs: 168 hourly spot indexes.

Side effects: none.

Reason: P0018 hourly optimizer needs hourly cost signals.

Tests: spot expansion test.

### `spot_indexes_for_week(week_number)`

Purpose: fetch P0017 forecast indexes and expand them to hourly values.

Inputs: ISO week number.

Outputs: 168 hourly spot indexes.

Side effects: reads committed P0017 historical data through the P0017 model.

Reason: reuse P0017 instead of duplicating the model.

Tests: output shape tests.

### `plan_heat(outdoor_temp_c, spot_index, current_house_temp)`

Purpose: produce hourly heat need, production, SOC and heat cost weights.

Inputs: 168 outdoor temperatures, 168 spot indexes, current house temperature.

Outputs: `HeatPlan`.

Side effects: none.

Reason: create heat and ventilation-cost signals.

Tests: heat balance and output shape tests.

### `rh_weight_for_hour(outdoor_temp_c, outdoor_rh_pct)`

Purpose: convert outdoor weather into an RH ventilation policy weight.

Inputs: outdoor temperature and RH.

Outputs: policy weight.

Side effects: none.

Reason: keep RH as policy/cost signal.

Tests: policy-case tests.

### `ppm_after_hour(ppm, supply_pct, occupancy_gain_ppm_h)`

Purpose: compute one-hour PPM transition for a supply mode.

Inputs: current PPM, supply percent, occupancy gain.

Outputs: next PPM.

Side effects: none.

Reason: deterministic PPM dynamics.

Tests: PPM dynamics tests.

### `ppm_cost(ppm)`

Purpose: compute air-quality discomfort cost.

Inputs: absolute PPM.

Outputs: numeric cost.

Side effects: none.

Reason: optimizer objective.

Tests: optimizer and continuation tests.

### `optimize_ppm_plan(heat_cost_weight, rh_weight, current_ppm, occupancy_gain_ppm_h)`

Purpose: choose 168 supply modes using dynamic programming.

Inputs: hourly heat weights, RH weights, current PPM, occupancy gain.

Outputs: `PpmPlan`.

Side effects: none.

Reason: required cross-hour optimization.

Tests: supply bounds and policy-case tests.

### `build_weekly_plan(week_number, current_ppm, current_house_temp, occupancy_gain_ppm_h)`

Purpose: orchestrate input, heat and PPM planning into one result.

Inputs: package-required user inputs plus optional occupancy gain.

Outputs: `WeeklyPlan`.

Side effects: reads committed spot history through P0017 model.

Reason: public API for CLI and tests.

Tests: output shape and CLI tests.

### `rows_for_plan(plan)`

Purpose: flatten plan structures to required output rows.

Inputs: `WeeklyPlan`.

Outputs: list of row dictionaries.

Side effects: none.

Reason: shared output for table/JSON/CSV.

Tests: output shape tests.

### `format_table(plan)`

Purpose: render human-readable 168-row table.

Inputs: `WeeklyPlan`.

Outputs: table string.

Side effects: none.

Reason: required human-readable POC output.

Tests: CLI/table tests.

### `format_json(plan)`

Purpose: render JSON output.

Inputs: `WeeklyPlan`.

Outputs: JSON string.

Side effects: none.

Reason: package optional but inexpensive machine-readable output.

Tests: JSON CLI test.

### `format_csv(plan)`

Purpose: render CSV output.

Inputs: `WeeklyPlan`.

Outputs: CSV string.

Side effects: none.

Reason: package optional but inexpensive inspectable output.

Tests: CSV output shape test.

## Changed functions

None.

## Removed functions

None.

## Important unchanged functions

### `forecast_period_indexes(target_week, history)`

Reason for no change: P0018 reuses the P0017 spot model contract; changing it would expand scope.

## Design deviations during implementation

None yet.
