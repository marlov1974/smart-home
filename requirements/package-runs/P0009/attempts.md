# Package P0009 Attempts

## Package

`P0009`

## Attempt 1

Change summary:
- Added generated metadata header and IIFE strict-mode wrapper to the Shelly build tool.
- Added tests for generated header, role/manifest/source metadata, wrapper and strict mode.
- Rebuilt fixture build/deploy artifacts.
- Updated source/build/deploy memory and function catalog.

Tests run:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
```

Result:
- Initial run failed because legacy 70-byte chunk fixture was too small for the new absolute manifest metadata line used by the unit test.

Follow-up:
- Adjusted artificial unit-test chunk limit to 120 bytes while preserving numeric chunk, recipe and reconstruction coverage.

## Attempt 2

Change summary:
- Re-ran tests after chunk-limit test adjustment.
- Rebuilt generated fixture artifacts from the wrapped built script.
- Validated deploy artifacts.

Tests run:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello
```

Result:
- Passed.

## Live Runtime

Not run. P0009 does not allow live testing or live write actions.
