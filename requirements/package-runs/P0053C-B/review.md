# P0053C-B Consistency Review

Status: WARN

Package P0053C-B is implementable with one important constraint: the persisted P0053C-A table `m4_price_shape_forecast_origin_log_p0053ca_v1` is a holdout-only, single-origin shape/index log. P0053C-B requires anchor selection on validation plus holdout reporting, so validation shape paths cannot be taken directly from that table.

Resolution: reuse the deterministic P0043/P0044/P0045/P0053C-A regeneration path to build rolling validation and holdout 168h shape paths in memory, and verify that the P0053C-A local shape log exists as the predecessor artifact. The new P0053C-B output table will contain anchored absolute SE1 forecasts.

Evidence checked:

- P0053C package exists and supplies `forecast_period_policy_v1_p0053c`.
- P0053C-A package evidence exists and the local table `m4_price_shape_forecast_origin_log_p0053ca_v1` exists.
- P0053C-A table contains `prediction_kind=shape_index` and `prediction_unit=centered_shape_index`, not absolute prices.
- Historical SE1 actuals are available in `ai2_hour_to_day_training_targets_v2` as `target_series='system_proxy_se1'` and `hour_price`.
- Prior anchoring evidence exists in P0040/P0046. P0040 documents level/shape separation using known prices for anchoring. P0046 contains anchored absolute backtest scenarios. I did not find a durable prior artifact proving this exact P0053C-B 48h formula set under the P0053C global split policy, so P0053C-B must define and prove it explicitly.

Safety classification:

- No API, device, Shelly, Home Assistant, KVS, A61 utilization, production activation, deployable runtime or live write is needed.
- Anchor history can be enforced as `[forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)`.
- Forecast rows can enforce `forecast_origin_timestamp_utc <= target_timestamp_utc <= forecast_origin_timestamp_utc + 167h`.
- Holdout will not be used for selection. A0-A3 selection will use validation `MAE_full_168h` only, with rank/top8 validation tie-breaks.

Proceeding with implementation is acceptable under WARN assumptions.
