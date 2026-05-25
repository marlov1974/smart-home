# Winter heat-pump flex planner

This is the canonical planning contract for the winter heat-pump optimizer.

It replaces the earlier temporary weekday/weekend macroblock discussion with one parameterized model.

## Planning horizon and cadence

The planner builds a plan from the current strategy period to the next Monday 06:00 boundary.

```text
Anchor:
  next Monday 06:00 = 100% house charge

Replanning cadence:
  every 8h, aligned with strategy periods

Strategy periods:
  22:00-06:00
  06:00-14:00
  14:00-22:00
```

At each replan:

```text
1. Read current house state / charge.
2. Fetch updated weather forecast.
3. Load period price indexes from fallback statistics or Mac model.
4. Recompute the remaining plan to next Monday 06:00.
5. Apply only the next executable block/period plan.
```

The planner does not normally need to look beyond next Monday 06:00.

## Heat need model

Use the G1 heat-balance model as the initial forecast model:

```text
heat_need_kWh_day = max(
  0,
  HOUSE_LOSS_KWH_DAY_PER_C * (target_temp_C - outdoor_temp_C)
  - BASE_INTERNAL_KWH_DAY
  - solar_Wm2 * SOLAR_KWH_DAY_PER_WM2
)
```

Initial constants from G1:

```text
HOUSE_LOSS_KWH_DAY_PER_C = 12.5
BASE_INTERNAL_KWH_DAY = 42.0
SOLAR_KWH_DAY_PER_WM2 = 0.06
```

Heat loss must be forecast against the house target temperature / setpoint, not the current house temperature.

## Virtual house battery

Comfort mode defines how much virtual house charge can be used.

```text
LOW:
  comfort_band_C = 2.0
  battery_kWh = 400

MEDIUM:
  comfort_band_C = 1.0
  battery_kWh = 200

HIGH:
  comfort_band_C = 0.5
  battery_kWh = 100
```

Mapping:

```text
battery_kWh = comfort_band_C * 2 * 100

100% charge = target_temp_C + comfort_band_C
0% charge   = target_temp_C - comfort_band_C
```

The virtual battery is a planning abstraction. Temperature does not have a hard physical cap at 100%; simulations may show temperatures above the nominal 100% point if the plan intentionally overproduces before later losses.

## Load flex factor

Price optimization should fade out as heat need approaches sustainable heat-pump capacity.

```text
weekly_sustainable_capacity_kWh = sustainable_heat_kw * 24 * 7
```

Initial planning value:

```text
sustainable_heat_kw = 22
weekly_sustainable_capacity_kWh = 3696
```

Load ratio:

```text
load_ratio = weekly_heat_need_kWh / weekly_sustainable_capacity_kWh
```

Flex:

```text
free_threshold = 0.50
flat_threshold = 0.98

load_flex = clamp(
  (flat_threshold - load_ratio) / (flat_threshold - free_threshold),
  0,
  1
)
```

Interpretation:

```text
load_flex = 1:
  high price-shifting freedom

load_flex = 0:
  no price-shifting freedom; production should be flat
```

## Comfort price factor

Comfort mode scales the load flex.

```text
LOW:
  comfort_price_factor = 1.00

MEDIUM:
  comfort_price_factor = 0.55

HIGH:
  comfort_price_factor = 0.25
```

Effective flex:

```text
effective_flex = load_flex * comfort_price_factor
```

## Period groups

Use two clean groups only.

```text
Weekday group:
  Monday 06:00 through Friday 22:00

Weekend group:
  Friday 22:00 through Monday 06:00
```

There is no special Friday daytime group in the canonical model.

## Parameter function

For each period, planner weight is:

```text
energy_weight = mass_weight / (price_index ^ price_exponent)
```

Parameters are generated from `effective_flex`:

```text
weekday_mass = 1.0 + 0.5 * effective_flex
weekday_exp  = 2.0 * effective_flex

weekend_mass = 1.0 + 0.7 * effective_flex
weekend_exp  = 0.8 * effective_flex
```

Period-specific values:

```text
if period is weekday group:
  mass_weight = weekday_mass
  price_exponent = weekday_exp

if period is weekend group:
  mass_weight = weekend_mass
  price_exponent = weekend_exp
```

This makes the model behave as follows:

```text
Mild weather + LOW:
  strong price shifting
  weekday nights and weekend periods get more production

Cold weather:
  price shifting fades as load ratio increases

Extreme cold:
  effective_flex approaches 0
  all mass weights approach 1
  all exponents approach 0
  production becomes flat across all periods

HIGH comfort:
  uses smaller virtual battery and smaller effective_flex
  production is much flatter and house temperature moves less
```

## Price-index source

Runtime must include a deterministic fallback price-index model.

Mac should later provide a better statistical / ML price-index model that can be more period-unique and may use weather, calendar, seasonality and live market signals.

Both sources must expose the same planner contract:

```text
period_price_index:
  1.0 = average price over the relevant horizon/week
  0.5 = half average price
  2.0 = double average price
```

The winter 2025 fallback table is stored in:

```text
memory/planning/spotprice-2025-winter-8h-weekly-period-index.md
```

## Allocation algorithm

For the current horizon to next Monday 06:00:

```text
1. Compute forecast heat loss per period.
2. Compute total production required:
     sum(period_heat_loss)
     + target_charge_at_anchor
     - current_charge
3. Compute each period's energy_weight.
4. Allocate production proportionally to energy_weight.
5. Simulate charge curve forward.
6. Replan every 8h with fresh state and forecasts.
```

The normal model should not require hard comfort/SoC constraints for ordinary planning. Safety constraints still exist outside the optimizer and may override it.

## Block execution

The strategy planner outputs kWh targets per 8h period, later broken down to 2h blocks and then controlled by a block regulator.

The desired runtime direction is kWh target control, not fixed logical level scheduling:

```text
Period/block planner:
  decides target heat production in kWh

Block regulator:
  drives heat pumps / pumps to hit kWh target using measured delivered heat
```

Delivered heat should eventually be calculated from measured water flow and delta-T:

```text
heat_kW ≈ flow_L_per_s * 4.18 * (flow_temp_C - return_temp_C)
```

## Calibration checkpoints

For constant -5 C, LOW comfort, the accepted planner behaviour is approximately:

```text
minimum simulated house temperature: about 18.5 C
max period effect: about 21 kW
end Monday 06: 100% charge
```

For constant -10 C:

```text
LOW:
  minimum simulated house temperature: about 18.7 C
  max period effect: about 23 kW

MEDIUM:
  minimum simulated house temperature: about 19.1 C
  max period effect: about 19 kW

HIGH:
  minimum simulated house temperature: about 19.6 C
  max period effect: about 16 kW
```

For constant -25 C:

```text
load_flex should approach 0
production should approach flat continuous operation
about 21.7 kW for the initial heat model and 22 kW sustainable capacity
```

## Economic sanity check

For constant -5 C, LOW comfort, and a 3 SEK/kWh weekly mean price, the approximate value of the optimized heat allocation versus flat no-optimization allocation was:

```text
flat heat-value cost:       about 5679 SEK/week
optimized heat-value cost:  about 4662 SEK/week
heat-value saving:          about 1018 SEK/week
relative saving:            about 17.9%
```

If COP is equal in both cases, monetary electricity-bill saving scales by COP. At COP 5 this corresponds to roughly:

```text
1018 / 5 ≈ 204 SEK/week
```

Actual savings must be adjusted for COP changes caused by brine temperature, flow temperature, DHW work and short-term boosting.
