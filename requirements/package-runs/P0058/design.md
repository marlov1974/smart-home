# Package P0058 Implementation Design

## Package

`P0058`

## Package interpretation

Change the imported G2 FTX state runtime so `VVX efficiency` is reported as `0` whenever `ctx.run.vvx` is false.

## Chosen implementation structure

Modify only `calcVvxEfficiencyFeature(ctx, hist)` in `src/shelly/ftx/state/perf-vvx.js`.

The state loop already computes `ctx.run.vvx` before calling `calcVvxEfficiencyFeature()`, so the guard can live at the feature boundary without touching the run calculation or output write path.

## Intended changes

### Files/modules to change

- `src/shelly/ftx/state/perf-vvx.js`
- `tests/mac/shelly_ftx/test_vvx_efficiency.py`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- package-run evidence files

### Files/modules intentionally not changed

- `src/shelly/ftx/state/run-process.js`
- `src/shelly/ftx/state/main.js`
- `src/shelly/ftx/scripts/vvx/*`
- `dep/s/**`
- Home Assistant config
- live devices

## Refactoring decisions

No refactor. This is a direct guard in the existing feature function.

## Test strategy

Add a focused unittest that verifies the source contains the stopped-run guard before the existing running-path calculation and that the stopped path writes zero percentage and zero history.

Run existing Mac tool tests to catch unrelated tooling regressions.

## Build / generated artifact strategy

No deploy artifacts are generated in P0058.

## Risks and uncertainties

- Source-level tests do not execute Shelly JS on a Shelly runtime.
- Clearing history while stopped means the first running calculation after restart/off-period will start from zero smoothing history. This is deliberate to avoid carrying invalid off-state efficiency.

## Design deviations during implementation

None yet.
