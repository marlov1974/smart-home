# Package P0021 Review Evidence

## Package

`P0021`

## Consistency result

PASS

## Files checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `requirements/packages/P0021-real-weather-and-occupancy-load-for-weekly-home-poc.md`
- `requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md`
- `requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md`
- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/weekly_home_optimizer_poc/**`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `memory/planning/weekly-home-poc-browser-ui.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `src/shelly/weather/weather.js`
- `git status --short --branch`

## Checks

### Package vs memory

Consistent. The work remains Mac POC/lab tooling and read-only browser/API/CLI execution. It does not change live device behavior.

### Package vs linked requirements

Linked requirements are TBD, but P0021 contains enough detailed requirements for implementation.

### Package vs previous packages

Consistent. P0021 explicitly supersedes P0018's initial public input contract by adding `people`, and extends P0020's browser/API wrapper. The existing P0018 planner already accepts `occupancy_gain_ppm_h`, so people can be mapped to that without changing the PPM optimizer semantics.

### Package vs implementation/deploy structure

Consistent. The existing lab package is the right source area. No deploy artifacts are required.

### Package vs G1/G2 boundary

Consistent. G1 is not touched. Current Shelly weather source coordinates can be reused as location facts for the Mac POC, but Shelly runtime code is not changed.

### Package vs invariants

Consistent. Tests can remain offline by using fixture/fallback providers. Manual runs can try read-only Open-Meteo archive weather and explicitly report fallback source/reason when unavailable.

### Package vs testability and rollback

Testable with standard-library unit tests and non-blocking smoke. Rollback is a later package or not running the lab server.

### Chat-only assumptions

No chat-only assumptions are required. The weather coordinate choice is based on existing G2 weather source code.

## Decision

Continue.

## Notes for human/ChatGPT review

Chosen weather location uses existing `src/shelly/weather/weather.js` constants:

```text
latitude 59.6214405
longitude 17.7336153
```

No live device action is involved.
