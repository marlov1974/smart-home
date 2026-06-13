# Package P0058 Review Evidence

## Package

`P0058`

## Consistency result

PASS

## Files checked

- `requirements/package-runs/P0057/CHANGELOG.md`
- `src/shelly/ftx/state/main.js`
- `src/shelly/ftx/state/run-process.js`
- `src/shelly/ftx/state/perf-vvx.js`
- `docs/functions/shelly/ftx-runtime-baseline.md`

## Checks

### Package vs memory

P0057 moved FTX runtime source inspection into G2. P0058 uses `src/shelly/ftx/` and does not read or edit G1.

### Package vs previous packages

P0057 intentionally left the VVX efficiency limitation unchanged. P0058 is the follow-up behavior fix.

### Package vs implementation/deploy structure

The change is source-only under `src/shelly/ftx/state/perf-vvx.js`. No `dep/s` artifacts exist yet for imported FTX runtime, so deploy generation is deferred.

### Package vs G1/G2 boundary

PASS. G2 imported source is now authoritative for this change.

### Package vs invariants

No live writes, no Home Assistant changes and no production activation.

### Package vs testability and rollback

The guard is simple and can be protected by source-level unittest coverage plus existing tool tests.

## Decision

Continue.

## Notes for human/ChatGPT review

The package sets efficiency to zero when stopped and clears smoothing history while stopped to avoid preserving invalid off-state values.
