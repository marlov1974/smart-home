# Package P0056O: Fix DayAhead DST delivery-day generation

## Status

planned

## Package order

P0056O

## Label

```text
FIX
```

## Purpose

Fix the confirmed DayAhead daylight-saving-time bug found in P0056N.

P0056N confirmed that Europe/Stockholm spring-forward day `2026-03-29` has 23 valid local hours, but the P0056K/P0056M DayAhead delivery-day generation emitted 24 positions and produced one duplicate UTC target.

This package must change DayAhead delivery-day row generation so local delivery days with 23 or 25 hours are handled correctly and cannot create duplicate UTC targets or invalid local-hour rows.

## Background evidence

P0056N classified `2026-03-28` as a probable target/source anomaly and separately confirmed a DST bug for `2026-03-29`.

P0056N evidence summary:

```text
2026-03-29 Europe/Stockholm = spring_forward_23h
expected_valid_local_hour_count = 23
expected_valid_local_hours = 00,01,03,04,...,23
P0056K position count = 24
P0056K unique UTC count = 23
P0056K duplicate UTC count = 1
```

P0056N recommendation:

```text
fix_or_special_case_DayAhead_delivery_day_generation_for_23h_25h_local_days_before_future_realistic_DayAhead_comparisons
```

## Scope

Fix DayAhead delivery-day generation and alignment for Europe/Stockholm local days:

```text
standard 24-hour local days
spring-forward 23-hour local days
fall-back 25-hour local days
```

Primary test dates:

```text
2026-03-29 Europe/Stockholm spring-forward 23h
2025-10-26 Europe/Stockholm fall-back 25h
2026-10-25 Europe/Stockholm fall-back 25h
standard control days around each transition
```

## Required design decision

Before changing code, define the canonical DayAhead representation.

Preferred representation:

```text
Use true local delivery-day hours.
A spring-forward local day has 23 delivery rows.
A fall-back local day has 25 delivery rows.
Each row has a unique UTC timestamp.
Repeated local hour on fall-back must be disambiguated by UTC offset/fold or UTC timestamp.
```

If the market-emulator requires fixed 24 positions, define a separate adapter layer. Do not corrupt the canonical hourly target table or canonical DayAhead evaluation rows to force 24 rows.

## Required implementation

Find and update the code paths used by P0056K/P0056M realistic DayAhead forecast generation, especially any code that does:

```text
for local_hour in range(24)
```

or otherwise assumes every local delivery day has 24 positions.

Replace it with a timezone-safe local-day iterator that:

```text
1. Starts at local midnight for the delivery date.
2. Ends at next local midnight.
3. Converts the interval to UTC.
4. Iterates actual UTC hours between those boundaries.
5. Converts each UTC target hour back to local metadata.
6. Preserves repeated local hour on fall-back with different UTC timestamps/offsets.
7. Skips nonexistent local hour on spring-forward.
```

## Required row schema

Every generated DayAhead row must include enough fields to disambiguate DST:

```text
forecast_origin_utc
forecast_origin_local
delivery_date_local
target_timestamp_utc
target_timestamp_local
local_date
local_hour
utc_offset_minutes
is_dst_transition_day
is_spring_forward_day
is_fall_back_day
local_hour_occurrence_index
horizon_h
```

For normal days:

```text
local_hour_occurrence_index = 0
```

For fall-back repeated hour:

```text
first repeated local hour occurrence_index = 0
second repeated local hour occurrence_index = 1
```

## Required validation rules

For every generated delivery day:

```text
UTC target timestamps must be unique.
UTC target timestamps must be monotonic.
Row count must equal true number of UTC hours between local midnights.
Spring-forward day must not contain nonexistent local 02:00.
Fall-back day must contain repeated local hour exactly twice with different UTC timestamps/offsets.
No duplicate target_timestamp_utc rows are allowed.
No invalid local timestamps are allowed.
```

## Required regression tests

Add tests for at least:

```text
Europe/Stockholm 2026-03-29 => 23 rows, no local 02:00, unique UTC
Europe/Stockholm 2025-10-26 => 25 rows, local 02:00 occurs twice with different UTC offsets, unique UTC
Europe/Stockholm 2026-10-25 => 25 rows, local 02:00 occurs twice with different UTC offsets, unique UTC
standard day => 24 rows
```

Also add a test that reproduces the P0056N bug condition and proves it is fixed:

```text
old behavior: 24 positions on 2026-03-29 with duplicate UTC
new behavior: 23 positions on 2026-03-29 with no duplicate UTC
```

## Required rerun / verification

After implementation, rerun a compact verification around:

```text
2026-03-25..2026-03-31
```

for SE2/P0056K or P0056M reconstructed forecast-row generation.

This verification must report:

```text
rows before fix
rows after fix
duplicate UTC before/after
spring-forward local 02:00 before/after
forecast-row alignment rows checked
whether 2026-03-29 duplicate target is gone
whether 2026-03-28 anomaly classification is unchanged
```

Do not retrain the model as part of the fix unless a minimal forecast reconstruction is required only to verify row alignment. If reconstruction is run, label it verification-only.

## Required evidence files

Create:

```text
requirements/package-runs/P0056O/CHANGELOG.md
requirements/package-runs/P0056O/review.md
requirements/package-runs/P0056O/design.md
requirements/package-runs/P0056O/functions.md
requirements/package-runs/P0056O/labb-label.md
requirements/package-runs/P0056O/p0056n-baseline-review.md
requirements/package-runs/P0056O/canonical-dayahead-representation.md
requirements/package-runs/P0056O/dst-fix-design.md
requirements/package-runs/P0056O/regression-tests.md
requirements/package-runs/P0056O/spring-forward-verification.md
requirements/package-runs/P0056O/fall-back-verification.md
requirements/package-runs/P0056O/se2-march-row-alignment-after-fix.md
requirements/package-runs/P0056O/decision.md
requirements/package-runs/P0056O/what-we-learned.md
requirements/package-runs/P0056O/next-package-recommendation.md
```

Optional compact evidence:

```text
dst-row-generation-before-after.csv
se2-march-row-alignment-after-fix.csv
metrics-summary.json
```

Do not commit large prediction dumps or raw source data.

## Files to inspect

```text
requirements/package-runs/P0056N/classification.md
requirements/package-runs/P0056N/dst-local-day-audit.md
requirements/package-runs/P0056N/forecast-row-alignment-audit.md
requirements/package-runs/P0056N/decision.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056M/hour-level-summary.md
src/mac/** DayAhead forecast generation, timezone and delivery-day mapping code
tests/mac/** timezone/DST tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056O-fix-dayahead-dst-delivery-day-generation.md
requirements/package-runs/P0056O/**
src/mac/** narrowly scoped DayAhead delivery-day/timezone generation fix
tests/mac/** narrowly scoped DST/local-day regression tests
docs/functions/** if function catalog needs to record changed helper behavior
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No model retraining for optimization.
No spot price features.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No result rewriting to hide bad rows.
No changing P0056A source ingestion as part of this package unless only adding audit metadata needed by the fix verification.
No large raw source/prediction dumps committed.
```

## Pass / WARN / STOP

PASS requires:

```text
canonical DayAhead representation documented
spring-forward 23h generation fixed
fall-back 25h generation supported/tested
UTC targets unique and monotonic
2026-03-29 duplicate UTC target removed
regression tests added and passing
SE2 March row-alignment verification completed
2026-03-28 anomaly classification remains separate from DST fix
```

WARN is acceptable if:

```text
fall-back support is implemented and unit-tested but not rerun through full forecast verification
verification is limited to row generation rather than full model reconstruction
```

STOP if:

```text
DayAhead row-generation code path cannot be found
DST fix cannot be verified
fix creates duplicate/missing UTC targets on normal days
fix breaks standard 24h days
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
files changed
tests/commands run
canonical representation chosen
spring-forward verification result
fall-back verification result
2026-03-29 duplicate target before/after
SE2 March row-alignment result
whether 2026-03-28 remains probable target/source anomaly
confirmation no runtime/device/model/production changes
recommended next package
```

## Completion notes

To be filled after implementation.
