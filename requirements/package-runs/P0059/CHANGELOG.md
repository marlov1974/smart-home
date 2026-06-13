# Package P0059 Changelog

## Status

verified

## Behavior Change

The FTX brain no longer adds an extra dewpoint safety margin when deriving minimum supply temperature.

Before:

```text
min_supply_temp_c = max(dewpoint_house_c + 1.0 C, 14.0 C)
```

After:

```text
min_supply_temp_c = max(dewpoint_house_c, 14.0 C)
```

The absolute `14.0 C` floor remains unchanged.

## Files Changed

- `src/shelly/ftx/brain/feature-target.js`
- `tests/mac/shelly_ftx/test_dewpoint_margin.py`
- `memory/physical/ftx/cooling-risk.md`
- `docs/functions/shelly/ftx-runtime-baseline.md`
- `docs/functions/00-index.md`
- P0059 package and package-run evidence

## Verification

```text
python3 -m unittest tests.mac.shelly_ftx.test_dewpoint_margin
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac/tools
git diff --check
```

Results:

```text
1 dewpoint margin source test passed
1 VVX efficiency regression test passed
68 Mac tool tests passed
git diff --check passed
```

## Live Actions

None. P0059 did not deploy to Shelly and did not change Home Assistant.

## Known Limitations

- No `dep/s` artifacts were generated.
- The live runtime will not change until a later package builds/deploys this G2 FTX source.

## Bootstrap Hints

For follow-up dewpoint/cooling work, inspect:

- `src/shelly/ftx/brain/feature-target.js`
- `src/shelly/ftx/brain/feature-thermal.js`
- `memory/physical/ftx/cooling-risk.md`
