# P0054W SE3 volume sanity check

```json
{
  "aggregation_method": "15m source MWh summed to hourly MWh; numeric value is comparable to average MW over one hour",
  "avg_entsoe_mw": 9807.542648289225,
  "avg_mga_hour_mwh": 2345.319130910388,
  "avg_ratio": 0.23219546472003358,
  "comparison": "sum(-eSett_MGA_LoadProfile_MWh_per_hour) versus ENTSO-E SE3 actual_total_load MW",
  "interpretation": "EXP18 LoadProfile is materially below ENTSO-E SE3 actual total load; treat it as profiled/load-profile component, not total SE3 consumption.",
  "joined_hours": 22709,
  "max_mga_count_per_hour": 170,
  "max_ratio": 0.39485972977851835,
  "max_timestamp": "2026-06-05T10:00:00Z",
  "min_mga_count_per_hour": 132,
  "min_ratio": 0.0,
  "min_timestamp": "2023-10-31T23:00:00Z"
}
```
