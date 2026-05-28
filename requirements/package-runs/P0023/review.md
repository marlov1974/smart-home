# Package P0023 Review Evidence

## Package

`P0023`

## Consistency Result

PASS

## Files Checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `requirements/packages/P0023-cop-emulator-and-optimized-vs-flat-electric-cost.md`
- `requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md`
- `requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md`
- `requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md`
- `requirements/packages/P0022-discrete-dp-heat-optimizer-for-weekly-home-poc.md`
- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/weekly_home_optimizer_poc/**`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `git status --short --branch`

## Checks

### Package vs memory

Consistent. The memory contract already defines the weekly home optimizer as Mac-only POC tooling with no live control. P0023 adds reporting, not control.

### Package vs P0018/P0020/P0021/P0022 implementation/evidence

Consistent. P0018 row output and P0020 browser/API shape can be extended with additive fields. P0021 weather and people inputs remain unchanged. P0022 heat output already exposes the optimized heat plan and price index needed for electric-cost comparison.

### Package vs heat-pump assumptions

Consistent with stated POC boundary. The package explicitly requires a deterministic emulator and forbids exact Mitsubishi/Geodan modeling, brine modeling or live heat-pump command mapping.

### Package vs Mac lab structure

Consistent. The expected source and tests are under `src/mac/labs/weekly_home_optimizer_poc/**` and `tests/mac/weekly_home_optimizer_poc/**`.

### Package vs G1/G2 boundary

Consistent. No G1 repository, Shelly deploy artifact, Home Assistant runtime or live device path is in scope.

### Package vs testability/offline constraints

Consistent. The COP model and comparison are deterministic and can be tested with fixture weather. Automated tests do not need internet.

### Package vs browser/API compatibility

Consistent. Existing inputs and endpoints remain valid; new summary and hourly fields are additive.

### Package vs no-live-control invariant

Consistent. P0023 performs local calculation only. Local HTTP smoke/manual testing is allowed; live writes are not.

## Decision

Continue.

## Assumptions

- Cost totals use the existing `heat_price_index` as a relative electricity price index, not currency.
- The CLI fixed-width table can keep compact hourly columns if JSON/CSV/API/browser expose all new hourly fields and the table header includes the weekly comparison.
