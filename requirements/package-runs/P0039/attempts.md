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

## Follow-up Correction

The first P0039 implementation interpreted M1B as the evaluated base for the sequential chain. The operator clarified that M1B should only be used for training/normalizing the component deltas, while M1 remains the price baseplate.

Corrected behavior:

```text
train M3A_m1b from actual - M1B
train M3B_m1b from actual - M1B - M3A_m1b
evaluate/predict as M1 + M3A_m1b + M3B_m1b
```

Evidence and tests were regenerated with variants:

```text
M1B_training_base_only
M1_M3A_m1b
M1_M3A_m1b_M3B_m1b
```
