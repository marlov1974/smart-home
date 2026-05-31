# P0040 weekly backtest method

primary_backtest_start = 2025-06-02
primary_backtest_end = 2026-05-18
forecast_origin_count = 50
origin_rule = Monday 06:00 local
known_spot_context = Monday 00:00..15:00, 16 hours
horizon = 168 complete Monday-start hours
weather_oracle = actual_weather_used_as_forecast_proxy
strict_fit = static pre-backtest P0037 train rows ending 2023-12-31; no forecast-horizon spot prices used as features
row_counts = {'train': 13945, 'validate': 8784, 'holdout': 8760, 'future': 3479}
