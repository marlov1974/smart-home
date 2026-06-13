# P0065 Changelog

## Status

verified-live

## Behavior

The live dampers `brain_v2_13_0` script now uses the P0059/P0060 target-floor behavior:

```text
TARGET_TO_HOUSE_MIN_C = 12.0
no DEWPOINT_SUPPLY_MARGIN_C
no dewPointHouseC addition
```

Live verification produced:

```text
target_to_house_c = 13.0
```

This confirms the live brain can now go below the previous `14 C` floor when the calculated dewpoint limit permits it.

Changed:

- `src/mac/tools/shelly_live/core.py`
- `tests/mac/tools/shelly_live/test_core.py`
- `docs/functions/mac/shelly-live-deploy-tool.md`
- `docs/functions/00-index.md`
- P0065 package definition and evidence

## Verification

```text
python3 -m unittest tests.mac.tools.shelly_live.test_core
python3 -m unittest tests.mac.shelly_ftx.test_dewpoint_margin tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac
git diff --check
```

## Live Actions

Target:

```text
http://192.168.86.240:8030
shellypro1pm-8813bfd99f54
```

Performed:

- uploaded `brain_v2_13_0` to existing script id `7`
- started `brain_v2_13_0` once
- brain wrote normal intent outputs to the existing FTX intent contracts
- brain wrote number `204 = 13`

Not performed:

- no executor upload/start
- no state upload/start
- no direct switch/relay/output writes by the Mac tool
- no Home Assistant changes

## Final Live State

```text
master_v1_8_0 running=true
telemetry_publisher_dampers_v0_2_0 running=true
brain_v2_13_0 running=false
state_v1_8_0 running=false
executor_dampers_v0_2_0 running=false
Number 204 = 13
VVX intent target_to_house_c = 13
```

## Uncertainty

The existing live master script attempted to start brain while the package-triggered brain run was active. The final state remained healthy and `brain DON` was observed.

## Knowhow Promotion

Skipped. P0063 already promoted the reusable lesson about comparing live script state before/after because master scripts can start/stop scripts during verification.
