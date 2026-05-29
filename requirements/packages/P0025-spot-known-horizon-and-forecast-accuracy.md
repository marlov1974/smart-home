# Package P0025: Spot known horizon and forecast accuracy

## Status
planned

## Package order
P0025

## Primary area
G2 / Mac lab POC / spot forecast / weekly home optimizer

## Decision summary

The weekly home optimizer POC must model the fact that, at planning time, only part of the coming 168-hour horizon has known actual spot prices.

For the first POC version, use a fixed known-price horizon:

```text
spot_actual_horizon_hours = 20
```

Meaning:

- the first 20 chronological planner hours use actual 2025 spot-price shape from the actual-price fixture
- the remaining 148 hours use the internal hourly forecast index curve
- actual-price patching must preserve the original forecast sum over the known actual overlap, as in P0024

The package must also add a separate forecast-accuracy series so the model can compare an estimated future spot price/index against the later actual outcome. This is needed for scenarios such as asking for a February 2026 day where both a forecast and an eventual actual outcome can be represented and compared.

## Background

In real operation, the amount of known spot price depends on time of day:

```text
Monday 06:00: known prices for the remaining 16 hours of Monday
Monday 14:00: known prices for about 10 hours of Monday plus 24 hours of Tuesday
Monday 13:00: worst case just before new prices are published, about 11 known hours
```

For this POC, do not implement dynamic clock-aware Nord Pool publication timing. Use a representative mean value of 20 known hours.

## Current behavior

P0024 supports hourly spot planning and actual-price patching. When the selected week is fully covered by the 2025 actual-price fixture, the entire 168-hour week may be patched as actual.

This is useful for fixture verification but unrealistic for a live planner because a real planning run does not know the whole future week of spot prices.

The current summary and rows expose actual-patched spot metadata, but there is not yet a distinct forecast-vs-actual accuracy comparison series.

## Problem

The current POC can overstate optimizer foresight by letting the optimizer see actual price shape for all 168 future hours when the fixture contains the whole week.

We need two separate concepts:

1. **Planning spot series**: what the optimizer is allowed to know at plan time.
2. **Outcome/accuracy series**: what later happened, used to compare forecast estimate vs actual outcome.

These must not be collapsed into one value.

## Target behavior

### Known-horizon planning model

For ordinary POC runs, `build_spot_plan` or its replacement must apply this horizon rule:

```text
known_actual_hours = min(20, available actual fixture hours in the requested planner window)
forecast_hours = 168 - known_actual_hours
```

The first `known_actual_hours` chronological hours use actual-price shape patched into the forecast. The remaining hours use forecast index values.

The summary must expose:

```text
spot_model = hourly_forecast_with_actual_horizon_patch_v1
spot_resolution = hourly
spot_actual_fixture_path
spot_actual_horizon_hours = 20
spot_actual_known_hours
spot_actual_patched_hours
spot_forecast_hours
spot_patch_strategy = actual_shape_forecast_sum_horizon
spot_index_min
spot_index_max
spot_index_avg
spot_patch_warnings
```

Expected invariant for standard 168-hour runs:

```text
spot_actual_patched_hours + spot_forecast_hours = 168
```

### Forecast-vs-actual accuracy series

Add a separate row-level series that allows comparison between the forecast estimate and actual outcome when actual outcome exists in the fixture.

Each hourly row should be able to expose:

```text
spot_forecast_index
spot_planning_index
spot_planning_source = actual_horizon_patched | forecast
spot_actual_price
spot_actual_proto_index
spot_actual_outcome_index
spot_actual_available
spot_forecast_error_index
spot_forecast_error_pct
```

Definitions:

- `spot_forecast_index`: internal hourly forecast baseline before actual-horizon patching.
- `spot_planning_index`: final index used by the optimizer for this run.
- `spot_planning_source`: whether the optimizer was allowed to use actual shape or forecast for the hour.
- `spot_actual_price`: raw actual fixture price when available.
- `spot_actual_proto_index`: actual fixture price divided by actual-period mean for the selected comparison basis.
- `spot_actual_outcome_index`: actual outcome normalized onto the same comparison/index basis as the forecast.
- `spot_actual_available`: boolean.
- `spot_forecast_error_index`: `spot_actual_outcome_index - spot_forecast_index`, null when no actual exists.
- `spot_forecast_error_pct`: relative error where mathematically meaningful; null when actual/forecast baseline is zero or missing.

The accuracy comparison must be diagnostic only. It must not give the optimizer knowledge of future actual prices outside the 20-hour known horizon.

### 2026 scenario support

The POC should support asking for a date/week in February 2026 in a way that can carry both:

```text
forecast estimate for the requested future period
actual outcome for the same period, when available in an actual/outcome fixture
```

If the current public API remains week-only for now, Codex may implement this as an internal function/test fixture capability first and document that public `reference_year` or date input remains a future API decision.

The implementation must not fake real 2026 actuals. It should support them as fixture/input data when supplied.

## Non-goals

- No live Nord Pool or external spot-price API integration in this package.
- No Home Assistant dashboard work.
- No Shelly runtime spot-price contract changes.
- No G1 repository changes.
- No real heat-pump control.
- No dynamic publication-time logic beyond the fixed 20-hour known horizon.
- No change to the public API unless Codex explicitly documents why a small optional parameter is needed and keeps existing calls compatible.

## Invariants

- The optimizer must only use `spot_planning_index`, not future `spot_actual_outcome_index` outside the known horizon.
- Actual/outcome comparison fields are diagnostics, not planner inputs.
- Standard POC output remains 168 hourly rows.
- Existing public calls using `week`, `ppm`, `houseTemp` and `people` must continue to work.
- Actual patching must preserve the forecast sum over the patched overlap window.
- The hourly time series must have no duplicate UTC hours and no missing hours.
- Python standard library only unless the existing lab package already depends on something else; do not add new dependencies for this package.

## Knowledge updates

Update if behavior changes are implemented:

- `docs/functions/mac/weekly-home-optimizer-poc.md`
- package-run evidence under `requirements/package-runs/P0025/**`

Update memory only if Codex discovers a durable general lesson or changes the architectural model.

## Files to inspect

- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/labs/weekly_home_optimizer_poc/**`
- `data/spot/spot_2025_hourly_europe_stockholm.csv`
- package-run evidence for P0024 if present locally

## Files allowed to change

- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/labs/weekly_home_optimizer_poc/**`
- `data/spot/**` only for small deterministic test fixtures or fixture documentation needed by this package
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `requirements/package-runs/P0025/**`
- `requirements/packages/P0025-spot-known-horizon-and-forecast-accuracy.md`

## Forbidden changes

- no G1 repository changes
- no Shelly runtime or deploy artifact changes
- no Home Assistant changes
- no live device access
- no real actuator/control changes
- no external package dependencies
- no broad refactor outside the weekly optimizer spot-plan path
- do not remove existing P0024 behavior without replacing it with test-covered horizon-aware behavior

## Pre-implementation consistency review

Codex must review the package against repository truth before editing and store:

```text
requirements/package-runs/P0025/review.md
```

Classification must be one of:

- `PASS`: consistent; continue
- `WARN`: implementable with stated assumptions
- `STOP`: inconsistent, unsafe, underspecified or out of scope

The review must specifically check:

- whether P0024 files/package evidence exist locally
- current public API shape
- current spot fixture schema
- current function names for spot planning and row rendering
- whether the 2026 actual/outcome capability can be implemented as internal fixture support without public API churn

## Implementation design policy

Before implementation, Codex must write:

```text
requirements/package-runs/P0025/design.md
```

The design must include:

```text
Known actual horizon model
Planning series vs outcome series separation
Forecast-sum preservation calculation
UTC/hour alignment and DST handling
2026 forecast-vs-actual fixture strategy
Public API compatibility decision
Test strategy
Risks and assumptions
```

## Function design policy

Before implementation, Codex must write:

```text
requirements/package-runs/P0025/functions.md
```

It must document changed or new functions around:

- resolving weekly UTC hours
- loading actual/outcome spot prices
- applying known-horizon actual patches
- computing forecast-vs-actual diagnostic rows
- formatting JSON/table/CSV rows if changed

## Test cases

### TC1: Fixed 20-hour known horizon

Given a 168-hour week with actual fixture data for all hours
When the weekly POC builds the spot plan
Then exactly 20 hours have `spot_planning_source = actual_horizon_patched` and 148 hours have `spot_planning_source = forecast`.

### TC2: Horizon patch preserves forecast sum

Given the first 20 hours have both forecast and actual prices
When actual shape is patched into the planning series
Then the sum of the 20 patched planning indexes equals the sum of the original 20 forecast indexes within a small numeric tolerance.

### TC3: Optimizer does not see future actuals

Given actual fixture data exists for all 168 hours
When the plan is built
Then hours 20..167 still use forecast planning indexes, while actual outcome fields may be present only as diagnostics.

### TC4: Forecast-vs-actual diagnostics

Given forecast and actual outcome values exist for an hour
When rows are rendered
Then the row includes forecast index, planning index, actual outcome index and forecast error fields.

### TC5: Missing actual outcome

Given actual outcome is missing for some hours
When rows are rendered
Then diagnostic actual/error fields are null or explicitly unavailable, and the planner still returns 168 rows.

### TC6: Partial actual horizon shorter than 20 hours

Given only 11 actual hours are available in the requested window
When the plan is built
Then 11 hours are patched and 157 hours remain forecast, with a warning or metadata explaining the shorter actual horizon.

### TC7: 2026 comparison fixture path

Given a deterministic February 2026 test fixture with both forecast and eventual actual outcome values
When the comparison function/test runs
Then it reports forecast-vs-actual error without using the outcome values as planner inputs outside the known horizon.

### TC8: Backward-compatible API smoke

Given the existing API call shape:

```text
/api/weekly-home-poc?week=48&ppm=500&houseTemp=22&people=4
```

When the server/API path is exercised
Then it still returns valid JSON with `input`, `summary` and 168 `hours`.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/labs/weekly_home_optimizer_poc
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4 --format json
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --smoke
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 8 --ppm 500 --house-temp 22 --people 4 --format json
git diff --check
```

If the server has no `--smoke` flag in current code, Codex must use the existing smoke command and document it in `design.md`.

## Runtime health checks

No live runtime or device checks. This is Mac lab POC only.

## Deployment plan

No production deployment. This package updates lab POC code/tests/docs only.

## Rollback plan

Rollback is a new forward package. If P0025 behavior is wrong, create a later package that corrects the spot planning contract or disables the new diagnostic fields while preserving package evidence.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- design path
- functions path
- files changed
- tests run
- sample summary for week 48 showing `spot_actual_horizon_hours = 20`
- sample row evidence showing planning vs outcome series separation
- verification results
- commit SHA after push
- uncertainty / skipped checks
- diff summary
