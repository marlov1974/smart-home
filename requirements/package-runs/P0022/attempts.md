# Package P0022 Attempts

## Attempt 1

Implemented the discrete DP heat optimizer for the Mac weekly home POC.

Changes made:

- Added `heat_optimizer.py` with `HeatOptimizerConfig`, default config, low-SOC penalty, DP optimizer and derived heat cost-weight logic.
- Replaced the heuristic heat allocator in `plan_heat()` with `optimize_heat_dp()`.
- Extended `HeatPlan` with optimizer metadata and hourly DP diagnostics.
- Exposed heat optimizer diagnostics in rows, JSON metadata, API summary and HTML summary/table.
- Added package tests for DP price shifting, SOC constraints, metadata exposure and derived heat cost weights.
- Updated durable planning and function documentation.

Verification:

```text
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
PASS, 36 tests

python3 -m unittest discover tests/mac
PASS, 110 tests

python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 6 --fixture-weather
PASS, rendered 168-hour table with heat SOC ending at 50.0%

python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
PASS, weekly_home_optimizer_poc server smoke ok

git diff --check
PASS
```

Live actions: none.

Uncertainty:

- The virtual SOC model is intentionally POC-level and not a live heat-pump/runtime constraint model.
- The CLI fixed-width table keeps the original compact heat columns; DP diagnostics are available through JSON/CSV/API/browser rows.
