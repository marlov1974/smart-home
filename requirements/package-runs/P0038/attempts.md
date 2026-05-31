# P0038 attempts

## Attempt 1

Result: WARN.

Actions:

- Added P0038 weather proxy locations.
- Ran local Open-Meteo backfill for P0038 proxy groups.
- Built M3C/M3D diagnostics and M3ABCD normalized local feature tables.
- Evaluated 2025 full-year holdout and M4 area-only policy.

Verification:

```text
python3 -B -m src.mac.services.weather_history init-db
python3 -B -m src.mac.services.weather_history backfill --start-date 2022-05-30 --end-date 2025-12-31
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0038
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0038
```

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device actions were performed.
