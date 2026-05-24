# Shelly Supply UNI Publisher Function Catalog

## Scope

P0016 supply UNI telemetry publisher/refresher proof.

Runtime files:

- `src/shelly/supply_uni/supply_uni_pub.js`
- `src/shelly/supply_uni/supply_uni_refresh.js`

Runtime scripts:

- `supply_uni_pub`
- `supply_uni_refresh`

KVS contract:

- `tele.supply_uni`

## Safety Contract

The publisher reads only local supply UNI status and writes one remote KVS key on dampers:

```text
tele.supply_uni
```

It does not call switch, relay, cover, output or device-configuration methods. It does not implement a central poller and does not read other FTX devices.

The refresher stops and starts only `supply_uni_pub`, then stops itself. P0016 does not implement hourly scheduling.

## Functions

### parseSupplyStatus()

Status: active

Owner/runtime:
- Shelly / supply UNI

Source:
- `src/shelly/supply_uni/supply_uni_pub.js`

Purpose:
- Parse local `Shelly.GetStatus` into the compact `tele.supply_uni` snapshot.

Inputs:
- Local status object.

Outputs:
- Snapshot object with `t`, `supply_pa`, `outdoor`, `post_vvx`, `to_outdoor`, `supply_rpm`.

Side effects:
- None.

Tests:
- Mac fixture parser tests mirror the expected component fields.
- Live P0016 verification reads final KVS output.

Introduced:
- P0016

Last changed:
- P0016

### changedEnough()

Status: active

Owner/runtime:
- Shelly / supply UNI

Source:
- `src/shelly/supply_uni/supply_uni_pub.js`

Purpose:
- Decide whether a complete snapshot should be published compared with the last successful snapshot.

Inputs:
- Current snapshot and previous successful snapshot.

Outputs:
- Boolean.

Side effects:
- None.

Thresholds:
- `supply_pa`: 10 Pa
- `outdoor`: 1.0 C
- `post_vvx`: 1.0 C
- `to_outdoor`: 1.0 C
- `supply_rpm`: 100 RPM

Introduced:
- P0016

Last changed:
- P0016

### writeRemoteSnapshot()

Status: active

Owner/runtime:
- Shelly / supply UNI

Source:
- `src/shelly/supply_uni/supply_uni_pub.js`

Purpose:
- Write the complete supply UNI snapshot to dampers with remote JSON-RPC `KVS.Set`.

Inputs:
- Snapshot object and callback.

Outputs:
- Callback success boolean.

Side effects:
- Performs `HTTP.POST` to `http://192.168.77.30/rpc` for `KVS.Set`.

Introduced:
- P0016

Last changed:
- P0016

### tick()

Status: active

Owner/runtime:
- Shelly / supply UNI

Source:
- `src/shelly/supply_uni/supply_uni_pub.js`

Purpose:
- Run one publisher cycle with overlap guard, local status read, parse, delta decision and optional publish.

Inputs:
- None.

Outputs:
- None.

Side effects:
- Calls local `Shelly.GetStatus`.
- May write `tele.supply_uni` remotely.
- Updates RAM `lastSent` only after successful write.
- Writes concise debug logs.

Introduced:
- P0016

Last changed:
- P0016

### runRefresh()

Status: active

Owner/runtime:
- Shelly / supply UNI

Source:
- `src/shelly/supply_uni/supply_uni_refresh.js`

Purpose:
- Restart `supply_uni_pub` so it sends a fresh initial snapshot.

Inputs:
- None.

Outputs:
- None.

Side effects:
- Calls `Script.Stop` and `Script.Start` only for `supply_uni_pub`.
- Stops `supply_uni_refresh` after completion.

Introduced:
- P0016

Last changed:
- P0016
