# Weekly Heat PPM RH POC

Last changed: P0018

This file records the durable contract for the Mac-only weekly heat, PPM and RH-policy planning POC.

## Purpose

The POC builds an inspectable 168-hour operational-week plan for:

- heat need and heat production
- spot-price cost weighting
- RH ventilation policy cost
- normal-operation supply percentage
- PPM evolution

It is not a live controller. It must not control Shelly, FTX, heat pumps or Home Assistant runtime behavior.

## Public input contract

The public operator inputs are:

```text
week_number
current_ppm
current_house_temp
```

The POC does not accept a reference year or current indoor RH in v1.

The CLI may expose diagnostic/output options such as:

```text
--occupancy-gain-ppm-h
--format
```

## Input model

Weather input is deterministic synthetic data keyed by ISO week number. This keeps the POC and tests independent from network access.

Spot-price input reuses the P0017 Mac spot period-index model:

```text
21 8h period indexes -> 168 hourly indexes
```

Each P0017 8h operational period is repeated for eight hourly values.

## Heat model

Hourly heat need uses:

```text
heat_need_day_kWh = max(0, 12.5 * (set_temp_c - outdoor_temp_c) - 42.0)
heat_need_kWh = heat_need_day_kWh / 24
```

In POC v1:

```text
set_temp_c = current_house_temp
```

Heat production is allocated toward lower spot-index hours, clamped by POC planning limits, and used to derive `heat_cost_weight` for ventilation planning.

These are POC planning values, not final live VP constraints.

## RH model

RH is represented as a ventilation policy/cost signal, not an RH setpoint and not an indoor RH forecast.

The POC derives `rh_weight` from outdoor temperature and outdoor RH:

- cold/dry-effect outdoor conditions make ventilation expensive for RH
- neutral conditions have near-zero RH policy cost
- mild/humid helpful conditions can reward ventilation

`rh_delta` is an inspectable policy result indicator, not a physical RH delta.

## PPM model

The POC uses a simplified dilution relation:

```text
removal_ppm_h = flow_lps * 3.6 / 780 * max(0, ppm - 420)
ppm_after = ppm + occupancy_gain_ppm_h - removal_ppm_h
```

Default occupancy gain is:

```text
70 ppm/h
```

Normal supply modes are restricted to:

```text
25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55
```

Supply above 55% remains outside this POC and belongs to later local override behavior for acute PPM, cooling/night-cooling or safety/fault cases.

## Optimization

The POC uses deterministic dynamic programming over discretized PPM state and allowed supply modes.

The objective combines:

```text
ppm_cost
+ heat_cost_weight * vent_cost
+ rh_weight * vent_cost
```

The optimizer is intended to demonstrate tradeoffs across time, such as allowing PPM to rise when ventilation is expensive/drying and ventilating more when heat/RH conditions are favorable.
