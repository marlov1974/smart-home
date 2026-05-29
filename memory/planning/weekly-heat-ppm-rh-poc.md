# Weekly Heat PPM RH POC

Last changed: P0024

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
people
```

The POC does not accept a reference year or current indoor RH in v1.

The CLI may expose diagnostic/output options such as:

```text
--format
--fixture-weather
```

## Input model

Manual weather input prefers Open-Meteo archive weather for the requested week. Because public input is week-number only, the internal strategy is:

```text
Use the latest completed ISO week occurrence.
If the requested week in the current year has fully completed, use current year.
Otherwise use previous year.
```

Weather source metadata is part of output:

```text
weather_source
weather_provider
weather_profile_strategy
weather_profile_year
weather_fallback_reason
```

Automated tests and offline development use deterministic fallback weather. Fallback must be explicit; synthetic weather must not be silently presented as real weather.

Spot-price input uses the P0024 hourly spot plan:

```text
spot_model = hourly_forecast_with_actual_patch_v1
spot_resolution = hourly
spot_patch_strategy = actual_shape_forecast_sum
```

The internal forecast baseline may reuse the P0017 21x8h period-index model expanded to 168 hours. Public output and optimizer input are always hourly.

When actual 2025 spot fixture prices overlap the requested week, the POC patches actual price shape into the forecast:

```text
actual_proto_index = actual_price / mean(actual_price over overlap)
patched_actual_index = actual_proto_index * forecast_overlap_sum / actual_proto_sum
```

The patch preserves the forecast sum over known actual hours. The public POC input remains week-only, so actual-price patching maps requested weeks to ISO year 2025 and uses `utc_hour_start` as the canonical fixture key.

Spot output metadata includes:

```text
spot_actual_fixture_path
spot_actual_known_hours
spot_forecast_hours
spot_actual_patched_hours
spot_index_min
spot_index_max
spot_index_avg
spot_patch_warnings
```

Rows expose:

```text
spot_index
spot_source
spot_forecast_index
spot_actual_price
spot_actual_proto_index
spot_patched_actual_index
```

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

Heat production is optimized by a deterministic discrete dynamic program over a virtual heat battery SOC.

P0022 default heat optimizer settings:

```text
heat_optimizer = discrete_dp
heat_modes_kw = 2..22
heat_soc_capacity_kWh = 300
heat_soc_step_kWh = 1
start_soc_pct = 100
end_soc_min_pct = 50
min_soc_pct = 0
max_soc_pct = 100
```

The DP chooses one delivered thermal output mode per hour. It minimizes spot-index-weighted heat production plus low-SOC and overflow penalties, then derives `heat_cost_weight` from the optimized heat action, SOC and price index for downstream ventilation planning.

Output keeps the established heat row fields:

```text
heat_need_kWh
heat_kWh
heat_soc_pct
heat_cost_weight
```

Rows may also expose DP diagnostics:

```text
heat_price_index
heat_action_kw
heat_dp_cost_component
soc_penalty_component
```

Plan metadata includes heat optimizer identity, mode list, SOC configuration, min/end SOC and optimizer warnings.

P0023 adds COP-emulated electric cost reporting. This is an emulated POC comparison, not measured real-world savings.

COP model:

```text
heat_cost_model = cop_emulated_v1
cop_model = outdoor_temp_and_load_v1
cop range = 2.2..5.2
```

The model estimates COP from outdoor temperature and delivered heat output, then computes:

```text
optimized_heat_el_kWh = heat_kWh / cop_optimized
optimized_heat_el_cost = optimized_heat_el_kWh * heat_price_index
flat_heat_kWh = heat_need_kWh
flat_heat_el_kWh = flat_heat_kWh / cop_flat
flat_heat_el_cost = flat_heat_el_kWh * heat_price_index
optimized_vs_flat_cost_pct = optimized_heat_el_cost_total / flat_heat_el_cost_total * 100
optimized_saving_pct = 100 - optimized_vs_flat_cost_pct
```

The flat-production baseline means producing each hour's heat need directly in that hour. It uses the same heat-need, weather and price-index inputs as the optimized plan.

Rows may expose:

```text
cop_optimized
heat_el_kWh
heat_el_cost
flat_heat_kWh
cop_flat
flat_heat_el_kWh
flat_heat_el_cost
```

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

Occupancy gain is derived from `people`:

```text
base_people = 3
base_occupancy_gain_ppm_h = 70
occupancy_gain_ppm_h = 70 * people / 3
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
