# P0054R LABB

Status: `PASS`

```json
{
  "median": {
    "source_models": [
      "HGB_no_price",
      "ExtraTrees_no_price",
      "LightGBM_no_price",
      "XGBoost_no_price"
    ]
  },
  "weighted": {
    "holdout_used_for_weights": false,
    "internal_validation_start": "2025-03-01T00:00:00Z",
    "method": "inverse_internal_validation_mae",
    "model_mae": {
      "ExtraTrees_no_price": 313.08342263380854,
      "HGB_no_price": 292.8569732300242,
      "LightGBM_no_price": 281.5606194933632,
      "XGBoost_no_price": 280.5587719505287
    },
    "selection_data": "internal_validation_only",
    "weights": {
      "ExtraTrees_no_price": 0.23272312870535258,
      "HGB_no_price": 0.24879637612006233,
      "LightGBM_no_price": 0.25877821192546985,
      "XGBoost_no_price": 0.25970228324911526
    }
  }
}
```
