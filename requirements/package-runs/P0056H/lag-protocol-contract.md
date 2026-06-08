# P0056H Lag Protocol Contract

- `L1_origin_known_fallback`: lag values that point into the forecast window are replaced with same-hour seasonal fallback values and flagged through unavailable counters.
- `L2_recursive_lags`: lag values that point into earlier forecast-window hours use the model's own previous forecast when available; otherwise they fall back like L1.
- Primary result excludes future actual load lag leakage.
- Oracle future-actual lag sensitivity was not run.
