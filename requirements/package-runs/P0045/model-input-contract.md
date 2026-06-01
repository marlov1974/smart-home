# P0045 model input contract

P0043/P0044 binary models were not committed. P0045 regenerates evaluation predictions deterministically from corrected P0042 train rows and the stored selected feature groups.

AI-2 source: P0043 selected groups `system_proxy_se1=F4_full`, `area_diff_proxy_se3=F2_time_calendar_weather_actual`; target is `hour_shape`.

AI-1 source: P0044 selected groups/fallbacks; targets are `day_level_shape`, `log_day_scale_index`, `log_local_7d_scale`.

This is artifact regeneration for historical evaluation, not new AI model development or hyperparameter selection.
