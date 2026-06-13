# Package P0060 Implementation Design

## Package

`P0060`

## Package interpretation

Set the FTX brain's absolute minimum supply target floor to `12.0 C`.

## Chosen implementation structure

Change the `TARGET_TO_HOUSE_MIN_C` constant in:

```text
src/shelly/ftx/brain/feature-target.js
```

Update source-level test expectations and docs/memory that mention the floor.

## Intended changes

### Files/modules to change

- `src/shelly/ftx/brain/feature-target.js`
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- package-run evidence

### Files/modules intentionally not changed

- `src/shelly/ftx/brain/feature-thermal.js`
- `dep/s/**`
- live devices
- Home Assistant config

## Refactoring decisions

No refactor. This is a direct constant change.

## Test strategy

Update `test_dewpoint_margin.py` to assert:

- `TARGET_TO_HOUSE_MIN_C = 12.0`
- old `14.0` floor is absent
- no dewpoint margin is reintroduced

Run the P0058 VVX regression and Mac tool tests.

## Build / generated artifact strategy

No deploy artifacts are generated in P0060.

## Risks and uncertainties

- Source-level tests do not execute Shelly JS on target hardware.
- The live runtime will remain unchanged until a later deploy package.

## Design deviations during implementation

None yet.
