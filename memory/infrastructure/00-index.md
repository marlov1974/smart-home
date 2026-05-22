# Infrastructure Memory Index

Infrastructure memory contains general access, network and device-identity facts that are shared across G2 domains.

This area is intentionally domain-neutral. It should answer:

- how devices are reached
- which IP/NAT pattern applies
- which physical/runtime device is which
- where operator access differs from internal device-to-device access

## Files

```text
network.md      network and access principles
router-nat.md   NAT and operator URL rules
devices.md      global device registry
```

## Boundary

Infrastructure owns device identity and reachability.

Physical domain folders own interpretation of sensors, actuators and measurements.

Rule:

```text
Device/IP/NAT identity -> infrastructure/devices.md
Sensor channel meaning -> memory/physical/<domain>/
Physical model/calibration -> memory/physical/<domain>/
```

## Package history

Created by `P0002-import-infrastructure-and-physical-baseline`.
