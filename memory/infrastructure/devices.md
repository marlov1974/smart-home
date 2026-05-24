# Global Device Registry

This registry contains device identity and reachability. Physical interpretation belongs in `memory/physical/`.

## Network convention

```text
Internal IP: 192.168.77.xx
NAT URL:     http://192.168.86.240:80xx/
```

## Known Shelly / edge devices imported from G1

| Role | Domain | Internal IP | Operator NAT URL | Shelly device id | Notes |
|---|---|---:|---|---|---|
| `ftx-supply-fan` | FTX | `192.168.77.10` | `http://192.168.86.240:8010/` | unknown | supply EC fan control/telemetry |
| `ftx-extract-fan` | FTX | `192.168.77.11` | `http://192.168.86.240:8011/` | unknown | extract EC fan control/telemetry |
| `ftx-heat-dim` | FTX | `192.168.77.12` | `http://192.168.86.240:8012/` | unknown | heating battery valve/load control |
| `ftx-cool-dim` | FTX | `192.168.77.13` | `http://192.168.86.240:8013/` | unknown | cooling battery valve/load control |
| `ftx-supply-uni` | FTX | `192.168.77.20` | `http://192.168.86.240:8020/` | unknown | supply UNI sensors |
| `ftx-extract-uni` | FTX | `192.168.77.21` | `http://192.168.86.240:8021/` | unknown | extract UNI sensors |
| `ftx-process-uni` | FTX | `192.168.77.22` | `http://192.168.86.240:8022/` | unknown | process/house/brine/hotwater/VVX sensors |
| `ftx-dampers` | FTX | `192.168.77.30` | `http://192.168.86.240:8030/` | `8813bfd99f54` | damper switch/device |
| `ftx-vvx` | FTX / runtime host | `192.168.77.40` | `http://192.168.86.240:8040/` | unknown | VVX control and current G1 runtime host |

## Current G1 runtime host

The current G1 runtime host is:

```text
ftx-vvx / 192.168.77.40 / http://192.168.86.240:8040/
```

G2 must not assume it owns this runtime until an explicit migration package is implemented.

## Dampers G2 lab residue

The dampers device is used as the current G2 Shelly lab device.

Known harmless G2 test residue after P0013:

```text
Device role: ftx-dampers
Physical Shelly id: 8813bfd99f54
Stable LAN address: 192.168.77.30
Operator NAT URL: http://192.168.86.240:8030/
Stopped test script: spotprice_v0_9_0
```

`spotprice_v0_9_0` on dampers is not production FTX or damper runtime. It is a stopped G2 test/runtime proof from the spotprice packages and must not be treated as current G1 control behavior.

## Open device registry gaps

To be filled by later packages:

- Mac mini host identity and Tailscale address
- Home Assistant host identity
- VP1/VP2 control Shelly devices
- floor heating/floor cooling Shelly devices
- VVB/VVC devices
- exact Shelly model names and device IDs for devices still marked unknown

## Source

Imported from G1 `marlov1974/shelly` device-topology and hardware-inventory memory during `P0002`.

Dampers physical Shelly id and stopped G2 spotprice test residue added from operator-provided project knowledge after P0013.