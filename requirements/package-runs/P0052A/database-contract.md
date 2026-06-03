# P0052A database contract

P0052A reuses and extends:

- `transfer_capacity_flow_raw_v1`
- `transfer_capacity_flow_hourly_v1`
- `transfer_capacity_flow_se1_se4_hourly_v1`

ENTSO-E rows use `source_name = ENTSO-E Transparency Platform` and source-specific datasets such as `A09 scheduled commercial exchange`, `A11 physical flow` and `A61 forecasted transfer capacity explicit A02/A03/A04`.

Existing SvK/Statnett rows are preserved because source identity is part of the long-table uniqueness key.
