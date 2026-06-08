# P0056D Forecast Retest Method

```json
{
  "areas": [
    "SE1",
    "SE2",
    "FI"
  ],
  "completed_jobs": 6,
  "failed_areas": [],
  "model_method_contract": {
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
  },
  "split_policy": {
    "holdout": "target_timestamp_utc >= 2025-06-01T00:00:00Z",
    "holdout_used_for_fit_or_selection": "false",
    "internal_selection_data": "internal_validation_only",
    "internal_validation": "2025-03-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z",
    "train_fit": "2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z"
  },
  "target_contract": {
    "areas": {
      "FI": {
        "duplicates": 0,
        "holdout_rows": 8913,
        "max_timestamp_utc": "2026-06-07T08:00:00Z",
        "mean_mw": 9392.04871242908,
        "median_mw": 9129.9,
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "nonfinite_values": 0,
        "rows": 35189,
        "train_fit_rows": 26276
      },
      "SE1": {
        "duplicates": 0,
        "holdout_rows": 8869,
        "max_timestamp_utc": "2026-06-07T08:00:00Z",
        "mean_mw": 1247.120749755091,
        "median_mw": 1213.0,
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "nonfinite_values": 0,
        "rows": 35047,
        "train_fit_rows": 26178
      },
      "SE2": {
        "duplicates": 0,
        "holdout_rows": 8869,
        "max_timestamp_utc": "2026-06-07T08:00:00Z",
        "mean_mw": 1720.6891102113743,
        "median_mw": 1649.0,
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "nonfinite_values": 0,
        "rows": 35072,
        "train_fit_rows": 26203
      }
    },
    "generated_by_package": "P0056A",
    "missing_areas": [],
    "ok": true,
    "old_physical_balance_target_used": false,
    "source_table": "area_consumption_hourly_v1",
    "target_column": "consumption_mw",
    "unit": "MW hourly mean"
  },
  "total_jobs": 6,
  "weather_contract": {
    "areas": {
      "FI": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T23:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35064,
        "snow_depth_available": false
      },
      "SE1": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T23:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35064,
        "snow_depth_available": false
      },
      "SE2": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T23:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35064,
        "snow_depth_available": false
      }
    },
    "fallback_areas": [],
    "generated_by_package": "P0056D",
    "input_classification": "historical_observed_only_weather_actual_proxy",
    "ok": true,
    "production_weather_forecast": false,
    "proxy_label": "weather_actual_as_forecast_proxy_p0056d_openmeteo_zone_weighted",
    "snow_depth_available": false,
    "source_table": "area_weather_features_hourly_p0056d_v1"
  }
}
```
