# P0050 local SE3 price rank features

```json
{
  "day_rank": "complete fixed-CET model date, explanatory behavioral feature, rank 1 is most expensive with timestamp tie-break",
  "oracle_fields": [
    "hours_until_next_bottom4_day_hour_if_known_oracle",
    "hours_until_next_bottom8_day_hour_if_known_oracle",
    "no_bottom4_recovery_window_next_12h_if_known_oracle",
    "no_bottom8_recovery_window_next_24h_if_known_oracle"
  ],
  "oracle_policy": "forward-known recovery fields are explanatory only and not deployable",
  "trailing_48h_rank": "current plus previous 47 rows, backward-looking/causal-style"
}
```

Forward-known recovery fields are suffixed `_oracle` and are explanatory only, not deployable.
