# P0051 time normalization and DST

Source `timestampUTC` is normalized to UTC and bucketed to hourly UTC keys. Fixed-CET fields use `timestamp_utc + 1h` all year. DST 23/25-hour local days do not affect primary keys because local civil time is not used as identity.
