# P0062 Changelog

## Status

verified

## Behavior

The legacy duplicate VVX efficiency source path now also reports `0` when VVX is not running.

Changed:

- `src/shelly/ftx/state/feature-vvx-efficiency.js`
- `tests/mac/shelly_ftx/test_vvx_efficiency.py`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- P0062 package evidence

## Verification

```text
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac
git diff --check
```

Results:

```text
2 focused VVX tests passed.
100 remaining Mac tests passed.
git diff --check passed.
```

## Live Actions

None.

## Known Limitation

P0062 does not deploy to Shelly. If Home Assistant is reading a live script that predates P0058/P0062, the live VVX efficiency value can remain nonzero until a deploy package updates the active state script.

## Knowhow Promotion

Skipped. The reusable lesson is package-local for FTX source-path consistency rather than a new global runtime/tooling rule.
