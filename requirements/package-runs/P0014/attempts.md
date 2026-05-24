# P0014 Attempts and Verification Evidence

## Attempt 1

Result: PASS

Runtime endpoint used for this Mac execution:

```text
http://192.168.86.240:8030
```

Stable package identity:

```text
logical role: ftx-dampers
stable LAN address: 192.168.77.30
physical Shelly id: 8813bfd99f54
live device id: shellypro1pm-8813bfd99f54
model: SPSW-201PE15UL
app: Pro1PM
firmware: 1.7.5
```

Initial read-only plan:

```text
action_count: 4
device_name before: null
switch name before: null
switch initial_state before: match_input
House Temp before: absent
switch output observed only: true
```

Applied actions:

```text
Sys.SetConfig {"config":{"device":{"name":"ftx_dampers"}}}
Switch.SetConfig {"id":0,"config":{"name":"dampers"}}
Switch.SetConfig {"id":0,"config":{"initial_state":"restore_last"}}
Virtual.Add {"type":"number","config":{"name":"House Temp","min":10,"max":30,"default_value":21,"persisted":true,"meta":{"ui":{"view":"field","step":0.1,"unit":"C"}}}}
Number.Set {"id":200,"value":21}
```

Readback after apply:

```text
verified: true
device_name: ftx_dampers
switch name: dampers
switch initial_state: restore_last
House Temp id: 200
switch output observed only: true
component_count: 11
```

Idempotent rerun:

```text
command: python3 -m src.mac.tools.shelly_device apply --base-url http://192.168.86.240:8030
action_count: 0
verified: true
```

Verify-only rerun:

```text
command: python3 -m src.mac.tools.shelly_device verify --base-url http://192.168.86.240:8030
verified: true
```

Actuator safety:

```text
No Switch.Set, Switch.Toggle, Relay, Cover or output-control RPC was used.
Switch output was read as status evidence only.
No reboot or power-cycle test was performed.
```

## Commands Run

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_device plan --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device apply --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device apply --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device verify --base-url http://192.168.86.240:8030
```

## Result

P0014 live package verification passed.
