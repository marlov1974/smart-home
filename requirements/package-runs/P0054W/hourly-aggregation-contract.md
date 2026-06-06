# P0054W hourly aggregation contract

Hourly aggregation was used only for SE3 volume sanity checking, not as source of truth.

Method:

```text
15m source MWh -> hourly MWh by sum(-value)
```

The negative source sign is inverted only for aggregate comparison against positive ENTSO-E load. Native rows in `esett_mga_consumption_native_v1` preserve the source sign.
