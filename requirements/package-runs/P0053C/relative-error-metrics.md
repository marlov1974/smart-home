# P0053C Relative Error Metrics

P0053C added these fields to direct-horizon metrics:

```text
mean_actual_mw
median_actual_mw
p10_actual_mw
p90_actual_mw
MAE_percent_of_mean
MAE_percent_of_median
```

For the best 1h forecast-safe model on holdout:

```text
model = M4_Ridge_G4_calendar_load_lags_weather
horizon = 1h
row_count = 8615
MAE = 6.431734387224803 MW
mean_actual_mw = 309.6312977542073 MW
median_actual_mw = 292.32350125 MW
MAE_percent_of_mean = 2.07722359949431
MAE_percent_of_median = 2.200211796737635
sMAPE = 0.0209
```

Full relative metrics are in:

```text
requirements/package-runs/P0053C/p0053b-rebuild/horizon-metrics.csv
```
