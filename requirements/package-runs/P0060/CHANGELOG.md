# Package P0060 Changelog

## Status

verified

## Behavior Change

The FTX brain absolute minimum supply target floor is now `12.0 C`.

Before:

```text
TARGET_TO_HOUSE_MIN_C = 14.0
```

After:

```text
TARGET_TO_HOUSE_MIN_C = 12.0
```

Dewpoint limiting remains direct after P0059:

```text
min_supply_temp_c = max(dewpoint_house_c, TARGET_TO_HOUSE_MIN_C)
```

## Files Changed

- `src/shelly/ftx/brain/feature-target.js`
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- P0060 package and package-run evidence

## Verification

```text
python3 -m unittest tests.mac.shelly_ftx.test_dewpoint_margin
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac/tools
git diff --check
```

Results:

```text
1 dewpoint/source floor test passed
1 VVX efficiency regression test passed
68 Mac tool tests passed
git diff --check passed
```

## Live Actions

None. P0060 did not deploy to Shelly and did not change Home Assistant.

## Known Limitations

- No `dep/s` artifacts were generated.
- The live runtime will not change until a later package builds/deploys this G2 FTX source.

## Bootstrap Hints

For follow-up cooling floor work, inspect:

- `src/shelly/ftx/brain/feature-target.js`
- `src/shelly/ftx/brain/feature-thermal.js`
- `memory/physical/ftx/cooling-risk.md`
