# Package P0018: Mac weekly heat PPM RH optimizer POC

## Status
planned

## Package order
P0018

## Primary area
G2 / Mac / whole-house planning / POC / heat / FTX / PPM / RH policy

## Linked requirements

Epic:
- E_TBD: Whole-house optimization

Features:
- F_TBD: Mac weekly heat planning POC
- F_TBD: Mac weekly PPM target planning POC
- F_TBD: RH-policy-aware ventilation planning POC

User stories:
- US_TBD: As an operator, I need a Mac POC that shows a one-week heat plan and PPM plan so that I can inspect whether the optimizer behaves sensibly before connecting it to live control.
- US_TBD: As the FTX controller, I need a PPM target curve that allows higher PPM when ventilation is expensive or drying, and lower PPM when ventilation is cheap or beneficial.
- US_TBD: As the future whole-house planner, I need RH to be represented as a ventilation policy/cost signal, not as a direct RH setpoint.

## Decision summary

- Build a Mac-only POC for weekly heat + PPM + RH-policy planning.
- The POC is not a live controller and must not change Shelly, FTX, heat-pump or Home Assistant runtime behavior.
- User input is intentionally small:
  - ISO week number
  - current PPM
  - current house temperature
- The POC assumes:
  - the house starts full/charged in the virtual heat battery
  - indoor RH is lower than desired, so RH does not need to be supplied as input in v1
  - week number is the external key; no reference year is part of the public POC input
- The Mac POC fetches or generates its own weekly inputs:
  - hourly outdoor temperature profile for the requested week
  - hourly outdoor relative-humidity profile for the requested week
  - relative spot price index for the requested week from the existing Mac spot period-index service/model
- Current spot input is 21 × 8h period indexes from P0017 and must be expanded to 168 hourly values for this POC.
- Later work may replace the 8h expansion with a true hourly spot forecast model.
- The POC creates:
  - `heat_kWh[168]`
  - `heat_cost_weight[168]`
  - `rh_weight[168]`
  - `supply_pct[168]`
  - `ppm_delta[168]`
  - `ppm_absolute[168]`
  - `rh_delta[168]`
- PPM planning is normal-operation planning only. Supply above 55% belongs to local override for acute PPM, cooling/night-cooling or safety/fault handling.

## Solution model

The package implements a deterministic Mac POC that plans one operational week.

The POC has three conceptual stages:

```text
1. Weekly input builder
   week_number -> weather profile, RH policy profile, spot index profile

2. Heat planner
   weather + spot + current house temp + full-start assumption
   -> heat_kWh[168], heat_cost_weight[168]

3. PPM planner
   heat_cost_weight + rh_weight + current_ppm
   -> supply_pct[168], ppm_delta[168], ppm_absolute[168], rh_delta[168]
```

The POC is meant to make the model inspectable. It should print/export a table where every hour shows the relevant inputs, decisions, modeled effects and cost components.

## Current behavior

- P0017 implements a Mac spot period-index service that returns 21 compact 8h weekly period indexes for a requested week.
- The repo contains FTX airflow documentation with current practical FTX maximum airflow around 250 l/s and normal fan balance rules.
- There is no Mac weekly heat + PPM + RH-policy planner yet.
- There is no POC table that shows heat kWh per hour, PPM target/evolution per hour and RH effect per hour.

## Problem

The whole-house controller has interacting objectives:

- heat optimization wants to minimize cost while using the house as a thermal battery
- ventilation/PPM wants acceptable air quality
- RH/fukt policy may discourage ventilation when air is drying, or reward ventilation when it helps fukt balance

Writing this as many scenario-specific `if` rules would become brittle. The POC should instead express tradeoffs as cost curves and show whether the resulting weekly plan matches operator intuition.

## Target behavior

Create a Mac POC executable/module that can be run from repo root with a simple interface such as:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
```

The exact module path may differ if Codex documents a better repo-consistent structure in the package design, but it must stay under `src/mac/labs/` unless the review phase finds an existing better lab location.

The POC shall produce an inspectable 168-hour plan table.

Minimum human-readable columns:

```text
hour
weekday_hour
outdoor_temp_c
outdoor_rh_pct
spot_index
heat_need_kWh
heat_kWh
heat_soc_pct
heat_cost_weight
rh_weight
supply_pct
flow_lps
vent_cost
ppm_delta
ppm_absolute
rh_delta
ppm_cost
heat_vent_cost
rh_cost
total_cost
```

The POC should also be able to emit JSON or CSV output if this is inexpensive. Human-readable table output is required for the first package.

## User input contract

Required POC inputs:

```text
week_number
current_ppm
current_house_temp
```

No `reference_year` input.

No current indoor RH input.

The POC shall internally use a configured weather-profile provider for `week_number`. In POC v1 this may be:

```text
- a deterministic built-in synthetic profile by week number, or
- an Open-Meteo historical/archive profile selected internally by the implementation, or
- a committed fixture profile
```

Codex must choose one implementable method in `requirements/package-runs/P0018/design.md`. If live internet/API access is not reliable during tests, Codex must provide deterministic fixture fallback so unit tests do not depend on network.

## Heat plan model

The POC heat planner produces hourly values for one week:

```text
heat_kWh[168]
heat_need_kWh[168]
heat_soc_pct[168]
heat_cost_weight[168]
```

Base heat need model:

```text
HOUSE_LOSS_KWH_DAY_PER_C = 12.5
BASE_INTERNAL_KWH_DAY = 42.0

heat_need_day_kWh[t] = max(0, 12.5 * (set_temp_c - outdoor_temp_c[t]) - 42.0)
heat_need_kWh[t] = heat_need_day_kWh[t] / 24.0
```

POC may use a fixed internal `set_temp_c`, documented in design, or derive it from `current_house_temp` if Codex gives a simple reasoned design. The input `current_house_temp` must be retained in the CLI/API and included in output metadata.

The house starts full/charged in the heat-battery model.

Heat planning should be simple and deterministic:

```text
1. Calculate heat_need_kWh[t].
2. Expand spot period index to hourly spot_index[t].
3. Allocate weekly heat production toward lower spot_index hours.
4. Clamp hourly production to reasonable POC limits.
5. Simulate heat battery:
   soc[t+1] = soc[t] + heat_kWh[t] - heat_need_kWh[t]
6. Derive heat_cost_weight[t] for ventilation cost.
```

Start heat production limits:

```text
min_heat_kWh_per_h = 2.0
max_heat_kWh_per_h = 25.0
```

These are POC planning values only, not final live VP constraints.

Start `heat_cost_weight[t]` logic:

```text
base = spot_index_hour[t]

if heat_kWh[t] > heat_need_kWh[t] + margin:
  heat_cost_weight[t] = 0.5 * base
elif heat_kWh[t] < heat_need_kWh[t] - margin:
  heat_cost_weight[t] = 2.0 * base
else:
  heat_cost_weight[t] = 1.0 * base

heat_cost_weight[t] = clamp(heat_cost_weight[t], 0.25, 2.5)
```

Codex may tune `margin` and normalization if it documents the choice and preserves the intended behavior:

```text
- ventilation is cheaper when the heat plan is charging/running hard
- ventilation is more expensive when the heat plan is saving/discharging
```

## Spot index expansion

The POC shall reuse the P0017 spot period-index model/service code if feasible, rather than duplicating the underlying weekly index model.

Input spot shape:

```text
21 values, 8h operational periods
```

For POC v1, expand each 8h period to 8 hourly values to produce:

```text
spot_index_hour[168]
```

Operational-week order starts Monday 06:00 and runs to next Monday 06:00. Period attribution must match the P0017 period order and operational-night semantics.

## RH policy model

RH is a policy/cost signal, not a setpoint and not an absolute RH forecast target.

The POC assumes indoor RH is lower than desired. Therefore ventilation can be considered drying/bad, neutral, or helpful only through a simple hourly policy derived from outdoor temperature/RH profile.

The POC shall produce:

```text
rh_weight[168]
rh_delta[168]
```

Start policy values:

```text
+2.5 = ventilation dries/försämrar RH strongly
+1.5 = ventilation dries/försämrar RH
 0.0 = ventilation is neutral
-1.0 = ventilation helps RH/fukt balance
```

POC v1 does not need a physically accurate moisture model. It must document the chosen heuristic and make output inspectable.

Expected directional behavior:

```text
- colder/drier outdoor profile should usually make ventilation RH-expensive
- neutral outdoor profile should produce rh_weight near 0
- profile that helps fukt balance should produce negative rh_weight
```

`rh_delta[t]` is a coarse result indicator from chosen supply and RH policy. It does not need to be a real percent-RH delta.

## PPM and ventilation model

The POC optimizes normal ventilation only.

Allowed `supply_pct` modes:

```text
25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55
```

These are discrete POC modes.

Normal PPM planning must not use supply above 55%.

Supply above 55% is reserved for local override outside this POC:

```text
- acute PPM
- cooling/night-cooling
- faults/safety/special modes
```

Flow conversion:

```text
flow_lps = supply_pct / 100.0 * 240.0
```

Interpretation:

```text
25% ~= 60 l/s  = PPM save / lowest normal mode
40% ~= 96 l/s  = approximate normal/VVX-good region
55% ~= 132 l/s = PPM recovery / highest normal mode
```

The POC shall model PPM as a state that changes by hourly delta:

```text
ppm[0] = current_ppm
ppm[t+1] = ppm[t] + occupancy_gain_ppm_h[t] + ventilation_delta_ppm[t]
```

Start assumptions:

```text
house_area_m2 = 300
ceiling_height_m = 2.6
house_volume_m3 = 780
outdoor_ppm = 420
occupancy_gain_ppm_h = 70 by default
```

`occupancy_gain_ppm_h` should be configurable in code or CLI, but the required user input remains only week, current PPM and current house temperature.

The ventilation removal may use a simplified linear approximation or the physically motivated dilution formula. If the implementation uses the physically motivated formula, it must keep the optimizer deterministic and tractable for the discrete search.

The useful relation is:

```text
removal_ppm_h ~= flow_lps * 3.6 / volume_m3 * (ppm - outdoor_ppm)
```

Codex must document the selected PPM dynamic model in `design.md`.

## Cost model

The POC minimizes the weekly sum of per-hour costs.

For each hour `t` and candidate supply mode `m`:

```text
total_cost[t, m] =
  ppm_cost(ppm_after[t, m])
  + heat_cost_weight[t] * vent_cost[m]
  + rh_weight[t] * vent_cost[m]
```

Ventilation cost table:

```text
supply_pct: 25  28  31  34  37  40  43  46  49  52  55
vent_cost:   0   1   3   6  10  15  21  28  36  45  55
```

This cost represents how much extra ventilation is being used relative to the lowest normal mode.

Meaning:

```text
heat_cost_weight[t] * vent_cost[m]
  = heat-loss/energy cost of ventilation

rh_weight[t] * vent_cost[m]
  = RH policy cost or reward

ppm_cost(ppm_after)
  = discomfort/air-quality cost of resulting absolute PPM
```

If `rh_weight[t]` is negative, ventilation can be rewarded when it helps fukt balance.

PPM ideal target:

```text
500 ppm
```

If conditions are favorable, the model should tend toward 500 ppm. It must not reward going below 500 ppm.

PPM cost table:

```text
ppm:      <=500 525 550 575 600 625 650 675 700 725 750 775 800 825 850 875 900 925 950 975 1000
ppm_cost:     0   1   3   6  10  15  21  28  36  45  55  66  78  91 105 120 136 153 171 190 210
```

Values above 1000 ppm must keep increasing or be clamped to a very high continuation cost. The exact continuation rule must be documented and tested.

Desired policy behavior to validate:

```text
Case A: RH says ventilate less and heat/spot cost is high
  -> optimizer should choose low supply, often near 25%
  -> PPM should be allowed to rise toward the upper normal range

Case B: RH neutral and heat/spot cost is high
  -> optimizer should still save ventilation, but less aggressively
  -> PPM should tend lower than Case A

Case C: heat/spot cost is low and RH direction is good/helpful
  -> optimizer should ventilate more and move toward 500 ppm
  -> if 46% or 49% is sufficient, optimizer should not unnecessarily choose 55%
```

Because 25% supply is already significant airflow for the modeled house and three-person default, POC tests must allow `occupancy_gain_ppm_h` to vary. A higher occupancy/load scenario may be needed to demonstrate PPM rising toward 800.

## Optimization method

This package does not require SciPy or MILP.

Preferred POC method:

```text
- deterministic dynamic programming / shortest-path over discrete PPM states and 11 supply modes
```

Acceptable simpler method:

```text
- greedy one-hour lookahead only if Codex documents why it is sufficient for POC and tests still demonstrate delayed ventilation behavior
```

The POC should prefer a method that can reason across time, because a key behavior is allowing PPM to rise now and ventilating later when heat/RH cost is better.

Suggested state discretization:

```text
ppm state step: 5 or 10 ppm
ppm range: at least 400..1400 ppm
```

The implementation should reconstruct the chosen hourly plan from the dynamic-programming result.

## Non-goals

- No live FTX control.
- No live heat-pump control.
- No Shelly code changes.
- No Home Assistant changes.
- No persistent service endpoint required in this package.
- No true hourly spot ML forecast in this package.
- No exact indoor RH forecast in this package.
- No floor cooling control in this package.
- No acute PPM override implementation in this package.
- No supply above 55% in the normal POC optimizer.
- No dependency on SciPy, pandas, numpy, scikit-learn or PyTorch unless Codex stops and proposes a package scope change.
- No reliance on live internet during automated tests.

## Invariants

- This is Mac POC/lab code only.
- G2 code/design must not be treated as current G1 runtime behavior.
- Current G1 runtime in `marlov1974/shelly` must not be modified.
- POC output must be deterministic for test fixtures.
- POC must keep user input limited to week number, current PPM and current house temperature.
- No `reference_year` input may be added to public CLI/API.
- Normal PPM optimization must restrict supply to 25..55%.
- RH must remain a policy/cost signal, not an RH setpoint.
- PPM target is represented through absolute PPM curve derived from PPM state and hourly deltas; the optimizer should expose both delta and absolute PPM in output.

## Knowledge updates

Codex should create or update durable planning memory if implementation clarifies this POC contract:

```text
memory/planning/weekly-heat-ppm-rh-poc.md
```

Update `memory/bootstrap-manifest.json` only if the new memory file becomes required future bootstrap context.

Update function docs if new reusable Mac lab functions should be remembered:

```text
docs/functions/mac/weekly-home-optimizer-poc.md
```

## Implementation updates

Expected source area:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

Suggested files:

```text
src/mac/labs/weekly_home_optimizer_poc/README.md
src/mac/labs/weekly_home_optimizer_poc/__init__.py
src/mac/labs/weekly_home_optimizer_poc/__main__.py
src/mac/labs/weekly_home_optimizer_poc/cli.py
src/mac/labs/weekly_home_optimizer_poc/heat_plan.py
src/mac/labs/weekly_home_optimizer_poc/input_profiles.py
src/mac/labs/weekly_home_optimizer_poc/ppm_plan.py
src/mac/labs/weekly_home_optimizer_poc/schema.py
src/mac/labs/weekly_home_optimizer_poc/tables.py
```

Expected tests:

```text
tests/mac/weekly_home_optimizer_poc/
```

Suggested tests:

```text
tests/mac/weekly_home_optimizer_poc/test_cli_contract.py
tests/mac/weekly_home_optimizer_poc/test_heat_plan.py
tests/mac/weekly_home_optimizer_poc/test_ppm_dynamics.py
tests/mac/weekly_home_optimizer_poc/test_ppm_optimizer_policy_cases.py
tests/mac/weekly_home_optimizer_poc/test_output_shape.py
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
memory/device-management/mac-layer.md
memory/physical/ftx/airflow.md
memory/physical/ftx/sensors.md
memory/physical/ftx/temperatures.md
memory/physical/ftx/cooling-risk.md
memory/physical/heating/heat-pumps.md
memory/physical/heating/geodan-smart-grid.md
memory/planning/spot-period-index-api.md
memory/planning/winter-heat-pump-flex-planner.md
requirements/packages/P0017-mac-spot-period-index-service.md
src/mac/services/spot_forecast/**
tests/mac/spot_forecast/**
docs/functions/mac/spot-forecast.md
```

## Files allowed to change

```text
src/mac/labs/weekly_home_optimizer_poc/**
tests/mac/weekly_home_optimizer_poc/**
memory/planning/weekly-heat-ppm-rh-poc.md
docs/functions/mac/weekly-home-optimizer-poc.md
docs/functions/00-index.md
requirements/package-runs/P0018/**
```

Codex may update project packaging/test discovery files only if required and must document why in `requirements/package-runs/P0018/design.md`.

## Forbidden changes

- Do not change `marlov1974/shelly`.
- Do not change `dep/s/**` Shelly deploy artifacts.
- Do not change live FTX/VP/Home Assistant control.
- Do not add a live service endpoint unless explicitly justified as a non-live lab endpoint in design.
- Do not add `reference_year` to the public POC input contract.
- Do not make RH an absolute setpoint target.
- Do not implement cooling override or acute PPM override as live control.
- Do not require external network access for unit tests.
- Do not add heavy ML/scientific dependencies.
- Do not modify P0017 spot service behavior unless an integration bug is found and documented inside P0018 evidence.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Checks:

- package vs memory
- package vs linked requirements
- package vs previous packages, especially P0017
- package vs implementation/deploy structure
- package vs G1/G2 boundary
- package vs FTX airflow facts
- package vs heat-pump capacity and heat-loss assumptions
- package vs invariants
- package vs testability and rollback
- package vs chat-only assumptions that should be made durable first

Useful review output should be stored under:

```text
requirements/package-runs/P0018/review.md
```

## Implementation design policy

For this code package, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0018/design.md
```

The design must cover:

- package interpretation
- weather-profile provider choice and deterministic fallback
- spot-index integration or fixture strategy
- heat planner algorithm
- PPM dynamic model
- optimization method
- cost tables and continuation behavior above 1000 ppm
- output format
- files/modules intended to change
- files/modules intentionally not changed
- test strategy
- risks and uncertainties

## Function design policy

For this code package, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0018/functions.md
```

The function design must list intended new, changed and removed functions, including purpose, inputs, outputs, side effects, reason and test coverage.

Codex must update function design before making an undocumented function-level change, or stop if the change expands package scope.

Durable cross-package function documentation belongs under:

```text
docs/functions/
```

Update the function catalog when functions are created and are relevant for future packages.

## Context-reset phase gates

Codex should use these phase gates:

```text
bootstrap -> review -> design -> function design -> implementation -> test/debug/verify -> final evidence
```

Each phase must read repository artifacts from earlier phases instead of relying on unwritten prior reasoning.

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
3

Codex may fix defects discovered during verification if they are inside package scope. Codex must stop after the attempt limit or if the fix requires scope/design changes.

Useful debug output should be stored under:

```text
requirements/package-runs/P0018/
```

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0018/
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

Do not store large raw logs by default. Prefer summaries or focused excerpts unless this package explicitly requires full logs.

## Test cases

### TC1: CLI input contract
Given `--week`, `--ppm` and `--house-temp`
When the POC runs
Then it produces a 168-hour plan without requiring `reference_year` or current RH.

### TC2: Output shape
Given a valid fixture scenario
When the POC runs
Then output contains 168 rows with heat, PPM, RH and cost columns.

### TC3: Spot expansion
Given a 21-value 8h period index vector
When expanded for the operational week
Then 168 hourly spot index values are produced with correct period attribution.

### TC4: Heat plan balance
Given a deterministic cold weather fixture
When heat planning runs
Then total `heat_kWh` approximately balances total `heat_need_kWh` within documented tolerance, and heat SOC is computed.

### TC5: Supply bounds
Given any optimizer scenario
When the normal PPM planner runs
Then every `supply_pct` is one of `[25,28,31,34,37,40,43,46,49,52,55]`.

### TC6: PPM target behavior under favorable conditions
Given low heat cost and RH that helps ventilation
When the optimizer runs from elevated PPM
Then the plan moves PPM toward 500 and does not choose 55% when a lower mode such as 46% or 49% is sufficient.

### TC7: PPM rises when ventilation is expensive and drying
Given high heat cost and RH that says ventilation dries/försämrar
When the optimizer runs
Then it chooses low supply, often near 25%, and allows PPM to rise relative to favorable conditions.

### TC8: Neutral RH high heat cost is between dry and favorable cases
Given high heat cost and neutral RH
When compared with dry/high-cost and helpful/low-cost scenarios
Then planned PPM and supply are between the two extremes.

### TC9: Configurable occupancy/load
Given a higher `occupancy_gain_ppm_h` fixture
When low supply is selected for expensive/drying hours
Then PPM can rise toward higher levels, demonstrating the policy case where upper normal range approaches 800.

### TC10: No network required in tests
Given the test suite is run offline
When all P0018 tests run
Then tests pass using deterministic fixtures/fallback profiles.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0018/design.md`.

Expected command shape:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json
```

If the implementation chooses a different module path, update the verification commands in design and completion evidence.

## Runtime health checks

No live runtime deployment in this package.

For local POC execution, verify:

- no exceptions
- exactly 168 hourly rows
- supply stays within 25..55 normal modes
- PPM absolute curve is finite and reasonable
- output includes cost components
- no network dependency during tests

## Deployment plan

No deployment in this package.

The POC remains under `src/mac/labs/` and is run manually from the repo or by tests.

## Rollback plan

Rollback is a new forward-moving package.

Because this package does not affect live runtime, rollback means not running the POC or superseding it with a later package.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification results
- sample POC output summary for at least one week
- policy-case comparison summary
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- memory updates created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
