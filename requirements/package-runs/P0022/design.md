# Package P0022 Implementation Design

## Package

`P0022`

## Package interpretation

Replace the weekly POC heat emulator with a deterministic discrete dynamic-programming heat optimizer that respects a bounded virtual heat battery and produces the same heat outputs needed by the PPM/RH planner.

## Selected SOC capacity/step/default constraints

Defaults:

```text
heat_soc_capacity_kWh = 300
heat_soc_step_kWh = 1
start_soc_pct = 100
end_soc_min_pct = 50
min_soc_pct = 0
max_soc_pct = 100
low_soc_threshold_pct = 25
```

Heat modes:

```text
2, 3, 4, ..., 22
```

## DP state/action representation

State is integer SOC kWh:

```text
0..300
```

Action is one delivered thermal kW/kWh-for-one-hour mode:

```text
heat_kw in 2..22
```

## Transition equation

For hour `t`:

```text
raw_next_soc = soc + heat_kw - heat_need_kWh[t]
next_soc = round(clamp(raw_next_soc, 0, capacity))
```

If `raw_next_soc` exceeds capacity, an overflow penalty is applied. This keeps all states bounded and avoids infeasible warm-hour cases caused by the package's minimum 2 kW heat mode.

## Objective function and penalties

Per-hour cost:

```text
heat_kw * spot_index[t]
+ low_soc_penalty(next_soc_pct)
+ overflow_penalty
+ small_tie_break_for_lower_heat_mode
```

Low SOC penalty is convex below 25%:

```text
((25 - soc_pct) / 25)^2 * 40
```

Overflow penalty:

```text
overflow_kWh^2 * 8
```

End-state selection requires `end_soc_pct >= 50` when feasible. If no feasible final state reaches 50%, choose the best available final state and expose a warning.

## Feasibility/fallback behavior

If the strict end target has any reachable final state, choose the cheapest such state. Otherwise choose the cheapest final state and record:

```text
end_soc_below_target
```

If reconstruction ever fails, raise an error because that indicates an implementation bug.

## Heat-cost weight derivation

Preserve P0018 directional semantics:

```text
base = normalized heat price / spot index

if heat_kWh > heat_need_kWh + 0.25:
  multiplier = 0.5
elif heat_kWh < heat_need_kWh - 0.25:
  multiplier = 2.0
else:
  multiplier = 1.0

if heat_soc_pct < 25:
  multiplier = max(multiplier, 2.0)

heat_cost_weight = clamp(base * multiplier, 0.25, 2.5)
```

## Output metadata/warnings

Extend heat plan metadata:

```text
heat_optimizer = discrete_dp
heat_modes_kw
heat_soc_capacity_kWh
heat_soc_step_kWh
start_soc_pct
end_soc_min_pct
min_heat_soc_pct
end_heat_soc_pct
heat_optimizer_warnings
```

Hourly rows also expose:

```text
heat_price_index
heat_action_kw
heat_dp_cost_component
soc_penalty_component
```

## Browser/API impact

Existing URLs and inputs remain valid. JSON/HTML summary adds heat optimizer metadata and warning visibility.

## Files/modules intended to change

- `src/mac/labs/weekly_home_optimizer_poc/heat_plan.py`
- `src/mac/labs/weekly_home_optimizer_poc/heat_optimizer.py`
- `src/mac/labs/weekly_home_optimizer_poc/schema.py`
- `src/mac/labs/weekly_home_optimizer_poc/tables.py`
- `src/mac/labs/weekly_home_optimizer_poc/server.py`
- `src/mac/labs/weekly_home_optimizer_poc/html.py`
- `src/mac/labs/weekly_home_optimizer_poc/README.md`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `docs/functions/00-index.md`
- `requirements/package-runs/P0022/**`

## Files/modules intentionally not changed

- P0017 spot forecast model.
- P0021 weather provider semantics.
- PPM optimizer supply modes and dynamics.
- Shelly, Home Assistant and deploy artifacts.

## Tests and manual verification

Run:

```bash
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 6 --fixture-weather
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
git diff --check
```

## Risks and uncertainties

- The DP uses rounded SOC states, so it is a discrete approximation.
- Minimum 2 kW heat mode can overproduce in warm/low-need hours; overflow penalty makes this visible in cost but bounded in SOC.
- No COP model is introduced in this package.

## Design deviations during implementation

None yet.
