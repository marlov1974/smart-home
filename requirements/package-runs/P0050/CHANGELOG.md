# P0050 changelog

- Built `se3_se1_demand_response_analysis_v1` from `se3_se1_bottleneck_training_dataset_v1` with 34968 rows.
- Selected `B2_smoothed_hour_daytype_dayofyear` as expected-spread baseline for residual diagnostics.
- Added local SE3 day/trailing-48h rank, top-N/bottom-N, consumer response and heat-pump pressure proxy features.
- Wrote baseline-corrected daytype, top-N response/rebound, heat-pressure and exploratory group evidence.
- Result status: PASS.
- No SE1-to-SE3 anchoring, SE3 API, production model artifact, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
