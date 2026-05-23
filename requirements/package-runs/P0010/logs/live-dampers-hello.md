# P0010 Live Dampers Hello Evidence

## Command

```bash
python3 -m src.mac.tools.shelly_live deploy-hello --base-url http://192.168.86.240:8030/ --script build/shelly/fixture/hello_v1_0_0.js --expect hello --log-timeout 20
```

## Target

```text
endpoint: http://192.168.86.240:8030
device:   ftx-dampers / dampers lab device
script:   hello_v1_0_0
```

## Result

```text
target=http://192.168.86.240:8030
script=hello_v1_0_0 id=1
before_scripts=[{"id":1,"name":"hello_v1_0_0","enable":false,"running":true}]
after_scripts=[{"id":1,"name":"hello_v1_0_0","enable":false,"running":false}]
cleaned_up=false
```

## Log Excerpt

```text
4167 [May 24 00:11:37.797] I shelly_debug.cpp:236    Streaming logs to 192.168.86.38:50576
4168 [May 24 00:11:38.099] I shos_rpc_inst.c:243     Script.Start [1@] via HTTP_in POST 192.168.86.38:50577
4169 [May 24 00:11:38.100] I shelly_user_script.:203 JS RAM stat: initial: 112036 after: 112000, used: 36
4170 [May 24 00:11:38.101] I hello world
```

## Boundary Check

Observed live actions were limited to:

- `Shelly.GetStatus`
- `Script.List`
- `Script.Stop` for `hello_v1_0_0` when it was already running
- `Script.PutCode` for `hello_v1_0_0`
- `Script.Start` for `hello_v1_0_0`
- `/debug/log` read

No device settings, actuator/output, relay, cover, switch, KVS, component, Wi-Fi, network, MQTT, Bluetooth or cloud operations were performed by the P0010 tool.

## Final State

`hello_v1_0_0` is installed and stopped. It was intentionally left installed as harmless test evidence.
