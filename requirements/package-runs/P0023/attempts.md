# Package P0023 Attempts

## Attempt 1

Implemented COP-emulated optimized-vs-flat heat electric cost comparison for the Mac weekly home POC.

Changes made:

- Added `cop.py` with deterministic COP emulator and optimized-vs-flat comparison helper.
- Added `HeatCostComparison` to the weekly plan schema.
- Wired cost comparison into `build_weekly_plan()` using the same weather, heat need, optimized heat output and price index as the plan.
- Exposed summary fields in CLI JSON metadata, API summary and browser summary.
- Exposed hourly COP/electric-cost fields in rows/CSV/JSON/API/browser table.
- Added browser wording that labels the result as emulated POC, not measured savings.
- Added tests for COP bounds/shape, hourly consistency, flat baseline, percentage math, zero-denominator warnings, full output fields and browser rendering.
- Updated planning and function documentation.

Verification:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
PASS, 46 tests

python3 -m unittest discover tests/mac
PASS, 120 tests

python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4 --fixture-weather
PASS, heat_cost_model=cop_emulated_v1, optimized_vs_flat_cost_pct=67.12, optimized_saving_pct=32.88

python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
PASS, weekly_home_optimizer_poc server smoke ok

git diff --check
PASS
```

Additional manual smoke:

```text
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4
PASS with escalated network, weather_source=real_open_meteo, weather_profile_year=2025, optimized_vs_flat_cost_pct=67.02, optimized_saving_pct=32.98
```

The same manual command inside the restricted sandbox fell back explicitly to `synthetic_fallback` with `weather_fallback_reason=open-meteo fetch failed: <urlopen error [Errno 8] ...>`, which is expected under network restriction and verifies the fallback remains explicit.

Live actions: none.

Uncertainty:

- Cost values are relative price-index cost, not measured SEK or metered electricity.
- COP is a first deterministic POC emulator and omits brine, flow temperature, DHW, defrost and compressor behavior.
- The P0022 heat optimizer objective remains thermal-output price proxy; P0023 adds reporting only.
