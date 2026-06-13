# P0063 Live Dampers FTX State Deploy

Target:

```text
http://192.168.86.240:8030
shellypro1pm-8813bfd99f54
```

Command:

```text
python3 -m src.mac.tools.shelly_live deploy-ftx-state --base-url http://192.168.86.240:8030 --recipe src/shelly/ftx/recipes/state.json --upload-chunk-bytes 1500 --log-timeout 20 --http-timeout 5
```

Result:

```text
script=state_v1_8_0 id=5
upload_chunk_count=9
zero_vvx_summary={"hist":{"r0":0.0,"r1":0.0,"r2":0.0},"number_202":0.0,"run_vvx":0}
```

Important log lines:

```text
state BOT
KVS.Set {"key":"ftx.state.run","value":{"sup":1,"ext":1,"vvx":0,"heat":0,"cool":1,"dmp":1}}
Number.Set {"id":202,"value":0}
Status change of number:202: {"value":0}
state OK SR=1 ER=1 VR=0 H=0 C=1
state DON
```

Post-check:

```text
Number 202 = 0
ftx.state.run = {"sup":1,"ext":1,"vvx":0,"heat":0,"cool":1,"dmp":1}
ftx.state.hist = {"r0":0,"r1":0,"r2":0}
```

Observed script state:

```text
master_v1_8_0 running=true
telemetry_publisher_dampers_v0_2_0 running=true
state_v1_8_0 running=false
brain_v2_13_0 running=false
executor_dampers_v0_2_0 running=false
```

During the log window the existing live master script issued a `Script.Stop {"id":7}`. The P0063 tool did not call `Script.Stop` for `brain_v2_13_0`; this is reported as remaining live-runtime uncertainty.
