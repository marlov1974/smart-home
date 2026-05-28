# Package P0018 Review Evidence

## Package

`P0018`

## Consistency result

PASS

## Files checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md`
- `requirements/packages/P0017-mac-spot-period-index-service.md`
- `memory/planning/spot-period-index-api.md`
- `memory/planning/winter-heat-pump-flex-planner.md`
- `memory/physical/ftx/airflow.md`
- `memory/physical/ftx/sensors.md`
- `memory/physical/ftx/temperatures.md`
- `memory/physical/heating/heat-pumps.md`
- `src/mac/services/spot_forecast/**`
- `tests/mac/spot_forecast/**`
- `docs/functions/mac/spot-forecast.md`
- `git status --short --branch`
- `git log --oneline --decorate --left-right HEAD...origin/main`

## Checks

### Package vs memory

Consistent. The package is Mac lab/POC work and does not change Shelly autonomy, G1 runtime, Home Assistant, deploy artifacts or live control. FTX airflow memory supports the POC flow conversion and practical max-flow context.

### Package vs linked requirements

Linked requirements are TBD in the package. The package itself contains enough scoped requirements to implement the POC.

### Package vs previous packages

Consistent with P0017. P0017 exposes a week-number-only 21-value period-index model and contract. P0018 can reuse `forecast_period_indexes()` and expand each 8h period to 8 hourly values without changing P0017 behavior.

### Package vs implementation/deploy structure

Consistent. There is no existing `src/mac/labs/` tree, but creating `src/mac/labs/weekly_home_optimizer_poc/` matches the package's expected source area. Tests can live under `tests/mac/weekly_home_optimizer_poc/`.

### Package vs G1/G2 boundary

Consistent. No G1 repository or current runtime behavior is touched.

### Package vs FTX airflow facts

Consistent. The POC uses supply modes up to 55%, with `flow_lps = supply_pct / 100 * 240`, staying below the documented practical max-flow reference.

### Package vs heat-pump capacity and heat-loss assumptions

Consistent for a POC. The package's `max_heat_kWh_per_h = 25.0` is higher than the conservative single-unit capacity note, but the house has two heat pumps and the package explicitly marks these as POC planning values, not live VP constraints.

### Package vs invariants

Consistent. The implementation can keep public input limited to week, current PPM and current house temperature; avoid reference year; keep RH as cost/policy; restrict supply modes to 25..55; and use deterministic fixtures.

### Package vs testability and rollback

Testable with standard-library `unittest` and CLI execution. Rollback is a future package; no live runtime is affected.

### Chat-only assumptions

No chat-only assumption is needed. Weather profile choice is documented in design as deterministic synthetic profile by week number.

## Decision

Continue.

## Notes for human/ChatGPT review

The implementation will not use live weather APIs in v1. This is deliberate to satisfy the no-network test invariant and keep the POC deterministic.
