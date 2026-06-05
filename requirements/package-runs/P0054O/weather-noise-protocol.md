# P0054O LABB

Status: `PASS`

```json
{
  "amplitude_c": 2.0,
  "formula": "temp_noisy = temp_actual_proxy + uniform(-2.0, +2.0)",
  "primary_analysis": "B_train_fit_and_holdout_noise",
  "required_scenario": "uniform_pm2c_train_and_holdout",
  "rng": "numpy.default_rng(seed)",
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
  ]
}
```
