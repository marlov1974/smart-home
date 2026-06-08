# P0056G Weekly Emulation Protocol

- Time zone: Europe/Stockholm.
- Training cutoff: Monday 00:00 local boundary after prior Sunday, applied as `target_timestamp_utc < training_cutoff_utc`.
- Forecast origin: Monday 06:00 local.
- Delivery window: Monday 00:00 through Sunday 23:00 local.
- `full_week_168h` includes Monday 00:00-05:00 as nowcast/backcast hours.
- `forward_162h` includes Monday 06:00 through Sunday 23:00.
- First week: `2025-06-02`.
- Last week: `2026-05-25`.
