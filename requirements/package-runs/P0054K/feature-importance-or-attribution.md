# P0054K LABB

Status: `PASS`

```json
{
  "ExtraTrees_no_price": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.16867389491977877
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.116140732753102
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.07937221499015414
      },
      {
        "feature": "consumption_se3_roll_mean_12h",
        "importance": 0.07356589533616786
      },
      {
        "feature": "consumption_se3_roll_mean_48h",
        "importance": 0.07081715053013356
      },
      {
        "feature": "consumption_se3_roll_max_24h",
        "importance": 0.06579502492745522
      },
      {
        "feature": "consumption_se3_lag_24h",
        "importance": 0.05666601985971373
      },
      {
        "feature": "consumption_se3_lag_12h",
        "importance": 0.054700320578884666
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.05403229710077041
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.05287329038344147
      },
      {
        "feature": "consumption_se3_roll_mean_24h",
        "importance": 0.05106035443442966
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.05039827641442191
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.024244971971718283
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.01801160194404021
      },
      {
        "feature": "consumption_se3_lag_72h",
        "importance": 0.01021965511527783
      },
      {
        "feature": "consumption_se3_lag_168h",
        "importance": 0.009815696892662002
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.006517168211349523
      },
      {
        "feature": "consumption_se3_lag_48h",
        "importance": 0.005818721330615808
      },
      {
        "feature": "consumption_se3_roll_std_24h",
        "importance": 0.0051695427368605145
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.004523440443768695
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.004424088783302969
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.004410438969709562
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.0019494798245804728
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.0015271680449997428
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.001053076072727362
      }
    ]
  },
  "ExtraTrees_with_p0054k_se3_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.1284337196527332
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.11157532865542334
      },
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.10304691604483848
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.07542594984011243
      },
      {
        "feature": "consumption_se3_roll_mean_48h",
        "importance": 0.07288055334147604
      },
      {
        "feature": "consumption_se3_lag_12h",
        "importance": 0.06062863828632584
      },
      {
        "feature": "consumption_se3_roll_max_24h",
        "importance": 0.060086891045251195
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.05977869141517054
      },
      {
        "feature": "consumption_se3_roll_mean_12h",
        "importance": 0.0588478375987747
      },
      {
        "feature": "consumption_se3_roll_mean_24h",
        "importance": 0.05363415758724407
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.052083452696474776
      },
      {
        "feature": "consumption_se3_lag_24h",
        "importance": 0.05077220571126452
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.02678261717330415
      },
      {
        "feature": "consumption_se3_lag_48h",
        "importance": 0.02134824706364427
      },
      {
        "feature": "consumption_se3_lag_72h",
        "importance": 0.010511998721792292
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.010230030148889976
      },
      {
        "feature": "consumption_se3_lag_168h",
        "importance": 0.0094738923222723
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.0064525702486750635
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.006064880877575105
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.004627158662225989
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.003983869908467598
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.001737854146640237
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.0010883989644779827
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.0009721667389604717
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.0009245956975445572
      }
    ]
  },
  "HGB_no_price": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "HGB_with_p0054k_se3_price_forecast": {
    "available": false,
    "reason": "model_has_no_feature_importances_attribute"
  },
  "LightGBM_no_price": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 1780.0
      },
      {
        "feature": "weather_proxy_wind_100m_se3",
        "importance": 1753.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se3",
        "importance": 1728.0
      },
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 1724.0
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 1305.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 1279.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 1279.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 1197.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 1189.0
      },
      {
        "feature": "horizon_h",
        "importance": 1044.0
      },
      {
        "feature": "weather_proxy_precipitation_se3",
        "importance": 878.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 830.0
      },
      {
        "feature": "consumption_se3_same_hour_24h_vs_168h",
        "importance": 689.0
      },
      {
        "feature": "consumption_se3_roll_std_24h",
        "importance": 669.0
      },
      {
        "feature": "consumption_se3_lag_72h",
        "importance": 613.0
      },
      {
        "feature": "consumption_se3_ramp_24h",
        "importance": 590.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 584.0
      },
      {
        "feature": "consumption_se3_ramp_1h",
        "importance": 581.0
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 529.0
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 511.0
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 501.0
      },
      {
        "feature": "consumption_se3_lag_48h",
        "importance": 484.0
      },
      {
        "feature": "consumption_se3_lag_168h",
        "importance": 448.0
      },
      {
        "feature": "consumption_se3_lag_12h",
        "importance": 346.0
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 327.0
      }
    ]
  },
  "LightGBM_with_p0054k_se3_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "weather_proxy_temperature_delta_from_train_normal_se3",
        "importance": 1436.0
      },
      {
        "feature": "weather_proxy_wind_100m_se3",
        "importance": 1408.0
      },
      {
        "feature": "price_forecast_ramp_from_previous_horizon",
        "importance": 1350.0
      },
      {
        "feature": "weather_proxy_humidity_se3",
        "importance": 1324.0
      },
      {
        "feature": "weather_proxy_cloud_cover_se3",
        "importance": 1302.0
      },
      {
        "feature": "price_forecast_horizon_value",
        "importance": 1271.0
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 1070.0
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 1041.0
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 979.0
      },
      {
        "feature": "horizon_h",
        "importance": 961.0
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 896.0
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 843.0
      },
      {
        "feature": "price_forecast_0_168h_mean",
        "importance": 747.0
      },
      {
        "feature": "price_forecast_rank_within_path",
        "importance": 718.0
      },
      {
        "feature": "weather_proxy_precipitation_se3",
        "importance": 682.0
      },
      {
        "feature": "target_model_cet_weekday",
        "importance": 660.0
      },
      {
        "feature": "consumption_se3_same_hour_24h_vs_168h",
        "importance": 643.0
      },
      {
        "feature": "consumption_se3_ramp_24h",
        "importance": 565.0
      },
      {
        "feature": "price_forecast_0_24h_mean",
        "importance": 552.0
      },
      {
        "feature": "consumption_se3_ramp_1h",
        "importance": 539.0
      },
      {
        "feature": "price_forecast_24_48h_mean",
        "importance": 506.0
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 495.0
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 489.0
      },
      {
        "feature": "consumption_se3_roll_std_24h",
        "importance": 459.0
      },
      {
        "feature": "consumption_se3_lag_72h",
        "importance": 428.0
      }
    ]
  },
  "XGBoost_no_price": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.43995755910873413
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.2773033082485199
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.16080553829669952
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.05290891230106354
      },
      {
        "feature": "consumption_se3_roll_mean_12h",
        "importance": 0.040314700454473495
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.0035267076455056667
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.0035244335886090994
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.0033714529126882553
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.0032044462859630585
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.0031598613131791353
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.0014829338761046529
      },
      {
        "feature": "target_month",
        "importance": 0.0014546428574249148
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0013987167039886117
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.0013636467047035694
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.0005911419284529984
      },
      {
        "feature": "consumption_se3_roll_mean_48h",
        "importance": 0.0005730855627916753
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.0005196909187361598
      },
      {
        "feature": "consumption_se3_roll_std_24h",
        "importance": 0.00048200314631685615
      },
      {
        "feature": "is_workday",
        "importance": 0.00046065563219599426
      },
      {
        "feature": "is_weekend",
        "importance": 0.0004591566394083202
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.0003778815735131502
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.00035665888572111726
      },
      {
        "feature": "target_dayofyear_sin",
        "importance": 0.00023700649035163224
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.00019248033640906215
      },
      {
        "feature": "horizon_h",
        "importance": 0.00018512204405851662
      }
    ]
  },
  "XGBoost_with_p0054k_se3_price_forecast": {
    "available": true,
    "top": [
      {
        "feature": "consumption_se3_roll_mean_6h",
        "importance": 0.4489407539367676
      },
      {
        "feature": "consumption_se3_lag_1h",
        "importance": 0.3400299847126007
      },
      {
        "feature": "consumption_se3_roll_min_24h",
        "importance": 0.08019226044416428
      },
      {
        "feature": "consumption_se3_lag_2h",
        "importance": 0.05176850035786629
      },
      {
        "feature": "consumption_se3_roll_mean_12h",
        "importance": 0.03807971999049187
      },
      {
        "feature": "consumption_se3_lag_3h",
        "importance": 0.007787787821143866
      },
      {
        "feature": "weather_proxy_heating_degree_hours_se3",
        "importance": 0.004068347625434399
      },
      {
        "feature": "consumption_se3_lag_6h",
        "importance": 0.003861007047817111
      },
      {
        "feature": "weather_proxy_apparent_temperature_se3",
        "importance": 0.0036422538105398417
      },
      {
        "feature": "weather_proxy_cold_spell_flag_se3",
        "importance": 0.0033472306095063686
      },
      {
        "feature": "target_hour_cos",
        "importance": 0.003149742726236582
      },
      {
        "feature": "consumption_se3_roll_mean_168h",
        "importance": 0.003010904649272561
      },
      {
        "feature": "target_dayofyear_cos",
        "importance": 0.002029816620051861
      },
      {
        "feature": "weather_proxy_shortwave_radiation_se3",
        "importance": 0.0017424848629161716
      },
      {
        "feature": "price_forecast_0_168h_mean",
        "importance": 0.001407882897183299
      },
      {
        "feature": "weather_proxy_temperature_2m_se3",
        "importance": 0.0012546656653285027
      },
      {
        "feature": "target_model_cet_day_of_year",
        "importance": 0.0007100806105881929
      },
      {
        "feature": "special_day_type=normal_weekday",
        "importance": 0.0005981303984299302
      },
      {
        "feature": "is_workday",
        "importance": 0.0004968036082573235
      },
      {
        "feature": "consumption_se3_roll_mean_48h",
        "importance": 0.0004549199074972421
      },
      {
        "feature": "consumption_se3_lag_48h",
        "importance": 0.0003190457646269351
      },
      {
        "feature": "weather_proxy_train_normal_temperature_2m_se3",
        "importance": 0.00030207575764507055
      },
      {
        "feature": "is_weekend",
        "importance": 0.0002116640971507877
      },
      {
        "feature": "target_month",
        "importance": 0.0002111145731760189
      },
      {
        "feature": "target_hour_sin",
        "importance": 0.00019089870329480618
      }
    ]
  }
}
```
