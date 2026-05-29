# P0024 function design

## New functions

### `spot.load_actual_spot_prices(path)`

- Purpose: Load the 2025 hourly spot fixture into a UTC-keyed mapping.
- Inputs: CSV path.
- Outputs: mapping from `utc_hour_start` to `ActualSpotPrice`.
- Side effects: reads a local fixture file only.
- Reason: package requires actual-price patching from the committed hourly fixture.
- Test coverage: fixture shape and DST uniqueness tests.

### `spot.resolve_week_utc_hours(week_number, iso_year=2025)`

- Purpose: Convert an operational week to exactly 168 chronological UTC hour keys.
- Inputs: week number and fixture ISO year.
- Outputs: tuple of UTC hour strings.
- Side effects: none.
- Reason: patching must use `utc_hour_start`, not ambiguous local wall-hour strings.
- Test coverage: hourly forecast and DST fixture tests.

### `spot.patch_forecast_with_actual_prices(forecast_index, utc_hours, actual_prices, actual_fixture_path)`

- Purpose: Apply actual-price shape to overlapping forecast hours while preserving forecast overlap sum.
- Inputs: 168 forecast values, 168 UTC hour keys, actual price mapping, fixture path label.
- Outputs: `SpotPlan`.
- Side effects: none.
- Reason: core P0024 algorithm.
- Test coverage: deterministic patch example and summary field tests.

### `spot.build_spot_plan(week_number, actual_fixture_path=DEFAULT_ACTUAL_SPOT_PATH)`

- Purpose: Build the complete 168-hour spot plan for the weekly home POC.
- Inputs: week number and optional fixture path.
- Outputs: `SpotPlan`.
- Side effects: reads the local actual-price fixture.
- Reason: planner integration point.
- Test coverage: hourly forecast, summary fields and API/browser tests.

### `spot.spot_indexes_for_week(week_number)`

- Purpose: Compatibility wrapper returning only final spot indexes.
- Inputs: week number.
- Outputs: tuple of 168 floats.
- Side effects: reads the local actual-price fixture.
- Reason: preserve existing public helper behavior while upgrading internals.
- Test coverage: existing spot expansion and output shape tests.

## Changed functions

### `planner.build_weekly_plan(...)`

- Change: builds `SpotPlan`, passes final spot index to heat planning, and stores `spot` in `WeeklyPlan`.
- Reason: optimizer must use patched hourly spot values.
- Test coverage: existing planner/output tests plus P0024 spot summary tests.

### `tables.rows_for_plan(plan)`

- Change: adds spot provenance and patch debug fields per hour.
- Reason: package requires hourly fields.
- Test coverage: output/browser tests.

### `tables._metadata(plan)`

- Change: adds spot summary metadata fields.
- Reason: package requires public summary fields.
- Test coverage: CLI/API summary tests.

### `server.plan_payload(request, prefer_real_weather=True)`

- Change: adds spot summary metadata to browser/API payload.
- Reason: browser and phone API consumers need spot patch status.
- Test coverage: server/browser tests.

### `html.render_result(payload)`

- Change: renders spot summary metrics and includes `spot_source` in the table.
- Reason: browser UI must show spot metadata and provenance.
- Test coverage: browser rendering test.

## Removed functions

None planned.

## Function catalog updates

Update `docs/functions/mac/weekly-home-optimizer-poc.md` and `docs/functions/00-index.md` to include the new spot model functions.
