# P0053B-A2 Consistency Review

Status: WARN

P0053B-A2 is implementable as an offline diagnostic backtest, but not as a canonical deployable train/validation/holdout consumption model.

Repository facts:

- P0053C PASS evidence exists and introduced `forecast_period_policy_v1_p0053c`.
- P0053C-A PASS evidence exists and rebuilt M4 shape/index.
- P0053C-B PASS evidence exists and created `m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1`.
- The P0053C-B price forecast log has forecast-origin semantics and leakage review passed.
- The P0053C-B log covers validation and holdout only:
  - validation rows: 24,192
  - holdout rows: 58,464
  - no canonical train rows before 2025-01-01
- P0053B/P0053C SE1 consumption warmup and `physical_balance_se1_se4_hourly_v1` exist.

Important inconsistency/assumption:

The package asks for global split policy and trained plus_G7 models, but also requires G7 features to come from the anchored forecast log. Since the anchored forecast log has no train-period rows, P0053B-A2 cannot train plus_G7 models on the canonical 2022-06-01..2024-12-31 train split without either creating new price forecast rows or using actual price, both outside this package scope.

Resolution:

Proceed as WARN with an explicitly labeled offline diagnostic:

- Use only P0053C-B forecast-log rows for G7 features.
- Use validation-origin joined rows as the development/training set for the P0053B-A2 comparison.
- Use holdout-origin joined rows only for final reporting.
- Compare base and plus_G7 on identical joined row sets.
- Label weather as `weather_actual_as_forecast_proxy`.
- Mark result `offline_backtest_ready_with_weather_proxy` and `deployable_requires_weather_forecast_feed`.

Safety result:

- No API, devices, Shelly, Home Assistant, KVS, A61 utilization, future A09/A11, future production/export/import or actual future price features are needed.
- Holdout will not be used for model fitting or feature/model selection.
- All price features will derive from predictions sharing the same `forecast_origin_timestamp_utc`.
