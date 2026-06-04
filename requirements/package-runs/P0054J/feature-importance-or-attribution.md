# P0054J LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se1_lag_1h",
        "importance": 0.27132799845491606
      },
      {
        "feature": "consumption_se1_roll_min_24h",
        "importance": 0.24885751421112953
      },
      {
        "feature": "consumption_se1_roll_mean_12h",
        "importance": 0.07696581347881389
      },
      {
        "feature": "consumption_se1_lag_3h",
        "importance": 0.0557920093867867
      },
      {
        "feature": "consumption_se1_roll_mean_48h",
        "importance": 0.04341821169582911
      },
      {
        "feature": "consumption_se1_lag_12h",
        "importance": 0.04279603614219338
      },
      {
        "feature": "consumption_se1_roll_mean_6h",
        "importance": 0.041096574444617145
      },
      {
        "feature": "consumption_se1_roll_mean_24h",
        "importance": 0.039089700374655985
      },
      {
        "feature": "consumption_se1_lag_24h",
        "importance": 0.03821581200946162
      },
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 0.037251333116035484
      },
      {
        "feature": "consumption_se1_lag_2h",
        "importance": 0.03406123381237458
      },
      {
        "feature": "consumption_se1_lag_6h",
        "importance": 0.028328241061469913
      },
      {
        "feature": "consumption_se1_roll_max_24h",
        "importance": 0.023694566297030404
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.002337172615381076
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 0.002033497332020483
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 0.0014783967587901547
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 0.0014000913983120435
      },
      {
        "feature": "consumption_se1_lag_72h",
        "importance": 0.001292369148682813
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.001233781809089771
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 0.0011957036129791425
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.0010693370654077607
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0008815268607060221
      },
      {
        "feature": "consumption_se1_lag_168h",
        "importance": 0.0005962344379345598
      },
      {
        "feature": "consumption_se1_lag_48h",
        "importance": 0.0005497856696361386
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se1",
        "importance": 0.0004426401124577342
      }
    ]
  },
  "ExtraTrees_with_p0054h_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se1_lag_1h",
        "importance": 0.2127204092225675
      },
      {
        "feature": "consumption_se1_roll_min_24h",
        "importance": 0.19581268434066534
      },
      {
        "feature": "consumption_se1_roll_mean_6h",
        "importance": 0.0709563059392407
      },
      {
        "feature": "consumption_se1_roll_mean_24h",
        "importance": 0.07063481702727978
      },
      {
        "feature": "consumption_se1_roll_mean_12h",
        "importance": 0.06022304450794346
      },
      {
        "feature": "consumption_se1_lag_12h",
        "importance": 0.05873614366260789
      },
      {
        "feature": "consumption_se1_lag_3h",
        "importance": 0.05555698976731919
      },
      {
        "feature": "consumption_se1_roll_max_24h",
        "importance": 0.05419306005828914
      },
      {
        "feature": "consumption_se1_lag_24h",
        "importance": 0.0537503069279549
      },
      {
        "feature": "consumption_se1_lag_2h",
        "importance": 0.040270395034672744
      },
      {
        "feature": "consumption_se1_roll_mean_48h",
        "importance": 0.03433332765250885
      },
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 0.03401529968962986
      },
      {
        "feature": "consumption_se1_lag_6h",
        "importance": 0.02312216648065578
      },
      {
        "feature": "consumption_se1_lag_48h",
        "importance": 0.011193319287124472
      },
      {
        "feature": "consumption_se1_lag_72h",
        "importance": 0.005963404230491777
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.002366969986123087
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 0.0018831466161394587
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 0.0016765286514201902
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 0.0014554542390353407
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 0.0012843200218615005
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.0012008091914035004
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.0010480617567705205
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0009395723996166083
      },
      {
        "feature": "consumption_se1_lag_168h",
        "importance": 0.0008383288362041604
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se1",
        "importance": 0.0004526119234380655
      }
    ]
  },
  "HGB_no_price": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "HGB_with_p0054h_price_forecast": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "LightGBM_no_price": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_cloud_cover_se1",
        "importance": 1954.0
      },
      {
        "feature": "weather_proxy_wind_100m_se1",
        "importance": 1907.0
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se1",
        "importance": 1874.0
      },
      {
        "feature": "weather_proxy_humidity_se1",
        "importance": 1819.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 1450.0
      },
      {
        "feature": "weather_proxy_precipitation_se1",
        "importance": 1373.0
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 1354.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 1143.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 1110.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 1060.0
      },
      {
        "feature": "horizon_h",
        "importance": 884.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 827.0
      },
      {
        "feature": "weather_proxy_snowfall_se1",
        "importance": 712.0
      },
      {
        "feature": "consumption_se1_same_hour_24h_vs_168h",
        "importance": 694.0
      },
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 628.0
      },
      {
        "feature": "consumption_se1_ramp_1h",
        "importance": 609.0
      },
      {
        "feature": "consumption_se1_ramp_24h",
        "importance": 602.0
      },
      {
        "feature": "consumption_se1_roll_std_24h",
        "importance": 563.0
      },
      {
        "feature": "consumption_se1_lag_168h",
        "importance": 541.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 508.0
      },
      {
        "feature": "consumption_se1_lag_1h",
        "importance": 488.0
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se1",
        "importance": 456.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 436.0
      },
      {
        "feature": "consumption_se1_lag_72h",
        "importance": 402.0
      },
      {
        "feature": "consumption_se1_lag_48h",
        "importance": 309.0
      }
    ]
  },
  "LightGBM_with_p0054h_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se1",
        "importance": 1543.0
      },
      {
        "feature": "weather_proxy_wind_100m_se1",
        "importance": 1527.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se1",
        "importance": 1509.0
      },
      {
        "feature": "weather_proxy_humidity_se1",
        "importance": 1497.0
      },
      {
        "feature": "price_forecast_horizon_value",
        "importance": 1460.0
      },
      {
        "feature": "price_forecast_ramp_from_previous_horizon",
        "importance": 1444.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 1259.0
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 1150.0
      },
      {
        "feature": "weather_proxy_precipitation_se1",
        "importance": 1135.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 989.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 850.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 776.0
      },
      {
        "feature": "horizon_h",
        "importance": 765.0
      },
      {
        "feature": "price_forecast_rank_within_path",
        "importance": 693.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 684.0
      },
      {
        "feature": "price_forecast_0_168h_mean",
        "importance": 606.0
      },
      {
        "feature": "consumption_se1_same_hour_24h_vs_168h",
        "importance": 576.0
      },
      {
        "feature": "weather_proxy_snowfall_se1",
        "importance": 544.0
      },
      {
        "feature": "consumption_se1_ramp_24h",
        "importance": 509.0
      },
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 469.0
      },
      {
        "feature": "consumption_se1_ramp_1h",
        "importance": 424.0
      },
      {
        "feature": "consumption_se1_roll_std_24h",
        "importance": 412.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 405.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 400.0
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se1",
        "importance": 391.0
      }
    ]
  },
  "XGBoost_no_price": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 0.3967363238334656
      },
      {
        "feature": "consumption_se1_lag_1h",
        "importance": 0.34298625588417053
      },
      {
        "feature": "consumption_se1_roll_mean_6h",
        "importance": 0.20515722036361694
      },
      {
        "feature": "consumption_se1_lag_3h",
        "importance": 0.020145609974861145
      },
      {
        "feature": "consumption_se1_roll_mean_12h",
        "importance": 0.015099836513400078
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 0.005530758295208216
      },
      {
        "feature": "consumption_se1_lag_168h",
        "importance": 0.0024071328807622194
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0015479569556191564
      },
      {
        "feature": "consumption_se1_lag_6h",
        "importance": 0.0014870853628963232
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 0.0010130429873242974
      },
      {
        "feature": "consumption_se1_lag_12h",
        "importance": 0.0008017279324121773
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 0.0006821090937592089
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.0006389003247022629
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.0005430723540484905
      },
      {
        "feature": "consumption_se1_roll_mean_24h",
        "importance": 0.0005008404259569943
      },
      {
        "feature": "consumption_se1_lag_2h",
        "importance": 0.00048261965275742114
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 0.00034840009175240993
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se1",
        "importance": 0.0003007504856213927
      },
      {
        "feature": "consumption_se1_roll_min_24h",
        "importance": 0.00026165845338255167
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.00023583066649734974
      },
      {
        "feature": "special_day_type=movable_public_holiday",
        "importance": 0.0002139894204447046
      },
      {
        "feature": "is_workday",
        "importance": 0.000193173618754372
      },
      {
        "feature": "special_day_group=all_saints",
        "importance": 0.00017581504653207958
      },
      {
        "feature": "consumption_se1_roll_mean_48h",
        "importance": 0.00017184806347358972
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se1",
        "importance": 0.0001676757528912276
      }
    ]
  },
  "XGBoost_with_p0054h_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se1_lag_1h",
        "importance": 0.40780502557754517
      },
      {
        "feature": "consumption_se1_roll_mean_168h",
        "importance": 0.39228153228759766
      },
      {
        "feature": "consumption_se1_roll_mean_6h",
        "importance": 0.14060251414775848
      },
      {
        "feature": "consumption_se1_lag_3h",
        "importance": 0.0211283378303051
      },
      {
        "feature": "consumption_se1_roll_mean_12h",
        "importance": 0.012522525154054165
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se1",
        "importance": 0.005942205432802439
      },
      {
        "feature": "consumption_se1_roll_mean_24h",
        "importance": 0.0042863632552325726
      },
      {
        "feature": "consumption_se1_lag_168h",
        "importance": 0.0023822872899472713
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.001217012177221477
      },
      {
        "feature": "weather_proxy_apparent_temperature_se1",
        "importance": 0.0011421691160649061
      },
      {
        "feature": "consumption_se1_roll_max_24h",
        "importance": 0.0010911313584074378
      },
      {
        "feature": "consumption_se1_roll_min_24h",
        "importance": 0.0010093334130942822
      },
      {
        "feature": "consumption_se1_lag_6h",
        "importance": 0.0008474286878481507
      },
      {
        "feature": "consumption_se1_lag_2h",
        "importance": 0.0007925395620986819
      },
      {
        "feature": "consumption_se1_lag_12h",
        "importance": 0.0006338641396723688
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.0005916442023590207
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se1",
        "importance": 0.0005160938017070293
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.0004797924484591931
      },
      {
        "feature": "weather_proxy_temperature_2m_se1",
        "importance": 0.00046310198376886547
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se1",
        "importance": 0.0003617130860220641
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.0003350046754349023
      },
      {
        "feature": "price_forecast_horizon_value",
        "importance": 0.0003343495191074908
      },
      {
        "feature": "special_day_group=bridge",
        "importance": 0.00024708526325412095
      },
      {
        "feature": "price_forecast_rank_within_path",
        "importance": 0.00023899204097688198
      },
      {
        "feature": "consumption_se1_roll_mean_48h",
        "importance": 0.00023376305762212723
      }
    ]
  }
}
```
