# P0053A derived feature definitions

- `net_scheduled_exchange_<border>_mw = north_to_south_scheduled_exchange - south_to_north_scheduled_exchange`.
- `net_physical_flow_<border>_mw = north_to_south_physical_flow - south_to_north_physical_flow`.
- `southward_exchange_pressure = max(0, net_scheduled_exchange_se2_se3_mw) + max(0, net_scheduled_exchange_se3_se4_mw)`.
- `southward_physical_flow_pressure = max(0, net_physical_flow_se2_se3_mw) + max(0, net_physical_flow_se3_se4_mw)`.
- Capacity utilization and bottleneck margin are intentionally absent from P0053A derivations.
