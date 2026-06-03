# P0052B time normalization and DST

ENTSO-E timestamps are stored as UTC `...Z`. Diagnostics joins normalize both `...Z` and `...+00:00` forms through SQLite datetime conversion. Fixed-CET fields remain UTC+1 all year.
