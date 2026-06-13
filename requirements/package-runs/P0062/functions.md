# P0062 Function Design

## Changed Functions

### applyVvxEfficiencyFeature(ctx, cb)

File:

```text
src/shelly/ftx/state/feature-vvx-efficiency.js
```

Purpose:

Legacy state path for calculating and writing VVX efficiency.

Inputs:

- `ctx.run.vvx`
- `ctx.telM`
- existing persisted history under `ftx.state.hist`

Outputs:

- persisted history under `ftx.state.hist`
- Shelly virtual number `202` VVX efficiency

Side effects:

- KVS write
- component number write

Change:

If VVX is not running, write zero history and number value `0` without calculating raw temperature efficiency.

Reason:

Keep all G2 state implementations aligned with the operator rule that VVX efficiency is `0` when VVX is off.

## New Functions

None.

## Removed Functions

None.

## Test Coverage

Source-level tests verify the stopped-VVX guard exists before the running formula in both state paths.
