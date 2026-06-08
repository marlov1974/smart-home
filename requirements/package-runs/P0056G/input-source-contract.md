# P0056G Input Source Contract

```json
{
  "ok": true,
  "p0056b_weather_contract": {
    "areas": {
      "FI": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T21:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35062,
        "snow_depth_available": false
      },
      "SE1": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T21:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35062,
        "snow_depth_available": false
      },
      "SE2": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T21:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35062,
        "snow_depth_available": false
      },
      "SE3": {
        "fallback_weather_proxy": false,
        "max_timestamp_utc": "2026-05-31T21:00:00Z",
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "rows": 35062,
        "snow_depth_available": false
      }
    },
    "fallback_areas": [
      "DE_LU",
      "DK1",
      "EE",
      "LT",
      "LV",
      "NL",
      "PL"
    ],
    "generated_by_package": "P0056B",
    "input_classification": "historical_observed_only_weather_actual_proxy",
    "ok": true,
    "production_weather_forecast": false,
    "proxy_label": "weather_actual_as_forecast_proxy",
    "source_table": "area_weather_features_hourly_v1"
  },
  "p0056d_weather_contract": {
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
      },
      "SE3": {
        "duplicates": 0,
        "holdout_rows": 8905,
        "max_timestamp_utc": "2026-06-07T08:00:00Z",
        "mean_mw": 9488.860993432085,
        "median_mw": 9124.0,
        "min_timestamp_utc": "2022-06-01T00:00:00Z",
        "nonfinite_values": 0,
        "rows": 35171,
        "train_fit_rows": 26266
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
  "weather_source_by_area": {
    "FI": "P0056D",
    "SE1": "P0056D",
    "SE2": "P0056D",
    "SE3": "P0056B"
  }
}
```
