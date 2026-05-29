# P0025 function design

## New functions

### `spot.normalize_actual_indexes(actual_prices_by_index, forecast_index)`

- Purpose: Normalize available actual prices onto the same sum basis as the forecast subset.
- Inputs: mapping of hour index to actual price and full or subset forecast indexes.
- Outputs: proto indexes and normalized actual indexes by hour index.
- Side effects: none.
- Reason: shared calculation for horizon patching and outcome diagnostics.
- Test coverage: horizon sum-preservation and forecast-vs-actual diagnostic tests.

### `spot.build_spot_plan_for_window(week_number, iso_year=2025, actual_fixture_path=..., actual_horizon_hours=20)`

- Purpose: Build a P0025 `SpotPlan` with explicit fixture year and horizon parameters.
- Inputs: week, fixture ISO year, fixture path, horizon hours.
- Outputs: `SpotPlan`.
- Side effects: reads local fixture path.
- Reason: supports internal 2026 fixture tests without public API changes.
- Test coverage: 2026 comparison fixture path test.

## Changed functions

### `spot.patch_forecast_with_actual_prices(...)`

- Change: apply actual patch only inside the fixed known horizon, compute separate outcome diagnostics for all available actual fixture hours, and emit P0025 model/strategy metadata.
- Inputs: add optional `actual_horizon_hours`.
- Outputs: `SpotPlan` with planning/outcome fields.
- Side effects: none.
- Reason: prevent optimizer from seeing future actuals while retaining diagnostics.
- Test coverage: TC1, TC2, TC3, TC4, TC5 and TC6.

### `spot.build_spot_plan(...)`

- Change: call the horizon-aware implementation with the default 2025 fixture and 20-hour horizon.
- Reason: existing planner integration should receive P0025 behavior without public API changes.
- Test coverage: existing planner/API/browser tests plus new P0025 tests.

### `spot.spot_indexes_for_week(week_number)`

- Change: return `SpotPlan.spot_planning_index` via compatibility `spot_index`.
- Reason: preserve existing helper behavior.
- Test coverage: existing spot expansion tests.

### `schema.SpotPlan`

- Change: add `spot_actual_horizon_hours`, `spot_planning_index`, `spot_planning_source`, `spot_actual_outcome_index`, `spot_actual_available`, `spot_forecast_error_index`, `spot_forecast_error_pct`; keep P0024 aliases where compatible.
- Reason: represent planning vs outcome separation.
- Test coverage: row and metadata tests.

### `tables.rows_for_plan(plan)`

- Change: render P0025 planning/outcome diagnostic fields.
- Reason: package requires row-level comparison fields.
- Test coverage: forecast-vs-actual diagnostic row tests.

### `tables._metadata(plan)`

- Change: render `spot_actual_horizon_hours` and P0025 model/strategy metadata.
- Reason: package requires summary visibility.
- Test coverage: API/CLI summary tests.

### `server.plan_payload(request, prefer_real_weather=True)`

- Change: include P0025 spot metadata in API/browser summary.
- Reason: browser/API smoke must show known-horizon behavior.
- Test coverage: backward-compatible API test.

### `html.render_result(payload)`

- Change: show horizon/patched/forecast spot summary and planning source in the browser table.
- Reason: manual browser/phone inspection.
- Test coverage: browser rendering tests.

## Removed functions

None planned.

## Function catalog updates

Update `docs/functions/mac/weekly-home-optimizer-poc.md`.
