# Package P0023 Implementation Design

## Package

`P0023`

## Package Interpretation

Add deterministic COP-emulated electric cost accounting to the weekly home POC and compare the optimized DP heat plan against a flat-production baseline where each hour produces exactly that hour's heat need.

## Selected COP Formula and Constants

Use the package-required `outdoor_temp_and_load_v1` formula:

```text
base_cop = 4.2
temp_adjustment:
  outdoor_temp_c < 5: -0.055 * (5 - outdoor_temp_c)
  otherwise: min(0.4, 0.03 * (outdoor_temp_c - 5))
load_adjustment:
  2..6 kW: +0.15
  7..14 kW: 0.0
  15..18 kW: -0.15
  19..22 kW: -0.35
cop clamp: 2.2..5.2
```

For flat production, `heat_kw` may be fractional because it equals heat need. The load bands will be applied by numeric range, with values below 7 kW using the low-load adjustment and values above 18 kW using the high-load adjustment.

## Flat-Production Baseline

For each hour:

```text
flat_heat_kWh[t] = heat_need_kWh[t]
flat_cop[t] = estimate_cop(outdoor_temp_c[t], flat_heat_kWh[t])
flat_heat_el_kWh[t] = flat_heat_kWh[t] / flat_cop[t]
flat_heat_el_cost[t] = flat_heat_el_kWh[t] * heat_price_index[t]
```

## Optimized Electric-kWh and Cost

For each optimized-plan hour:

```text
optimized_heat_kWh[t] = heat_kWh[t]
cop_optimized[t] = estimate_cop(outdoor_temp_c[t], optimized_heat_kWh[t])
heat_el_kWh[t] = optimized_heat_kWh[t] / cop_optimized[t]
heat_el_cost[t] = heat_el_kWh[t] * heat_price_index[t]
```

Weekly totals are rounded for output but computed from unrounded hourly values.

## Summary and Hourly Schema Changes

Add a new `HeatCostComparison` dataclass to `schema.py` and add it to `WeeklyPlan`.

Summary-level fields:

```text
heat_cost_model
cop_model
cop_min
cop_max
optimized_heat_el_kWh
flat_heat_el_kWh
optimized_heat_el_cost
flat_heat_el_cost
optimized_vs_flat_cost_pct
optimized_saving_pct
avg_cop_optimized
avg_cop_flat
heat_cost_comparison_warnings
```

Hourly row fields:

```text
cop_optimized
heat_el_kWh
heat_el_cost
flat_heat_kWh
cop_flat
flat_heat_el_kWh
flat_heat_el_cost
```

## UI Rendering Changes

The browser summary will add compact metric cards for cost model, optimized/flat electric cost, optimized-vs-flat percentage, saving percentage and average COP values. It will also render a plain sentence:

```text
Optimized heat did the weekly job at X% of flat-production cost (emulated POC).
```

Warnings are displayed when present.

## Warning Behavior

If `flat_heat_el_cost_total` is zero, percentage fields become `None` and `heat_cost_comparison_warnings` includes `flat_heat_el_cost_zero`.

If optimized or flat electric kWh totals are zero, average COP for that side becomes `None`.

## Files Intended to Change

- `src/mac/labs/weekly_home_optimizer_poc/cop.py`
- `src/mac/labs/weekly_home_optimizer_poc/schema.py`
- `src/mac/labs/weekly_home_optimizer_poc/planner.py`
- `src/mac/labs/weekly_home_optimizer_poc/tables.py`
- `src/mac/labs/weekly_home_optimizer_poc/server.py`
- `src/mac/labs/weekly_home_optimizer_poc/html.py`
- `src/mac/labs/weekly_home_optimizer_poc/README.md`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `docs/functions/00-index.md`

## Files Intentionally Not Changed

- P0017 spot forecast compact API.
- P0022 heat optimizer constraints and objective.
- Shelly, Home Assistant and deploy artifacts.

## Tests and Manual Verification

Required commands:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4 --fixture-weather
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
git diff --check
```

Manual server command:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Manual phone URL:

```text
http://<mac-lan-ip>:8081/?week=48&ppm=500&houseTemp=22&people=4
```

## Risks and Uncertainties

- The model reports relative indexed electric cost, not measured SEK or metered power import.
- COP is intentionally a first emulator and excludes brine, flow temperature, defrost, DHW and compressor behavior.
- The optimized DP objective still uses thermal output times price index; P0023 only adds electric-cost reporting.
