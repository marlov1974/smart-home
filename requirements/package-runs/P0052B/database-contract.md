# P0052B database contract

P0052B reuses and extends:

- `transfer_capacity_flow_raw_v1`
- `transfer_capacity_flow_hourly_v1`
- `transfer_capacity_flow_se1_se4_hourly_v1`

Added metadata columns are documented in schema summary:

```json
{
  "added_columns": {
    "transfer_capacity_flow_hourly_v1": [],
    "transfer_capacity_flow_raw_v1": [],
    "transfer_capacity_flow_se1_se4_hourly_v1": []
  }
}
```

Existing SvK/Statnett and P0052A rows are preserved.
