# P0054J LABB

Status: `PASS`

```json
{
  "conditional_price_help_summary": {
    "by_regime": {
      "cold_hours": {
        "ExtraTrees": {
          "no_price_MAE": 17.22718809968323,
          "relative_change_percent": -0.5561327245231058,
          "with_price_MAE": 17.13138206914574
        },
        "HGB": {
          "no_price_MAE": 17.38306499822313,
          "relative_change_percent": -5.234141886718971,
          "with_price_MAE": 16.47321071195555
        },
        "LightGBM": {
          "no_price_MAE": 19.27407014131186,
          "relative_change_percent": -3.5752152436641103,
          "with_price_MAE": 18.584980647545166
        },
        "XGBoost": {
          "no_price_MAE": 17.217493080707285,
          "relative_change_percent": -1.6676110197750873,
          "with_price_MAE": 16.930372268764398
        }
      },
      "evening_peak": {
        "ExtraTrees": {
          "no_price_MAE": 16.52387475091714,
          "relative_change_percent": -1.4547523272172875,
          "with_price_MAE": 16.283493298431704
        },
        "HGB": {
          "no_price_MAE": 16.16742285232324,
          "relative_change_percent": -3.452700168416466,
          "with_price_MAE": 15.609210216272475
        },
        "LightGBM": {
          "no_price_MAE": 15.800345712214325,
          "relative_change_percent": -4.396753682722668,
          "with_price_MAE": 15.105643430229629
        },
        "XGBoost": {
          "no_price_MAE": 13.824182414672501,
          "relative_change_percent": -2.1780114358132825,
          "with_price_MAE": 13.523090140773245
        }
      },
      "forecast_price_spike": {
        "ExtraTrees": {
          "no_price_MAE": 14.457076752066095,
          "relative_change_percent": -2.409342043522796,
          "with_price_MAE": 14.108756323614207
        },
        "HGB": {
          "no_price_MAE": 13.879132694070945,
          "relative_change_percent": -1.9176434579914894,
          "with_price_MAE": 13.612980413937136
        },
        "LightGBM": {
          "no_price_MAE": 13.342750926160813,
          "relative_change_percent": 3.850213181881132,
          "with_price_MAE": 13.856475281145423
        },
        "XGBoost": {
          "no_price_MAE": 12.251560392116309,
          "relative_change_percent": -1.1946462756097267,
          "with_price_MAE": 12.105197582187815
        }
      },
      "high_forecast_price": {
        "ExtraTrees": {
          "no_price_MAE": 15.119609865992691,
          "relative_change_percent": 1.1272442065872694,
          "with_price_MAE": 15.290044792265691
        },
        "HGB": {
          "no_price_MAE": 15.908181469482692,
          "relative_change_percent": -5.02233854180848,
          "with_price_MAE": 15.109218740240028
        },
        "LightGBM": {
          "no_price_MAE": 17.164120560981566,
          "relative_change_percent": 0.3238650860935298,
          "with_price_MAE": 17.219709154813586
        },
        "XGBoost": {
          "no_price_MAE": 16.11112291768518,
          "relative_change_percent": -3.835925090274793,
          "with_price_MAE": 15.493112311360681
        }
      },
      "holiday": {
        "ExtraTrees": {
          "no_price_MAE": 13.118244204367192,
          "relative_change_percent": -5.089242289703868,
          "with_price_MAE": 12.45062497265191
        },
        "HGB": {
          "no_price_MAE": 13.465388636384153,
          "relative_change_percent": 8.022117364358254,
          "with_price_MAE": 14.54559791636185
        },
        "LightGBM": {
          "no_price_MAE": 12.538817157322233,
          "relative_change_percent": 7.492694697038489,
          "with_price_MAE": 13.478312445540269
        },
        "XGBoost": {
          "no_price_MAE": 12.028896906842554,
          "relative_change_percent": 7.710443481180776,
          "with_price_MAE": 12.956378204254152
        }
      },
      "large_forecast_price_ramp": {
        "ExtraTrees": {
          "no_price_MAE": 14.028549470652647,
          "relative_change_percent": -0.9275125122403879,
          "with_price_MAE": 13.898432919026511
        },
        "HGB": {
          "no_price_MAE": 14.138369421444107,
          "relative_change_percent": -0.4516239350861125,
          "with_price_MAE": 14.07451716110597
        },
        "LightGBM": {
          "no_price_MAE": 13.845305440488684,
          "relative_change_percent": 2.8450864276464807,
          "with_price_MAE": 14.239216346442227
        },
        "XGBoost": {
          "no_price_MAE": 13.67840659208631,
          "relative_change_percent": -1.5303936121816553,
          "with_price_MAE": 13.469073131352786
        }
      },
      "low_forecast_price": {
        "ExtraTrees": {
          "no_price_MAE": 12.561302947119426,
          "relative_change_percent": -1.8280614473685217,
          "with_price_MAE": 12.33167461065597
        },
        "HGB": {
          "no_price_MAE": 13.56067831075182,
          "relative_change_percent": -2.99495347742523,
          "with_price_MAE": 13.15454230412151
        },
        "LightGBM": {
          "no_price_MAE": 12.813842500504002,
          "relative_change_percent": -3.022392016030739,
          "with_price_MAE": 12.426557947822015
        },
        "XGBoost": {
          "no_price_MAE": 12.166812299090278,
          "relative_change_percent": -0.4383300242796485,
          "with_price_MAE": 12.113481507785616
        }
      },
      "morning_ramp": {
        "ExtraTrees": {
          "no_price_MAE": 14.008838199433894,
          "relative_change_percent": -1.7459931023431494,
          "with_price_MAE": 13.764244850753366
        },
        "HGB": {
          "no_price_MAE": 14.342109525014266,
          "relative_change_percent": -2.438132293363086,
          "with_price_MAE": 13.99242992113539
        },
        "LightGBM": {
          "no_price_MAE": 13.896551729288312,
          "relative_change_percent": 1.713369389228363,
          "with_price_MAE": 14.134650992776223
        },
        "XGBoost": {
          "no_price_MAE": 13.322900680959496,
          "relative_change_percent": -1.3927100630101064,
          "with_price_MAE": 13.13735130249093
        }
      },
      "summer_low_load": {
        "ExtraTrees": {
          "no_price_MAE": 11.143314400282087,
          "relative_change_percent": 0.07445408957889459,
          "with_price_MAE": 11.15161105356773
        },
        "HGB": {
          "no_price_MAE": 12.761892379418125,
          "relative_change_percent": -5.342420775251474,
          "with_price_MAE": 12.080098389624856
        },
        "LightGBM": {
          "no_price_MAE": 12.11037800404629,
          "relative_change_percent": -8.971831181389144,
          "with_price_MAE": 11.023855334095172
        },
        "XGBoost": {
          "no_price_MAE": 10.598354658159753,
          "relative_change_percent": 3.1288443890882056,
          "with_price_MAE": 10.929960683217253
        }
      },
      "very_cold_hours": {
        "ExtraTrees": {
          "no_price_MAE": 17.77784388224249,
          "relative_change_percent": 0.3613069320158861,
          "with_price_MAE": 17.842076464551994
        },
        "HGB": {
          "no_price_MAE": 17.618225889983293,
          "relative_change_percent": -4.758614920594361,
          "with_price_MAE": 16.77984236403853
        },
        "LightGBM": {
          "no_price_MAE": 18.354357935303096,
          "relative_change_percent": -2.684683799241146,
          "with_price_MAE": 17.86160146135928
        },
        "XGBoost": {
          "no_price_MAE": 17.015649642796912,
          "relative_change_percent": 0.61706060181585,
          "with_price_MAE": 17.12064651288563
        }
      },
      "weekday": {
        "ExtraTrees": {
          "no_price_MAE": 13.702486572501478,
          "relative_change_percent": -0.5091183767996761,
          "with_price_MAE": 13.632724695282365
        },
        "HGB": {
          "no_price_MAE": 14.01887899091748,
          "relative_change_percent": -2.764238334064959,
          "with_price_MAE": 13.63136376384436
        },
        "LightGBM": {
          "no_price_MAE": 14.159829586412949,
          "relative_change_percent": -1.383112723578851,
          "with_price_MAE": 13.963983181766189
        },
        "XGBoost": {
          "no_price_MAE": 13.02579387334602,
          "relative_change_percent": -1.7458978228773836,
          "with_price_MAE": 12.798376821698776
        }
      },
      "weekend": {
        "ExtraTrees": {
          "no_price_MAE": 15.290966533113846,
          "relative_change_percent": -0.4295895332022565,
          "with_price_MAE": 15.225278141362129
        },
        "HGB": {
          "no_price_MAE": 16.29163897474401,
          "relative_change_percent": -1.0636306201595922,
          "with_price_MAE": 16.11835611408278
        },
        "LightGBM": {
          "no_price_MAE": 16.697820212809148,
          "relative_change_percent": 0.40299340197070255,
          "with_price_MAE": 16.7651113265397
        },
        "XGBoost": {
          "no_price_MAE": 15.844458437499972,
          "relative_change_percent": -0.40521059529275194,
          "with_price_MAE": 15.780255013144465
        }
      },
      "winter_high_load": {
        "ExtraTrees": {
          "no_price_MAE": 16.854513861353144,
          "relative_change_percent": -0.5084661186553401,
          "with_price_MAE": 16.768814368904096
        },
        "HGB": {
          "no_price_MAE": 17.479160949753837,
          "relative_change_percent": -4.597988186969318,
          "with_price_MAE": 16.6754711941028
        },
        "LightGBM": {
          "no_price_MAE": 19.53377327001158,
          "relative_change_percent": -3.0892988499078213,
          "with_price_MAE": 18.93031663703751
        },
        "XGBoost": {
          "no_price_MAE": 17.3414262593334,
          "relative_change_percent": -3.8079402244177376,
          "with_price_MAE": 16.681075113316503
        }
      }
    },
    "count": 14,
    "improvements_at_least_3_percent": [
      {
        "family": "HGB",
        "regime": "cold_hours",
        "relative_change_percent": -5.234141886718971
      },
      {
        "family": "LightGBM",
        "regime": "cold_hours",
        "relative_change_percent": -3.5752152436641103
      },
      {
        "family": "HGB",
        "regime": "very_cold_hours",
        "relative_change_percent": -4.758614920594361
      },
      {
        "family": "ExtraTrees",
        "regime": "holiday",
        "relative_change_percent": -5.089242289703868
      },
      {
        "family": "HGB",
        "regime": "evening_peak",
        "relative_change_percent": -3.452700168416466
      },
      {
        "family": "LightGBM",
        "regime": "evening_peak",
        "relative_change_percent": -4.396753682722668
      },
      {
        "family": "HGB",
        "regime": "summer_low_load",
        "relative_change_percent": -5.342420775251474
      },
      {
        "family": "LightGBM",
        "regime": "summer_low_load",
        "relative_change_percent": -8.971831181389144
      },
      {
        "family": "HGB",
        "regime": "winter_high_load",
        "relative_change_percent": -4.597988186969318
      },
      {
        "family": "LightGBM",
        "regime": "winter_high_load",
        "relative_change_percent": -3.0892988499078213
      },
      {
        "family": "XGBoost",
        "regime": "winter_high_load",
        "relative_change_percent": -3.8079402244177376
      },
      {
        "family": "HGB",
        "regime": "high_forecast_price",
        "relative_change_percent": -5.02233854180848
      },
      {
        "family": "XGBoost",
        "regime": "high_forecast_price",
        "relative_change_percent": -3.835925090274793
      },
      {
        "family": "LightGBM",
        "regime": "low_forecast_price",
        "relative_change_percent": -3.022392016030739
      }
    ]
  },
  "interpretation_category": "supports_hypothesis",
  "learning_threshold": "keep if holdout or weekly improves by >=2%, or >=3% in at least two important regimes without broad worsening",
  "per_model_family": [
    {
      "family": "HGB",
      "holdout_no_price_MAE": 13.042352312888172,
      "holdout_relative_change_percent": 0.8927455419055711,
      "holdout_with_minus_no_MAE": 0.11643501883292728,
      "holdout_with_price_MAE": 13.158787331721099,
      "price_helped_holdout": false,
      "price_helped_weekly": true,
      "weekly_no_price_MAE_full_168h": 14.668238986296489,
      "weekly_relative_change_percent": -2.224575014299145,
      "weekly_with_minus_no_MAE_full_168h": -0.32630597952683793,
      "weekly_with_price_MAE_full_168h": 14.34193300676965
    },
    {
      "family": "ExtraTrees",
      "holdout_no_price_MAE": 12.679515980941702,
      "holdout_relative_change_percent": 0.09963703752656679,
      "holdout_with_minus_no_MAE": 0.012633494096117914,
      "holdout_with_price_MAE": 12.69214947503782,
      "price_helped_holdout": false,
      "price_helped_weekly": true,
      "weekly_no_price_MAE_full_168h": 14.15633798981931,
      "weekly_relative_change_percent": -0.4845746426637863,
      "weekly_with_minus_no_MAE_full_168h": -0.06859802422844474,
      "weekly_with_price_MAE_full_168h": 14.087739965590865
    },
    {
      "family": "LightGBM",
      "holdout_no_price_MAE": 13.913560205866226,
      "holdout_relative_change_percent": -1.029787203889473,
      "holdout_with_minus_no_MAE": -0.14328006260546822,
      "holdout_with_price_MAE": 13.770280143260758,
      "price_helped_holdout": true,
      "price_helped_weekly": true,
      "weekly_no_price_MAE_full_168h": 14.884969765383296,
      "weekly_relative_change_percent": -0.8106449555549822,
      "weekly_with_minus_no_MAE_full_168h": -0.12066425653896395,
      "weekly_with_price_MAE_full_168h": 14.764305508844332
    },
    {
      "family": "XGBoost",
      "holdout_no_price_MAE": 12.60041062463637,
      "holdout_relative_change_percent": -0.12006947345773429,
      "holdout_with_minus_no_MAE": -0.015129246690513298,
      "holdout_with_price_MAE": 12.585281377945856,
      "price_helped_holdout": true,
      "price_helped_weekly": true,
      "weekly_no_price_MAE_full_168h": 13.831126605961474,
      "weekly_relative_change_percent": -1.3070850398320675,
      "weekly_with_minus_no_MAE_full_168h": -0.18078458670675523,
      "weekly_with_price_MAE_full_168h": 13.650342019254719
    }
  ],
  "price_forecast_should_be_kept_for_future_se1_experiments": true,
  "required_model_pairs_complete": true
}
```
