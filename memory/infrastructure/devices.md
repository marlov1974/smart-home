# Global Device Registry

This registry contains device identity and reachability. Physical interpretation belongs in `memory/physical/`.

## Network convention

```text
Internal IP: 192.168.77.xx
NAT URL:     http://192.168.86.240:80xx/
```

## Current FTX Shelly / edge topology

Current G2 FTX source under `src/shelly/ftx/scripts/` is organized around these runtime roles:

| Role | Domain | Internal IP | Operator NAT URL | Shelly device id | Notes |
|---|---|---:|---|---|---|
| `ftx-supply-fan` | FTX | `192.168.77.10` | `http://192.168.86.240:8010/` | unknown | Pro-class fan actuator with Sensor Add-On; owns supply-side sensors and publishes telemetry |
| `ftx-extract-fan` | FTX | `192.168.77.11` | `http://192.168.86.240:8011/` | unknown | Pro-class fan actuator with Sensor Add-On; owns extract/house sensors and publishes telemetry |
| `ftx-heat-dim` | FTX | `192.168.77.12` | `http://192.168.86.240:8012/` | unknown | Pro-class 0-10 V/light actuator for heating battery; consumes direct thermal telemetry from supply device |
| `ftx-cool-dim` | FTX | `192.168.77.13` | `http://192.168.86.240:8013/` | unknown | Pro-class 0-10 V/light actuator for cooling battery; consumes direct thermal telemetry from supply device |
| `ftx-dampers` | FTX / coordination host | `192.168.77.30` | `http://192.168.86.240:8030/` | `8813bfd99f54` | Shelly Pro 1PM; damper actuator plus current FTX brain/state/telemetry hub role |
| `ftx-vvx` | FTX | `192.168.77.40` | `http://192.168.86.240:8040/` | unknown | VVX actuator/runtime role |

Exact model names and device ids for the Pro devices still marked `unknown` should be captured from live read-only inventory when convenient.

## Retired UNI topology

The former standalone UNI devices are no longer part of the current physical FTX topology:

```text
ftx-supply-uni  / 192.168.77.20
ftx-extract-uni / 192.168.77.21
ftx-process-uni / 192.168.77.22
```

Their measurement roles were consolidated onto Sensor Add-On hardware attached to the current supply- and extract-fan Pro devices.

Historical package evidence for P0016 and older G1 imports may still mention these UNI devices. Those records are provenance and must not be interpreted as current hardware inventory.

## Current telemetry topology from source

The current supply-fan telemetry publisher reads local Shelly components and publishes:

```text
ftx.tel.dev.sup          -> ftx-dampers / 192.168.77.30
ftx.tel.thermal.cool     -> ftx-cool-dim / 192.168.77.13
ftx.tel.thermal.heat     -> ftx-heat-dim / 192.168.77.12
```

The current extract-fan telemetry publisher reads local Shelly components and publishes:

```text
ftx.tel.dev.ext          -> ftx-dampers / 192.168.77.30
```

This is direct Shelly-to-Shelly HTTP/RPC KVS distribution. It does not require a central MQTT broker or L3 process for normal telemetry delivery.

## Dampers identity and verified configuration

Known verified identity from P0014 and later live packages:

```text
Device role: ftx-dampers
Physical Shelly id: 8813bfd99f54
Stable LAN address: 192.168.77.30
Operator NAT URL: http://192.168.86.240:8030/
Live device id: shellypro1pm-8813bfd99f54
Model/app: Shelly Pro 1PM / Pro1PM
```

P0014 verified device name `ftx_dampers`, channel name `dampers`, `restore_last` switch behavior and virtual `House Temp` number component.

Later P0063/P0065 live verification used this device as the FTX brain/state coordination host as well as the damper device.

## Open device registry gaps

To be filled by later documentation or packages:

- exact model/device id for current supply-fan Pro device
- exact model/device id for current extract-fan Pro device
- exact model/device id for heat/cool/VVX Pro devices
- Mac mini host identity and Tailscale address
- Home Assistant host identity
- VP1/VP2 control Shelly devices
- floor heating/floor cooling Shelly devices
- VVB/VVC devices

## Source

Original FTX topology was imported from G1 during `P0002`.

Current Pro/Sensor Add-On topology is confirmed by current G2 FTX runtime source under `src/shelly/ftx/scripts/` and operator-confirmed physical replacement of the former UNI devices.
