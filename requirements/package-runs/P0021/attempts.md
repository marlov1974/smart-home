# Package P0021 Attempts

## Attempt 1

Result: passed.

## Implementation summary

- Added `weather.py` with Open-Meteo archive provider, week-to-year strategy, parser and explicit fallback.
- Added `people` input across CLI, browser form and JSON API.
- Added `occupancy_gain_for_people()` using `70 * people / 3`.
- Added weather source metadata to `InputProfile`, `WeeklyPlan`, CLI metadata, HTML summary and JSON summary.
- Updated planning memory, browser UI memory and function catalog.
- Added offline tests for weather parsing, fallback metadata, people load and browser/API people handling.

## Weather strategy

Real weather provider:

```text
Open-Meteo archive
```

Location:

```text
latitude 59.6214405
longitude 17.7336153
```

No-reference-year strategy:

```text
latest_completed_iso_week_or_previous_year
```

## Verification

### `python3 -m unittest discover tests/mac/weekly_home_optimizer_poc`

```text
Ran 32 tests in 1.306s

OK
```

### `python3 -m unittest discover tests/mac`

```text
Ran 106 tests in 1.752s

OK
```

### `python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22 --people 6 --fixture-weather`

Passed. Produced a 168-hour table.

Header excerpt:

```text
people=6 occupancy_gain_ppm_h=140.0 weather_source=synthetic_fallback weather_provider=internal synthetic profile weather_fallback_reason=real weather disabled
```

### `python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke`

```text
weekly_home_optimizer_poc server smoke ok
```

### Manual-mode weather check without network escalation

Fallback was explicit:

```text
weather_source synthetic_fallback
weather_provider internal synthetic profile
weather_profile_strategy latest_completed_iso_week_or_previous_year
weather_profile_year None
weather_fallback_reason open-meteo fetch failed: <urlopen error [Errno 8] nodename nor servname provided, or not known>
people 3.0
occupancy_gain_ppm_h 70.0
hours 168
```

### Manual-mode weather check with read-only network escalation

Open-Meteo succeeded:

```text
weather_source real_open_meteo
weather_provider open-meteo archive
weather_profile_strategy latest_completed_iso_week_or_previous_year
weather_profile_year 2026
weather_fallback_reason None
people 3.0
occupancy_gain_ppm_h 70.0
hours 168
```

### People/CO2 pressure comparison using fixture weather

```text
people 3 gain 70.0 weather synthetic_fallback max_ppm 651.49 avg_supply 28.5
people 6 gain 140.0 weather synthetic_fallback max_ppm 798.03 avg_supply 35.9
```

### `git diff --check`

Passed with no output.

## Live actions

None.

## Manual phone test

Not run as an interactive phone test. The local browser server is read-only and can be started manually.

## Knowhow promotion

Skipped. The reusable contracts are captured in planning memory and function docs. No live-device, deploy, rollback or repeated workflow lesson was discovered.
