# P0056C Model Method Contract

```json
{
  "default_model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
  "fallback_order": [
    "F1_reduced_feature_set",
    "F2_weighted_ensemble_no_price",
    "F3_seasonal_same_week"
  ],
  "feature_count": 50,
  "feature_families": [
    "calendar_time",
    "holiday_weekend",
    "historical_area_load_lags",
    "rolling_area_load_statistics",
    "area_weather_proxy_features"
  ],
  "forbidden_features_excluded": true,
  "model_families_available": [
    "HGB",
    "ExtraTrees",
    "LightGBM",
    "XGBoost"
  ],
  "reduced_feature_count": 49
}
```
