# P0037 attempts

## Attempt 1

Result: WARN diagnostic completed.

Actions:

- Built analysis-only strict 2025 full-year component attribution.
- Recomputed train-only M1, M2 anomaly normals, M3A, M3B and M4 without 2025 holdout rows.
- Persisted required P0037 evidence files.

Verification:

```text
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0037
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0037
```

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device actions were performed.
