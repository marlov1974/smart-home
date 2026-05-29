# P0024 attempts

## Attempt 1

Implemented the hourly spot model, schema additions, planner integration, output rendering and package tests.

Initial focused unittest discovery failed because:

- `resolve_week_utc_hours()` emitted UTC keys as `YYYY-MM-DDTHH:00:00Z`, while the fixture uses `YYYY-MM-DDTHH:00Z`; this caused zero actual-price overlap and forecast-only output.
- The deterministic patch example used exact float equality for values produced by floating-point arithmetic.
- The DST test expected `T` separators in `local_wall_hour`, while the fixture uses a space, for example `2025-10-26 02:00`.

Fixes:

- Changed UTC key formatting to match the fixture.
- Changed patch-example assertions to tolerant float comparisons.
- Changed the DST test to match fixture `local_wall_hour` formatting.

Result:

```text
python3 -m unittest tests.mac.weekly_home_optimizer_poc.test_actual_spot_patch tests.mac.weekly_home_optimizer_poc.test_hourly_spot_forecast tests.mac.weekly_home_optimizer_poc.test_spot_fixture_dst tests.mac.weekly_home_optimizer_poc.test_spot_summary_fields tests.mac.weekly_home_optimizer_poc.test_browser_spot_rendering
Ran 9 tests in 4.212s
OK
```

## Final verification

Package verification passed after the implementation and documentation updates:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
Ran 55 tests in 30.488s
OK

python3 -m unittest discover tests/mac
Ran 129 tests in 30.756s
OK

python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4
exit 0

python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
weekly_home_optimizer_poc server smoke ok
exit 0

git diff --check
exit 0
```
