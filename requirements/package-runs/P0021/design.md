# Package P0021 Implementation Design

## Package

`P0021`

## Package interpretation

Upgrade the weekly home POC so manual runs prefer real weather, all outputs expose weather source metadata, and `people` becomes a public scenario input that derives occupancy CO2 pressure.

## Chosen real weather provider and no-reference-year strategy

Provider:

```text
Open-Meteo archive API
```

Location:

```text
latitude 59.6214405
longitude 17.7336153
```

These coordinates are already used by the G2 Shelly weather script.

No-reference-year strategy:

```text
Use the latest completed ISO week occurrence.
If the requested ISO week in the current year has fully completed, use current year.
Otherwise use previous year.
```

The public input remains week number only. The chosen profile year/strategy is surfaced in metadata.

## Offline fixture/fallback strategy

Add `weather.py` with a provider interface:

- `fetch_open_meteo_archive_profile(...)`
- `synthetic_fallback_profile(...)`
- `weather_profile_for_week(...)`

Default manual mode:

1. Try Open-Meteo archive.
2. If fetch/parse/shape validation fails, use synthetic fallback.
3. Always set explicit metadata:

```text
weather_source
weather_provider
weather_profile_strategy
weather_profile_year
weather_fallback_reason
```

Automated tests use fixture/synthetic paths and mocks; no live internet is required.

## Weather source metadata

Extend `InputProfile` and `WeeklyPlan` to include:

```text
weather_source
weather_provider
weather_profile_strategy
weather_profile_year
weather_fallback_reason
```

Expose these in:

- CLI JSON metadata and table header
- browser/API summary
- HTML summary

## People input handling in CLI/API/browser UI

Add `people`, default `3`, valid range `0..20`.

CLI:

```bash
--people 6
```

Browser/API:

```text
people=6
```

Existing calls without people continue to work and default to 3.

## Occupancy gain formula

Default formula:

```text
base_people = 3
base_occupancy_gain_ppm_h = 70
occupancy_gain_ppm_h = base_occupancy_gain_ppm_h * people / base_people
```

This uses existing P0018 PPM optimizer input and does not change supply bounds.

## Tests and manual verification

Add tests for:

- weather provider shape with fixture Open-Meteo payload
- fallback metadata when provider fails
- default and explicit people in CLI/API/browser parser
- people=6 doubles occupancy gain relative to people=3
- people=6 changes max PPM and/or average supply relative to people=3
- browser form includes people
- JSON endpoint includes people/weather metadata

Verification commands:

```bash
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22 --people 6
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
git diff --check
```

## Files/modules intended to change

- `src/mac/labs/weekly_home_optimizer_poc/weather.py`
- `src/mac/labs/weekly_home_optimizer_poc/input_profiles.py`
- `src/mac/labs/weekly_home_optimizer_poc/schema.py`
- `src/mac/labs/weekly_home_optimizer_poc/planner.py`
- `src/mac/labs/weekly_home_optimizer_poc/tables.py`
- `src/mac/labs/weekly_home_optimizer_poc/cli.py`
- `src/mac/labs/weekly_home_optimizer_poc/server.py`
- `src/mac/labs/weekly_home_optimizer_poc/html.py`
- `src/mac/labs/weekly_home_optimizer_poc/README.md`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0021/**`

## Files/modules intentionally not changed

- P0017 spot forecast service and compact API.
- Shelly runtime code.
- Home Assistant code.
- Deploy artifacts.

## Risks and uncertainties

- Open-Meteo archive availability can vary; fallback must be explicit.
- A week-number-only real-weather request is inherently historical/strategy-based, not a true forecast for an arbitrary future week.
- Manual network weather fetch may be unavailable in sandboxed Codex execution; verification can still prove fallback/source metadata.

## Design deviations during implementation

None yet.
