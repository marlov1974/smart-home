# Package P0022: Discrete DP heat optimizer for weekly home POC

## Status
planned

## Package order
P0022

## Primary area
G2 / Mac / whole-house planning / POC / heat optimization / dynamic programming

## Linked requirements

Epic:
- E_TBD: Whole-house optimization

Features:
- F_TBD: Discrete weekly heat optimizer for Mac POC
- F_TBD: Heat-battery-constrained weekly heat planning
- F_TBD: Heat-cost signal for PPM/RH ventilation planning

User stories:
- US_TBD: As an operator, I need the weekly POC heat plan to be a real constrained optimizer so that the plan does not empty the virtual house battery for long periods.
- US_TBD: As the PPM/RH planner, I need a credible `heat_cost_weight` signal based on optimized heat charging/discharging rather than a heuristic heat emulator.
- US_TBD: As a developer, I need a small deterministic heat optimizer without heavy solver dependencies so it can be tested offline and inspected easily.

## Decision summary

- Replace or supplement the current heuristic heat-plan emulator in the weekly home POC with a discrete dynamic-programming heat optimizer.
- The optimizer shall choose hourly heat output from discrete modes:

```text
2, 3, 4, ..., 22 kW
```

- Treat these modes as delivered thermal output for the first optimizer version, not electrical input.
- Optimize over the operational week:

```text
Monday 06:00 -> next Monday 06:00
168 hours
```

- Use a discrete heat battery/SOC state.
- Avoid SciPy, MILP, pandas, numpy, scikit-learn or other heavy dependencies.
- This remains Mac POC/lab tooling and must not control live VP, FTX, Shelly or Home Assistant runtime.

## Solution model

Current POC stages remain:

```text
weather + spot + input -> heat plan -> heat_cost_weight -> PPM/RH ventilation plan
```

P0022 changes the heat-plan stage from a heuristic allocation to a constrained optimizer:

```text
state:
  heat_soc_kWh[t]

decision:
  heat_kw[t] in {2..22}

dynamics:
  heat_soc_kWh[t+1] = heat_soc_kWh[t] + heat_kw[t] - heat_need_kWh[t]

objective:
  minimize weekly heat cost + SOC penalties + optional power shaping penalties
```

The output shape consumed by PPM/RH planning should remain compatible:

```text
heat_need_kWh[168]
heat_kWh[168]
heat_soc_pct[168]
heat_cost_weight[168]
```

## Current behavior

P0018/P0020/P0021 created a working browser-accessible weekly home POC with real Open-Meteo weather and configurable people/CO2 pressure. The POC output shows realistic PPM behavior, but heat planning is still an emulator.

Observed issue:

```text
heat_soc_pct can fall to 0% and remain there for many hours
```

This means the heat plan is not yet a credible optimized whole-house heat plan and can produce misleading `heat_cost_weight` signals for ventilation.

## Problem

The current heat plan does not enforce a real comfort/thermal-battery constraint. It may defer too much heating into expensive periods or let SOC run empty. That is acceptable for early PPM/RH exploration, but not for the next optimizer iteration.

The POC needs a cheap, deterministic algorithm that can optimize heat over a week while respecting a bounded house heat battery.

## Target behavior

Implement a discrete dynamic-programming heat optimizer for the weekly home POC.

### Heat modes

Allowed heat output modes:

```text
heat_modes_kw = [2, 3, 4, ..., 22]
```

This gives 21 candidate actions per hour.

### Heat demand

Use the existing POC heat-need model unless Codex finds and documents a repository-approved replacement:

```text
HOUSE_LOSS_KWH_DAY_PER_C = 12.5
BASE_INTERNAL_KWH_DAY = 42.0

heat_need_day_kWh[t] = max(0, 12.5 * (set_temp_c - outdoor_temp_c[t]) - 42.0)
heat_need_kWh[t] = heat_need_day_kWh[t] / 24.0
```

The optimizer shall consume the same hourly weather profile used by P0021.

### Heat price

Use hourly spot index expanded from the P0017 8h period model as current input, unless an hourly price/index model exists in the repo.

Start cost:

```text
heat_energy_cost[t, mode] = heat_kw[mode] * heat_price_index[t]
```

If a COP proxy already exists in the POC, Codex may use:

```text
heat_energy_cost[t, mode] = heat_kw[mode] * heat_price_index[t] / cop_index[t]
```

but must document it. Do not invent a complex COP model in this package.

### Heat battery / SOC

Use a bounded virtual heat battery.

Required configurable constants:

```text
heat_soc_capacity_kWh
heat_soc_step_kWh
start_soc_pct
end_soc_min_pct
min_soc_pct
max_soc_pct
```

Start defaults for POC:

```text
heat_soc_capacity_kWh = 300
heat_soc_step_kWh = 1
start_soc_pct = 100
end_soc_min_pct = 50
min_soc_pct = 0
max_soc_pct = 100
```

The POC assumption that the house starts full/charged remains valid:

```text
start_soc_pct = 100
```

The DP must keep SOC in bounds:

```text
0 <= heat_soc_pct[t] <= 100
```

The end state should satisfy:

```text
heat_soc_pct[168] >= end_soc_min_pct
```

If strict end constraint makes a scenario infeasible, the optimizer may use a documented high penalty fallback instead of failing hard, but the output must expose the infeasibility/fallback warning.

### Comfort/SOC penalties

Even though SOC 0 is technically within bounds, the optimizer should not prefer long periods at zero if avoidable. Add soft penalties for low SOC, for example:

```text
soc_penalty[t] = 0 for soc_pct >= 25
soc_penalty[t] increases convexly below 25
```

or use a stricter default:

```text
min_comfort_soc_pct = 10 or 20
```

Codex must choose the simplest deterministic design and document it in `requirements/package-runs/P0022/design.md`.

Expected behavior:

```text
- heat_soc_pct should not sit at 0 for long periods when a feasible alternative exists
- heat production should shift toward cheap hours
- expensive hours may discharge the battery, but not destroy comfort feasibility
- end SOC should be at or above the configured minimum or output a warning
```

### Heat-cost weight for PPM/RH planner

The optimizer must continue producing `heat_cost_weight[t]` for the PPM/RH planner.

Preferred semantics:

```text
low heat_cost_weight:
  heat plan is charging or heat price is cheap; ventilation heat loss is cheaper

high heat_cost_weight:
  heat plan is discharging, price is high, or SOC is low; ventilation heat loss is expensive
```

Start formula may be:

```text
base = normalized_heat_price_index[t]

if heat_kWh[t] > heat_need_kWh[t] + margin:
  multiplier = 0.5
elif heat_kWh[t] < heat_need_kWh[t] - margin:
  multiplier = 2.0
else:
  multiplier = 1.0

if heat_soc_pct[t] < low_soc_threshold:
  multiplier = max(multiplier, 2.0)

heat_cost_weight[t] = clamp(base * multiplier, 0.25, 2.5)
```

Codex may tune this if the intent is preserved and the formula is documented.

### Output metadata

The plan summary and JSON/HTML output shall expose heat optimizer metadata:

```text
heat_optimizer = "discrete_dp"
heat_modes_kw
heat_soc_capacity_kWh
heat_soc_step_kWh
start_soc_pct
end_soc_min_pct
min_heat_soc_pct
end_heat_soc_pct
heat_optimizer_warnings
```

Hourly rows should continue to include:

```text
heat_need_kWh
heat_kWh
heat_soc_pct
heat_cost_weight
```

If inexpensive, include:

```text
heat_price_index
heat_action_kw
heat_dp_cost_component
soc_penalty_component
```

`heat_kWh` may equal `heat_action_kw` because each time step is one hour.

## Algorithm requirements

Use dynamic programming / shortest path over discrete SOC states and heat modes.

Approximate size with defaults:

```text
168 hours * 301 SOC states * 21 heat modes ~= 1.1M transitions
```

This is small enough for standard-library Python.

Implementation must be deterministic.

Tie-breaking should be stable. Prefer lower power in ties unless design documents another rule.

No heavy solver or scientific dependencies.

## Browser/API behavior

The browser UI and JSON API from P0020/P0021 should continue to work.

Existing URLs should remain valid:

```text
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=3
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=6
```

The output should make it clear that heat is now optimized with `discrete_dp`.

The UI should visibly warn if:

```text
heat_optimizer_warnings is non-empty
heat_soc_pct reaches 0
end SOC is below configured target
```

## Non-goals

- No live heat-pump control.
- No live FTX control.
- No Shelly changes.
- No Home Assistant changes.
- No launchd installation.
- No exact heat-pump COP model unless already available and trivial to reuse.
- No exact floor/slab thermodynamic model.
- No multi-zone room temperature model.
- No continuous LP/MILP solver.
- No external optimizer dependency.
- No changing P0017 spot forecast compact API.
- No changing P0021 real-weather provider semantics except as required to feed heat optimization.

## Invariants

- This remains Mac POC/lab tooling only.
- G2 POC output must not be treated as current G1 runtime behavior.
- Current G1 runtime in `marlov1974/shelly` must not be modified.
- Browser/API must remain read-only and side-effect-free beyond running the local calculation.
- Server must not perform live actuator writes.
- Automated tests must pass offline.
- Weather fetching remains fixture/mockable for tests.
- Normal PPM optimization remains bounded to existing supply modes unless a later package changes it.
- Heat action modes are POC delivered heat-output modes, not live VP commands.

## Knowledge updates

Codex should update durable planning docs if they exist:

```text
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
```

Codex should update function documentation if reusable heat optimizer functions are created:

```text
docs/functions/mac/weekly-home-optimizer-poc.md
```

Update `memory/bootstrap-manifest.json` only if new memory files become required future bootstrap context.

## Implementation updates

Expected source area:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

Expected additions/changes may include:

```text
heat_plan.py              # replace heuristic with DP optimizer or add selected optimizer mode
heat_optimizer.py         # optional new DP module
schema.py                 # optimizer metadata/warnings
cli.py                    # expose optional heat optimizer config only if useful
server.py/html.py         # display optimizer metadata and warnings
README.md                 # document discrete DP heat optimizer
```

Expected tests:

```text
tests/mac/weekly_home_optimizer_poc/test_heat_optimizer_dp.py
tests/mac/weekly_home_optimizer_poc/test_heat_optimizer_constraints.py
tests/mac/weekly_home_optimizer_poc/test_heat_optimizer_output_metadata.py
tests/mac/weekly_home_optimizer_poc/test_heat_cost_weight_from_dp.py
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md
requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md
requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md
src/mac/labs/weekly_home_optimizer_poc/**
tests/mac/weekly_home_optimizer_poc/**
docs/functions/mac/weekly-home-optimizer-poc.md
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
```

Optional docs may not exist. Do not fail solely because optional docs are absent.

## Files allowed to change

```text
src/mac/labs/weekly_home_optimizer_poc/**
tests/mac/weekly_home_optimizer_poc/**
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
docs/functions/mac/weekly-home-optimizer-poc.md
docs/functions/00-index.md
requirements/package-runs/P0022/**
```

## Forbidden changes

- Do not change `marlov1974/shelly`.
- Do not change `dep/s/**` Shelly deploy artifacts.
- Do not change live FTX, VP or Home Assistant runtime.
- Do not add any command that writes to devices.
- Do not bind web server to `0.0.0.0` by default.
- Do not add `reference_year` to public input.
- Do not silently fall back from real weather to synthetic weather.
- Do not make tests require live internet.
- Do not add heavy/scientific/ML/optimizer dependencies.
- Do not implement live VP command mapping for the 2..22 kW modes.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Useful review output should be stored under:

```text
requirements/package-runs/P0022/review.md
```

Review checks:

```text
- package vs memory
- package vs P0018/P0020/P0021 implementation/evidence
- package vs heat-pump and heat-loss assumptions
- package vs Mac lab structure
- package vs G1/G2 boundary
- package vs testability/offline constraints
- package vs browser/API compatibility
```

## Implementation design policy

For this code package, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0022/design.md
```

The design must cover:

```text
- package interpretation
- selected SOC capacity/step/default constraints
- DP state/action representation
- transition equation
- objective function and penalties
- feasibility/fallback behavior
- heat_cost_weight derivation
- output metadata/warnings
- browser/API impact
- files/modules intended to change
- files/modules intentionally not changed
- tests and manual verification
- risks and uncertainties
```

## Function design policy

For this code package, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0022/functions.md
```

The function design must list intended new, changed and removed functions, including purpose, inputs, outputs, side effects, reason and test coverage.

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Local Mac HTTP testing allowed:
yes

Phone/LAN browser manual test allowed:
yes, read-only local POC only

Network weather fetch during manual smoke:
yes, read-only external HTTP weather data only

Network weather fetch during automated tests:
no

Max implementation/debug attempts:
3

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0022/
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

## Test cases

### TC1: DP chooses valid heat modes
Given any valid fixture week
When heat optimization runs
Then every `heat_kWh`/`heat_action_kw` is in `[2, 3, ..., 22]`.

### TC2: SOC bounds
Given a fixture week
When heat optimization runs
Then every `heat_soc_pct` is within `0..100`.

### TC3: End SOC target
Given a feasible fixture week
When heat optimization runs
Then final SOC is at or above `end_soc_min_pct`.

### TC4: Avoids prolonged empty SOC
Given a fixture week where the old emulator would hit zero SOC for many hours
When DP heat optimization runs
Then SOC does not remain at zero for a prolonged period if a feasible alternative exists, or the plan exposes a warning if infeasible.

### TC5: Shifts heat toward cheap hours
Given a fixture with alternating high/low spot periods and sufficient battery capacity
When optimized
Then average heat output is higher in low-price hours than in high-price hours.

### TC6: Heat-cost weight reflects charging/discharging
Given optimized heat output and heat need
When deriving `heat_cost_weight`
Then charging/cheap hours produce lower weights and discharging/low-SOC hours produce higher weights.

### TC7: Output metadata
Given a full weekly POC run
When JSON/API output is produced
Then summary includes `heat_optimizer = discrete_dp` and heat optimizer metadata/warnings.

### TC8: Browser compatibility
Given the local web UI is opened
When a plan is produced
Then existing fields still render and heat optimizer warnings/metadata are visible.

### TC9: No heavy dependencies
Given project dependencies are inspected
When P0022 is implemented
Then no SciPy, MILP solver, pandas, numpy, scikit-learn or PyTorch dependency is added.

### TC10: Offline tests
Given the test suite runs without internet
When weekly_home_optimizer_poc tests run
Then they pass using fixtures/mocks.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0022/design.md`.

Expected command shape:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 6
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
```

Manual phone test command:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Manual phone URL:

```text
http://<mac-lan-ip>:8081/?week=48&ppm=500&houseTemp=22&people=6
```

## Runtime health checks

No live runtime deployment in this package.

For local manual testing, verify:

```text
- heat_optimizer shows discrete_dp
- heat_soc_pct stays within bounds
- heat_soc_pct does not sit at 0 for long periods unless warning says infeasible
- end_heat_soc_pct is at/above target or warning is shown
- PPM/RH plan still returns 168 hours
- no device writes or actuator actions occur
```

## Deployment plan

No deployment in this package.

The server remains manually started from the repo for POC inspection.

## Rollback plan

Rollback is a new forward-moving package.

Because this package is read-only lab tooling, rollback means not running this version or superseding it with a later package.

## Expected Codex output

- consistency review result: PASS/WARN/STOP
- implementation design path
- function design path
- files changed
- tests run
- verification results
- local server command
- phone URL example
- heat optimizer metadata summary
- SOC before/after comparison against old behavior if easy
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- memory updates created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
