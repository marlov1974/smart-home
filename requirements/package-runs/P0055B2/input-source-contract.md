# P0055B2 input source contract

```json
{
  "aligned_hours": 22709,
  "cluster_table": "se3_profiled_mga_cluster_hourly_v1",
  "direct_table": "entsoe_consumption_area_hourly_v1",
  "end": "2026-06-05T10:00:00Z",
  "ok": true,
  "residual_table": "se3_consumption_metered_residual_hourly_v1",
  "start": "2023-10-31T23:00:00Z",
  "weather_contract": {
    "end": "2026-05-31T21:00:00Z",
    "generated_by_package": "P0054Z",
    "input_classification": "proxy",
    "proxy_label": "weather_actual_as_forecast_proxy",
    "rows_by_zone": {
      "SE3_BROAD_PROXY": 35062,
      "SE3_EAST_COAST_MALARDALEN_STOCKHOLM": 35062,
      "SE3_NORTHERN_INLAND": 35062,
      "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND": 35062,
      "SE3_WEST_COAST_GOTHENBURG": 35062
    },
    "start": "2022-06-01T00:00:00Z",
    "table": "se3_climate_zone_weather_hourly_v1",
    "zones": [
      "SE3_BROAD_PROXY",
      "SE3_EAST_COAST_MALARDALEN_STOCKHOLM",
      "SE3_NORTHERN_INLAND",
      "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND",
      "SE3_WEST_COAST_GOTHENBURG"
    ]
  }
}
```
