# P0052 changelog

- Selected SvK Kontrollrummet / Statnett as the auth-free source for observed SE1-SE4 border flows and zone import/export.
- Built `transfer_capacity_flow_hourly_v1` and `transfer_capacity_flow_se1_se4_hourly_v1` with 24542 canonical rows and 599 wide hourly rows.
- Documented ENTSO-E token blocker for historical capacity ingestion; no capacity values were invented.
- Result status: WARN.
- No continental price pressure, SE1-to-SE3 anchoring, API, production model, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
