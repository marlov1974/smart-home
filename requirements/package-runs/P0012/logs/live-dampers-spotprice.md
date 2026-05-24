# P0012 Live Dampers Spotprice Evidence

## Target

```text
endpoint: http://192.168.86.240:8030
device:   ftx-dampers / dampers lab device
script:   spotprice_v0_9_0
```

## Live Command

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

## Attempt Results

### Attempt 1

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: bad_count
```

Read-only diagnostics:

```text
hp.price.status = bad_count
hp.price.area = missing
spotprice_v0_9_0 was still running until manually stopped
```

Mac-side check of the attempted tomorrow URL:

```text
https://www.elprisetjustnu.se/api/v1/prices/2026/05-25_SE3.json
404: Data not found or not ready yet
```

### Attempt 2

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: fetching
```

Read-only diagnostics:

```text
spotprice_v0_9_0 running=false
hp.price.status = fetching
hp.price.area = missing
script:1 errors=["out_of_memory"]
```

### Attempt 3

```text
error: spotprice KVS verification timed out: spotprice KVS status is not ok: fetching
```

Read-only diagnostics:

```text
spotprice_v0_9_0 running=false
hp.price.status = fetching
hp.price.area = missing
script:1 errors=["out_of_memory"]
Script.Stop?id=1 -> {"was_running":false}
```

## Boundary Check

Observed Mac tool actions were limited to:

- `Shelly.GetStatus`
- `Script.List`
- `Script.Stop` for `spotprice_v0_9_0`
- `Script.Create` or reuse for `spotprice_v0_9_0`
- `Script.PutCode` for `spotprice_v0_9_0`
- `Script.Start` for `spotprice_v0_9_0`
- `/debug/log` read
- `KVS.Get` for corrected spotprice keys

Read-only diagnostics additionally used `KVS.Get`, `Script.List`, `Shelly.GetStatus` and `Script.Stop?id=1` to verify/stop the allowed test script.

No device settings, actuator/output, relay, cover, switch, component, Wi-Fi, network, MQTT, Bluetooth or cloud operations were performed by the P0012 Mac tool.

## Final Live State

```text
spotprice_v0_9_0 installed
spotprice_v0_9_0 stopped
hp.price.status = fetching
hp.price.area missing
```
