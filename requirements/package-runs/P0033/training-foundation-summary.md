# P0033 training foundation summary

## Generated feature DB

```text
path = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
size = 146M
```

## Build result

Command:

```bash
python3 -m src.mac.services.spotprice_temperature_normalization build --price-db /Users/marcus.lovenstad/.smart-home/data/spotprice_history.sqlite3 --weather-db /Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3 --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 --start-date 2022-05-30
```

Result:

```json
{
  "ok": true,
  "start_date": "2022-05-30",
  "end_date": "2026-05-24",
  "row_count": 34944,
  "run_id": 2,
  "feature_db": "/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3"
}
```

## Output table counts

```text
model_runs: 2
m1_normal_price_v1: 69888
m2_climate_anomalies: 279552
m2_climate_normals: 279552
m2_climate_weights: 16
m3_temp_normalized_prices_v1: 34944
m3_temperature_delta_buckets: 10
m3_temperature_delta_v1: 69888
training_foundation_manifest: 13
```

## Scope confirmations

```text
M1 implemented: yes
M2 implemented: yes
M3 implemented: yes
M4/M5/M6/M7 implemented: no
full ML implemented: no
forecast API implemented: no
wind normalization in M3: no
device/Shelly/HA/KVS access: no
```
