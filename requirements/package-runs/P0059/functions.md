# Package P0059 Function Design

## Package

`P0059`

## Scope

FTX brain target and condensate/dewpoint minimum supply calculation.

## New functions

None.

## Changed functions

### calcTarget(ctx)

Current purpose:
- Calculates house target, house dewpoint, minimum allowed supply temperature and initial target-to-house signals.

Change:
- Remove the added dewpoint safety margin from `ctx.sig.min_supply_temp_c`.
- Use calculated house dewpoint directly against the absolute minimum floor.

Inputs changed:
- None.

Outputs changed:
- `ctx.sig.min_supply_temp_c` can now be up to `1.0 C` lower in cases where dewpoint controls over the absolute `14.0 C` floor.

Side effects changed:
- Downstream cooling target clipping may allow lower supply targets when dewpoint previously constrained cooling.

Reason:
- Operator physical testing showed the ventilation pipe surface remains warmer than the air in the pipe, so the extra margin is unnecessary.

Tests:
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`

## Removed functions

None.

## Removed constants

### DEWPOINT_SUPPLY_MARGIN_C

Reason:
- No longer needed after removing the added dewpoint margin.

Replacement:
- Direct use of `dewPointHouseC`.

Tests:
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`

## Important unchanged functions

### calcDewPointC(tempC, rhPct)

Reason for no change:
- The dewpoint formula itself remains valid; only the extra margin is removed.

### calcThermal(ctx)

Reason for no change:
- It already consumes `ctx.sig.min_supply_temp_c`; the upstream signal changes without altering thermal control structure.

## Design deviations during implementation

None yet.
