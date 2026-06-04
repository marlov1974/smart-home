# P0053A database contract

P0053A reuses `transfer_capacity_flow_raw_v1`, `transfer_capacity_flow_hourly_v1` and `transfer_capacity_flow_se1_se4_hourly_v1`.

P0053A creates or replaces `physical_balance_flow_exchange_analysis_v1` as an offline analysis table joined from observed A09/A11 wide features, P0051 physical balance and P0048/P0049 price/spread columns.

No utilization or bottleneck-margin features are created or populated by P0053A.
