# P0062 Design

## Interpretation

The G2 source should not contain any VVX efficiency path that can report a temperature-derived efficiency when VVX is not running.

## Implementation

Update `applyVvxEfficiencyFeature(ctx, cb)` in `src/shelly/ftx/state/feature-vvx-efficiency.js`.

When `!ctx.run || !ctx.run.vvx`:

- write `{r0:0,r1:0,r2:0}` to `ftx.state.hist`
- write `0` to `number:202`
- call the callback
- return without calling the running VVX formula

Keep the existing formula and history smoothing unchanged when VVX runs.

## Test Strategy

Extend `tests/mac/shelly_ftx/test_vvx_efficiency.py` so it checks both:

- current recipe path: `perf-vvx.js`
- legacy duplicate path: `feature-vvx-efficiency.js`

## Risks

The live runtime may still have an older deployed script. This package does not deploy.
