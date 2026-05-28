# Package P0022 Review Evidence

## Package

`P0022`

## Consistency result

PASS

## Files checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `requirements/packages/P0022-discrete-dp-heat-optimizer-for-weekly-home-poc.md`
- `requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md`
- `requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md`
- `requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md`
- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `git status --short --branch`

## Checks

### Package vs memory

Consistent. The change remains Mac-only POC planning and does not change live runtime ownership or actuation.

### Package vs P0018/P0020/P0021 implementation/evidence

Consistent. Existing `HeatPlan` output can be extended with metadata while preserving the rows consumed by PPM/RH planning and browser/API output.

### Package vs heat-pump and heat-loss assumptions

Consistent for POC. Heat modes are documented as delivered thermal output modes, not live heat-pump commands.

### Package vs Mac lab structure

Consistent. The existing lab package is the correct location.

### Package vs G1/G2 boundary

Consistent. No G1 repository or current runtime behavior is touched.

### Package vs testability/offline constraints

Consistent. The DP optimizer uses only standard-library Python and can be tested with fixture weather.

### Package vs browser/API compatibility

Consistent. Existing URLs remain valid. Browser/API summaries can add heat optimizer fields without removing existing fields.

## Decision

Continue.

## Notes for human/ChatGPT review

The implementation will keep the existing heat need formula and P0021 weather semantics. It will replace the heuristic allocation inside `plan_heat()` with a discrete dynamic-programming optimizer.
