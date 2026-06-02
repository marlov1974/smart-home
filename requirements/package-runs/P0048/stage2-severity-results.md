# P0048 Stage 2 severity results

## se3_minus_se1

| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |
|---|---:|---:|---:|---:|---|
| R0_regime_mean_baseline | 0.721684 | 0.771950 | 0.718104 | 0.749620 | train_mean_baseline |
| R1_time_calendar_baseline | 0.514940 | 0.819937 | 0.190995 | 0.250367 | HistGradientBoostingRegressor |
| R2_weather_gradient_regressor | 0.504713 | 0.807581 | 0.197435 | 0.254155 | HistGradientBoostingRegressor |
| R3_weather_anomaly_gradient_regressor | 0.522258 | 0.850042 | 0.190571 | 0.249717 | HistGradientBoostingRegressor |
| R4_with_lagged_spread_features_diagnostic | 0.140713 | 0.210866 | 0.102628 | 0.145233 | HistGradientBoostingRegressor |
## log_positive_spread

| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |
|---|---:|---:|---:|---:|---|
| R0_regime_mean_baseline | 0.735239 | 0.834082 | 0.674119 | 0.769186 | train_mean_baseline |
| R1_time_calendar_baseline | 0.640903 | 0.796702 | 0.358294 | 0.444981 | HistGradientBoostingRegressor |
| R2_weather_gradient_regressor | 0.597569 | 0.753607 | 0.349101 | 0.438289 | HistGradientBoostingRegressor |
| R3_weather_anomaly_gradient_regressor | 0.588524 | 0.749385 | 0.347774 | 0.441085 | HistGradientBoostingRegressor |
| R4_with_lagged_spread_features_diagnostic | 0.203038 | 0.282605 | 0.197190 | 0.261472 | HistGradientBoostingRegressor |

## spread_excess_positive

| group | validate MAE | validate RMSE | holdout MAE | holdout RMSE | model |
|---|---:|---:|---:|---:|---|
| R0_regime_mean_baseline | 0.721684 | 0.771950 | 0.718104 | 0.749620 | train_mean_baseline |
| R1_time_calendar_baseline | 0.514940 | 0.819937 | 0.190995 | 0.250367 | HistGradientBoostingRegressor |
| R2_weather_gradient_regressor | 0.504713 | 0.807581 | 0.197435 | 0.254155 | HistGradientBoostingRegressor |
| R3_weather_anomaly_gradient_regressor | 0.522258 | 0.850042 | 0.190571 | 0.249717 | HistGradientBoostingRegressor |
| R4_with_lagged_spread_features_diagnostic | 0.140713 | 0.210866 | 0.102628 | 0.145233 | HistGradientBoostingRegressor |
