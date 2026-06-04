# P0053A data validation

```json
{
  "a61_requested": false,
  "analysis_rows": 34968,
  "duplicates_in_fetched_hourly_rows": 0,
  "failed_chunks": 0,
  "forbidden_row_documents": [],
  "forbidden_task_documents": [],
  "full_target_directional_complete": false,
  "full_target_directional_coverage": {
    "complete": false,
    "end": "2026-05-25T22:00:00Z",
    "expected_hours_per_direction": 34968,
    "max_missing_hours": 34740,
    "min_hours": 228,
    "missing_hours_by_contract": {
      "A09:SE1->SE2": 2768,
      "A09:SE2->SE1": 22127,
      "A09:SE2->SE3": 4034,
      "A09:SE3->SE2": 28434,
      "A09:SE3->SE4": 4188,
      "A09:SE4->SE3": 23408,
      "A11:SE1->SE2": 2507,
      "A11:SE2->SE1": 31035,
      "A11:SE2->SE3": 121,
      "A11:SE3->SE2": 34740,
      "A11:SE3->SE4": 642,
      "A11:SE4->SE3": 33963
    },
    "start": "2022-05-29T23:00:00Z"
  },
  "full_target_net_complete": false,
  "full_target_net_feature_coverage": {
    "complete": false,
    "completion_percent_by_feature": {
      "net_physical_flow_se1_se2_mw": 99.946,
      "net_physical_flow_se2_se3_mw": 99.946,
      "net_physical_flow_se3_se4_mw": 99.877,
      "net_scheduled_exchange_se1_se2_mw": 98.413,
      "net_scheduled_exchange_se2_se3_mw": 89.957,
      "net_scheduled_exchange_se3_se4_mw": 91.956
    },
    "counts": {
      "net_physical_flow_se1_se2_mw": 34949,
      "net_physical_flow_se2_se3_mw": 34949,
      "net_physical_flow_se3_se4_mw": 34925,
      "net_scheduled_exchange_se1_se2_mw": 34413,
      "net_scheduled_exchange_se2_se3_mw": 31456,
      "net_scheduled_exchange_se3_se4_mw": 32155
    },
    "end": "2026-05-25T22:00:00Z",
    "expected_hours": 34968,
    "min_completion_percent": 89.957,
    "start": "2022-05-29T23:00:00Z"
  },
  "nonfinite_fetched_hourly_values": 0,
  "ok": true,
  "one_row_per_wide_timestamp": true,
  "secret_checked": true,
  "secret_safe": true,
  "token_leak_scan_required": true,
  "utilization_or_margin_derived_by_p0053a": false,
  "warn_minimum_directional_complete": false,
  "warn_minimum_directional_coverage": {
    "complete": false,
    "end": "2026-05-25T22:00:00Z",
    "expected_hours_per_direction": 21023,
    "max_missing_hours": 20890,
    "min_hours": 133,
    "missing_hours_by_contract": {
      "A09:SE1->SE2": 1951,
      "A09:SE2->SE1": 14364,
      "A09:SE2->SE3": 797,
      "A09:SE3->SE2": 18259,
      "A09:SE3->SE4": 1487,
      "A09:SE4->SE3": 16259,
      "A11:SE1->SE2": 1822,
      "A11:SE2->SE1": 18187,
      "A11:SE2->SE3": 76,
      "A11:SE3->SE2": 20890,
      "A11:SE3->SE4": 388,
      "A11:SE4->SE3": 20390
    },
    "start": "2024-01-01T00:00:00Z"
  },
  "warn_minimum_net_complete": false,
  "warn_minimum_net_feature_coverage": {
    "complete": false,
    "completion_percent_by_feature": {
      "net_physical_flow_se1_se2_mw": 99.91,
      "net_physical_flow_se2_se3_mw": 99.91,
      "net_physical_flow_se3_se4_mw": 99.8,
      "net_scheduled_exchange_se1_se2_mw": 98.768,
      "net_scheduled_exchange_se2_se3_mw": 97.255,
      "net_scheduled_exchange_se3_se4_mw": 95.624
    },
    "counts": {
      "net_physical_flow_se1_se2_mw": 21004,
      "net_physical_flow_se2_se3_mw": 21004,
      "net_physical_flow_se3_se4_mw": 20981,
      "net_scheduled_exchange_se1_se2_mw": 20764,
      "net_scheduled_exchange_se2_se3_mw": 20446,
      "net_scheduled_exchange_se3_se4_mw": 20103
    },
    "end": "2026-05-25T22:00:00Z",
    "expected_hours": 21023,
    "min_completion_percent": 95.624,
    "start": "2024-01-01T00:00:00Z"
  },
  "warn_minimum_net_substantial": true
}
```
