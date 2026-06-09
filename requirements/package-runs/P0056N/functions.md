# P0056N Function Design

## Package

`P0056N`

## Scope

Mac-side LABB diagnostics for SE2 target anomaly, DST and DayAhead row-alignment audit.

## New functions

### `run_p0056n_dst_target_anomaly_audit()`

Purpose: Orchestrate the full P0056N audit and write evidence.

Inputs: Optional feature DB path and evidence directory.

Outputs: Result object with status, row counts and evidence paths.

Side effects: Writes package-run evidence only.

Reason: Package entry point.

Tests: Module execution plus pure-helper unit tests.

### `load_native_rows()`

Purpose: Load compact SE2 P0056A native interval rows for the audit windows.

Inputs: SQLite connection, local audit dates.

Outputs: Native interval dictionaries.

Side effects: None.

Reason: Required raw/native source audit.

Tests: Covered by module execution.

### `load_hourly_rows()`

Purpose: Load compact SE2 P0056A hourly rows for the audit windows.

Inputs: SQLite connection, local audit dates.

Outputs: Hourly row dictionaries with UTC/local metadata.

Side effects: None.

Reason: Required hourly target audit.

Tests: Covered by module execution.

### `expected_local_hours_for_day()`

Purpose: Build the valid UTC/local timestamp mapping for a Europe/Stockholm local day.

Inputs: Local date.

Outputs: List of valid UTC/local hour dictionaries.

Side effects: None.

Reason: DST audit must know that `2026-03-29` has 23 valid local hours and no `02:00`.

Tests: Unit-tested.

### `p0056k_delivery_day_mapping()`

Purpose: Describe what P0056K currently emits for a delivery day.

Inputs: Local date.

Outputs: P0056K target UTC/local mapping with duplicate/missing flags.

Side effects: None.

Reason: Required forecast-row alignment and DayAhead DST audit.

Tests: Unit-tested through duplicate UTC detection.

### `daily_row_audit()`

Purpose: Aggregate native/hourly row counts, duplicate/missing counts and load statistics per local day.

Inputs: Native rows, hourly rows and expected local-day mappings.

Outputs: Daily audit rows.

Side effects: None.

Reason: Required raw/native and hourly row-count evidence.

Tests: Covered by module execution.

### `target_anomaly_classification()`

Purpose: Classify `2026-03-28` using native, hourly, neighbor-day and DayAhead evidence.

Inputs: Daily audit rows, top spikes and alignment audit.

Outputs: Classification dictionary.

Side effects: None.

Reason: Required anomaly decision.

Tests: Unit-tested with synthetic summary rows.

### `forecast_row_alignment_audit()`

Purpose: Join P0056M forecast rows around the audit window to UTC/local/DST flags.

Inputs: P0056M hour rows and P0056K delivery-day mapping.

Outputs: Forecast alignment row dictionaries.

Side effects: None.

Reason: Required forecast-origin/target-hour alignment evidence.

Tests: Covered by module execution.

## Changed functions

None planned.

## Removed functions

None planned.

## Important unchanged functions

### `p0056k.delivery_day_target_utc_hours()`

Reason for no change: P0056N audits its behavior but does not fix model or row-generation logic.

### `p0056a.aggregate_native_to_hourly()`

Reason for no change: P0056N audits persisted aggregation output but does not rewrite source ingestion.

## Design deviations during implementation

None yet.
