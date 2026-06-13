# P0065 Live deploy FTX brain target floor

## Goal

Deploy the current G2 FTX brain script to dampers so the live runtime uses:

```text
TARGET_TO_HOUSE_MIN_C = 12.0
no extra dewpoint supply margin
```

## Background

P0059 removed the extra dewpoint margin in G2 source only. P0060 changed the absolute minimum supply target floor from `14.0 C` to `12.0 C` in G2 source only. Live `brain_v2_13_0` still contains:

```js
var TARGET_TO_HOUSE_MIN_C = 14.0;
var DEWPOINT_SUPPLY_MARGIN_C = 1.0;
ctx.sig.min_supply_temp_c = d1(max2(dewPointHouseC + DEWPOINT_SUPPLY_MARGIN_C, TARGET_TO_HOUSE_MIN_C));
```

P0065 deploys the corrected G2 brain recipe to the verified dampers endpoint.

## Scope

Allowed repository changes:

- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `docs/functions/**`
- package-run evidence under `requirements/package-runs/P0065/**`

Allowed live target:

- `ftx-dampers`
- physical id suffix `8813bfd99f54`
- current reachable endpoint `http://192.168.86.240:8030/`

Allowed live writes:

- upload code to existing script `brain_v2_13_0`
- start `brain_v2_13_0` once for verification
- writes performed by `brain_v2_13_0` itself:
  - `Number.Set` for number `204` (`Target to house`)
  - local KVS write for `ftx.intent.dev.dmp`
  - remote KVS intent writes to the existing FTX device intent keys for supply, extract, heat, cool and vvx
  - forced-mode state writes already present in brain runtime

Forbidden live actions:

- no executor upload/start
- no state script upload/start
- no direct switch/relay/output writes by the Mac tool
- no G1 repository edits
- no Home Assistant changes

## Required Verification

Before live deploy:

- verify dampers identity.
- verify built brain script contains `TARGET_TO_HOUSE_MIN_C = 12.0`.
- verify built brain script does not contain `DEWPOINT_SUPPLY_MARGIN_C` or `dewPointHouseC +`.

After live deploy:

- observe `brain DON`.
- read back live `brain_v2_13_0` code with `Script.GetCode`.
- verify live code contains `TARGET_TO_HOUSE_MIN_C = 12.0`.
- verify live code does not contain `DEWPOINT_SUPPLY_MARGIN_C` or `dewPointHouseC +`.
- read back local `ftx.intent.dev.dmp` as proof the brain completed its normal output path.
- run relevant unit tests.
- run `git diff --check`.

## Commit/Push Authorization

If verification passes and the diff is inside package scope, this package authorizes commit and push.
