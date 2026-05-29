# Package P0024: Hourly spot forecast with actual-price patching

## Status
planned

## Package order
P0024

## Primary area
G2 / Mac / weekly home optimizer POC / spot price forecast / price-index modeling / fixture data

## Linked requirements

Epic:
- E_TBD: Whole-house optimization

Features:
- F_TBD: Hourly spot-price index for weekly optimizer POC
- F_TBD: Actual spot-price patching into forecast index curve
- F_TBD: DST-safe 2025 spot-price fixture usage

User stories:
- US_TBD: As an operator, I want the optimizer to use hourly spot-price values instead of coarse period values, so weekly heat and ventilation optimization can react to real hourly price shape.
- US_TBD: As an operator, I want known actual spot prices to replace the forecast shape where available, while preserving the forecast model scale.
- US_TBD: As a developer, I want a deterministic DST-safe 2025 hourly spot fixture, so tests and POC runs can reproduce known price weeks offline.

## Decision summary

Change the weekly home optimizer POC spot model so that it always emits 168 hourly spot-index values for the requested week.

Where actual spot prices exist, the model shall patch the forecast index using actual price shape:

1. Build hourly forecast index for the whole 168-hour week.
2. Load actual hourly prices where available.
3. Convert actual prices for the known overlap period to a proto-index.
4. Compute the forecast index sum for the same overlap period.
5. Rescale actual proto-index so its sum equals the forecast index sum for that period.
6. Replace forecast values with patched actual-index values for those hours.
7. Keep forecast values for hours without actual prices.

This makes known actual spot hours affect the hourly shape without unexpectedly changing the whole model scale.

## Input data from conversion work

A DST-safe conversion was performed from a 2025 CET/CEST 15-minute price series.

Committed metadata report:

```text
data/spot/spot_2025_conversion_report.json
```

Generated local artifacts from the conversion:

```text
/mnt/data/spot_2025_hourly_europe_stockholm.csv
/mnt/data/spot_2025_15m_europe_stockholm_resolved.csv
/mnt/data/spot_2025_conversion_report.json
```

The intended repository fixture is:

```text
data/spot/spot_2025_hourly_europe_stockholm.csv
```

The hourly fixture has these columns:

```text
utc_hour_start
local_hour_start
local_wall_hour
utc_offset
fold
quarter_count
price_mean
price_min
price_max
```

Recommended canonical fields for code:

```text
utc_hour_start      # primary chronological key
local_hour_start    # human-readable local hour including offset
fold                # distinguishes repeated autumn DST hour
price_mean          # hourly spot price from four 15-minute values
```

The conversion report verifies:

```text
input_rows = 35040
resolved_15m_rows = 35040
hourly_rows = 8760
timezone = Europe/Stockholm
utc_15m_gaps_count = 0
all_hourly_quarter_count_is_4 = true
spring_2025_03_30_hour_count_local_day = 23
fall_2025_10_26_hour_count_local_day = 25
```

## Important data-handling note

If `data/spot/spot_2025_hourly_europe_stockholm.csv` is not present when implementation starts, Codex must stop with a clear message unless the user has placed it locally.

Codex may use the committed report to verify expected shape, but it must not fabricate price rows from the report. The actual hourly CSV is the source for actual prices.

## Current behavior

The weekly home optimizer POC currently uses a relative spot-price shape that behaves like coarse period/block values. Recent output shows repeated blocks and summary fields such as:

```text
spot_index
heat_price_index
```

The optimizer can run but does not yet use an explicitly hourly spot forecast with actual spot-price patching.

## Problem

The heat optimizer and COP/electric-cost reporting depend strongly on spot-price timing. Period/block values are too coarse for the weekly optimizer because they hide intra-day variation.

Also, when actual spot prices are known for part or all of a week, the POC should use their actual hourly shape rather than the synthetic forecast shape.

## Target behavior

For every POC run, the spot model shall produce a 168-hour series:

```text
spot_index[t] for t in 0..167
```

Each hour should expose provenance:

```text
spot_source = forecast | actual_patched
```

When actual prices are available for hours in the requested week, those hours should be patched into the forecast index as normalized actual shape.

## Actual-price patch algorithm

Given:

```text
forecast_index[t]  # 168-hour forecast index
actual_price[t]    # hourly actual spot price for some subset of hours
K                  # overlap hours where actual_price exists
```

Compute:

```text
actual_mean = mean(actual_price[t] for t in K)
actual_proto_index[t] = actual_price[t] / actual_mean
forecast_known_sum = sum(forecast_index[t] for t in K)
actual_proto_sum = sum(actual_proto_index[t] for t in K)
patched_actual_index[t] = actual_proto_index[t] * forecast_known_sum / actual_proto_sum
```

Then:

```text
if t in K:
  spot_index[t] = patched_actual_index[t]
  spot_source[t] = "actual_patched"
else:
  spot_index[t] = forecast_index[t]
  spot_source[t] = "forecast"
```

If `actual_proto_sum` is zero or no overlap exists, do not patch and emit a warning.

## Required deterministic example

The implementation must have a unit test equivalent to:

```text
forecast_index for known period = [1, 1, 2, 2]
forecast_known_sum = 6
actual_price = [10, 20, 30, 40]
actual_mean = 25
actual_proto = [0.4, 0.8, 1.2, 1.6]
actual_proto_sum = 4
patched = actual_proto * 6 / 4 = [0.6, 1.2, 1.8, 2.4]
sum(patched) = 6
```

The test must verify both shape replacement and sum preservation.

## Forecast hourly model

The existing forecast index model must be changed or wrapped so the public result is always hourly.

Required properties:

```text
- exactly 168 values for a requested week
- one value per POC hour
- no period/block-only public API
- stable deterministic behavior when actual fixture is absent or does not overlap
- compatible with existing weekly POC inputs: week, ppm, houseTemp, people
```

The internal forecast model may continue using coarse assumptions as a first approximation, but it must be expanded to hourly values before patching and before optimizer use.

## 2025 fixture semantics

The actual-price fixture covers calendar year 2025 in Europe/Stockholm local time after DST resolution.

For local dates:

```text
2025-03-30 has 23 local hours
2025-10-26 has 25 local hours, including two distinct 02:00 hours
```

Implementation must use `utc_hour_start` as the canonical unique key and chronological ordering key.

Do not join only on `local_wall_hour`; that is ambiguous on the autumn DST day.

## Public output schema additions

Summary fields:

```text
spot_model = "hourly_forecast_with_actual_patch_v1"
spot_resolution = "hourly"
spot_actual_fixture_path
spot_actual_known_hours
spot_forecast_hours
spot_actual_patched_hours
spot_patch_strategy = "actual_shape_forecast_sum"
spot_index_min
spot_index_max
spot_index_avg
spot_patch_warnings
```

Hourly fields:

```text
spot_index
spot_source
spot_forecast_index
spot_actual_price
spot_actual_proto_index
spot_patched_actual_index
```

Debug fields may be nullable where not applicable.

Keep existing fields stable:

```text
spot_index
heat_price_index
heat_cost_weight
```

## Browser/UI requirements

The browser UI must remain read-only.

Show summary-level spot metadata:

```text
Spot model: hourly forecast with actual patch v1
Actual patched hours: <n>
Forecast hours: <n>
Spot index min/max/avg
Warnings, if any
```

The hourly table/JSON view should include at least:

```text
spot_index
spot_source
```

It is acceptable for detailed debug columns to appear only in JSON or behind the existing JSON view.

## CLI/API behavior

Existing commands and URLs must remain valid:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4
http://<mac-lan-ip>:8081/?week=48&ppm=500&houseTemp=22&people=4
```

No new required public argument shall be added.

Optional future/debug arguments are allowed only if defaults preserve existing usage:

```text
--spot-fixture data/spot/spot_2025_hourly_europe_stockholm.csv
--disable-actual-spot-patch
--spot-debug
```

## Non-goals

- No live Nord Pool API integration.
- No electricity tariff/tax/grid-fee model.
- No absolute SEK billing promise.
- No VP/FTX/Shelly live control.
- No Home Assistant changes.
- No changing weather fetching behavior except as needed for time alignment.
- No adding `reference_year` as a public input.
- No heavy/scientific/ML dependencies.
- No changing P0023 COP formula unless strictly required for field wiring.

## Invariants

- Mac POC remains read-only.
- Automated tests must run offline.
- Actual spot fixture must be local-file based.
- No automated test may require live internet.
- `utc_hour_start` is the unique actual-price key.
- Patch algorithm must preserve forecast sum over known actual overlap hours.
- The POC must still produce exactly 168 hours.
- Existing PPM, RH and heat optimizer fields must remain present.
- Do not modify current G1 runtime in `marlov1974/shelly`.

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

Codex should add or update a data note if the repo has a suitable data docs location. If not, add:

```text
data/spot/README.md
```

The README should document:

```text
- fixture source shape
- timezone handling
- DST spring/fall behavior
- canonical key
- price column semantics
- conversion report path
```

## Implementation updates

Expected source area:

```text
src/mac/labs/weekly_home_optimizer_poc/
```

Expected additions/changes may include:

```text
spot.py or spot_forecast.py       # hourly forecast + actual patch logic
server/html files                 # spot metadata display
model/schema files                # new summary/hourly fields
README.md                         # spot model docs
```

Expected data files:

```text
data/spot/spot_2025_hourly_europe_stockholm.csv
data/spot/spot_2025_conversion_report.json
data/spot/README.md
```

Expected tests:

```text
tests/mac/weekly_home_optimizer_poc/test_hourly_spot_forecast.py
tests/mac/weekly_home_optimizer_poc/test_actual_spot_patch.py
tests/mac/weekly_home_optimizer_poc/test_spot_fixture_dst.py
tests/mac/weekly_home_optimizer_poc/test_spot_summary_fields.py
tests/mac/weekly_home_optimizer_poc/test_browser_spot_rendering.py
```

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md
requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md
requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md
requirements/packages/P0022-discrete-dp-heat-optimizer-for-weekly-home-poc.md
requirements/packages/P0023-cop-emulator-and-optimized-vs-flat-electric-cost.md
src/mac/labs/weekly_home_optimizer_poc/**
tests/mac/weekly_home_optimizer_poc/**
data/spot/spot_2025_conversion_report.json
data/spot/spot_2025_hourly_europe_stockholm.csv
docs/functions/mac/weekly-home-optimizer-poc.md
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
```

Optional docs may not exist. Do not fail solely because optional docs are absent.

## Files allowed to change

```text
src/mac/labs/weekly_home_optimizer_poc/**
tests/mac/weekly_home_optimizer_poc/**
data/spot/**
memory/planning/weekly-heat-ppm-rh-poc.md
memory/planning/weekly-home-poc-browser-ui.md
docs/functions/mac/weekly-home-optimizer-poc.md
docs/functions/00-index.md
requirements/package-runs/P0024/**
```

## Forbidden changes

- Do not change `marlov1974/shelly`.
- Do not change `dep/s/**` Shelly deploy artifacts.
- Do not change live FTX, VP or Home Assistant runtime.
- Do not add any command that writes to devices.
- Do not bind web server to `0.0.0.0` by default.
- Do not add `reference_year` to public input.
- Do not make tests require live internet.
- Do not add heavy/scientific/ML/optimizer dependencies.
- Do not use local wall time alone as a unique key for the actual price fixture.
- Do not silently fabricate actual spot prices if the fixture is missing.
- Do not present patched/forecast price index as measured total electricity bill.

## Pre-implementation consistency review

Before editing, Codex must verify this package against repository truth.

Codex must classify the package as:

- `PASS`: consistent; continue implementation.
- `WARN`: implementable but with stated assumptions or minor uncertainty.
- `STOP`: inconsistent, unsafe, underspecified or out of scope; do not edit.

Review output should be stored under:

```text
requirements/package-runs/P0024/review.md
```

Review checks:

```text
- package vs memory
- package vs P0018/P0020/P0021/P0022/P0023 implementation/evidence
- package vs existing spot-price code
- package vs data fixture availability
- package vs DST and timezone handling
- package vs G1/G2 boundary
- package vs testability/offline constraints
- package vs browser/API compatibility
- package vs no-live-control invariant
```

## Implementation design policy

For this code package, Codex must create package-scoped implementation design before coding:

```text
requirements/package-runs/P0024/design.md
```

The design must cover:

```text
- package interpretation
- hourly forecast expansion
- actual-price CSV loading
- timezone/DST/key handling
- patch algorithm
- output schema changes
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
requirements/package-runs/P0024/functions.md
```

The function design must list intended new, changed and removed functions, including purpose, inputs, outputs, side effects, reason and test coverage.

Expected function candidates:

```text
load_actual_spot_prices(path)
aggregate_or_validate_hourly_spot_fixture(rows)
build_hourly_forecast_index(week, hours=168)
patch_forecast_with_actual_prices(forecast_hours, actual_prices)
resolve_week_utc_hours(week, start_local_hour="mon 06:00")
```

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

Network price fetch during manual smoke:
no, fixture-only for actual spot in this package

Network fetch during automated tests:
no

Max implementation/debug attempts:
3

## Evidence and learning policy

Package-specific evidence location:

```text
requirements/package-runs/P0024/
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

### TC1: Forecast is hourly
Given a requested week
When the spot model runs
Then exactly 168 hourly forecast values are produced.

### TC2: Patch preserves forecast sum
Given deterministic forecast and actual arrays
When patching runs
Then patched actual values have the same sum as the original forecast values over the known period.

### TC3: Patch uses actual shape
Given actual prices [10,20,30,40] and forecast [1,1,2,2]
When patching runs
Then patched values are [0.6,1.2,1.8,2.4].

### TC4: Non-overlap leaves forecast unchanged
Given no actual prices overlapping the requested week
When patching runs
Then all hours use forecast and a clear metadata value indicates zero patched hours.

### TC5: Fixture loads unique UTC keys
Given the 2025 hourly fixture
When it is loaded
Then `utc_hour_start` values are unique and count is 8760.

### TC6: DST spring day is valid
Given the 2025 fixture
When local date 2025-03-30 is inspected
Then it has 23 local hours and no fabricated 02:00 local hour.

### TC7: DST fall day is valid
Given the 2025 fixture
When local date 2025-10-26 is inspected
Then it has 25 local hours and two distinct 02:00 hours with different offsets/fold values.

### TC8: Full POC output includes spot metadata
Given a weekly POC run
When JSON output is produced
Then summary includes spot model, resolution, patched/forecast hour counts and min/max/avg.

### TC9: Hourly output includes source
Given a weekly POC run
When hours are emitted
Then each hour includes `spot_source` and debug fields are nullable or populated correctly.

### TC10: Browser renders spot metadata
Given the local web UI renders a plan
When summary is displayed
Then spot model and patched-hour counts are visible.

### TC11: Offline tests
Given the test suite runs without internet
When weekly_home_optimizer_poc tests run
Then tests pass using fixtures/mocks.

## Verification commands

Codex should define exact commands in `requirements/package-runs/P0024/design.md`.

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
- summary shows spot_model = hourly_forecast_with_actual_patch_v1
- spot_resolution = hourly
- actual patched hour count is visible
- every output hour has spot_index and spot_source
- total output remains exactly 168 hours
- heat optimizer still runs discrete_dp
- COP/electric-cost summary still works if P0023 is present
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
- whether actual CSV fixture was found
- implementation design path
- function design path
- files changed
- tests run
- verification results
- local server command
- phone URL example
- spot patch summary
- debug attempts used
- package-run evidence paths created/updated
- function catalog updates
- memory/data docs updates
- uncertainty / skipped checks
- diff summary

## Completion notes

Filled after implementation.
