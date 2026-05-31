# P0034 baseline comparison

Baseline:

```text
P0033 M1 normal_price_v1
```

Older index predecessor:

```text
src.mac.services.spot_forecast
```

The older index service is a 21-period weekly index provider, not a like-for-like hourly SE1/area-diff model. P0034 records it as architectural predecessor; numeric comparison uses P0033 M1.

## Holdout MAE

```text
system_proxy_se1:
  M4 Ridge = 0.7557426179825617
  P0033 M1 = 0.3430024913169314

area_diff_proxy_se3:
  M4 Ridge = 0.8419591554396414
  P0033 M1 = 0.20408917583212727

recomposed_se3:
  M4 Ridge = 1.5972354402476179
  P0033 M1 = 0.39073463277858034
```

## Validation MAE

```text
system_proxy_se1:
  M4 Ridge = 0.2839128397234254
  P0033 M1 = 0.23420638213470302

area_diff_proxy_se3:
  M4 Ridge = 0.595734560494431
  P0033 M1 = 0.27243155707762545

recomposed_se3:
  M4 Ridge = 0.8275429465193468
  P0033 M1 = 0.3043555941780826
```

Conclusion: P0034 is a working reproducible M4 training/backtest foundation, but the fallback Ridge model is not production-quality and should not replace P0033 M1 as the best normal model yet.
