# P0024 findings

## Result

P0024 implemented hourly spot forecast with actual-price patching for the weekly home optimizer POC.

## Verification

Required commands:

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

Additional check:

```text
build_spot_plan(53)
168 hours, spot_patch_warnings = ("actual_fixture_week_unavailable",)
```

## Live actions

No Shelly, Home Assistant, heat pump, FTX or other live-device actions were performed.

## Knowhow promotion

Skipped. P0024 had no live debugging, runtime anomaly, external API discovery or repeated workflow problem that should become global knowhow. Package-specific UTC fixture key formatting evidence is stored in `attempts.md`.
