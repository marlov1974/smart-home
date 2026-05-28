# Package P0018 Implementation Design

## Package

`P0018`

## Package interpretation

Create a Mac-only deterministic lab POC that builds one 168-hour operational-week plan combining heat production, spot-index cost, RH ventilation policy and PPM ventilation planning. It must be inspectable from CLI and tests, but it must not control live devices.

## Weather-profile provider choice and deterministic fallback

Use a deterministic synthetic profile by ISO week number in `input_profiles.py`.

Reason:

- no network dependency during tests
- week number remains the only public weather key
- enough variation can be produced for winter/cold, shoulder/neutral and summer/humid policy cases

The profile will generate 168 hourly outdoor temperature and outdoor RH values. It is a POC input generator, not a climate truth source.

## Spot-index integration or fixture strategy

Reuse P0017 `forecast_period_indexes(week)` from `src.mac.services.spot_forecast.model`.

Expand the 21 8h values to 168 hourly values by repeating each period value 8 times. This preserves P0017 operational-week order:

```text
mon 06-14, mon 14-22, mon 22-06, ... sun 22-06
```

Tests may pass explicit 21-value vectors to isolate expansion behavior.

## Heat planner algorithm

Use the package heat-need formula:

```text
heat_need_day_kWh = max(0, 12.5 * (set_temp_c - outdoor_temp_c) - 42.0)
heat_need_kWh = heat_need_day_kWh / 24.0
```

Set temperature:

```text
set_temp_c = current_house_temp
```

Reason: the CLI already supplies current house temperature, and using it as the POC setpoint keeps v1 input simple without adding another public parameter.

Allocation:

1. Compute hourly heat need.
2. Start from total weekly need.
3. Allocate heat preferentially to lower spot-index hours using inverse price weights.
4. Clamp each hour to `2.0..25.0` kWh/h, then redistribute remaining weekly energy within available capacity.
5. Simulate a virtual heat store starting full enough to cover one day of average need.
6. Compute `heat_soc_pct`.
7. Compute `heat_cost_weight` from whether production is above or below current need, clamped to `0.25..2.5`.

The heat plan is intended as a cost-signal generator for the PPM planner, not final heat-pump control.

## PPM dynamic model

Use the physically motivated dilution approximation from the package:

```text
removal_ppm_h = flow_lps * 3.6 / house_volume_m3 * max(0, ppm - outdoor_ppm)
ppm_after = ppm + occupancy_gain_ppm_h - removal_ppm_h
```

Constants:

```text
house_volume_m3 = 780
outdoor_ppm = 420
default occupancy_gain_ppm_h = 70
```

Clamp modeled PPM states to a finite planning range for dynamic programming, while retaining actual output values from reconstructed simulation.

## Optimization method

Use deterministic dynamic programming over:

```text
ppm state step = 10 ppm
ppm state range = 400..1400 ppm
supply modes = 25,28,31,34,37,40,43,46,49,52,55
```

For each hour and state, evaluate all supply modes, compute next PPM state and add:

```text
ppm_cost(ppm_after)
+ heat_cost_weight[t] * vent_cost[m]
+ rh_weight[t] * vent_cost[m]
```

Add a small supply tie-break penalty so the optimizer avoids higher modes when lower modes achieve the same PPM objective. When RH is favorable, also add a POC-specific high-supply penalty above 49% so negative RH cost does not turn into unconditional 55% overventilation.

Reconstruct the chosen 168-hour mode sequence and simulate exact hourly `ppm_delta`, `ppm_absolute`, `flow_lps`, cost components and total cost.

## Cost tables and continuation behavior above 1000 ppm

Use the package ventilation and PPM cost tables.

For PPM above 1000, continue quadratically:

```text
ppm_cost = 210 + 25 * steps + steps * steps
steps = ceil((ppm - 1000) / 25)
```

This keeps high PPM increasingly expensive without requiring a larger table.

## RH policy model

Compute `rh_weight` from deterministic outdoor temperature/RH heuristics:

- cold dry outdoor conditions: `+2.5`
- cool/dry conditions: `+1.5`
- neutral: `0.0`
- mild and humid/helpful: `-1.0`

Compute `rh_delta` as a coarse result indicator:

```text
rh_delta = -rh_weight * (supply_pct - 25) / 30
```

This is not a physical RH forecast; it only makes the policy effect inspectable.

## Output format

Default CLI output is a human-readable fixed-width table with 168 rows and required columns.

Optional formats:

- `--format json`: metadata plus hourly rows
- `--format csv`: CSV header plus hourly rows

The public CLI accepts only required POC inputs plus output/diagnostic options:

```text
--week
--ppm
--house-temp
--occupancy-gain-ppm-h
--format
```

No reference year or current indoor RH input is added.

## Files/modules intended to change

- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0018/**`

## Files/modules intentionally not changed

- `src/mac/services/spot_forecast/**`: reused but not changed.
- `tests/mac/spot_forecast/**`: existing P0017 tests remain intact.
- `dep/**`: no deploy artifacts.
- G1 repository: not touched.
- Home Assistant and Shelly runtime code: not touched.

## Test strategy

Unit tests cover:

- CLI contract and no reference-year input
- output has 168 rows and required columns
- 21-to-168 spot expansion
- heat plan balances weekly need within tolerance
- supply modes stay in allowed set
- PPM dynamics direction
- policy cases A/B/C
- higher occupancy can push PPM toward upper normal range
- JSON/CSV output shape

Verification commands:

```bash
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json
git diff --check
```

## Risks and uncertainties

- The synthetic weather profile is a POC approximation and should not be used as forecast truth.
- Heat allocation is intentionally simple and may need later replacement with the canonical heat-pump planner.
- RH output is policy evidence only, not indoor RH physics.
- Dynamic programming discretization can affect exact supply choices; tests focus on required directional behavior.

## Design deviations during implementation

Attempt 1 added a high-supply penalty above 49% when `rh_weight < 0`. Reason: the first implementation rewarded favorable RH strongly enough that the optimizer selected 55% even when PPM was already near the desired range. This keeps the package behavior that 46% or 49% should be preferred when sufficient.
