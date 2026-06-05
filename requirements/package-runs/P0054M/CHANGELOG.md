# P0054M Changelog

Status: `PASS`

- Selected `rolling_oof_train_plus_holdout`.
- Created train-side blocked OOF advanced SE3 price rows in `advanced_spotprice_forecast_log_p0054m_se3_train_blocked_oof_v1`.
- Used P0054L2 Ensemble holdout rows for holdout evaluation.
- Trained paired no-price and with-advanced-price SE3 consumption models for HGB, ExtraTrees, LightGBM and XGBoost.
- Wrote direct, weekly path, conditional, ablation and P0054K comparison evidence.
- No API, device, runtime, A61, future-flow or actual future price leakage work was performed.
