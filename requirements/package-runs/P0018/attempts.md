# Package P0018 Attempts

## Attempt 1

Result: passed after one package-scoped policy adjustment.

## Implementation summary

- Added Mac lab module `src/mac/labs/weekly_home_optimizer_poc/`.
- Added deterministic synthetic weekly input profiles.
- Reused P0017 `forecast_period_indexes()` and expanded 21x8h indexes to 168 hourly values.
- Added heat planner, RH policy heuristic, PPM dynamic model and dynamic-programming optimizer.
- Added table, JSON and CSV output.
- Added unit tests under `tests/mac/weekly_home_optimizer_poc/`.
- Added durable planning memory and function catalog documentation.

## Debug adjustment

Initial P0018 tests failed because favorable RH conditions rewarded ventilation strongly enough that the optimizer selected 55% when PPM was already near the desired range.

Fix:

- Added a POC-specific high-supply penalty above 49% when `rh_weight < 0`.
- Updated `design.md` with the deviation and reason.

This preserves favorable-condition ventilation while matching the package expectation that 46% or 49% should be preferred when sufficient.

## Verification

### `python3 -m unittest discover tests/mac/weekly_home_optimizer_poc`

```text
Ran 12 tests in 0.483s

OK
```

### `python3 -m unittest discover tests/mac`

```text
Ran 86 tests in 0.942s

OK
```

### `python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22`

Passed. Produced a 168-hour table with required columns.

Sample summary:

```text
sample_rows 168
first_ppm 547.85
last_ppm 651.49
sample_supply_minmax 25 34
sample_heat_need_total 2147.7
heat_total 2147.7
```

### `python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json`

Passed. Produced JSON metadata and 168 hourly rows.

### `git diff --check`

Passed with no output.

## Policy-case comparison

Using direct optimizer fixtures:

```text
dry avg_ppm 645.6 avg_supply 28.0 minmax_supply 25 31
neutral avg_ppm 645.5 avg_supply 28.0 minmax_supply 25 31
favorable avg_ppm 549.4 avg_supply 49.0 minmax_supply 49 55
```

The favorable case clearly ventilates more and moves PPM toward 500. Dry and neutral high-cost cases are close in this POC because both settle on low ventilation under high heat cost; unit tests still confirm the expected ordering.

## Live actions

None.

## Knowhow promotion

Skipped. This package did not include live debugging, runtime anomalies, Shelly API discoveries, deploy/rollback lessons or repeated workflow problems. The reusable POC contract is captured in `memory/planning/weekly-heat-ppm-rh-poc.md`.
