# Weekly Home Optimizer POC

Last changed: P0018

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
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json
```

## Important Functions

`build_input_profile(week_number)` returns deterministic 168-hour outdoor temperature and outdoor RH profiles.

`expand_period_indexes_to_hours(period_indexes)` converts P0017 21x8h period indexes to 168 hourly spot indexes.

`spot_indexes_for_week(week_number)` reuses the P0017 spot forecast model and expands it to hourly values.

`plan_heat(outdoor_temp_c, spot_index, current_house_temp)` computes heat need, heat production, heat SOC and heat-derived ventilation cost weights.

`rh_weight_for_hour(outdoor_temp_c, outdoor_rh_pct)` converts weather into RH policy cost or reward.

`ppm_after_hour(ppm, supply_pct, occupancy_gain_ppm_h)` computes one-hour PPM evolution using the POC dilution model.

`ppm_cost(ppm)` computes air-quality discomfort cost, including continuation above 1000 ppm.

`optimize_ppm_plan(heat_cost_weight, rh_weight, current_ppm, occupancy_gain_ppm_h)` chooses 168 normal-operation supply modes using deterministic dynamic programming.

`build_weekly_plan(week_number, current_ppm, current_house_temp, occupancy_gain_ppm_h)` orchestrates the full POC.

`rows_for_plan(plan)` flattens the plan into required output rows.

`format_table(plan)`, `format_json(plan)` and `format_csv(plan)` render inspectable outputs.

## Contracts

Public required inputs are:

```text
week_number
current_ppm
current_house_temp
```

There is no public `reference_year` input and no current indoor RH input in v1.

Normal supply modes are limited to:

```text
25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55
```
