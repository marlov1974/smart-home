# P0052 derived feature definitions

```json
{
  "balance_residual_z": "production_z + import_z - consumption_z - export_z. Reported only as compatibility diagnostic.",
  "capacity_utilization": "null in P0052 because capacity is unavailable from selected auth-free source.",
  "net_import_z": "import_z - export_z; positive means the zone is supplied by imports.",
  "north_export_pressure": "-(net_import_se1_mw + net_import_se2_mw)",
  "north_to_south_flow_min_or_chain_proxy": "minimum positive internal north-to-south flow across SE1-SE2, SE2-SE3 and SE3-SE4 where present.",
  "south_import_pressure": "net_import_se3_mw + net_import_se4_mw"
}
```
