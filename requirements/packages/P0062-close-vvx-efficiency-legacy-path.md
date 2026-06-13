# P0062 - Close VVX efficiency legacy path

## Intent

Make the G2 FTX source unambiguous: reported VVX efficiency must be `0` whenever VVX is not running, across both current and legacy state implementation files.

## Background

P0058 added the run-state guard to the current `perf-vvx.js` path, but did not deploy live code. The operator still sees nonzero VVX efficiency values in Home Assistant when VVX is off.

Inspection after P0058 shows:

- `src/shelly/ftx/recipes/state.json` uses `rt/state/perf-vvx.js`.
- `src/shelly/ftx/state/perf-vvx.js` has the P0058 guard.
- `src/shelly/ftx/state/feature-vvx-efficiency.js` is a legacy duplicate and still lacks the guard.

## Scope

- Add the same stopped-VVX zero guard to the legacy `feature-vvx-efficiency.js` path.
- Strengthen tests so both paths are checked.
- Update FTX function docs and package evidence.

## Non-goals

- No live Shelly deploy.
- No Home Assistant writes.
- No production activation.
- No change to VVX run detection thresholds.
- No change to the running-VVX efficiency formula.

## Verification

```bash
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac
git diff --check
```

## Deployment Note

This package is commit/push only. Live values will not change until the corrected G2 state script is built and deployed in a later package that explicitly authorizes live writes.
