# P0065 Implementation Design

## Package Interpretation

Deploy the G2 FTX brain recipe to dampers so the live brain no longer adds a dewpoint safety margin and uses the `12.0 C` absolute minimum supply floor.

## Implementation Structure

- Extend `shelly_live` with `brain_v2_13_0` allowlist support.
- Reuse the P0063 FTX recipe builder for `src/shelly/ftx/recipes/brain.json`.
- Add `deploy-ftx-brain` CLI command.
- Verify code before upload and after live readback.
- Start brain once and verify `brain DON`.

## Intended Changes

The deploy tool should:

1. verify dampers identity
2. build brain recipe
3. reject stale brain code
4. upload `brain_v2_13_0` to script id 7
5. start it once
6. verify live code and local intent output

## Test Strategy

- Add unit tests for deploy sequence and stale-code rejection.
- Run focused `shelly_live` tests.
- Run focused dewpoint/source tests.
- Run full `tests/mac` discovery.

## Risks

- Brain writes intents by design. This package explicitly allows the existing brain output path.
- Live physical behavior may change immediately because the corrected brain can allow lower cooling supply target when dewpoint permits it.
- Master script may also run brain periodically; final script state should be reported from live `Script.List`.
