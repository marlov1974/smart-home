# P0056E Model Variant Contract

```json
[
  {
    "description": "P0056C baseline reproduction with current weather.",
    "feature_group": "current_best_feature_set",
    "method": "horizon_bias_weighted_ensemble",
    "model_family": "ensemble",
    "model_name": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "variant_id": "V0",
    "weather_proxy_version": "P0056B"
  },
  {
    "description": "P0056D weather with current model.",
    "feature_group": "current_best_feature_set",
    "method": "horizon_bias_weighted_ensemble",
    "model_family": "ensemble",
    "model_name": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "variant_id": "V1",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "Weighted ensemble without horizon-bias correction.",
    "feature_group": "current_best_feature_set",
    "method": "weighted_ensemble_no_bias",
    "model_family": "ensemble",
    "model_name": "WeightedEnsemble_no_price",
    "variant_id": "V2",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "LightGBM-focused model.",
    "feature_group": "current_best_feature_set",
    "method": "single_family",
    "model_family": "LightGBM",
    "model_name": "LightGBM_no_price",
    "variant_id": "V3",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "XGBoost-focused model.",
    "feature_group": "current_best_feature_set",
    "method": "single_family",
    "model_family": "XGBoost",
    "model_name": "XGBoost_no_price",
    "variant_id": "V4",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "HGB-focused robust small-data model.",
    "feature_group": "current_best_feature_set",
    "method": "single_family",
    "model_family": "HGB",
    "model_name": "HGB_no_price",
    "variant_id": "V5",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "Load-lag-heavy model.",
    "feature_group": "lag_heavy",
    "method": "weighted_ensemble_no_bias",
    "model_family": "ensemble",
    "model_name": "LagHeavy_WeightedEnsemble_no_price",
    "variant_id": "V6",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "Weather-heavy model.",
    "feature_group": "weather_heavy",
    "method": "horizon_bias_weighted_ensemble",
    "model_family": "ensemble",
    "model_name": "WeatherHeavy_HorizonBiasCorrected_WeightedEnsemble_no_price",
    "variant_id": "V7",
    "weather_proxy_version": "P0056D"
  },
  {
    "description": "Simple internal-validation learned regime correction.",
    "feature_group": "weather_plus_lags",
    "method": "regime_correction",
    "model_family": "ensemble",
    "model_name": "RegimeCorrected_HorizonBiasCorrected_WeightedEnsemble_no_price",
    "variant_id": "V8",
    "weather_proxy_version": "P0056D"
  }
]
```
