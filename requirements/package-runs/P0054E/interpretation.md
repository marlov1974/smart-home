# P0054E LABB

Best direct holdout model: `LightGBM_G4_se4_load_weather` with MAE `17.70265003542135`.

Best weekly 168h model: `XGBoost_G4_se4_load_weather` with MAE `18.251117862247646`.

LightGBM/XGBoost versus ExtraTrees:

```json
{
  "LightGBM_G4_se4_load_weather": {
    "p0054d_extratrees_relative_holdout_MAE_percent": -4.878532400380407,
    "p0054d_extratrees_relative_weekly_MAE_full_168h_percent": -5.778430422691697,
    "same_run_minus_extratrees_holdout_MAE": -0.9079228269890898,
    "same_run_minus_extratrees_weekly_MAE_full_168h": -1.13286925637766,
    "same_run_relative_to_extratrees_holdout_MAE_percent": -4.87853240038037,
    "same_run_relative_to_extratrees_weekly_MAE_full_168h_percent": -5.778430422691663
  },
  "XGBoost_G4_se4_load_weather": {
    "p0054d_extratrees_relative_holdout_MAE_percent": -2.5803811246094015,
    "p0054d_extratrees_relative_weekly_MAE_full_168h_percent": -6.906455348113622,
    "same_run_minus_extratrees_holdout_MAE": -0.4802237093233117,
    "same_run_minus_extratrees_weekly_MAE_full_168h": -1.3540200992466715,
    "same_run_relative_to_extratrees_holdout_MAE_percent": -2.5803811246093646,
    "same_run_relative_to_extratrees_weekly_MAE_full_168h_percent": -6.906455348113588
  }
}
```

This is LABB evidence with realized weather used as `weather_actual_as_forecast_proxy`; it is not deployable candidate evidence.
