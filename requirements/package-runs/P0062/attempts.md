# P0062 Attempts

## Attempt 1

Status: passed.

Finding:

P0058 fixed the current recipe path `perf-vvx.js`, but the repository still had a legacy duplicate `feature-vvx-efficiency.js` without the stopped-VVX guard.

Change:

- Added stopped-VVX zero write to `applyVvxEfficiencyFeature()`.
- Extended source tests to cover both current and legacy VVX efficiency paths.

Verification:

```text
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
Ran 2 tests
OK

python3 -m unittest discover tests/mac
Ran 100 tests
OK
```

Live actions:

None.

## Remaining Live Risk

Home Assistant may still show nonzero live values until a later package builds and deploys the corrected G2 state script to the Shelly runtime.
