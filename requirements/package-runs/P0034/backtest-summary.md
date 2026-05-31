# P0034 backtest summary

Command:

```bash
python3 -m src.mac.services.spotprice_ml_model backtest-m4 --feature-db /Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3 --model-dir /Users/marcus.lovenstad/.smart-home/data/spotprice_ml_models/m4
```

## Model

```text
model_version = m4_sklearn_polynomial_ridge_v2
algorithm = sklearn_polynomial_features_ridge
features = 14 calendar/slow-trend features, expanded to degree 2 inside sklearn pipeline
random_seed = none used by Ridge; pipeline is deterministic
```

## Split

```text
train:    2022-05-30..2024-12-31, rows = 22729
validate: 2025-01-01..2025-12-31, rows = 8760
holdout:  2026-01-01..2026-05-24, rows = 3455
```

## Hourly M4 metrics

```text
system_proxy_se1:
  validate MAE = 0.3528195341162272
  validate RMSE = 0.46054628650885504
  holdout MAE = 0.5955499675395327
  holdout RMSE = 0.7683190174304994

area_diff_proxy_se3:
  validate MAE = 0.5473248439196239
  validate RMSE = 0.6920127067810532
  holdout MAE = 1.8329536040834036
  holdout RMSE = 1.8847956763097777

recomposed_se3:
  validate MAE = 0.5894016049668596
  validate RMSE = 0.7219547613721147
  holdout MAE = 1.6277238925618174
  holdout RMSE = 1.8226038667974305
```

## Level metrics

```text
system_proxy_se1:
  validate week MAE = 0.31035215528902216
  validate week RMSE = 0.36850410883600065
  validate month MAE = 0.28357115293266727
  validate month RMSE = 0.3207320766160648
  holdout week MAE = 0.5122083103454314
  holdout week RMSE = 0.641117004359569
  holdout month MAE = 0.46691726105832004
  holdout month RMSE = 0.577284981183712

area_diff_proxy_se3:
  validate week MAE = 0.42573690775052087
  validate week RMSE = 0.5645209416864667
  validate month MAE = 0.4249221769783483
  validate month RMSE = 0.5535319433126531
  holdout week MAE = 1.8204474183871173
  holdout week RMSE = 1.8290741826451842
  holdout month MAE = 1.833699195358216
  holdout month RMSE = 1.8372697780570382
```

## Curve-index metrics

```text
system_proxy_se1:
  validate week MAE = 1.9226953745051973
  validate week RMSE = 3.8550933134231817
  validate month MAE = 1.4901612605876562
  validate month RMSE = 2.2378272854499732
  holdout week MAE = 2.2211370565726325
  holdout week RMSE = 6.426912798459319
  holdout month MAE = 1.160191494454649
  holdout month RMSE = 1.5632991141042716

area_diff_proxy_se3:
  validate week MAE = 0.8003157169011603
  validate week RMSE = 1.0921595607509291
  validate month MAE = 0.8223974625418778
  validate month RMSE = 1.1170265588901278
  holdout week MAE = 1.0644801606909382
  holdout week RMSE = 1.8417655219874325
  holdout month MAE = 0.9767511137275435
  holdout month RMSE = 1.3696159141968047
```

Assessment: P0034 now uses scikit-learn and rebuilds successfully, but holdout metrics remain worse than the P0033 M1 baseline. Result classification is `WARN`, not production replacement quality.
