# P0054E LABB

```json
{
  "ExtraTrees_G4_se4_load_weather": {
    "available": true,
    "method": "model_feature_importances_",
    "top": [
      {
        "feature": "consumption_se4_roll_min_24h",
        "importance": 0.11578069252023081
      },
      {
        "feature": "consumption_se4_roll_mean_6h",
        "importance": 0.11237333254614021
      },
      {
        "feature": "consumption_se4_roll_mean_12h",
        "importance": 0.10366673249750981
      },
      {
        "feature": "consumption_se4_roll_mean_48h",
        "importance": 0.07260303150310832
      },
      {
        "feature": "consumption_se4_roll_mean_168h",
        "importance": 0.07067911277950135
      },
      {
        "feature": "consumption_se4_roll_mean_24h",
        "importance": 0.0668243534740213
      },
      {
        "feature": "consumption_se4_lag_1h",
        "importance": 0.05846904517966584
      },
      {
        "feature": "consumption_se4_lag_12h",
        "importance": 0.05775986176794581
      },
      {
        "feature": "consumption_se4_roll_max_24h",
        "importance": 0.04584269668977823
      },
      {
        "feature": "consumption_se4_lag_3h",
        "importance": 0.04370463776661998
      },
      {
        "feature": "consumption_se4_lag_6h",
        "importance": 0.04311447318673636
      },
      {
        "feature": "consumption_se4_lag_24h",
        "importance": 0.03760289933019124
      },
      {
        "feature": "consumption_se4_lag_2h",
        "importance": 0.030991800651642636
      },
      {
        "feature": "consumption_se4_lag_48h",
        "importance": 0.029098354611641706
      },
      {
        "feature": "consumption_se4_lag_72h",
        "importance": 0.014751139645775867
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.013566903358135075
      },
      {
        "feature": "consumption_se4_roll_std_24h",
        "importance": 0.008796316855447196
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se4",
        "importance": 0.007933383937679728
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se4",
        "importance": 0.007405007769131605
      },
      {
        "feature": "consumption_se4_lag_168h",
        "importance": 0.006568134511245411
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.006546111418170481
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se4",
        "importance": 0.005843931447788551
      },
      {
        "feature": "target_model_cet_hour",
        "importance": 0.005334955969590987
      },
      {
        "feature": "weather_proxy_apparent_temperature_se4",
        "importance": 0.005202233744820621
      },
      {
        "feature": "weather_proxy_temperature_2m_se4",
        "importance": 0.00520056717204458
      }
    ]
  },
  "LightGBM_G4_se4_load_weather": {
    "available": true,
    "method": "model_feature_importances_",
    "top": [
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 3010.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 2654.0
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 2611.0
      },
      {
        "feature": "target_model_cet_hour",
        "importance": 2411.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 2145.0
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se4",
        "importance": 2105.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se4",
        "importance": 2048.0
      },
      {
        "feature": "weather_proxy_wind_100m_se4",
        "importance": 1978.0
      },
      {
        "feature": "weather_proxy_humidity_se4",
        "importance": 1741.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se4",
        "importance": 1549.0
      },
      {
        "feature": "consumption_se4_lag_1h",
        "importance": 1532.0
      },
      {
        "feature": "consumption_se4_roll_mean_168h",
        "importance": 1423.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se4",
        "importance": 1387.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se4",
        "importance": 1348.0
      },
      {
        "feature": "target_hour_sin",
        "importance": 1338.0
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se4",
        "importance": 1131.0
      },
      {
        "feature": "target_hour_cos",
        "importance": 1120.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se4",
        "importance": 844.0
      },
      {
        "feature": "weather_proxy_precipitation_se4",
        "importance": 722.0
      },
      {
        "feature": "horizon_h",
        "importance": 716.0
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 469.0
      },
      {
        "feature": "consumption_se4_lag_72h",
        "importance": 467.0
      },
      {
        "feature": "consumption_se4_lag_2h",
        "importance": 433.0
      },
      {
        "feature": "consumption_se4_roll_min_24h",
        "importance": 381.0
      },
      {
        "feature": "consumption_se4_roll_max_24h",
        "importance": 365.0
      }
    ]
  },
  "XGBoost_G4_se4_load_weather": {
    "available": true,
    "method": "model_feature_importances_",
    "top": [
      {
        "feature": "consumption_se4_lag_1h",
        "importance": 0.555890679359436
      },
      {
        "feature": "consumption_se4_lag_2h",
        "importance": 0.2602328658103943
      },
      {
        "feature": "consumption_se4_roll_max_24h",
        "importance": 0.055547744035720825
      },
      {
        "feature": "consumption_se4_roll_mean_6h",
        "importance": 0.01883424073457718
      },
      {
        "feature": "consumption_se4_roll_mean_168h",
        "importance": 0.016189705580472946
      },
      {
        "feature": "is_workday",
        "importance": 0.010916593484580517
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.010863874107599258
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.010600895620882511
      },
      {
        "feature": "is_weekend",
        "importance": 0.008897276595234871
      },
      {
        "feature": "consumption_se4_roll_min_24h",
        "importance": 0.0072982432320714
      },
      {
        "feature": "target_month",
        "importance": 0.005547475069761276
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se4",
        "importance": 0.005277054384350777
      },
      {
        "feature": "weather_proxy_apparent_temperature_se4",
        "importance": 0.003320726566016674
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.003041817108169198
      },
      {
        "feature": "consumption_se4_lag_12h",
        "importance": 0.002831017831340432
      },
      {
        "feature": "target_model_cet_hour",
        "importance": 0.002647395245730877
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.002594080986455083
      },
      {
        "feature": "weather_proxy_temperature_2m_se4",
        "importance": 0.002459583804011345
      },
      {
        "feature": "special_day_type=movable_public_holiday",
        "importance": 0.0019730785861611366
      },
      {
        "feature": "target_hour_sin",
        "importance": 0.0015051504597067833
      },
      {
        "feature": "is_holiday_period",
        "importance": 0.0013329720823094249
      },
      {
        "feature": "special_day_group=midsummer",
        "importance": 0.0012264227261766791
      },
      {
        "feature": "special_day_type=major_social_holiday",
        "importance": 0.0010960669023916125
      },
      {
        "feature": "is_major_social_holiday",
        "importance": 0.0009478703141212463
      },
      {
        "feature": "holiday_strength",
        "importance": 0.0008314072038047016
      }
    ]
  },
  "feature_group": [
    "horizon_h",
    "target_model_cet_hour",
    "target_model_cet_weekday",
    "target_model_cet_day_of_year",
    "target_month",
    "target_hour_sin",
    "target_hour_cos",
    "target_dayofyear_sin",
    "target_dayofyear_cos",
    "is_weekend",
    "is_workday",
    "is_holiday",
    "is_bridge_day",
    "is_holiday_period",
    "is_major_social_holiday",
    "holiday_strength",
    "special_day_type",
    "special_day_group",
    "consumption_se4_lag_1h",
    "consumption_se4_lag_2h",
    "consumption_se4_lag_3h",
    "consumption_se4_lag_6h",
    "consumption_se4_lag_12h",
    "consumption_se4_lag_24h",
    "consumption_se4_lag_48h",
    "consumption_se4_lag_72h",
    "consumption_se4_lag_168h",
    "consumption_se4_roll_mean_6h",
    "consumption_se4_roll_mean_12h",
    "consumption_se4_roll_mean_24h",
    "consumption_se4_roll_mean_48h",
    "consumption_se4_roll_mean_168h",
    "consumption_se4_roll_min_24h",
    "consumption_se4_roll_max_24h",
    "consumption_se4_roll_std_24h",
    "consumption_se4_ramp_1h",
    "consumption_se4_ramp_24h",
    "consumption_se4_same_hour_24h_vs_168h",
    "weather_proxy_temperature_2m_se4",
    "weather_proxy_apparent_temperature_se4",
    "weather_proxy_wind_100m_se4",
    "weather_proxy_cloud_cover_se4",
    "weather_proxy_shortwave_radiation_se4",
    "weather_proxy_precipitation_se4",
    "weather_proxy_snowfall_se4",
    "weather_proxy_humidity_se4",
    "weather_proxy_heating_degree_hours_se4",
    "weather_proxy_cooling_degree_hours_se4",
    "weather_proxy_train_normal_temperature_2m_se4",
    "weather_proxy_temperature_delta_from_train_normal_se4",
    "weather_proxy_cold_spell_flag_se4"
  ]
}
```
