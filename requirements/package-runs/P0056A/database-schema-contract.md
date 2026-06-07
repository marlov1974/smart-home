# P0056A database schema contract

```json
{
  "catalog_table": "area_consumption_area_catalog_v1",
  "generated_by_package": "P0056A",
  "hourly_primary_key": [
    "timestamp_utc",
    "area_code",
    "source_system",
    "generated_by_package"
  ],
  "hourly_table": "area_consumption_hourly_v1",
  "native_primary_key": [
    "area_code",
    "interval_start_utc",
    "interval_end_utc",
    "value_kind",
    "source_system",
    "generated_by_package"
  ],
  "native_table": "area_consumption_native_v1"
}
```
