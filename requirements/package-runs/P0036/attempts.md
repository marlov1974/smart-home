# P0036 attempts

## Attempt 1

Result: PASS.

Actions:

- Replaced the primary M4 residual model with bounded `HistGradientBoostingRegressor`.
- Built strict train-only M1 baselines for raw actual and M3AB-normalized targets.
- Removed `days_since_start_scaled` and polynomial feature expansion from the primary schema/path.
- Added quality-gated staging/active promotion.
- Ran local P0036 backtest against `~/.smart-home/data/spotprice_model_features.sqlite3`.

Verification:

```text
python3 -B -m unittest tests.mac.services.spotprice_ml_model.test_core
python3 -B -m src.mac.services.spotprice_ml_model backtest-m4
```

Notes:

- The first local backtest attempt was blocked by sandbox write permissions for `~/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3`.
- The same command was rerun with approved escalation for local model artifact writes.
- No Shelly, Home Assistant, KVS or device calls were made.
