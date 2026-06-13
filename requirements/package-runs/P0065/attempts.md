# P0065 Attempts

## Attempt 1

Status: passed.

Precheck:

- live dampers `brain_v2_13_0` had `TARGET_TO_HOUSE_MIN_C = 14.0`
- live dampers `brain_v2_13_0` had `DEWPOINT_SUPPLY_MARGIN_C = 1.0`
- G2 source had `TARGET_TO_HOUSE_MIN_C = 12.0`
- G2 source had no `DEWPOINT_SUPPLY_MARGIN_C`

Implementation:

- added `brain_v2_13_0` to `shelly_live` allowlist
- added `deploy-ftx-brain`
- added live code readback via `Script.GetCode`
- added stale-code guard for `TARGET_TO_HOUSE_MIN_C = 12.0`, no `DEWPOINT_SUPPLY_MARGIN_C`, no `dewPointHouseC +`
- added unit tests

Live result:

- deployed `brain_v2_13_0` to dampers script id `7`
- uploaded in `16` RPC chunks
- observed `brain DON`
- verified live code summary: `{"dewpoint_margin_removed":true,"target_to_house_min_c":12.0}`
- read `Number 204 = 13`
- read local dampers intent from `ftx.intent.dev.dmp`
- read VVX intent with `target_to_house_c = 13`

Runtime observation:

- the existing master script attempted to start brain during the package-triggered run
- final `Script.List` showed brain stopped after completion, which matches one-shot self-stop behavior
