# P0052 time normalization and DST

SvK `ticks` are epoch milliseconds and are normalized to UTC. Quarter-hour MW values are aggregated to hourly mean MW. Fixed-CET fields use `timestamp_utc + 1h` all year, so DST 23/25-hour local days do not change the primary key.
