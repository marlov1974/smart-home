# Package P0008 Attempts

## Package

`P0008`

## Attempt 1

### Goal

Implement deterministic Shelly source/build/deploy tooling, fixture, generated artifacts and tests.

### Implementation summary

Created:

- `src/mac/tools/shelly_build/`
- `tests/mac/tools/shelly_build/`
- `src/shelly/fixture/`
- `build/shelly/fixture/hello.js`
- `dep/s/ch/hello/01.js`
- `dep/s/rec/hello.json`
- `docs/functions/mac/shelly-build-tool.md`

### Issue found

Initial build command failed on Python 3.9 because `Path.write_text(..., newline="\n")` is not supported.

### Fix

Changed the internal `_write_text()` helper to use `Path.open("w", encoding="utf-8", newline="\n")`.

### Verification

Passed:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello
git diff --check
```

Observed outputs:

```text
Ran 7 tests in 0.031s
OK
built hello: 1 chunks
valid hello
```

### Live testing

Not run. P0008 does not allow live testing or live write actions.

### Result

PASS.
