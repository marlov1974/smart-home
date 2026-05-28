# Package P0023 Function Design

## Package

`P0023`

## Scope

COP emulator and optimized-vs-flat electric cost comparison for the Mac weekly home POC.

## New Functions

### `estimate_cop(outdoor_temp_c, heat_kw)`

Purpose: estimate heat-pump COP from outdoor temperature and delivered thermal output.

Inputs: outdoor temperature and delivered thermal kW/kWh for one hour.

Outputs: COP clamped to the POC model range.

Side effects: none.

Reason: convert thermal output to estimated electric input.

Tests: COP clamp, cold-weather monotonicity and high-output penalty tests.

### `compare_heat_costs(outdoor_temp_c, heat_need_kWh, optimized_heat_kWh, heat_price_index)`

Purpose: compute optimized and flat-production electric kWh/cost hourly arrays and weekly totals.

Inputs: 168 outdoor temperatures, heat needs, optimized heat output and heat price indexes.

Outputs: `HeatCostComparison`.

Side effects: none.

Reason: expose operator-facing optimized-vs-flat cost result.

Tests: hourly consistency, flat baseline, percentage math and zero-denominator warning tests.

### `_validate_hourly(values, name)`

Purpose: validate and coerce 168-hour numeric COP/comparison inputs.

Inputs: numeric sequence and field name.

Outputs: tuple of floats.

Side effects: none.

Reason: keep helper validation local to COP module.

Tests: indirectly through comparison tests.

### `_safe_avg_cop(thermal_kWh, electric_kWh)`

Purpose: compute average COP only when electric-kWh denominator is positive.

Inputs: thermal and electric kWh totals.

Outputs: float or `None`.

Side effects: none.

Reason: avoid division by zero while keeping warnings explicit.

Tests: zero-denominator warning tests.

## Changed Functions

### `build_weekly_plan(week_number, current_ppm, current_house_temp, people, prefer_real_weather)`

Change: compute `heat_cost_comparison` from the same weather, heat plan and spot index used by the weekly plan.

Inputs changed: none.

Outputs changed: `WeeklyPlan` gains `heat_cost_comparison`.

Side effects changed: none.

Tests: full POC output includes comparison.

### `rows_for_plan(plan)`

Change: include hourly COP/electric-cost comparison fields.

Reason: JSON/CSV/API/browser visibility.

Tests: output shape and heat cost summary tests.

### `_metadata(plan)`

Change: include summary-level heat cost model, COP model, totals, percentages and warnings.

Reason: CLI JSON metadata and output transparency.

Tests: output shape and summary field tests.

### `format_table(plan)`

Change: include compact weekly COP-cost comparison in the metadata header.

Reason: CLI human-readable output should show the result without requiring JSON.

Tests: output shape tests.

### `plan_payload(request, prefer_real_weather=True)`

Change: include heat cost comparison fields in API/browser summary.

Reason: browser/API visibility.

Tests: browser contract and summary field tests.

### `render_result(payload)`

Change: render heat cost comparison metrics and the operator-facing emulated/POC sentence.

Reason: package UI requirement.

Tests: browser heat cost rendering.

## Removed Functions

None.

## Important Unchanged Functions

### `optimize_heat_dp()`

Reason for no change: P0023 reports electric cost comparison only and does not alter heat optimizer constraints/objective.

### `estimate weather` and provider functions

Reason for no change: P0023 consumes existing weather profile output.

### `optimize_ppm_plan()`

Reason for no change: ventilation planning consumes existing heat cost weights and is outside package scope.

## Design Deviations During Implementation

None yet.
