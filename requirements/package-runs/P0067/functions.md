# P0067 Function Design

## Changed Test Helpers

No runtime functions are added, changed or removed.

The existing HA dashboard unit test module is extended with path constants and assertions for the new SVG asset:

- Purpose: verify source/deploy equality and SVG validity.
- Inputs: tracked SVG files.
- Outputs: unittest pass/fail.
- Side effects: none.
- Reason: keep Home Assistant deploy asset synchronized with source.
- Coverage: `python3 -m unittest tests.mac.ha.test_ftx_dashboard`.

## Durable Function Catalog

No `docs/functions/` update is required because no production function or reusable runtime API is added.
