# Weekly Home Optimizer POC

Last changed: P0021

## Module

```text
src.mac.labs.weekly_home_optimizer_poc
```

## Purpose

Mac-only lab POC for a 168-hour weekly heat, PPM and RH-policy plan.

The module is inspectable and deterministic. It does not perform live control.

## CLI

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --people 6 --format json
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22 --people 3 --fixture-weather
```

## Browser Server

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

The first command is local-only. The second command is for explicit trusted-LAN phone testing.

## Important Functions

`build_input_profile(week_number, prefer_real_weather)` returns 168-hour outdoor temperature and outdoor RH profiles with explicit weather source metadata.

`latest_completed_iso_year_for_week(week_number, today)` maps week-only input to the latest completed internal weather profile year.

`parse_open_meteo_hourly(payload, year, week_number)` parses Open-Meteo archive hourly weather into exactly 168 operational-week values.

`fetch_open_meteo_archive_profile(week_number, timeout)` fetches read-only Open-Meteo archive weather for manual runs.

`synthetic_fallback_profile(week_number, reason)` returns deterministic fallback weather with explicit fallback metadata.

`expand_period_indexes_to_hours(period_indexes)` converts P0017 21x8h period indexes to 168 hourly spot indexes.

`spot_indexes_for_week(week_number)` reuses the P0017 spot forecast model and expands it to hourly values.

`plan_heat(outdoor_temp_c, spot_index, current_house_temp)` computes heat need, heat production, heat SOC and heat-derived ventilation cost weights.

`rh_weight_for_hour(outdoor_temp_c, outdoor_rh_pct)` converts weather into RH policy cost or reward.

`ppm_after_hour(ppm, supply_pct, occupancy_gain_ppm_h)` computes one-hour PPM evolution using the POC dilution model.

`ppm_cost(ppm)` computes air-quality discomfort cost, including continuation above 1000 ppm.

`validate_people(people)` validates public people input in the POC range `0..20`.

`occupancy_gain_for_people(people)` derives hourly PPM occupancy gain as `70 * people / 3`.

`optimize_ppm_plan(heat_cost_weight, rh_weight, current_ppm, occupancy_gain_ppm_h)` chooses 168 normal-operation supply modes using deterministic dynamic programming.

`build_weekly_plan(week_number, current_ppm, current_house_temp, people, prefer_real_weather)` orchestrates the full POC.

`rows_for_plan(plan)` flattens the plan into required output rows.

`format_table(plan)`, `format_json(plan)` and `format_csv(plan)` render inspectable outputs.

`parse_plan_query(query)` validates HTTP query parameters for `week`, `ppm`, `houseTemp` and optional `people`.

`plan_payload(request)` builds the JSON-compatible browser/API payload by calling the P0018 planner and flattening rows.

`build_handler()` creates the standard-library HTTP request handler for `/`, `/health` and `/api/weekly-home-poc`.

`run_server(host, port)` starts the local read-only HTTP server.

`run_once_smoke()` performs a non-blocking server smoke check for package verification.

## Contracts

Public required inputs are:

```text
week_number
current_ppm
current_house_temp
people
```

There is no public `reference_year` input and no current indoor RH input in v1.

Normal supply modes are limited to:

```text
25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55
```

Browser API endpoint:

```text
GET /api/weekly-home-poc?week=2&ppm=500&houseTemp=22&people=6
```

The JSON response contains:

```text
input
summary
hours
```

`hours` has 168 rows for a valid plan.

`summary` includes people, occupancy gain and weather source metadata.
