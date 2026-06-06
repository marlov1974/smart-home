# P0054T4 LABB

Status: `WARN`

```json
{
  "limitation": "noise is applied to final model-input temperature columns, not raw weather followed by derived-feature recomputation",
  "magnitude_c": 2.0,
  "seeds": [
    1000,
    1001,
    1002,
    1003,
    1004,
    1005,
    1006,
    1007,
    1008,
    1009
  ],
  "temperature_columns": [
    "weather_proxy_apparent_temperature_se3",
    "weather_proxy_temperature_2m_se3"
  ],
  "w0": "clean train_fit and clean holdout actual-weather proxy",
  "w1": "clean train_fit; holdout/inference final temperature model-input columns plus deterministic uniform noise"
}
```
