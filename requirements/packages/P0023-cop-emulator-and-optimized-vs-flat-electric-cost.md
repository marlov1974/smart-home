# Package P0023: COP emulator and optimized-vs-flat electric cost comparison

## Status
planned

## Package order
P0023

## Primary area
G2 / Mac / weekly home optimizer POC / heat planning / cost reporting / COP emulation

## Linked requirements

Epic:
- E_TBD: Whole-house optimization

Features:
- F_TBD: COP-emulated electric cost accounting for weekly heat plans
- F_TBD: Optimized heat plan versus flat production baseline comparison
- F_TBD: Weekly home POC cost transparency

User stories:
- US_TBD: As an operator, I want to see whether optimized heat planning is cheaper than straight heat production, so I can judge whether the optimizer is useful.
- US_TBD: As an operator, I want the UI to show a simple relative cost result such as "optimized heat did the job at 73% of flat-production cost".
- US_TBD: As a developer, I need a deterministic first COP emulator so optimized heat cost is based on estimated electrical input, not thermal output.

## Decision summary

- Add a first-version COP emulator to the Mac weekly home optimizer POC.
- Use the COP emulator to convert thermal heat output to estimated electrical kWh.
- Compute electric cost for the optimized DP heat plan.
- Compute electric cost for a baseline called `flat_production`, meaning each hour produces that hour's heat need directly:

```text
flat_heat_kWh[t] = heat_need_kWh[t]
```

- Compare the two costs and expose:

```text
optimized_vs_flat_cost_pct = optimized_heat_el_cost_total / flat_heat_el_cost_total * 100
optimized_saving_pct = 100 - optimized_vs_flat_cost_pct
```

- Keep the POC read-only. No live VP, FTX, Shelly or Home Assistant control.

## Current behavior

P0022 added a discrete dynamic-programming heat optimizer. Current output includes:

```text
heat_optimizer = "discrete_dp"
heat_modes_kw = [2..22]
heat_soc_pct
heat_action_kw
heat_kWh
heat_price_index
heat_dp_cost_component
soc_penalty_component
heat_cost_weight
```

The optimizer currently minimizes thermal production cost proxy. It does not yet expose whether the optimized schedule is cheaper than a straight hourly production baseline in estimated electrical terms.

## Problem

The POC needs an operator-facing efficiency/result metric:

```text
optimized did the same weekly heat job at X% of flat-production electric cost
```

Without this, it is hard to know whether the heat optimizer actually saves cost or only reshapes the SOC graph.

Also, thermal kWh and electrical kWh are not the same for a heat pump. A first COP approximation is needed before reporting electric cost.

## Target behavior

Given a weekly plan, output shall include a summary similar to:

```json
{
  "heat_cost_model": "cop_emulated_v1",
  "optimized_heat_el_kWh": 412.3,
  "flat_heat_el_kWh": 438.8,
  "optimized_heat_el_cost": 521.4,
  "flat_heat_el_cost": 714.2,
  "optimized_vs_flat_cost_pct": 73.0,
  "optimized_saving_pct": 27.0,
  "avg_cop_optimized": 3.33,
  "avg_cop_flat": 3.12
}
```

The browser UI should show this in plain language, for example:

```text
Optimized heat cost: 73% of flat production (-27%)
```

## COP emulator v1

Implement a deterministic first COP emulator.

### Required function semantics

```text
estimate_cop(outdoor_temp_c, heat_kw) -> cop
```

Inputs:

```text
outdoor_temp_c: hourly outdoor temperature from the same weather profile as heat planning
heat_kw: delivered thermal output for the hour
```

Output:

```text
cop: estimated heat pump COP, clamped to a plausible POC range
```

### Initial formula

Use this as the required starting point unless Codex finds a clearly better repo-approved assumption and documents it:

```text
base_cop = 4.2  # around +5 C and medium load

temp_component:
  if outdoor_temp_c < 5:
    temp_adjustment = -0.055 * (5 - outdoor_temp_c)
  else:
    temp_adjustment = min(0.4, 0.03 * (outdoor_temp_c - 5))

load_component:
  2..6 kW:   +0.15
  7..14 kW:   0.0
  15..18 kW: -0.15
  19..22 kW: -0.35

cop = clamp(base_cop + temp_adjustment + load_component, 2.2, 5.2)
```

Expected rough behavior:

```text
-10 C, 22 kW -> COP about 3.0
  0 C, 12 kW -> COP about 3.9
 +5 C,  8 kW -> COP about 4.2
 +7 C,  5 kW -> COP about 4.4
```

This is intentionally an emulator, not a verified heat-pump model.

### Rationale

The first version should capture only the largest obvious effects:

```text
- colder outdoor temperature reduces COP
- very high thermal output is less efficient
- mild weather and low/moderate output can be more efficient
```

Do not model brine temperature, compressor maps, start/stop losses, defrost, flow temperature, DHW or exact Mitsubishi/Geodan behavior in this package.

## Optimized heat electric cost

For each hour in the optimized plan:

```text
optimized_heat_kWh[t] = heat_kWh[t]
optimized_cop[t] = estimate_cop(outdoor_temp_c[t], optimized_heat_kWh[t])
optimized_heat_el_kWh[t] = optimized_heat_kWh[t] / optimized_cop[t]
optimized_heat_el_cost[t] = optimized_heat_el_kWh[t] * heat_price_index[t]
```

Weekly totals:

```text
optimized_heat_el_kWh_total = sum(optimized_heat_el_kWh)
optimized_heat_el_cost_total = sum(optimized_heat_el_cost)
avg_cop_optimized = sum(optimized_heat_kWh) / sum(optimized_heat_el_kWh)
```

## Flat-production baseline

Define baseline as direct hourly heat production matching heat need:

```text
flat_heat_kWh[t] = heat_need_kWh[t]
flat_cop[t] = estimate_cop(outdoor_temp_c[t], flat_heat_kWh[t])
flat_heat_el_kWh[t] = flat_heat_kWh[t] / flat_cop[t]
flat_heat_el_cost[t] = flat_heat_el_kWh[t] * heat_price_index[t]
```

Weekly totals:

```text
flat_heat_el_kWh_total = sum(flat_heat_el_kWh)
flat_heat_el_cost_total = sum(flat_heat_el_cost)
avg_cop_flat = sum(flat_heat_kWh) / sum(flat_heat_el_kWh)
```

Relative comparison:

```text
optimized_vs_flat_cost_pct = 100 * optimized_heat_el_cost_total / flat_heat_el_cost_total
optimized_saving_pct = 100 - optimized_vs_flat_cost_pct
```

If the denominator is zero, output `null` for percentage fields and add a warning.

## Interpretation constraints

The comparison means:

```text
Using the same heat-need model and the same COP emulator, how expensive was the optimized schedule versus producing heat exactly when needed?
```

It does not mean:

```text
verified real-world measured saving
```

The UI and docs must label it as emulated/POC.

## Output schema additions

Summary-level fields:

```text
heat_cost_model = "cop_emulated_v1"
cop_model = "outdoor_temp_and_load_v1"
cop_min
cop_max
optimized_heat_el_kWh
flat_heat_el_kWh
optimized_heat_el_cost
flat_heat_el_cost
optimized_vs_flat_cost_pct
optimized_saving_pct
avg_cop_optimized
avg_cop_flat
heat_cost_comparison_warnings
```

Hourly fields:

```text
cop_optimized
heat_el_kWh
heat_el_cost
flat_heat_kWh
cop_flat
flat_heat_el_kWh
flat_heat_el_cost
```

Keep existing fields stable:

```text
heat_need_kWh
heat_kWh
heat_soc_pct
heat_action_kw
heat_cost_weight
```

## Browser/UI requirements

The browser UI from P0020/P0021/P0022 shall remain accessible and read-only.

Display near the summary:

```text
Heat cost model: COP emulated v1
Optimized electric heat cost: <value>
Flat-production electric heat cost: <value>
Optimized vs flat: <pct>%
Estimated saving: <pct>%
Average COP optimized: <value>
Average COP flat: <value>
```

Preferred operator-facing sentence:

```text
Optimized heat did the weekly job at 73% of flat-production cost.
```

Show a warning marker if `heat_cost_comparison_warnings` is non-empty.

## CLI/API behavior

Existing manual commands and URLs must remain valid:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4
http://<mac-lan-ip>:8081/?week=48&ppm=500&houseTemp=22&people=4
```

The output should include the new cost comparison without requiring a new argument.

Optional future toggles may be designed but are not required:

```text
--cop-model outdoor_temp_and_load_v1
--disable-cop-cost-comparison
```

Do not add required public input for COP.

## Non-goals

- No live heat-pump control.
- No live FTX control.
- No Shelly changes.
- No Home Assistant changes.
- No exact Mitsubishi/Geodan COP model.
- No brine-temperature model.
- No flow-temperature model.
- No DHW/varmvatten modeling.
- No compressor start/stop loss modeling.
- No measured energy import integration.
- No real electricity price API changes.
- No changing P0017 spot forecast compact API.
- No changing P0022 heat optimizer constraints unless strictly required for cost accounting.
- No heavy/scientific dependencies.

## Invariants

- This remains Mac POC/lab tooling only.
- G2 POC output must not be treated as current G1 runtime behavior.
- Current G1 runtime in `marlov1974/shelly` must not be modified.
- Browser/API must remain read-only and side-effect-free beyond running local calculation.
- Server must not perform live actuator writes.
- Automated tests must pass offline.
- Weather fetching remains fixture/mockable for tests.
- COP model must be deterministic.
- Cost comparison must use the same weather and price index as the optimized plan.
- The baseline must use the same heat-need model as the optimized plan.

## Knowledge updates

Codex should update durable planning docs if they exist:

```text
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
```

Codex should update function documentation if reusable functions are created:

```text
docs/functions/mac/weekly-home-optimizer-poc.md
```

Update `docs/functions/00-index.md` only if function docs are added or renamed.

Update `memory/bootstrap-manifest.json` only if new memory files become required future bootstrap context.

## Implementation updates

Expected source area:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

Expected additions/changes may include:

```text
cop.py                    # COP emulator and cost-comparison helpers
heat_optimizer.py         # cost objective may continue using price proxy; only change if needed
model/schema files        # summary/hourly output fields
server/html files         # display comparison
README.md                 # document COP emulator and comparison
```

Expected tests:

```text
tests/mac/weekly_home_optimizer_poc/test_cop_emulator.py
tests/mac/weekly_home_optimizer_poc/test_heat_cost_comparison.py
tests/mac/weekly_home_optimizer_poc/test_heat_cost_summary_fields.py
tests/mac/weekly_home_optimizer_poc/test_browser_heat_cost_rendering.py
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md
requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md
requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md
requirements/packages/P0022-discrete-dp-heat-optimizer-for-weekly-home-poc.md
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
requirements/package-runs/P0023/**
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
- Do not present emulated savings as measured real savings.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Useful review output should be stored under:

```text
requirements/package-runs/P0023/review.md
```

Review checks:

```text
- package vs memory
- package vs P0018/P0020/P0021/P0022 implementation/evidence
- package vs heat-pump assumptions
- package vs Mac lab structure
- package vs G1/G2 boundary
- package vs testability/offline constraints
- package vs browser/API compatibility
- package vs no-live-control invariant
```

## Implementation design policy

For this code package, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0023/design.md
```

The design must cover:

```text
- package interpretation
- selected COP formula and constants
- flat-production baseline definition
- electric-kWh and cost calculations
- summary/hourly schema changes
- UI rendering changes
- warning behavior
- files/modules intended to change
- files/modules intentionally not changed
- tests and manual verification
- risks and uncertainties
```

## Function design policy

For this code package, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0023/functions.md
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
requirements/package-runs/P0023/
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

### TC1: COP emulator clamps plausible range
Given extreme temperature/load inputs
When `estimate_cop` runs
Then output stays within configured `cop_min..cop_max`.

### TC2: COP decreases in cold weather
Given same heat output
When outdoor temperature decreases
Then COP does not increase.

### TC3: COP penalizes high output
Given same outdoor temperature
When heat output moves from moderate to high mode
Then COP does not increase.

### TC4: Optimized electric cost fields
Given a fixture optimized heat plan
When cost comparison runs
Then optimized hourly and summary electric-kWh/cost fields are present and numerically consistent.

### TC5: Flat-production baseline fields
Given a fixture heat-need profile
When cost comparison runs
Then flat hourly and summary electric-kWh/cost fields are present and use `flat_heat_kWh = heat_need_kWh`.

### TC6: Relative cost percentage
Given known optimized and flat cost totals
When summary is produced
Then `optimized_vs_flat_cost_pct` and `optimized_saving_pct` are correct.

### TC7: Zero denominator warning
Given a zero heat-need/zero flat-cost fixture
When comparison runs
Then percentage fields are null and `heat_cost_comparison_warnings` includes a clear warning.

### TC8: Full POC output includes comparison
Given a weekly POC fixture run
When JSON/API output is produced
Then summary includes `heat_cost_model`, `cop_model`, optimized/flat totals and percentage fields.

### TC9: Browser renders comparison
Given the local web UI renders a plan
When summary is displayed
Then the operator can read optimized vs flat cost percentage and saving percentage.

### TC10: Offline tests
Given the test suite runs without internet
When weekly_home_optimizer_poc tests run
Then tests pass using fixtures/mocks.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0023/design.md`.

Expected command shape:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
```

Manual phone test command:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Manual phone URL:

```text
http://<mac-lan-ip>:8081/?week=48&ppm=500&houseTemp=22&people=4
```

## Runtime health checks

No live runtime deployment in this package.

For local manual testing, verify:

```text
- heat_cost_model shows cop_emulated_v1
- optimized_vs_flat_cost_pct is visible in JSON and UI
- optimized_saving_pct is visible in JSON and UI
- optimized and flat electric cost totals are non-negative
- avg COP fields are plausible
- percentage wording says emulated/POC
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
- heat cost comparison summary
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- memory updates created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
