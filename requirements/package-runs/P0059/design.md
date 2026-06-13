# Package P0059 Implementation Design

## Package

`P0059`

## Package interpretation

Remove the extra dewpoint safety margin from FTX supply target limiting while preserving the absolute minimum supply floor.

## Chosen implementation structure

Change `calcTarget(ctx)` in `src/shelly/ftx/brain/feature-target.js`:

```text
max2(dewPointHouseC + DEWPOINT_SUPPLY_MARGIN_C, TARGET_TO_HOUSE_MIN_C)
```

becomes:

```text
max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C)
```

Remove the now-unused `DEWPOINT_SUPPLY_MARGIN_C` constant.

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
- `src/shelly/ftx/brain/feature-ventilation.js`
- `dep/s/**`
- live devices
- Home Assistant config

## Refactoring decisions

No refactor. This is a direct formula simplification.

## Test strategy

Add a source-level unittest verifying:

- no `DEWPOINT_SUPPLY_MARGIN_C`
- no `dewPointHouseC +` in the `min_supply_temp_c` assignment
- `TARGET_TO_HOUSE_MIN_C = 14.0` remains
- direct `max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C)` is used

Run P0058 VVX test and existing Mac tool tests as regression coverage.

## Build / generated artifact strategy

No deploy artifacts are generated in P0059.

## Risks and uncertainties

- Source-level tests do not execute Shelly JS on a Shelly runtime.
- Physical assumption is operator-tested for current installation. Future duct insulation/placement changes may require revisiting condensate constraints.

## Design deviations during implementation

None yet.
