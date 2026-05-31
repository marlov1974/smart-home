# P0034 backtest summary

Command:

```bash
python3 -m src.mac.services.spotprice_ml_model backtest-m4 --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 --model-dir /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
```

## Split

```text
train:    2022-05-30..2024-12-31
validate: 2025-01-01..2025-12-31
holdout:  2026-01-01..2026-05-24
```

## Hourly M4 metrics

```text
system_proxy_se1:
  validate MAE = 0.2839128397234254
  validate RMSE = 0.4127636783422947
  holdout MAE = 0.7557426179825617
  holdout RMSE = 0.9004664171632266

area_diff_proxy_se3:
  validate MAE = 0.595734560494431
  validate RMSE = 0.7160904861715117
  holdout MAE = 0.8419591554396414
  holdout RMSE = 0.9125707992013449

recomposed_se3:
  validate MAE = 0.8275429465193468
  validate RMSE = 0.9479903872356269
  holdout MAE = 1.5972354402476179
  holdout RMSE = 1.6663916698473933
```

## Level metrics

```text
system_proxy_se1:
  validate MAE = 0.2392452608983912
  holdout MAE = 0.7585623183911553

area_diff_proxy_se3:
  validate MAE = 0.590180737507082
  holdout MAE = 0.835729269002431
```

## Curve-index metrics

```text
system_proxy_se1:
  validate MAE = 3.7461861418058207
  holdout MAE = 0.7802954714990695

area_diff_proxy_se3:
  validate MAE = 1.0564133676111724
  holdout MAE = 1.0488384838117089
```

Assessment: P0034 successfully creates reproducible M4 artifacts and metrics, but the pure-Python Ridge baseline is not better than P0033 M1 on holdout. This is expected risk from the dependency fallback and should be improved in a later package with a stronger model class.
