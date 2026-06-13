# P0065 Live Dampers FTX Brain Deploy

Target:

```text
http://192.168.86.240:8030
shellypro1pm-8813bfd99f54
```

Command:

```text
python3 -m src.mac.tools.shelly_live deploy-ftx-brain --base-url http://192.168.86.240:8030 --recipe src/shelly/ftx/recipes/brain.json --upload-chunk-bytes 1500 --log-timeout 30 --http-timeout 5
```

Result:

```text
script=brain_v2_13_0 id=7
upload_chunk_count=16
code_summary={"dewpoint_margin_removed":true,"target_to_house_min_c":12.0}
target_to_house_c=13.0
```

Local dampers intent:

```json
{"act":{"on":1},"device":"dmp","driver_inhibit":0,"mode":"STD","source":"brain","ts":1781347772,"v":1}
```

VVX intent readback:

```json
{"v":1,"source":"brain","ts":1781347772,"device":"vvx","mode":"STD","driver_inhibit":0,"act":{"on":1,"target_to_house_c":13},"target_to_house_c":13,"temp":{"out_c":19.3,"house_c":22.3}}
```

Important log lines:

```text
brain BOT
Number.Set {"id":204,"value":13}
HTTP.GET ... ftx.intent.dev.sup ...
HTTP.GET ... ftx.intent.dev.ext ...
HTTP.GET ... ftx.intent.dev.heat ... target_to_house_c 13
HTTP.GET ... ftx.intent.dev.cool ... target_to_house_c 13
KVS.Set {"key":"ftx.intent.dev.dmp",...}
HTTP.GET ... ftx.intent.dev.vvx ... target_to_house_c 13
brain DON
```

Observed final script state:

```text
master_v1_8_0 running=true
telemetry_publisher_dampers_v0_2_0 running=true
brain_v2_13_0 running=false
state_v1_8_0 running=false
executor_dampers_v0_2_0 running=false
```

During the log window the existing live master script also attempted `Script.Start {"id":7}` while the package-triggered brain verification was running. This is device-local master behavior and did not prevent successful `brain DON` and live code verification.
