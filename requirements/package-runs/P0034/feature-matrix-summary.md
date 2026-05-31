# P0034 feature matrix summary

Command:

```bash
python3 -m src.mac.services.spotprice_ml_model build-features-m4 --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 --model-dir /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
```

Result:

```json
{
  "ok": true,
  "row_count": 34944,
  "feature_count": 14,
  "model_db": "/Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4/m4_model.sqlite3"
}
```

Feature schema:

```text
intercept
hour_sin
hour_cos
weekday_sin
weekday_cos
day_of_year_sin
day_of_year_cos
iso_week_sin
iso_week_cos
month_sin
month_cos
is_weekend
week_of_month
days_since_start_scaled
```

Forbidden weather/temperature features:

```text
none
```

Split counts:

```text
train = 22729
validate = 8760
holdout = 3455
```
