# P0065 Review

## Classification

WARN

## Evidence

- G2 source has `TARGET_TO_HOUSE_MIN_C = 12.0`.
- G2 source has no `DEWPOINT_SUPPLY_MARGIN_C` in `src/shelly/ftx/brain/feature-target.js`.
- Live dampers `brain_v2_13_0` still has `TARGET_TO_HOUSE_MIN_C = 14.0`.
- Live dampers `brain_v2_13_0` still has `DEWPOINT_SUPPLY_MARGIN_C = 1.0`.
- Live dampers target identity is `shellypro1pm-8813bfd99f54`.

## Consistency Result

The requested live action is consistent with P0059/P0060 source changes and corrects the live/runtime mismatch.

The package is `WARN` because brain writes runtime intents to multiple FTX devices. The write set is the existing brain output contract and is explicitly allowed by P0065.
