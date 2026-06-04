# P0053C Changelog

- Added canonical forecast period policy in `memory/spotprice-forecast-period-policy.md`.
- Added reusable policy helpers in `forecast_period_policy.py`.
- Updated P0053B SE1 consumption warmup to split by `timestamp_utc`, hold out from `2025-06-01T00:00:00Z`, and exclude scored target rows before `2022-06-01T00:00:00Z`.
- Rebuilt P0053B SE1 consumption diagnostics under P0053C evidence at `requirements/package-runs/P0053C/p0053b-rebuild/`.
- Added relative error metrics to P0053B direct-horizon metrics.
- Classified old P0043/P0044/P0045/P0053B metrics as stale or diagnostic-only where split-incompatible.
- No production API, deployable model, API/device path, A61 utilization, future actual price feature, SE3 production model, Shelly, Home Assistant or KVS action was performed.
