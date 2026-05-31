# P0040 Attempts

## Attempt 1

Implemented P0040 as a Mac-side diagnostics package:

- added `src/mac/services/spotprice_model_diagnostics/p0040.py`
- added `tests/mac/services/spotprice_model_diagnostics/test_p0040.py`
- generated required P0040 evidence under `requirements/package-runs/P0040/`

The implementation uses a strict static pre-backtest component fit:

```text
fit rows = P0037 train split ending 2023-12-31
primary origins = 2025-06-02..2026-05-18
forecast origins = 50
weather_oracle = actual_weather_used_as_forecast_proxy
```

This differs from the initial expanding-window design, but still prevents forecast-horizon spot leakage for P0040 because all component fits end before the primary origin range. The deviation is documented in `design.md`.

Result:

```text
status = WARN
reason = V0 naive flat 16h-anchored week beat all component variants on anchored absolute recomposed SE3 MAE
```

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
