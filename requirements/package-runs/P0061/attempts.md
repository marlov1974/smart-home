# P0061 Attempts

## Attempt 1

Status: passed.

Actions:

- Cloned `https://github.com/marlov74/Market-Simulator.git` into `/Users/marcus.lovenstad/dev/Market-Simulator`.
- Copied Mac-side market simulator source, tests, data, docs, memory and package evidence from G2 into Market-Simulator.
- Removed the copied market simulator artifacts from G2.
- Updated active G2 bootstrap/function/memory indexes so they no longer require migrated market docs.

Verification:

```text
python3 -m unittest discover tests/mac
Ran 99 tests in 5.555s
OK

python3 -B -m unittest tests.mac.spot_forecast.test_contract_shape tests.mac.spot_forecast.test_period_index_api tests.mac.spotprice_history.test_source_parser tests.mac.services.spotprice_model_diagnostics.test_forecast_period_policy tests.mac.services.spotprice_temperature_normalization.test_core tests.mac.services.swedish_calendar.test_core tests.mac.weekly_home_optimizer_poc.test_output_shape
Ran 35 tests in 1.797s
OK
```

Live actions:

None.

## Notes

The migration intentionally kept `src.mac...` imports in Market-Simulator. No function behavior was changed.
