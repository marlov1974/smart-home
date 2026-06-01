# P0041 leakage and window policy

AI-1 window policy: the local seven-day period is exactly D-2..D+4. Rows without all 168 hourly prices and complete daily weather aggregates are skipped.
Year boundary policy: D-2..D+4 uses continuous date arithmetic and is allowed to cross calendar years. P0041 skipped-center evidence verifies that no rows are skipped solely because a window crosses December/January.
AI-2 window policy: the intraday period is exactly local 00:00..23:00. Only complete 24-hour local days are emitted.
No raw `week_of_year` categorical feature is emitted. Cyclic day and weekday encodings are emitted.
M2 normal weather surfaces aggregate calendar buckets across all available years with +/-14 day smoothing and include `year_count` per bucket. They are climate/signal normals, not price baselines.
P0041 does not train models or evaluate holdout performance, so model-fitting leakage is deferred to P0042.
