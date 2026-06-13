# Package P0058 Changelog

## Status

verified

## Behavior Change

VVX efficiency is now reported as `0` when `ctx.run.vvx` is false.

When VVX is not running, `calcVvxEfficiencyFeature()` now:

```text
ctx.vvx_eff_pct = 0
ctx.vvx_eff_hist = {r0:0,r1:0,r2:0}
```

When VVX is running, the existing four-temperature efficiency calculation remains unchanged.

## Files Changed

- `src/shelly/ftx/state/perf-vvx.js`
- `tests/mac/shelly_ftx/test_vvx_efficiency.py`
- `tests/mac/shelly_ftx/__init__.py`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- P0058 package and package-run evidence

## Verification

```text
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac/tools
git diff --check
```

Results:

```text
1 Shelly FTX source test passed
68 Mac tool tests passed
git diff --check passed
```

## Live Actions

None. P0058 did not deploy to Shelly and did not change Home Assistant.

## Known Limitations

- No `dep/s` artifacts were generated.
- The live runtime will not change until a later package builds/deploys this G2 FTX source.

## Bootstrap Hints

For follow-up VVX efficiency work, inspect:

- `src/shelly/ftx/state/perf-vvx.js`
- `src/shelly/ftx/state/run-process.js`
- `docs/functions/shelly/ftx-runtime-baseline.md`
