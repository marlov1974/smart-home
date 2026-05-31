# P0033 training foundation summary

## Generated feature DB

```text
path = /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
size = 158M
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
  "run_id": 4,
  "feature_db": "/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3"
}
```

## Output table counts

```text
model_runs: 4
m1_normal_price_v1: 69888
m2_climate_anomalies: 314496
m2_climate_normals: 314496
m2_climate_weights: 17
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

## M1/M2 anti-year-memorization

M1 and M2 normal surfaces do not condition on year. The rebuilt feature DB stores `bucket_year_count` as diagnostic coverage only.

Observed local coverage:

```text
M1 bucket_year_count: min 4, max 5, avg 4.1043956043956
M2 bucket_year_count: min 4, max 5, avg 4.05494505494505
```

## Area-diff local temperature delta

P0033 stores `se3_load_temperature` as an M2 signal, but uses `temp_gradient_se3_load_minus_se1_core` as the primary M3 anomaly signal for `area_diff_proxy_se3`.

```text
area_diff_proxy_se3 anomaly_signal = temp_gradient_se3_load_minus_se1_core
```

Reason: the area-diff target is a SE3-SE1 spread, so local weather pressure is represented by SE3-load temperature deviating relative to SE1-core temperature.
