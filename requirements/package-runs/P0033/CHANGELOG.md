# P0033 changelog

## In progress

- Added package review/design/function-design evidence.
- Added `src.mac.services.spotprice_temperature_normalization` with M1/M2/M3 local feature-store builder.
- Added unit tests for P0033 core behavior.
- Added generated local feature DB evidence and diagnostics.
- Added cross-package function documentation for P0033.
- Corrected M1 to use Python ISO week and optimized M1/M2 calendar bucket normal calculation.
- Added `bucket_year_count` diagnostics for M1/M2 normals and documented cross-year smoothing to prevent year-specific normal memorization.
- Added `se3_load_temperature` as an M2 signal and confirmed `area_diff_proxy_se3` M3 deltas use SE3-load minus SE1-core temperature-gradient anomaly.
- Added a daily 16:00 user LaunchAgent for rebuilding the P0033 feature DB after daily spotprice and weather ingest.
- Installed and verified the P0033 daily rebuild LaunchAgent on the local Mac.
