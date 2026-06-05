# P0054O LABB

Status: `PASS`

```json
{
  "derived_recomputed_after_noise": [
    "weather_proxy_temperature_delta_from_train_normal_se3",
    "weather_proxy_train_normal_temperature_2m_se3"
  ],
  "selected_for_noise": [
    "weather_proxy_apparent_temperature_se3",
    "weather_proxy_temperature_2m_se3"
  ],
  "selection_rule": "perturb source temperature-like weather proxy columns; recompute train normal/delta/cold-spell derived features after noise",
  "used_temperature_like_features": [
    "weather_proxy_apparent_temperature_se3",
    "weather_proxy_temperature_2m_se3",
    "weather_proxy_temperature_delta_from_train_normal_se3",
    "weather_proxy_train_normal_temperature_2m_se3"
  ]
}
```
