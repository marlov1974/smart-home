# P0054M Package Consistency Review

Status: `WARN`

## Understanding

P0054M is a LABB package that tests whether the improved P0054L2 SE3 price forecast helps SE3 consumption forecasting. It must not treat P0054L2's holdout-only forecast log as a train-period consumption feature source.

## Repository Truth Checked

- P0054L2 created `advanced_spotprice_forecast_log_p0054l2_se3_v1` with `model_name=Ensemble`, 59,136 holdout rows and leakage review `ok`.
- P0054L2 explicitly warns that the global train_fit price model is holdout-safe for evaluation but not automatically a train-period downstream feature source.
- P0054K has the canonical SE3 consumption source: `physical_balance_se1_se4_hourly_v1.consumption_se3`, unit `MW hourly mean`.
- P0054K established the no-price and simple-price SE3 consumption comparison baseline.
- P0054E/P0054L2 evidence shows LightGBM and XGBoost are locally importable.

## Consistency Result

`WARN`.

The package is implementable if it uses `price_feature_protocol=rolling_oof_train_plus_holdout` with explicit limited train_fit coverage. The safe route is:

```text
train-side price feature:
  blocked out-of-fold price predictions for 2025-03-01..2025-05-31,
  trained only on reconstructed SE3 price rows before 2025-03-01.

holdout-side price feature:
  P0054L2 Ensemble forecast log.
```

Consumption no-price and with-price models must train on identical train target rows, namely rows with safe train-side price coverage, and score identical holdout rows.

The warning is that train-side advanced price coverage is intentionally partial inside train_fit, not a full 2022-06..2025-05 rolling forecast source.

## Safety Review

Allowed and planned:

- Local SQLite reads/writes for a package-scoped train-side advanced price feature table.
- Local deterministic LABB model training/evaluation.
- Package-run evidence.

Forbidden and avoided:

- No live API calls.
- No Shelly, Home Assistant, device, KVS or runtime changes.
- No actual future spot price as a feature.
- No P0054L2 holdout-only forecast as train_fit feature.
- No production/export/import/A61/future-flow features.
- No model binaries or large raw datasets committed.
