# P0054Y2 hourly aggregation contract

Native P0054W energy rows are stored as MWh and source-negative for load.

Aggregation:

```text
positive_hourly_MWh = sum(-source_value) by UTC hour
consumption_mw = positive_hourly_MWh over one hour
```

`settlement_class` remains `profiled_load_profile`.
