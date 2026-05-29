# P0025 attempts

## Attempt 1

Implemented the P0025 known-horizon spot planner:

- model changed to `hourly_forecast_with_actual_horizon_patch_v1`
- default `spot_actual_horizon_hours = 20`
- `spot_index` remains a compatibility alias for `spot_planning_index`
- future fixture actuals outside the horizon are diagnostics only
- added outcome/error row fields
- added internal fixture year/path support for deterministic 2026 tests

Initial focused tests failed only because P0024 tests still expected the old full-week model:

- old model string `hourly_forecast_with_actual_patch_v1`
- old patch source `actual_patched`
- old count of 168 patched hours

Updated tests to P0025 contracts and added `test_spot_known_horizon.py`.

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

The package requested a server `--smoke` command, but the current implementation exposes `--once-smoke`; verification used the existing smoke flag as planned in `design.md`.
