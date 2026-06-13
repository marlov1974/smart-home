# Package P0058 Function Design

## Package

`P0058`

## Scope

FTX state runtime VVX efficiency calculation.

## New functions

None.

## Changed functions

### calcVvxEfficiencyFeature(ctx, hist)

Current purpose:
- Calculate smoothed VVX efficiency from telemetry and store it on `ctx` for output.

Change:
- Add an early stopped-run guard.
- If `ctx.run.vvx` is false, set `ctx.vvx_eff_pct = 0` and `ctx.vvx_eff_hist = {r0: 0, r1: 0, r2: 0}`.
- If `ctx.run.vvx` is true, keep existing calculation behavior.

Inputs changed:
- No signature change.
- Existing `ctx.run.vvx` is now used.

Outputs changed:
- `ctx.vvx_eff_pct` is guaranteed to be `0` when VVX is not running.
- `ctx.vvx_eff_hist` is zeroed when VVX is not running.

Side effects changed:
- Existing `writeVvxEfficiencyFeature()` will write zero history while VVX is stopped.

Reason:
- Temperature-only efficiency math is misleading when VVX is off, especially during active cooling.

Tests:
- `tests/mac/shelly_ftx/test_vvx_efficiency.py`

## Removed functions

None.

## Important unchanged functions

### calcVvxEfficiencyRaw(telM)

Reason for no change:
- Existing four-temperature formula remains the running-state calculation.

### applyVvxRun(ctx)

Reason for no change:
- Existing run definition already represents stopped/running based on switch and power.

### writeVvxEfficiencyFeature(ctx, cb)

Reason for no change:
- It already writes `ctx.vvx_eff_pct`; the upstream feature now guarantees the stopped value is zero.

## Design deviations during implementation

None yet.
