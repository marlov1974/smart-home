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

## Holdout hourly comparison

| target | metric | M4 sklearn | P0033 M1 | delta M4-M1 | winner |
|---|---:|---:|---:|---:|---|
| system_proxy_se1 | MAE | 0.5955499675395327 | 0.3430024913169314 | 0.2525474762226013 | P0033 M1 |
| system_proxy_se1 | RMSE | 0.7683190174304994 | 0.48352073558571185 | 0.2847982818447876 | P0033 M1 |
| area_diff_proxy_se3 | MAE | 1.8329536040834036 | 0.20408917583212727 | 1.6288644282512764 | P0033 M1 |
| area_diff_proxy_se3 | RMSE | 1.8847956763097777 | 0.29430242065818596 | 1.5904932556515918 | P0033 M1 |
| recomposed_se3 | MAE | 1.6277238925618174 | 0.39073463277858034 | 1.236989259783237 | P0033 M1 |
| recomposed_se3 | RMSE | 1.8226038667974305 | 0.5037357192319121 | 1.3188681475655184 | P0033 M1 |

## Holdout level comparison

| target | metric scope | metric | M4 sklearn | P0033 M1 | delta M4-M1 | winner |
|---|---|---:|---:|---:|---:|---|
| system_proxy_se1 | week level | MAE | 0.5122083103454314 | 0.277581889525318 | 0.23462642082011338 | P0033 M1 |
| system_proxy_se1 | week level | RMSE | 0.641117004359569 | 0.35468130617359367 | 0.2864356981859753 | P0033 M1 |
| system_proxy_se1 | month level | MAE | 0.46691726105832004 | 0.2644712680472346 | 0.20244599301108543 | P0033 M1 |
| system_proxy_se1 | month level | RMSE | 0.577284981183712 | 0.3068883190278867 | 0.2703966621558253 | P0033 M1 |
| area_diff_proxy_se3 | week level | MAE | 1.8204474183871173 | 0.15250283211319704 | 1.6679445862739203 | P0033 M1 |
| area_diff_proxy_se3 | week level | RMSE | 1.8290741826451842 | 0.1784245975631708 | 1.6506495850820134 | P0033 M1 |
| area_diff_proxy_se3 | month level | MAE | 1.833699195358216 | 0.12877349115751635 | 1.7049257042006997 | P0033 M1 |
| area_diff_proxy_se3 | month level | RMSE | 1.8372697780570382 | 0.15667058475188234 | 1.6805991933051558 | P0033 M1 |

## Holdout curve-index comparison

| target | metric scope | metric | M4 sklearn | P0033 M1 | delta M4-M1 | winner |
|---|---|---:|---:|---:|---:|---|
| system_proxy_se1 | week curve index | MAE | 2.2211370565726325 | 0.4737497337069649 | 1.7473873228656677 | P0033 M1 |
| system_proxy_se1 | week curve index | RMSE | 6.426912798459319 | 0.6588152814779519 | 5.768097516981367 | P0033 M1 |
| system_proxy_se1 | month curve index | MAE | 1.160191494454649 | 0.5427705767162805 | 0.6174209177383685 | P0033 M1 |
| system_proxy_se1 | month curve index | RMSE | 1.5632991141042716 | 0.7438427018373691 | 0.8194564122669025 | P0033 M1 |
| area_diff_proxy_se3 | week curve index | MAE | 1.0644801606909382 | 1.1646626040015942 | -0.10018244331065598 | M4 sklearn |
| area_diff_proxy_se3 | week curve index | RMSE | 1.8417655219874325 | 1.9490726728797394 | -0.10730715089230693 | M4 sklearn |
| area_diff_proxy_se3 | month curve index | MAE | 0.9767511137275435 | 1.0552730780183368 | -0.07852196429079337 | M4 sklearn |
| area_diff_proxy_se3 | month curve index | RMSE | 1.3696159141968047 | 1.553164003188756 | -0.1835480889919514 | M4 sklearn |

## Status

`WARN`: M4 sklearn is reproducible and uses the requested dependency, but P0033 M1 wins the key holdout hourly and level metrics. M4 should remain a research artifact until a later model improves holdout quality.
