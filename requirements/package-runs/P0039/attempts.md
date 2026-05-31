# P0039 Attempts

## Attempt 1

Implemented P0039 as a Mac-side diagnostics package:

- added `src/mac/services/spotprice_model_diagnostics/p0039.py`
- added `tests/mac/services/spotprice_model_diagnostics/test_p0039.py`
- updated `docs/functions/mac/spotprice-ml-normal-model.md`
- generated required P0039 evidence under `requirements/package-runs/P0039/`

Initial sandboxed P0039 analysis failed when writing the local feature DB:

```text
sqlite3.OperationalError: attempt to write a readonly database
```

The same analysis was rerun with explicit escalation for local `~/.smart-home` database writes and completed:

```text
status = WARN
train = 13945
validate = 8784
holdout = 8760
future = 3479
```

Local diagnostic table counts after the rerun:

```text
m1b_holiday_clean_normal_price = 31489
m1b_training_row_policy = 31489
m3a_temperature_delta_m1b = 62978
m3b_special_day_delta_m1b = 62978
m3abcd_normalized_prices_m1b = 31489
```

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
