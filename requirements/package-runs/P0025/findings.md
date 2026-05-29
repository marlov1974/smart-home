# P0025 findings

## Result

P0025 implemented fixed known-horizon spot planning and forecast-vs-actual diagnostics for the weekly home optimizer POC.

## Sample week 48 evidence

Summary:

```text
spot_model = hourly_forecast_with_actual_horizon_patch_v1
spot_actual_horizon_hours = 20
spot_actual_known_hours = 20
spot_actual_patched_hours = 20
spot_forecast_hours = 148
spot_patch_warnings = ()
```

Rows:

```text
hour 0:
  spot_planning_source = actual_horizon_patched
  spot_forecast_index = 1.92
  spot_planning_index = 1.8666
  spot_actual_available = True
  spot_actual_outcome_index = 3.421226
  spot_forecast_error_index = 1.501226

hour 19:
  spot_planning_source = actual_horizon_patched
  spot_forecast_index = 1.12
  spot_planning_index = 0.8432
  spot_actual_available = True
  spot_actual_outcome_index = 1.545393
  spot_forecast_error_index = 0.425393

hour 20:
  spot_planning_source = forecast
  spot_forecast_index = 1.12
  spot_planning_index = 1.12
  spot_actual_available = True
  spot_actual_outcome_index = 1.487015
  spot_forecast_error_index = 0.367015
```

This demonstrates that actual outcome is available diagnostically at hour 20, but the planning value remains forecast.

## Verification

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
Ran 62 tests in 33.335s
OK

python3 -m unittest discover tests/mac
Ran 136 tests in 33.703s
OK

python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4 --format json
exit 0

python3 -m src.mac.labs.weekly_home_optimizer_poc --week 8 --ppm 500 --house-temp 22 --people 4 --format json
exit 0

python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
weekly_home_optimizer_poc server smoke ok
exit 0

git diff --check
exit 0
```

## Live actions

No Shelly, Home Assistant, heat pump, FTX or other live-device actions were performed.

## Knowhow promotion

Skipped. The package changed a local lab POC contract and did not include live debugging, runtime anomalies, external API discoveries or repeated workflow issues that should become global knowhow.
