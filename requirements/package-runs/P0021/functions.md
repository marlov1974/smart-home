# Package P0021 Function Design

## Package

`P0021`

## Scope

Weekly home optimizer POC weather and occupancy input contract.

## New functions

### `occupancy_gain_for_people(people)`

Purpose: derive hourly PPM occupancy gain from people count.

Inputs: people numeric value.

Outputs: occupancy gain ppm/h.

Side effects: none.

Reason: make CO2 load scenario explicit and testable.

Tests: people occupancy tests.

### `validate_people(people)`

Purpose: validate public people input range.

Inputs: numeric/string people value.

Outputs: float people count.

Side effects: none.

Reason: shared CLI/API input validation.

Tests: CLI/API/browser invalid input tests.

### `latest_completed_iso_year_for_week(week_number, today=None)`

Purpose: map week-only public input to an internal real-weather profile year.

Inputs: ISO week and optional date for tests.

Outputs: integer year.

Side effects: none.

Reason: avoid adding public reference year.

Tests: weather provider tests.

### `operational_week_dates(year, week_number)`

Purpose: compute Monday 06:00 to next Monday 06:00 operational window.

Inputs: year and ISO week.

Outputs: start/end dates and hour offset metadata.

Side effects: none.

Reason: Open-Meteo archive request shaping.

Tests: weather provider shape tests.

### `parse_open_meteo_hourly(payload, year, week_number)`

Purpose: parse Open-Meteo hourly temperature/RH arrays into exactly 168 operational-week values.

Inputs: decoded API payload, year and week.

Outputs: `InputProfile`.

Side effects: none.

Reason: isolate provider parsing and make tests offline.

Tests: fixture provider tests.

### `fetch_open_meteo_archive_profile(week_number, timeout=...)`

Purpose: fetch real hourly weather from Open-Meteo archive.

Inputs: week number and timeout.

Outputs: `InputProfile`.

Side effects: read-only external HTTP request.

Reason: real weather for manual POC runs.

Tests: parser tested with fixture; fetch not used in offline tests.

### `synthetic_fallback_profile(week_number, reason=None)`

Purpose: build explicit fallback weather profile.

Inputs: week number and optional reason.

Outputs: `InputProfile`.

Side effects: none.

Reason: offline deterministic fallback with visible metadata.

Tests: fallback metadata tests.

### `weather_profile_for_week(week_number, prefer_real=True)`

Purpose: return real weather when available or explicit fallback when not.

Inputs: week number and preference flag.

Outputs: `InputProfile`.

Side effects: possible read-only external HTTP request when `prefer_real`.

Reason: single planner entrypoint for weather selection.

Tests: mocked/fallback provider tests.

## Changed functions

### `build_input_profile(week_number)`

Current purpose: build deterministic synthetic weather.

Change: delegate to weather provider and return explicit weather metadata.

Inputs changed: optional provider/prefer-real settings may be added.

Outputs changed: `InputProfile` now includes weather metadata.

Side effects changed: default path may perform read-only external weather fetch.

Reason: P0021 real weather behavior.

Tests: weather source metadata tests.

### `build_weekly_plan(...)`

Current purpose: orchestrate weekly planning.

Change: accept `people`, derive occupancy gain and carry weather metadata.

Inputs changed: add `people=3`.

Outputs changed: `WeeklyPlan` includes people and weather metadata.

Side effects changed: possible read-only external weather fetch through input profile.

Reason: public people/weather contract.

Tests: people and metadata tests.

### `parse_args(argv)`

Current purpose: parse CLI inputs.

Change: add `--people`, default 3.

Inputs changed: optional people argument.

Outputs changed: argparse namespace includes people.

Side effects changed: none.

Reason: CLI contract update.

Tests: CLI contract tests.

### `parse_plan_query(query)`

Current purpose: parse browser/API week, ppm and houseTemp.

Change: parse optional `people`, default 3.

Inputs changed: optional `people`.

Outputs changed: `PlanRequest` includes people.

Side effects changed: none.

Reason: browser/API contract update.

Tests: browser people tests.

### `plan_payload(request)`

Current purpose: build API/HTML payload.

Change: include people, occupancy gain and weather metadata in input/summary.

Inputs changed: `PlanRequest.people`.

Outputs changed: payload summary/input fields.

Side effects changed: possible read-only external weather fetch.

Reason: output visibility.

Tests: JSON endpoint tests.

### `render_form(values=None, error=None)`

Current purpose: render browser input form.

Change: add people input.

Tests: browser form tests.

### `render_result(payload)`

Current purpose: render summary/table.

Change: show people, occupancy gain and weather source metrics; keep people in JSON link.

Tests: browser result tests.

## Removed functions

None.

## Important unchanged functions

### `optimize_ppm_plan()`

Reason for no change: P0021 changes occupancy input, not normal PPM optimizer semantics.

### `forecast_period_indexes()`

Reason for no change: P0021 does not change P0017 spot contract.

## Design deviations during implementation

None yet.
