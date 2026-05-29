# P0025 design

## Known Actual Horizon Model

Use a fixed POC horizon:

```text
spot_actual_horizon_hours = 20
```

For each 168-hour plan:

- Build the 168-hour internal forecast baseline.
- Resolve the requested operational week to UTC hour keys.
- Load actual/outcome spot fixture rows keyed by UTC hour.
- Only the first `min(20, available actual hours in the planner window)` chronological hours are eligible for actual-horizon patching.
- Hours outside that known horizon use forecast planning values even when an actual fixture outcome exists.

## Planning Series vs Outcome Series Separation

The optimizer must use only the planning series:

```text
spot_planning_index
```

`spot_index` remains as a compatibility alias for `spot_planning_index`.

Diagnostic outcome fields are separate:

```text
spot_actual_outcome_index
spot_actual_available
spot_forecast_error_index
spot_forecast_error_pct
```

Future actual fixture data outside the 20-hour horizon must not affect `spot_planning_index`.

## Forecast-Sum Preservation Calculation

For the known horizon overlap:

```text
actual_proto_index = actual_price / mean(actual_price over known overlap)
patched = actual_proto_index * sum(forecast over known overlap) / sum(actual_proto_index)
```

The sum of patched planning indexes over the known horizon must match the original forecast sum over the same horizon within numeric tolerance.

For outcome diagnostics, normalize all available actual outcome prices in the 168-hour window onto the same 168-hour forecast-sum basis:

```text
actual_outcome_proto = actual_price / mean(actual_price over available outcome hours)
spot_actual_outcome_index = actual_outcome_proto * forecast_available_sum / actual_proto_sum
```

This diagnostic basis is independent of planner knowledge.

## UTC/Hour Alignment and DST Handling

Use `utc_hour_start` as the only join key. Keep `resolve_week_utc_hours()` as the 168-hour planner window resolver. No local wall-hour joins are introduced.

## 2026 Forecast-vs-Actual Fixture Strategy

Do not fake real 2026 prices. Add internal function parameters so tests can supply a deterministic fixture path and ISO year. This supports a February 2026 comparison fixture without adding public `reference_year` or date inputs.

## Public API Compatibility Decision

Keep existing CLI and HTTP inputs unchanged. The existing API response shape stays:

```text
input
summary
hours
```

Rows gain P0025 spot planning/outcome diagnostics. Summary gains `spot_actual_horizon_hours` and updated model/strategy identifiers.

## Test Strategy

- Fixed 20-hour horizon count.
- Horizon patch preserves first-20 forecast sum.
- Optimizer/planner does not use future actuals outside the horizon.
- Forecast-vs-actual diagnostic fields render in rows.
- Missing actual outcomes return forecast-only planning rows with nullable diagnostics.
- Partial actual horizon shorter than 20 emits metadata/warning and keeps 168 rows.
- Deterministic 2026 fixture exercises internal year/path support.
- Existing API call shape still works.

## Verification Commands

Use the repository's actual test path:

```bash
python3 -m unittest discover tests/mac/weekly_home_optimizer_poc
python3 -m unittest discover tests/mac
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 48 --ppm 500 --house-temp 22 --people 4 --format json
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 8 --ppm 500 --house-temp 22 --people 4 --format json
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081 --once-smoke
git diff --check
```

P0025 mentions `--smoke`, but current server uses `--once-smoke`; use the existing command and record it.

## Risks and Assumptions

- The forecast baseline remains the P0017 period-index expansion; P0025 only changes actual-horizon access and diagnostics.
- Accuracy diagnostics are normalized indexes, not currency.
- Existing browser table may become wider; keep only high-signal P0025 columns visible in HTML while full JSON/CSV rows contain all diagnostics.
