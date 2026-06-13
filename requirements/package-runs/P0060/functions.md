# Package P0060 Function Design

## Package

`P0060`

## Scope

FTX brain target lower-bound calculation.

## New functions

None.

## Changed functions

### calcTarget(ctx)

Current purpose:
- Calculates house target, house dewpoint, minimum allowed supply temperature and initial target-to-house signals.

Change:
- Its lower clipping constant `TARGET_TO_HOUSE_MIN_C` changes from `14.0` to `12.0`.

Inputs changed:
- None.

Outputs changed:
- `ctx.sig.min_supply_temp_c` and `ctx.sig.target_to_house_c` may now be clipped at `12.0 C` instead of `14.0 C` when dewpoint does not impose a higher limit.

Side effects changed:
- Downstream cooling target clipping may allow lower supply targets.

Reason:
- Operator requested a lower absolute floor after validating the previous cooling constraints were too conservative.

Tests:
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`

## Removed functions

None.

## Important unchanged functions

### calcDewPointC(tempC, rhPct)

Reason for no change:
- Dewpoint formula remains unchanged.

### calcThermal(ctx)

Reason for no change:
- It consumes `ctx.sig.min_supply_temp_c`; no structural thermal control change is needed.

## Design deviations during implementation

None yet.
