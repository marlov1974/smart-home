# P0056O Function Design

## New Functions

### `p0056k.delivery_day_target_rows(day)`

- Purpose: generate canonical DayAhead target rows for one Europe/Stockholm local delivery day.
- Inputs: `day: date`.
- Outputs: list of `DeliveryDayTarget` objects with UTC timestamp, local timestamp, local hour, UTC offset, DST flags and occurrence index.
- Side effects: none.
- Reason: replace fixed 24-position generation with true local-day generation.
- Test coverage: P0056O spring-forward, fall-back and standard-day tests.

### `p0056o.legacy_fixed_24_target_rows(day)`

- Purpose: reproduce the old fixed-24 P0056K behavior for before/after evidence.
- Inputs: `day: date`.
- Outputs: compact dict rows.
- Side effects: none.
- Reason: prove the P0056N bug condition is fixed without depending on current P0056K to stay buggy.
- Test coverage: indirectly through P0056O regression test and evidence generator.

### `p0056n.legacy_fixed_24_delivery_day_target_utc_hours(local_day)`

- Purpose: preserve P0056N's historical pre-P0056O fixed-24 mapping.
- Inputs: `local_day: date`.
- Outputs: list of 24 UTC timestamp strings generated with the old direct-local-time method.
- Side effects: none.
- Reason: P0056N baseline evidence should remain a pre-fix audit after current P0056K behavior changes.
- Test coverage: existing P0056N DST audit tests.

### `p0056k.validate_delivery_day_target_rows(day, rows)`

- Purpose: enforce canonical DayAhead row validity rules for one local delivery day.
- Inputs: `day: date`, `rows: list[DeliveryDayTarget]`.
- Outputs: none.
- Side effects: raises `ValueError` on invalid row shape.
- Reason: make duplicate UTC, non-monotonic UTC, wrong row count, spring local 02:00 and fall repeated-hour ambiguity fail close to row generation.
- Test coverage: P0056O DST tests exercise the valid spring-forward, fall-back and standard cases.

### `p0056o.run_p0056o_dst_fix_verification(...)`

- Purpose: generate compact package evidence for P0056O.
- Inputs: optional feature DB and evidence directory paths.
- Outputs: `P0056OResult` with status, row counts and evidence paths.
- Side effects: reads local feature DB; writes P0056O evidence files.
- Reason: required package evidence and compact SE2 March row-alignment verification.
- Test coverage: py_compile plus package verification run.

## Changed Functions

### `p0056k.delivery_day_target_utc_hours(day)`

- Previous behavior: generated 24 UTC timestamps from fixed local positions.
- New behavior: returns UTC timestamps from `delivery_day_target_rows(day)`.
- Side effects: none.
- Reason: existing callers can keep using the function name while receiving canonical DST-safe timestamps.
- Test coverage: P0056K existing test and P0056O DST tests.

### `p0056k.build_dayahead_rows(area, target_rows, weather_rows, origins)`

- Previous behavior: generated 24 rows per origin and lacked DST disambiguation fields.
- New behavior: generates canonical 23/24/25 rows and includes the required DST metadata schema.
- Side effects: none.
- Reason: ensure evaluation rows cannot contain duplicate UTC target timestamps on DST days.
- Test coverage: P0056O evidence generator and existing P0056K protocol tests.

### `p0056k.run_p0056k_realistic_dayahead_restart(...)`

- Previous behavior: skipped any origin whose forecast row count was not 24.
- New behavior: compares forecast rows to the canonical delivery-day target count.
- Side effects: unchanged existing evidence writes when a long P0056K run is explicitly started.
- Reason: canonical DST days must not be falsely marked incomplete.
- Test coverage: py_compile; behavior covered by row-generation verification.

### `p0056m.reconstruct_se2_m6_predictions(...)`

- Previous behavior: skipped any reconstructed DayAhead origin whose forecast rows were not exactly 24.
- New behavior: compares forecast rows to the canonical P0056K delivery-day target count.
- Side effects: unchanged existing P0056M evidence writes when the package is explicitly rerun.
- Reason: P0056M is a P0056K realistic DayAhead reconstruction path and must not reject canonical 23/25-row DST days.
- Test coverage: py_compile; P0056O SE2 March row-alignment verification covers the shared row generator.

### `p0056l.run_p0056l_neural_dayahead_smoke(...)`

- Previous behavior: failed any selected DayAhead origin whose forecast rows were not exactly 24.
- New behavior: compares forecast rows to the canonical P0056K delivery-day target count.
- Side effects: unchanged existing P0056L evidence writes when the package is explicitly rerun.
- Reason: P0056L consumes the same DayAhead row contract and should not retain the fixed-24 assumption.
- Test coverage: py_compile.

### `p0056n.p0056k_delivery_day_mapping(local_day)`

- Previous behavior: called current P0056K mapping.
- New behavior: calls an explicit legacy fixed-24 mapping to preserve P0056N historical baseline evidence.
- Side effects: none.
- Reason: P0056N remains a pre-fix audit package after P0056K is corrected.
- Test coverage: existing P0056N DST audit tests.

## Removed Functions

None.
