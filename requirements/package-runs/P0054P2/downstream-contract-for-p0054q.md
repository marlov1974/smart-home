# Downstream Contract For P0054Q

```json
{
  "forecast_safety_class": "historical_observed_only_target",
  "join_key": [
    "timestamp_utc",
    "area"
  ],
  "source_type": "actual_total_load",
  "table": "entsoe_consumption_area_hourly_v1",
  "target_column": "consumption_mw",
  "usage": "Use as historical target only; any future use requires a separate forecast model."
}
```
