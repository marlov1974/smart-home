# Shelly Knowhow

Durable Shelly lessons learned from G2 packages, live tests and package reviews.

This file is for general reusable knowledge, not raw package logs.

## Current baseline

### Use bounded log capture

When streaming Shelly logs during live testing, use bounded capture so the process does not hang indefinitely.

Mac-compatible example:

```bash
perl -e 'alarm shift; exec @ARGV' 60 curl -N http://192.168.86.240:8040/debug/log
```

### Treat log streaming as read-only diagnostics

Opening `/debug/log` is diagnostic observation. It does not itself change device state.

Starting/stopping scripts, writing KVS, uploading scripts, changing components or changing actuators are live actions and require explicit package permission.

### Log final outcome honestly

Shelly one-shot scripts should make the final log line reflect the true outcome.

Use a success marker such as:

```text
DONE
```

only after the script's critical work has succeeded.

If a critical write or verification step fails, log a distinct terminal state before self-stop, for example:

```text
DONE_WITH_ERROR
KVS_ERR_DONE
FALLBACK_DONE
```

The exact marker may be package-specific, but it must not make a failed KVS write, failed parse, fallback-only result or partial result look like a clean success.

This is especially important for one-shot scripts that self-stop after writing KVS. A script may still self-stop safely after failure, but its logs and package evidence must distinguish safe termination from successful output.

### Keep Shelly HTTP payloads small

P0012 showed that fetching and parsing a large spot-price JSON object list on Shelly can cause memory pressure, including `out_of_memory` and a stuck/failing runtime before KVS output is written.

P0013 verified a safer pattern for Shelly-hosted HTTP runtimes:

- prefer compact upstream payloads designed for small clients
- prefer endpoints that return only the values needed by the Shelly script
- avoid large object-list responses when a compact array is available
- avoid retaining large response strings after parsing
- avoid large intermediate arrays and diagnostic strings
- write compact final KVS values only
- verify live logs for memory errors, stuck states and missing final KVS output

For spot price specifically, the verified G2 low-memory source model is:

```text
https://se.elpris.eu/api/v1/prices/YYYY/MM-DD_SE3.json?avg24
```

The compact `avg24` response lets the Shelly runtime parse hourly values and reduce them to 12 two-hour values with low heap pressure.

### Do not assume `JSON.parse` is safe for large responses

`JSON.parse` may be acceptable for small compact payloads after live verification, but large responses should be treated as unsafe until proven otherwise on the target Shelly hardware.

When a package introduces Shelly-side HTTP parsing, Codex must document the payload size/shape assumption and verify runtime health during live testing if live testing is allowed.

### Separate Mac deploy chunks from repo deploy chunks

Mac direct deploy uses temporary in-memory RPC upload chunks to send one complete built script with `Script.PutCode`.

Repo deploy chunks under `dep/s/ch/**` are generated artifacts for a possible Shelly-side pull/install model. They must not be treated as the source for Mac direct deploy unless a future package explicitly changes that model.

### Shelly-to-Shelly KVS publish can use HTTP.POST JSON-RPC

P0016 verified a Shelly Plus UNI script can publish a compact telemetry object to another Shelly on the local Shelly network by calling:

```text
HTTP.POST http://<target-ip>/rpc
{"id":1,"method":"KVS.Set","params":{"key":"tele.supply_uni","value":{...}}}
```

The verified case was `ftx-supply-uni` writing `tele.supply_uni` to dampers at `192.168.77.30`. The response completed with HTTP 200 and the value was readable from dampers KVS.

Use this pattern only for explicitly allowed KVS contracts. Do not generalize it to actuator, device configuration, network, MQTT, Bluetooth, cloud or component writes without a package that explicitly allows and verifies those actions.

## Future promoted lessons

Promote repeated or important package observations here, for example:

- RPC sequencing issues
- timer/concurrency behavior
- heap/memory thresholds
- KVS size/shape limits
- script runtime duration concerns
- WebSocket/logging side effects
- installer/deploy edge cases
