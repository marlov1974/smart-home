# P0048 continuous spread baseline results

| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |
|---|---:|---:|---:|---:|---|
| S0_time_calendar_baseline | 0.272976 | 0.381635 | 0.261219 | 0.325493 | weekday_hour_mean_baseline |
| S1_weather_gradient_regression | 0.305413 | 0.533371 | 0.218676 | 0.300786 | HistGradientBoostingRegressor |
| S2_with_lagged_spread_features_diagnostic | 0.093744 | 0.155419 | 0.081839 | 0.125637 | HistGradientBoostingRegressor |
