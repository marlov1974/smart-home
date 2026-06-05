# Table Schema

```json
{
  "columns": {
    "area": "SE1-SE4 bidding zone",
    "consumption_mw": "hourly mean MW",
    "package_id": "P0054P2",
    "resolution": "source resolution, with ->hourly_mean for aggregated subhourly data",
    "source_area_code": "ENTSO-E EIC bidding zone code",
    "source_measure": "actual_total_load",
    "source_system": "ENTSO-E",
    "timestamp_utc": "UTC hourly target timestamp",
    "timezone_handling": "source period timestamps normalized to UTC",
    "unit": "MW"
  },
  "primary_key": [
    "timestamp_utc",
    "area",
    "source_system",
    "source_measure",
    "package_id"
  ],
  "table": "entsoe_consumption_area_hourly_v1"
}
```
