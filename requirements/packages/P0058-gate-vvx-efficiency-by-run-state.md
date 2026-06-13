# Package P0058: gate VVX efficiency by run state

## Status
verified

## Package order
P0058

## Primary area
G2 / Shelly / FTX

## Label
G2-KANDIDAT

## Decision summary

VVX efficiency must be `0` when `vvx.run=0`.

P0057 imported the current G1 FTX runtime as the G2 baseline. P0058 changes that baseline so the state runtime no longer reports a calculated VVX efficiency when the VVX rotor is not running.

## Solution model

The FTX state loop already derives `ctx.run.vvx` before performance calculations:

```text
applyVvxRun(ctx)
calcVvxEfficiencyFeature(ctx, hist)
```

P0058 adds a run-state guard to `calcVvxEfficiencyFeature()`.

When `ctx.run.vvx` is false:

- `ctx.vvx_eff_pct = 0`
- `ctx.vvx_eff_hist = {r0: 0, r1: 0, r2: 0}`
- `number:202 VVX efficiency` is written as `0` by the existing output function
- invalid/off-state raw temperature math does not remain in the smoothing history

When `ctx.run.vvx` is true, the existing four-temperature efficiency calculation remains unchanged.

## Current behavior

The imported baseline calculates VVX efficiency from temperatures regardless of whether VVX is running. During cooling with VVX off, active cooling can make the formula report a nonzero efficiency.

## Problem

The operator observed VVX off with active cooling and an efficiency around 50 percent. This is misleading because the VVX rotor was not running.

## Target behavior

If `vvx.run=0`, reported VVX efficiency is `0`.

## Non-goals

- No live Shelly deploy.
- No Home Assistant change.
- No change to VVX on/off control logic.
- No rewrite of the efficiency formula when VVX is running.
- No deploy artifact generation.

## Invariants

- Keep the change package-scoped.
- Do not read or edit G1.
- Do not perform live writes.
- Shelly devices must still not fetch from `src/`.

## Knowledge updates

- Update `docs/functions/shelly/ftx-runtime-baseline.md`.
- Add package-run evidence.

## Implementation updates

- Change `src/shelly/ftx/state/perf-vvx.js`.
- Add focused test coverage for the source guard.

## Files to inspect

- `requirements/package-runs/P0057/CHANGELOG.md`
- `src/shelly/ftx/state/main.js`
- `src/shelly/ftx/state/run-process.js`
- `src/shelly/ftx/state/perf-vvx.js`
- `docs/functions/shelly/ftx-runtime-baseline.md`

## Files allowed to change

- `requirements/packages/P0058-gate-vvx-efficiency-by-run-state.md`
- `requirements/package-runs/P0058/**`
- `src/shelly/ftx/state/perf-vvx.js`
- `tests/mac/shelly_ftx/**`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`

## Forbidden changes

- No G1 repository changes.
- No live Shelly writes.
- No Home Assistant writes.
- No unrelated source, deploy or memory changes.

## Pre-implementation consistency review

Codex must write:

```text
requirements/package-runs/P0058/review.md
```

## Implementation design policy

Codex must write:

```text
requirements/package-runs/P0058/design.md
```

## Function design policy

Codex must write:

```text
requirements/package-runs/P0058/functions.md
```

## Live test/debug policy

Live testing allowed:
no

Live write actions allowed:
no

Shelly log capture required:
no

Max implementation/debug attempts:
1

## Evidence and learning policy

Package evidence belongs under:

```text
requirements/package-runs/P0058/
```

## Test cases

### TC1: stopped VVX reports zero
Given `ctx.run.vvx=0`
When `calcVvxEfficiencyFeature()` runs
Then `ctx.vvx_eff_pct` is set to `0`.

### TC2: stopped VVX clears invalid smoothing history
Given `ctx.run.vvx=0`
When `calcVvxEfficiencyFeature()` runs
Then `ctx.vvx_eff_hist` is `{r0:0,r1:0,r2:0}`.

### TC3: running VVX keeps existing formula
Given `ctx.run.vvx=1`
When `calcVvxEfficiencyFeature()` runs
Then the existing `calcVvxEfficiency()` path remains used.

## Verification commands

```bash
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac/tools
git diff --check
```

## Runtime health checks

Not applicable; no live runtime changes are allowed.

## Deployment plan

Commit and push only. This package does not authorize deploy or production activation.

## Rollback plan

Rollback is a later forward-moving package that changes the efficiency gate behavior again.
