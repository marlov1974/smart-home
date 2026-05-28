# Package P0022 Function Design

## Package

`P0022`

## Scope

Discrete heat optimizer for the Mac weekly home POC.

## New functions

### `optimize_heat_dp(heat_need_kWh, heat_price_index, config=None)`

Purpose: choose hourly heat modes and SOC trajectory with dynamic programming.

Inputs: 168 heat need values, 168 price indexes, optional config.

Outputs: `HeatPlan`.

Side effects: none.

Reason: replace heuristic heat allocation with constrained optimizer.

Tests: heat optimizer DP, constraints, metadata.

### `default_heat_optimizer_config()`

Purpose: return P0022 default optimizer constants.

Inputs: none.

Outputs: `HeatOptimizerConfig`.

Side effects: none.

Reason: keep defaults explicit and testable.

Tests: metadata tests.

### `low_soc_penalty(soc_pct, threshold_pct=25.0, scale=40.0)`

Purpose: compute convex low-SOC comfort penalty.

Inputs: SOC percent, threshold and penalty scale.

Outputs: numeric cost.

Side effects: none.

Reason: discourage prolonged empty battery.

Tests: constraint/cost tests.

### `derive_heat_cost_weight(heat_need_kWh, heat_action_kw, heat_soc_pct, heat_price_index, margin=0.25)`

Purpose: derive ventilation heat-cost signal from optimized heat plan.

Inputs: need, action, SOC, price and action/need margin.

Outputs: cost weight.

Side effects: none.

Reason: preserve PPM/RH planner contract.

Tests: heat cost weight tests.

## Changed functions

### `plan_heat(outdoor_temp_c, spot_index, current_house_temp)`

Current purpose: heuristic heat allocation and cost weights.

Change: compute heat need and call `optimize_heat_dp()`.

Inputs changed: none.

Outputs changed: `HeatPlan` gains optimizer metadata and optional hourly diagnostic arrays.

Side effects changed: none.

Reason: P0022 target behavior.

Tests: existing and new heat tests.

### `rows_for_plan(plan)`

Current purpose: flatten plan rows.

Change: include heat optimizer hourly diagnostic fields.

Reason: browser/API visibility.

Tests: output shape and metadata tests.

### `plan_payload(request, prefer_real_weather=True)`

Current purpose: build API/HTML payload.

Change: include heat optimizer metadata/warnings in summary.

Reason: browser/API visibility.

Tests: browser/API metadata tests.

### `render_result(payload)`

Current purpose: render HTML summary/table.

Change: show heat optimizer metadata and warnings.

Reason: operator inspection.

Tests: browser compatibility tests.

## Removed functions

### `_allocate_heat()`

Reason: replaced by `optimize_heat_dp()`.

Replacement: `optimize_heat_dp()`.

Tests: heat optimizer tests.

## Important unchanged functions

### `build_weekly_plan()`

Reason for no change: orchestration stays the same and continues to call `plan_heat()`.

### `optimize_ppm_plan()`

Reason for no change: P0022 changes heat planning only.

### `weather_profile_for_week()`

Reason for no change: P0022 consumes the existing weather profile.

## Design deviations during implementation

Function signatures kept the package design intent but expose default penalty scale and action/need margin as testable optional arguments.
