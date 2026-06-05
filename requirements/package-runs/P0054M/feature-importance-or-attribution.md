# P0054M LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "available": true,
    "top": [
      {
        "feature": "target_month",
        "importance": 0.2066655482446522
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.11021486352730035
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.08935713289404822
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.06208453906775841
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.04928638063889724
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.04638726838130996
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 0.045305647983952875
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.03419320386226289
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.03396458076445811
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.03385881934011258
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.0330709484735153
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.02626457771249475
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.02604989690273032
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.023070188063714057
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.023012895692524276
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.020506412089170464
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.019748487334761238
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.01507131624337195
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.013315051184628144
      },
      {
        "feature": "is_workday",
        "importance": 0.010341196108396117
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.009480208598620437
      },
      {
        "feature": "consumption_se3_roll_max_24h",
        "importance": 0.007596676817796343
      },
      {
        "feature": "is_weekend",
        "importance": 0.007195856362318688
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 0.0064998460163989925
      },
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 0.005126620310412481
      }
    ]
  },
  "ExtraTrees_with_p0054l2_ensemble_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "target_month",
        "importance": 0.20343154262759922
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.11552315232276984
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0787187710704821
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.05619602590286115
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.04748097705098049
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 0.04492296709937687
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.040329593760695746
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.035114186911717714
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.03234883505526393
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.03199648908116612
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.030223891316149044
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.028443639175698355
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.02599071246713992
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.025648451854631677
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.02186409613850934
      },
      {
        "feature": "price_forecast_peak_offpeak_indicator",
        "importance": 0.018412791898960806
      },
      {
        "feature": "consumption_se3_roll_mean_12h",
        "importance": 0.014898635374250284
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.014181534359221506
      },
      {
        "feature": "consumption_se3_roll_max_24h",
        "importance": 0.012004574884737631
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.011539496232059493
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.011536340523937118
      },
      {
        "feature": "consumption_se3_roll_mean_24h",
        "importance": 0.008336180626897728
      },
      {
        "feature": "is_workday",
        "importance": 0.00828132659750198
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.006238293741509062
      },
      {
        "feature": "is_weekend",
        "importance": 0.005774768975642596
      }
    ]
  },
  "HGB_no_price": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "HGB_with_p0054l2_ensemble_price_forecast": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "LightGBM_no_price": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 308.0
      },
      {
        "feature": "weather_proxy_wind_100m_se3",
        "importance": 254.0
      },
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 246.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 240.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se3",
        "importance": 235.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 227.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 195.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 137.0
      },
      {
        "feature": "horizon_h",
        "importance": 135.0
      },
      {
        "feature": "weather_proxy_precipitation_se3",
        "importance": 126.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 124.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 74.0
      },
      {
        "feature": "target_hour_sin",
        "importance": 63.0
      },
      {
        "feature": "is_workday",
        "importance": 57.0
      },
      {
        "feature": "target_hour_cos",
        "importance": 54.0
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 52.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 41.0
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 37.0
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 34.0
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 32.0
      },
      {
        "feature": "consumption_se3_ramp_1h",
        "importance": 32.0
      },
      {
        "feature": "consumption_se3_same_hour_24h_vs_168h",
        "importance": 32.0
      },
      {
        "feature": "consumption_se3_roll_std_24h",
        "importance": 31.0
      },
      {
        "feature": "consumption_se3_lag_168h",
        "importance": 28.0
      },
      {
        "feature": "consumption_se3_lag_48h",
        "importance": 27.0
      }
    ]
  },
  "LightGBM_with_p0054l2_ensemble_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 268.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 222.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 214.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se3",
        "importance": 203.0
      },
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 203.0
      },
      {
        "feature": "weather_proxy_wind_100m_se3",
        "importance": 181.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 135.0
      },
      {
        "feature": "price_forecast_rank_within_path",
        "importance": 132.0
      },
      {
        "feature": "price_forecast_ramp_from_previous_horizon",
        "importance": 126.0
      },
      {
        "feature": "price_forecast_horizon_value",
        "importance": 102.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 99.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 97.0
      },
      {
        "feature": "horizon_h",
        "importance": 79.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 79.0
      },
      {
        "feature": "weather_proxy_precipitation_se3",
        "importance": 65.0
      },
      {
        "feature": "target_hour_sin",
        "importance": 61.0
      },
      {
        "feature": "target_hour_cos",
        "importance": 53.0
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 50.0
      },
      {
        "feature": "price_forecast_0_168h_mean",
        "importance": 46.0
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 43.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 39.0
      },
      {
        "feature": "is_workday",
        "importance": 37.0
      },
      {
        "feature": "price_forecast_24_48h_mean",
        "importance": 37.0
      },
      {
        "feature": "consumption_se3_same_hour_24h_vs_168h",
        "importance": 33.0
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 30.0
      }
    ]
  },
  "XGBoost_no_price": {
    "available": true,
    "top": [
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.3454578220844269
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.2719990313053131
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.06004996970295906
      },
      {
        "feature": "is_workday",
        "importance": 0.043898437172174454
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.038954537361860275
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.028703885152935982
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.019929660484194756
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.01657152734696865
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.014741094782948494
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 0.014115983620285988
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.013529702089726925
      },
      {
        "feature": "is_weekend",
        "importance": 0.011792680248618126
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.011576317250728607
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.010840793140232563
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 0.010818078182637691
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.010497031733393669
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.007931205444037914
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.007229768671095371
      },
      {
        "feature": "target_month",
        "importance": 0.0066457088105380535
      },
      {
        "feature": "target_model_cet_hour",
        "importance": 0.00568964472040534
      },
      {
        "feature": "special_day_type=normal_saturday",
        "importance": 0.0043593901209533215
      },
      {
        "feature": "special_day_type=normal_sunday",
        "importance": 0.004115951247513294
      },
      {
        "feature": "target_hour_sin",
        "importance": 0.003997559193521738
      },
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 0.0035402916837483644
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.003521204460412264
      }
    ]
  },
  "XGBoost_with_p0054l2_ensemble_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "target_month",
        "importance": 0.2997187376022339
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.24518190324306488
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.17780114710330963
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.03991774469614029
      },
      {
        "feature": "is_weekend",
        "importance": 0.03208623453974724
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.028529858216643333
      },
      {
        "feature": "is_workday",
        "importance": 0.02295537479221821
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.019029829651117325
      },
      {
        "feature": "price_forecast_peak_offpeak_indicator",
        "importance": 0.01607552543282509
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.014439760707318783
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.012101114727556705
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.009077168069779873
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 0.008336898870766163
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.007059528026729822
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.006512096151709557
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.005989861208945513
      },
      {
        "feature": "price_forecast_rank_within_path",
        "importance": 0.004904811270534992
      },
      {
        "feature": "holiday_strength",
        "importance": 0.004733646288514137
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 0.004644133150577545
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.004029413219541311
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.003971109166741371
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.003945745062083006
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.003007367020472884
      },
      {
        "feature": "price_forecast_ramp_from_previous_horizon",
        "importance": 0.002287136623635888
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.0021113227121531963
      }
    ]
  }
}
```
