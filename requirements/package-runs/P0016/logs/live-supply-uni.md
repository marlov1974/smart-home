# P0016 Live Supply UNI Evidence

## Command

```bash
python3 -m src.mac.tools.shelly_live deploy-supply-uni --supply-base-url http://192.168.86.240:8020/ --dampers-base-url http://192.168.86.240:8030/ --publisher-script build/shelly/supply_uni/supply_uni_pub.js --refresher-script build/shelly/supply_uni/supply_uni_refresh.js --log-timeout 30 --kvs-timeout 30 --http-timeout 5
```

## Identity

```text
supply_target=http://192.168.86.240:8020
dampers_target=http://192.168.86.240:8030
supply_device_id=shellyplusuni-e08cfe8c1d18
dampers_device_id=shellypro1pm-8813bfd99f54
```

## Supply Status Summary

```json
{"outdoor":20.6,"post_vvx":20.4,"supply_pa":341,"supply_rpm":2316,"to_outdoor":22.8}
```

## Upload Evidence

```text
publisher_script=supply_uni_pub id=1
refresher_script=supply_uni_refresh id=2
upload_chunk_bytes=1500
publisher_upload_chunk_count=3
refresher_upload_chunk_count=2
```

## Final Script State

```json
[
  {"id":1,"name":"supply_uni_pub","enable":false,"running":true},
  {"id":2,"name":"supply_uni_refresh","enable":false,"running":false}
]
```

`supply_uni_pub` is intentionally left running as the P0016 proof artifact.

## KVS Readback

Key:

```text
tele.supply_uni
```

Value:

```json
{"outdoor":20.6,"post_vvx":20.4,"supply_pa":342,"supply_rpm":2316,"t":1779644164,"to_outdoor":22.8}
```

Validated summary:

```json
{"outdoor":20.6,"post_vvx":20.4,"supply_pa":342,"supply_rpm":2316,"t":1779644164,"to_outdoor":22.8}
```

## Log Excerpts

Publisher:

```text
supply_uni_pub BOT
supply_uni_pub READ pa=342 rpm=2316
Shelly.call HTTP.POST {"url":"http://192.168.77.30/rpc","body":"{\"id\":1,\"method\":\"KVS.Set\",\"params\":{\"key\":\"tele.supply_uni\",\"value\":{\"t\":1779644164,\"supply_pa\":342,\"outdoor\":20.6,\"post_vvx\":20.4,\"to_outdoor\":22.8,\"supply_rpm\":2316}}}","headers":{"Content-Type":"application/json"},"timeout":5}
HTTP POST http://192.168.77.30/rpc
Finished; bytes 214, code 200, redir 0/3, auth 0, status OK
supply_uni_pub PUB OK pa=342 rpm=2316
```

Refresher:

```text
supply_uni_refresh BOT
supply_uni_refresh STOP PUB
Shelly.call Script.Stop {"id":1}
supply_uni_refresh START PUB
Shelly.call Script.Start {"id":1}
supply_uni_pub BOT
supply_uni_refresh DONE
```

## Forbidden Operation Review

Observed live operations stayed inside the P0016 allowlist:

- supply UNI identity/status/script/log operations
- script create/update/start for `supply_uni_pub` and `supply_uni_refresh`
- `supply_uni_refresh` stop/start of only `supply_uni_pub`
- publisher remote `KVS.Set` only for `tele.supply_uni` on dampers
- dampers KVS readback

No actuator/output/switch/relay/cover/device-config/Home Assistant/G1 production operations were performed.
