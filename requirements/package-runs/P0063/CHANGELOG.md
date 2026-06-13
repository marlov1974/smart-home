# P0063 Changelog

## Status

verified-live

## Behavior

`state_v1_8_0` can now be deployed from the G2 FTX state recipe to the verified dampers endpoint and verified live.

The live dampers state script was deployed and run once. With `ftx.state.run.vvx = 0`, the live result is:

```text
Number 202 = 0
ftx.state.hist = {"r0":0,"r1":0,"r2":0}
```

Changed:

- `src/mac/tools/shelly_live/core.py`
- `tests/mac/tools/shelly_live/test_core.py`
- `docs/functions/mac/shelly-live-deploy-tool.md`
- `docs/functions/00-index.md`
- `memory/knowhow/shelly.md`
- P0063 package definition and evidence

## Verification

```text
python3 -m unittest tests.mac.tools.shelly_live.test_core
python3 -m unittest tests.mac.shelly_ftx.test_vvx_efficiency
python3 -m unittest discover tests/mac
git diff --check
```

Results:

```text
35 focused shelly_live tests passed.
2 focused FTX VVX tests passed.
102 Mac tests passed.
git diff --check passed.
```

## Live Actions

Target:

```text
http://192.168.86.240:8030
shellypro1pm-8813bfd99f54
```

Performed:

- uploaded `state_v1_8_0` to existing script id `5`
- started `state_v1_8_0` once
- state script wrote its normal aggregate KVS and virtual numbers

Not performed:

- no upload/start for brain scripts
- no upload/start for executor scripts
- no write to `ftx-vvx`

## Final Live State

```text
master_v1_8_0 running=true
telemetry_publisher_dampers_v0_2_0 running=true
state_v1_8_0 running=false
brain_v2_13_0 running=false
executor_dampers_v0_2_0 running=false
Number 202 = 0
ftx.state.run.vvx = 0
ftx.state.hist = {"r0":0,"r1":0,"r2":0}
```

## Uncertainty

The existing live `master_v1_8_0` issued `Script.Stop {"id":7}` during the live log window, leaving `brain_v2_13_0` stopped. P0063 did not directly stop that script and did not restart it because the package scope did not authorize brain actions.

## Knowhow Promotion

Updated `memory/knowhow/shelly.md` with the reusable rule to compare live script state before/after package verification and distinguish tool RPC actions from device-local master-script behavior.
