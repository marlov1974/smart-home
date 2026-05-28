# Package P0021: Real weather and occupancy load for weekly home POC

## Status
planned

## Package order
P0021

## Primary area
G2 / Mac / whole-house planning / POC / weather / CO2 load / browser UI

## Linked requirements

Epic:
- E_TBD: Whole-house optimization

Features:
- F_TBD: Real weather input for weekly heat/PPM/RH POC
- F_TBD: Configurable occupancy CO2 pressure for weekly POC
- F_TBD: Browser-visible weather source and person count

User stories:
- US_TBD: As an operator, I need the weekly POC to use real weather data for the requested week so that heat and RH behavior is not based on synthetic-looking curves.
- US_TBD: As an operator, I need to specify number of people in the house so that I can test harder CO2 pressure and see PPM rise toward upper normal ranges.
- US_TBD: As a developer, I need deterministic fixture fallback for tests so real weather support does not make tests depend on live internet.

## Decision summary

- Replace the default synthetic weather behavior in the weekly home POC with real weather data for normal manual runs.
- Keep deterministic fixture/fallback weather for automated tests and offline developer use.
- Add `people` as a user-controllable POC parameter in CLI, JSON API and browser UI.
- Compute CO2 occupancy pressure from `people` instead of only using a hidden fixed `occupancy_gain_ppm_h` default.
- Make weather source explicit in JSON summary and HTML summary.
- Continue to keep this as read-only Mac POC/lab tooling; no live FTX, VP, Shelly or Home Assistant control.

## Solution model

P0018 created the weekly heat/PPM/RH optimizer POC. P0020 exposed it through a local phone/browser UI. P0021 improves the input fidelity and scenario control:

```text
week + current_ppm + current_house_temp + people
  -> real weather profile for operational week
  -> heat plan
  -> RH policy
  -> PPM plan under chosen CO2 pressure
  -> browser/API output with weather source and people count
```

The POC should now distinguish weather profiles as:

```text
weather_source = real_open_meteo | fixture | synthetic_fallback
```

The source must be visible in:

```text
- JSON summary
- HTML summary
- CLI output metadata/summary
```

## Current behavior

- The browser UI works and returns JSON/HTML with 168 hourly rows.
- Observed output appears synthetic: outdoor temperature and RH repeat smooth daily waves and do not clearly identify their data source.
- Current CO2 pressure is effectively fixed/defaulted. It is not convenient to test harder occupancy from the phone UI.

## Problem

The current POC is hard to validate because weather appears synthetic and the CO2 load cannot be varied from the UI/API. This hides important behavior:

- real weather variation should influence heat plan and RH policy
- higher occupancy should allow PPM to rise higher under low ventilation
- the operator must know whether a run used real weather or fallback data

## Target behavior

### Inputs

Extend POC inputs to include `people`.

Required browser/API/CLI inputs after this package:

```text
week
ppm
houseTemp
people
```

Defaults:

```text
people = 3
```

The earlier P0018 statement that required user input is only week/ppm/houseTemp is superseded for the POC interface by this package. `people` is now part of the manual scenario input. No `reference_year` input may be added.

### Real weather

Normal manual runs should use real weather data for the requested week if available.

Required weather variables per hour:

```text
temperature_2m
relative_humidity_2m
```

The POC operational week remains:

```text
Monday 06:00 -> next Monday 06:00
168 hourly values
```

Because the public input remains week-number-only, the implementation must choose and document an internal strategy for mapping a week number to real weather data without asking the user for reference year. Acceptable strategies include:

```text
- use a configured internal weather reference year
- use the latest completed year for the requested ISO week
- use an internal normal-year/profile-cache strategy
```

The chosen strategy must be documented in `requirements/package-runs/P0021/design.md` and surfaced as metadata, for example:

```text
weather_source
weather_provider
weather_profile_year_or_strategy
weather_fallback_reason
```

Tests must not require live internet. Real weather fetching must be behind a provider interface that can be fixture-backed in tests.

### Weather fallback

If real weather cannot be fetched during manual use, the POC may fall back to fixture/synthetic data, but it must show this clearly:

```text
weather_source = fixture
```

or

```text
weather_source = synthetic_fallback
weather_fallback_reason = <reason>
```

Do not silently use synthetic weather.

### People and CO2 pressure

Add people count to CLI/API/browser UI.

```text
people: integer or numeric value, default 3, valid range 0..20 for POC
```

The PPM model shall derive occupancy gain from people.

Start model:

```text
house_area_m2 = 300
ceiling_height_m = 2.6
house_volume_m3 = 780
outdoor_ppm = 420
base_people = 3
base_occupancy_gain_ppm_h = 70
occupancy_gain_ppm_h = base_occupancy_gain_ppm_h * people / base_people
```

This means:

```text
people = 3 -> 70 ppm/h before ventilation
people = 6 -> 140 ppm/h before ventilation
```

The exact values may be configured in code, but this linear scaling must be the default POC behavior unless Codex documents a better simple model in design.

JSON and HTML output must include:

```text
people
occupancy_gain_ppm_h
```

### Browser UI

Update the phone/browser form to include `people`.

Example URL:

```text
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=6
```

JSON endpoint:

```text
GET /api/weekly-home-poc?week=2&ppm=500&houseTemp=22&people=6
```

### Output summary

JSON `summary` and HTML summary must include at least:

```text
hours
min_ppm
max_ppm
avg_supply_pct
total_heat_kWh
total_cost
people
occupancy_gain_ppm_h
weather_source
weather_provider
weather_profile_strategy
weather_fallback_reason, if any
```

Hourly rows must keep existing useful fields, especially:

```text
outdoor_temp_c
outdoor_rh_pct
heat_kWh
heat_cost_weight
rh_weight
supply_pct
ppm_delta
ppm_absolute
rh_delta
total_cost
```

## Expected behavior to validate

### Case A: default people

Given:

```text
week=2
ppm=500
houseTemp=22
people=3
```

Then the plan should remain in a normal low-to-moderate PPM range unless weather/RH/price conditions encourage otherwise.

### Case B: harder CO2 pressure

Given the same week and house temperature but:

```text
people=6
```

Then `occupancy_gain_ppm_h` should approximately double and the resulting plan should show one or both:

```text
- higher max_ppm than people=3
- higher average supply_pct than people=3
```

The model does not need to force PPM to 800 in every run, but the UI/API must make it possible to test scenarios where stronger CO2 pressure pushes PPM upward under expensive/drying ventilation.

### Case C: weather source visibility

Every run must clearly identify whether real weather or fallback weather was used.

## Non-goals

- No live FTX control.
- No live heat-pump control.
- No Shelly changes.
- No Home Assistant changes.
- No launchd installation.
- No persistence/database unless a tiny optional cache is justified in design.
- No adding `reference_year` to public user input.
- No changing P0017 spot forecast compact API.
- No external Python dependencies unless Codex stops and proposes a package-scope change.
- No test dependency on live internet.

## Invariants

- This remains Mac POC/lab tooling only.
- G2 POC output must not be treated as current G1 runtime behavior.
- Current G1 runtime in `marlov1974/shelly` must not be modified.
- Browser/API must remain read-only and side-effect-free beyond running the local calculation.
- Normal PPM optimization remains bounded to P0018/P0020 normal supply rules unless a later package changes them.
- Weather fallback must be explicit, not silent.
- No `reference_year` field may be added to the public CLI/API/browser form.
- Automated tests must pass offline.

## Knowledge updates

Codex should update durable planning docs if they exist or are created by earlier packages:

```text
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
```

Codex should update function documentation if reusable weather or occupancy functions are created:

```text
docs/functions/mac/weekly-home-optimizer-poc.md
```

Update `memory/bootstrap-manifest.json` only if new memory files become required future bootstrap context.

## Implementation updates

Expected source area:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

Expected changes may include:

```text
input_profiles.py      # real weather provider + fixture fallback
weather.py             # optional provider module
schema.py              # input/output metadata including people/weather_source
ppm_plan.py            # people-derived occupancy gain
cli.py                 # --people option
server.py/html.py      # people field and weather source display
README.md              # manual phone test examples
```

Expected tests:

```text
tests/mac/weekly_home_optimizer_poc/test_real_weather_provider.py
tests/mac/weekly_home_optimizer_poc/test_people_occupancy_load.py
tests/mac/weekly_home_optimizer_poc/test_browser_people_input.py
tests/mac/weekly_home_optimizer_poc/test_weather_source_metadata.py
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md
requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md
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
requirements/package-runs/P0021/**
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
- Do not add heavy/scientific/ML dependencies.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Useful review output should be stored under:

```text
requirements/package-runs/P0021/review.md
```

## Implementation design policy

For this code package, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0021/design.md
```

The design must cover:

- package interpretation
- chosen real weather provider and no-reference-year strategy
- offline fixture/fallback strategy
- weather source metadata
- people input handling in CLI/API/browser UI
- occupancy gain formula
- tests and manual verification
- files/modules intended to change
- files/modules intentionally not changed
- risks and uncertainties

## Function design policy

For this code package, Codex must create package-scoped function design before coding:

```text
requirements/package-runs/P0021/functions.md
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
requirements/package-runs/P0021/
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

### TC1: People input in CLI/API/browser
Given people is supplied as 6
When the POC runs through CLI, JSON API or browser query
Then output metadata includes `people=6` and a higher `occupancy_gain_ppm_h` than default.

### TC2: Default people
Given people is omitted
When the POC runs
Then people defaults to 3 and existing week/ppm/houseTemp flows still work.

### TC3: Occupancy pressure affects plan
Given identical week/ppm/houseTemp with people 3 and people 6
When both plans run using the same deterministic fixture weather
Then people 6 produces higher max PPM and/or higher average supply than people 3.

### TC4: Real weather provider shape
Given a mocked/fixture weather provider response
When the real-weather provider adapter parses it
Then it returns exactly 168 hourly temperature/RH values for the operational week.

### TC5: Weather source metadata
Given real weather, fixture weather, or fallback weather
When a plan is produced
Then summary contains explicit weather source metadata.

### TC6: No silent synthetic fallback
Given real weather fetch fails during manual-mode provider use
When fallback is used
Then output includes a fallback source and reason.

### TC7: Browser form includes people
Given `GET /`
When the page is rendered
Then it contains a people input field.

### TC8: JSON endpoint accepts people
Given `/api/weekly-home-poc?week=2&ppm=500&houseTemp=22&people=6`
When called
Then JSON returns 168 hours and includes people/weather metadata.

### TC9: Offline tests
Given the test suite runs without internet
When all weekly_home_optimizer_poc tests run
Then they pass using fixtures/mocks.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0021/design.md`.

Expected command shape:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22 --people 6
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
```

Manual phone test command:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Manual phone URLs:

```text
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=3
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=6
```

## Runtime health checks

No live runtime deployment in this package.

For local manual testing, verify:

- UI shows people field
- UI/API summary shows weather source
- people=6 changes occupancy gain and plan behavior relative to people=3
- real weather is used when available
- fallback is explicit if real weather is unavailable
- no device writes or actuator actions occur

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
- phone URL examples with people=3 and people=6
- weather source behavior summary
- people/CO2 pressure comparison summary
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- memory updates created/updated
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
