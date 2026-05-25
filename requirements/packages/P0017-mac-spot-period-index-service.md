# Package P0017: Mac spot period index service

## Status
planned

## Package order
P0017

## Primary area
G2 / Mac / spot price forecast / tooling

## Linked requirements

Epic:
- E_TBD: Winter heat-pump optimization

Features:
- F_TBD: Mac spot period index forecast service
- F_TBD: Planner price-index input contract

User stories:
- US_TBD: As the winter heat-pump planner, I need 21 compact period price indexes for a requested ISO week so that production can be allocated by relative price shape.
- US_TBD: As an operator, I need the Mac service to expose a minimal trusted-local API.

## Decision summary

- Build the first Mac-side spot price forecast model as a simple week-weight analog/index model.
- The model predicts relative weekly price shape, not absolute SEK/kWh.
- Output is 21 period price indexes for the fixed 8h strategy periods.
- Forecast API takes ISO week number only in v1.
- Forecast API response is only a JSON array of 21 numbers.
- Values are rounded to two decimals.
- The service is intended for trusted local/LAN use in v1.
- Historical 2025 winter converted training/source data exists under `data/spot/spotprices-2025-winter-8h-weekly-period-index.json`.
- Compact API contract is stored in `memory/planning/spot-period-index-api.md`.
- Winter heat-pump planner consumes price indexes through `memory/planning/winter-heat-pump-flex-planner.md`.

## Solution model

The Mac service owns price-index production for the G2 winter heat-pump planner.

The planner needs the expected shape of one operational week expressed as normalized period indexes:

```text
period_price_index = period_price / week_mean_price
```

The model produces one 21-value vector for a requested ISO week.

Period order is fixed:

```text
0   mon 06-14
1   mon 14-22
2   mon 22-06
3   tue 06-14
4   tue 14-22
5   tue 22-06
6   wed 06-14
7   wed 14-22
8   wed 22-06
9   thu 06-14
10  thu 14-22
11  thu 22-06
12  fri 06-14
13  fri 14-22
14  fri 22-06
15  sat 06-14
16  sat 14-22
17  sat 22-06
18  sun 06-14
19  sun 14-22
20  sun 22-06
```

Night periods use operational-night attribution:

```text
D 22-06 = D 22-00 + D+1 00-06
```

Initial model:

```text
For requested target_week:
  use historical weeks where ISO week distance is 0, 1 or 2.
  week_weight:
    distance 0 => 1.00
    distance 1 => 0.70
    distance 2 => 0.40
    else       => 0.00

  optionally multiply by recency_weight when multiple years are available.

  predicted_index[p] = weighted_average(historical_week_index[p])
  normalize predicted indexes so arithmetic mean is 1.00 before rounding.
  return 21 values rounded to two decimals.
```

The first training/source dataset is one year of winter 2025 converted total-cost data. With only one source year, the model is effectively a week-neighborhood analog smoother over the available winter weeks. It must still be implemented in a way that naturally supports additional years later.

## Current behavior

- GitHub contains converted winter 2025 data in JSON form.
- GitHub contains a compact API contract for `/spot/period-index?week=WW`.
- There is no Mac service implementation yet.
- The heat-pump flex planner currently depends on period price indexes but has no live Mac provider.

## Problem

The planner needs a small, stable, local provider for 21 period price indexes. The Mac layer should own the first forecast/model service so later improvements can use additional history, recency, weather and market signals without changing the planner contract.

## Target behavior

A local Mac service or runnable Mac module shall expose:

```text
GET /spot/period-index?week=WW
```

Example compact response:

```json
[0.97,0.73,0.38,0.49,0.48,0.33,0.59,0.62,0.77,2.14,3.34,1.73,3.12,2.74,0.57,0.37,0.41,0.34,0.30,0.30,0.29]
```

Behavior:

- Accept `week` as ISO week number.
- Return exactly 21 numbers.
- Round all returned values to two decimals.
- Return compact JSON array by default.
- Return HTTP 400 for invalid week input.
- Return HTTP 404 when the requested week cannot be modeled from available data.
- Avoid adding metadata to the default response.
- Keep the model code deterministic and testable.

## Non-goals

- No weather-aware model in this package.
- No Home Assistant integration in this package.
- No Shelly consumer implementation in this package.
- No automatic launchd deployment unless explicitly added by a later package.
- No dependency on pandas, scikit-learn, numpy or external packages; initial implementation should use Python standard library only.
- No raw uploaded Excel parsing is required if the committed JSON source file is sufficient.

## Invariants

- The compact response must remain a plain JSON array of 21 numbers.
- Array order must match `memory/planning/spot-period-index-api.md`.
- Indexes are relative to weekly mean price; 1.00 means weekly mean price.
- Values are rounded to two decimals only at output boundary.
- Internal calculations should retain higher precision.
- Operational-night attribution must be preserved.
- Forecast v1 must not give different results merely because a future year differs; week number and current model/data drive the output.
- G2 design/code in `smart-home` must not be treated as current G1 runtime behavior.

## Knowledge updates

Memory files to inspect and update only if implementation reveals a contract change:

```text
memory/planning/spot-period-index-api.md
memory/planning/winter-heat-pump-flex-planner.md
memory/device-management/mac-layer.md
```

## Implementation updates

Expected source areas:

```text
src/mac/services/spot_forecast/
tests/mac/spot_forecast/
```

Suggested files:

```text
src/mac/services/spot_forecast/README.md
src/mac/services/spot_forecast/model.py
src/mac/services/spot_forecast/server.py
src/mac/services/spot_forecast/schema.py
tests/mac/spot_forecast/test_week_weight_model.py
tests/mac/spot_forecast/test_period_index_api.py
tests/mac/spot_forecast/test_contract_shape.py
```

Deploy artifacts are optional in this package. If added, use:

```text
dep/m/services/spot_forecast/
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
memory/device-management/mac-layer.md
memory/planning/spot-period-index-api.md
memory/planning/winter-heat-pump-flex-planner.md
memory/planning/spotprice-2025-winter-8h-weekly-period-index.md
data/spot/spotprices-2025-winter-8h-weekly-period-index.json
requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md
requirements/packages/P0013-spotprice-low-memory-se-elpris-runtime.md
```

## Files allowed to change

```text
src/mac/services/spot_forecast/**
tests/mac/spot_forecast/**
dep/m/services/spot_forecast/**
memory/planning/spot-period-index-api.md
memory/planning/winter-heat-pump-flex-planner.md
docs/functions/**
requirements/package-runs/P0017/**
```

Codex may also update packaging/check files if required for tests, but must document why in `requirements/package-runs/P0017/design.md`.

## Forbidden changes

- Do not change G1 `marlov1974/shelly` runtime code.
- Do not change Shelly deploy artifacts.
- Do not change heat-pump production allocation logic in this package.
- Do not change compact response to an object by default.
- Do not add external Python dependencies in v1.
- Do not replace or delete the historical converted JSON data file.
- Do not make Friday daytime a special planner group here; that belongs to planner logic, not the spot-index service.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Useful review output should be stored under:

```text
requirements/package-runs/P0017/review.md
```

## Implementation design policy

For code packages, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0017/design.md
```

## Function design policy

For code packages, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0017/functions.md
```

Codex must update function design before making an undocumented function-level change, or stop if the change expands package scope.

## Context-reset phase gates

For substantial code packages, Codex should use phase gates that may run in fresh context:

```text
bootstrap -> review -> design -> function design -> implementation -> build/generation -> test/debug/verify -> final evidence
```

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

Useful debug output should be stored under:

```text
requirements/package-runs/P0017/
```

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0017/
```

Expected evidence files when relevant:

```text
review.md
design.md
functions.md
attempts.md
findings.md
logs/
```

Reusable global lessons should be promoted to:

```text
memory/knowhow/
```

## Test cases

### TC1: Compact response shape
Given a valid modeled ISO week
When `/spot/period-index?week=WW` is requested
Then the response is a JSON array with exactly 21 numeric values and no object metadata.

### TC2: Two-decimal output
Given a valid modeled ISO week
When the endpoint returns indexes
Then every number is rounded to at most two decimals.

### TC3: Week-weight model
Given historical records for target week and nearby weeks
When the forecast model runs
Then only weeks with ISO week distance 0, 1 or 2 contribute, using weights 1.00, 0.70 and 0.40.

### TC4: Normalization
Given weighted raw indexes
When the forecast vector is produced
Then the unrounded vector is normalized to arithmetic mean 1.00 before output rounding.

### TC5: Invalid input
Given missing, non-numeric or out-of-range week input
When the endpoint is requested
Then HTTP 400 is returned with a small JSON error object.

### TC6: Missing model data
Given a valid ISO week that cannot be modeled from available data
When the endpoint is requested
Then HTTP 404 is returned with a small JSON error object.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0017/design.md`.

Expected command shape:

```text
python3 -m unittest discover tests/mac/spot_forecast
python3 src/mac/services/spot_forecast/server.py --once --week 2
```

## Runtime health checks

No live runtime deployment in this package.

For local service testing, verify:

- process starts without exception
- valid week returns 21-number array
- invalid week returns HTTP 400
- unknown modeled week returns HTTP 404
- no unexpected stdout/stderr stack traces

## Deployment plan

No production deployment required in this package unless Codex explicitly scopes a local Mac service artifact under `dep/m/services/spot_forecast/`.

## Rollback plan

Rollback is a new forward-moving package. Do not rely on lowering runtime versions.

Because this package should not affect live Shelly runtime, rollback is expected to mean disabling/not running the Mac service or superseding it with a later package.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification results
- local service observations when tested
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- knowhow promotions created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
