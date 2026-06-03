# P0052 database contract

Tables created/rebuilt:

- `transfer_capacity_flow_raw_v1`
- `transfer_capacity_flow_hourly_v1`
- `transfer_capacity_flow_se1_se4_hourly_v1`

Long-format columns include timestamp, fixed-CET fields, source, dataset, from/to area, border id, measure, value, unit, capacity method label, flow type label and quality flag.

Wide columns include internal SE1-SE2/SE2-SE3/SE3-SE4 signed flows, SE1-SE4 import/export/net import, balance residual diagnostics, pressure features and nullable capacity/utilization fields.
