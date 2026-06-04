# P0053A time normalization and DST

ENTSO-E timestamps are stored as UTC `...Z`. Joins normalize both `...Z` and `...+00:00` text forms before matching. Fixed-CET fields remain UTC+1 all year for continuity with prior model datasets.
