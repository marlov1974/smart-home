# P0048 Stage 1 classification results

## binary_positive_bottleneck

| group | validate precision/recall/F1 | holdout precision/recall/F1 | model |
|---|---|---|---|
| C0_time_calendar_baseline | 0.000000/0.000000/0.000000 | 0.000000/0.000000/0.000000 | weekday_hour_majority_baseline |
| C1_time_calendar_weather_actual | 0.841165/0.177193/0.292723 | 0.661710/0.117569/0.199663 | HistGradientBoostingClassifier |
| C2_time_calendar_weather_gradient | 0.831867/0.168481/0.280211 | 0.666667/0.095112/0.166474 | HistGradientBoostingClassifier |
| C3_time_calendar_weather_anomaly_gradient | 0.856707/0.166898/0.279370 | 0.618605/0.087847/0.153846 | HistGradientBoostingClassifier |
| C4_with_lagged_spread_features_diagnostic | 0.942685/0.836864/0.886628 | 0.924387/0.896301/0.910127 | HistGradientBoostingClassifier |

## binary_positive_spike

| group | validate precision/recall/F1 | holdout precision/recall/F1 | model |
|---|---|---|---|
| C0_time_calendar_baseline | 0.000000/0.000000/0.000000 | 0.000000/0.000000/0.000000 | weekday_hour_majority_baseline |
| C1_time_calendar_weather_actual | 0.175824/0.056805/0.085868 | 0.100000/0.006579/0.012346 | HistGradientBoostingClassifier |
| C2_time_calendar_weather_gradient | 0.257028/0.075740/0.117002 | 0.088235/0.019737/0.032258 | HistGradientBoostingClassifier |
| C3_time_calendar_weather_anomaly_gradient | 0.200000/0.068639/0.102203 | 0.173913/0.026316/0.045714 | HistGradientBoostingClassifier |
| C4_with_lagged_spread_features_diagnostic | 0.860963/0.762130/0.808537 | 0.825243/0.559211/0.666667 | HistGradientBoostingClassifier |

## multiclass_regime

| group | validate precision/recall/F1 | holdout precision/recall/F1 | model |
|---|---|---|---|
| C0_time_calendar_baseline | accuracy=0.267123, macro_f1=0.084324 | accuracy=0.328161, macro_f1=0.098832 | weekday_hour_majority_baseline |
| C1_time_calendar_weather_actual | accuracy=0.285046, macro_f1=0.142853 | accuracy=0.302299, macro_f1=0.110954 | DecisionTreeClassifier |
| C2_time_calendar_weather_gradient | accuracy=0.303425, macro_f1=0.157385 | accuracy=0.301149, macro_f1=0.124730 | DecisionTreeClassifier |
| C3_time_calendar_weather_anomaly_gradient | accuracy=0.289726, macro_f1=0.134945 | accuracy=0.333908, macro_f1=0.109074 | DecisionTreeClassifier |
| C4_with_lagged_spread_features_diagnostic | accuracy=0.811644, macro_f1=0.616899 | accuracy=0.809195, macro_f1=0.611261 | DecisionTreeClassifier |
