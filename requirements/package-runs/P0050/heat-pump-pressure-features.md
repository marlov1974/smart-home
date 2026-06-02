# P0050 heat-pump pressure features

```json
{
  "delta_field": "temperature_south_proxy_delta",
  "heat_debt_pressure": "max(0, train_p25-temp) * (1 + top4 + 0.6*top8 + 0.4*p80) - (0.7*bottom4 + 0.3*bottom8)",
  "temperature_field": "temperature_south_proxy_actual",
  "train_p10": 0.145,
  "train_p25": 3.8349999999999995
}
```
