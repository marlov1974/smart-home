# P0053C SE1 Consumption Rebuild Results

P0053B SE1 consumption was rebuilt under the P0053C split policy.

Evidence directory:

```text
requirements/package-runs/P0053C/p0053b-rebuild/
```

## Rebuild Status

```text
status = PASS
direct_horizon_rows = 382106
persisted_rows = 382106
source_rows = 34968
path_origins = 1006
```

Split counts:

```text
train = 247477
validate = 39864
holdout = 94765
```

## Key Holdout Metrics

| model | horizon | MAE | RMSE | bias | sMAPE | MAE % mean | MAE % median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 same-hour previous-day | 1h | 12.330 | 16.111 | 0.054 | 0.0393 | 3.98% | 4.22% |
| M4 Ridge G4 calendar/load/weather | 1h | 6.432 | 8.219 | -0.148 | 0.0209 | 2.08% | 2.20% |
| M4 Ridge G4 calendar/load/weather | 24h | 13.299 | 17.161 | -0.419 | 0.0432 | 4.30% | 4.55% |
| M4 Ridge G4 calendar/load/weather | 168h | 27.835 | 36.665 | -2.267 | 0.0942 | 8.99% | 9.52% |
| M7 HGB G4 calendar/load/weather | 1h | 6.506 | 8.423 | 3.050 | 0.0213 | 2.10% | 2.23% |
| M7 HGB G4 calendar/load/weather | 24h | 12.694 | 16.503 | 3.597 | 0.0404 | 4.10% | 4.34% |
| M7 HGB G4 calendar/load/weather | 168h | 18.854 | 24.958 | 9.058 | 0.0594 | 6.09% | 6.45% |

Best forecast-safe direct model:

```text
M4_Ridge_G4_calendar_load_lags_weather, horizon=1h, holdout_MAE=6.431734387224803
```

The P0053C rebuild confirms SE1 consumption remains forecast-ready under the new holdout policy.
