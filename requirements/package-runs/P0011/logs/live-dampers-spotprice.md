# P0011 Live Dampers Spotprice Evidence

## Command

```bash
python3 -m src.mac.tools.shelly_live deploy-spotprice --base-url http://192.168.86.240:8030/ --script build/shelly/spotprice/spotprice_v0_9_0.js --expect spotprice --upload-chunk-bytes 1500 --log-timeout 30 --kvs-timeout 30
```

## Target

```text
endpoint: http://192.168.86.240:8030
device:   ftx-dampers / dampers lab device
script:   spotprice_v0_9_0
```

## Result

```text
target=http://192.168.86.240:8030
script=spotprice_v0_9_0 id=1
cleaned_hello=false
upload_chunk_bytes=1500
upload_chunk_count=6
before_scripts=[{"id":1,"name":"spotprice_v0_9_0","enable":false,"running":true}]
after_scripts=[{"id":1,"name":"spotprice_v0_9_0","enable":false,"running":false}]
```

`hello_v1_0_0` was already absent. `spotprice_v0_9_0` was present from the first attempt and was replaced by chunked upload.

## KVS Evidence

Allowed keys read:

```text
hp.price.2h
hp.price.date
hp.price.status
hp.price.updated
hp.price.source
hp.price.debug
hp.price.debug.len
```

Safe summary:

```json
{"date":"2026-05-25","debug_len":"0","price_count":12,"price_max":5.8,"price_min":3.2,"source":"fallback","status":"no_token","updated":"2026-05-24T00:57:21"}
```

Values:

```json
{"hp.price.2h":"3.2,3.3,4.1,5.8,5.1,3.9,3.4,4.0,5.1,5.1,4.1,3.4","hp.price.date":"2026-05-25","hp.price.debug":"no_token ","hp.price.debug.len":"0","hp.price.source":"fallback","hp.price.status":"no_token","hp.price.updated":"2026-05-24T00:57:21"}
```

The device has no Tibber token in `text:201`, so the script followed the documented fallback path. KVS verification passed because the fallback path still wrote a 12-block spotprice series and status/source/date/update metadata.

## Log Excerpt

```text
4301 [May 24 00:58:01.223] I shelly_debug.cpp:236    Streaming logs to 192.168.86.38:50759
4302 [May 24 00:58:01.454] I shos_rpc_inst.c:243     Script.Start [1@] via HTTP_in POST 192.168.86.38:50760
4303 [May 24 00:58:01.455] I shelly_user_script.:203 JS RAM stat: initial: 110156 after: 110120, used: 36
4304 [May 24 00:58:01.456] I shelly_ejs_rpc.cpp:41   Shelly.call Text.GetStatus {"id":201}
4305 [May 24 00:58:01.457] I shelly_user_script.:219 JS RAM stat: after user code: 110156 after: 108612, used: 1544
4306 [May 24 00:58:01.457] I shelly_notification:164 Status change of script:1: {"error_msg":null,"errors":[],"running":true}
4307 [May 24 00:58:01.458] I shos_rpc_inst.c:243     Text.GetStatus [2699@RPC.LOCAL] via loopback 
4308 [May 24 00:58:01.601] I spotprice_v0_9_0 NO TOKEN
```

## Boundary Check

Observed tool actions were limited to:

- `Shelly.GetStatus`
- `Script.List`
- `Script.Stop` for `spotprice_v0_9_0` when needed
- `Script.Create` or reuse for `spotprice_v0_9_0`
- `Script.PutCode` for `spotprice_v0_9_0`
- `Script.Start` for `spotprice_v0_9_0`
- `/debug/log` read
- `KVS.Get` for documented spotprice keys

The deployed script performed:

- `Text.GetStatus` for Tibber token text id `201`
- `KVS.Set` only for documented spotprice-owned keys

No device settings, actuator/output, relay, cover, switch, component, Wi-Fi, network, MQTT, Bluetooth or cloud operations were performed by the P0011 Mac tool.

## Final State

`spotprice_v0_9_0` is installed and stopped.
