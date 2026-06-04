# P0054H Verification Results

Generation command:

```text
python3 -m src.mac.services.spotprice_model_diagnostics.p0054h
```

Generation status:

```text
WARN
```

Rows persisted:

```text
240912
```

Final `git diff --check` and large-artifact checks are recorded in the final package report after command execution.

Executed checks:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054h: pass
python3 -m src.mac.services.spotprice_model_diagnostics.p0054h: WARN, 240912 rows persisted
SQLite schema check for anchored_absolute_price_forecast_log_p0054h_se1_v1: pass
SQLite row/origin/range check: 240912 rows, 1434 origins, 2022-06-01T23:00:00Z..2026-05-25T22:00:00Z
SQLite leakage-order check: 0 cutoff/origin/history/training/source violations, horizons 0..167
requirements/package-runs/P0054H size: 316K
```
