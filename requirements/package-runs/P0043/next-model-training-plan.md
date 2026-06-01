# P0043 next model training plan

P0044 should train AI-1 next if ChatGPT accepts P0043 metrics. AI-2 now has trained SE1 and area_diff diagnostics on the corrected P0042 fixed-CET dataset. SE1 selected F4_full; area_diff selected F2_time_calendar_weather_actual because it has the best validation MAE and better holdout MAE/Spearman/bottom3 than F0. The next missing piece is day-to-local-week shape/scale.
