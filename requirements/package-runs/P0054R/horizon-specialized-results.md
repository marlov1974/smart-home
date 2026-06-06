# P0054R LABB

Status: `PASS`

```json
{
  "HorizonBiasCorrected_WeightedEnsemble_no_price": {
    "applied_rows": 52173,
    "base_model_key": "WeightedEnsemble_no_price",
    "fit_data": "internal_validation_horizon_mean_bias_only",
    "holdout_used_for_fit": false,
    "horizon_bias_mw": {
      "1": -114.08456758771239,
      "10": -120.08602022539617,
      "11": -168.69248598481457,
      "12": -152.53499224571007,
      "13": -129.77833360007844,
      "14": -169.40136668061348,
      "15": -145.56211142167197,
      "16": -118.29244673539652,
      "17": -121.42451798467259,
      "18": -114.91534112795078,
      "19": -21.52006733038815,
      "2": -67.19222754272346,
      "20": 61.52594632948515,
      "21": 14.938497372471552,
      "22": -30.689861418138374,
      "23": -63.03836435261944,
      "24": -83.19549725020204,
      "25": -100.16804168507979,
      "26": -55.00166540109659,
      "27": -10.434972584383292,
      "28": 30.922523675443372,
      "29": 38.716919256746095,
      "3": -20.54666317804222,
      "30": -101.79987554872493,
      "31": -114.67679161721445,
      "32": -70.61857454616215,
      "33": -81.78174113831071,
      "34": -97.03675915510428,
      "35": -146.52464173338444,
      "36": -112.17186072824911,
      "4": 23.785564391075507,
      "5": 32.43653498955358,
      "6": -111.82875284386704,
      "7": -127.35894828415475,
      "8": -87.30734018981107,
      "9": -95.40394334806763
    }
  },
  "HorizonSpecialized_HGB_no_price": {
    "applied_rows": 13188,
    "details": [
      {
        "applied_rows": 366,
        "horizon_h": 1,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 2,
        "train_rows": 1082
      },
      {
        "applied_rows": 366,
        "horizon_h": 3,
        "train_rows": 1084
      },
      {
        "applied_rows": 365,
        "horizon_h": 4,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 5,
        "train_rows": 1082
      },
      {
        "applied_rows": 366,
        "horizon_h": 6,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 7,
        "train_rows": 1080
      },
      {
        "applied_rows": 365,
        "horizon_h": 8,
        "train_rows": 1084
      },
      {
        "applied_rows": 366,
        "horizon_h": 9,
        "train_rows": 1083
      },
      {
        "applied_rows": 365,
        "horizon_h": 10,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 11,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 12,
        "train_rows": 1085
      },
      {
        "applied_rows": 366,
        "horizon_h": 13,
        "train_rows": 1083
      },
      {
        "applied_rows": 366,
        "horizon_h": 14,
        "train_rows": 1084
      },
      {
        "applied_rows": 366,
        "horizon_h": 15,
        "train_rows": 1083
      },
      {
        "applied_rows": 367,
        "horizon_h": 16,
        "train_rows": 1082
      },
      {
        "applied_rows": 367,
        "horizon_h": 17,
        "train_rows": 1080
      },
      {
        "applied_rows": 367,
        "horizon_h": 18,
        "train_rows": 1082
      },
      {
        "applied_rows": 367,
        "horizon_h": 19,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 20,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 21,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 22,
        "train_rows": 1082
      },
      {
        "applied_rows": 366,
        "horizon_h": 23,
        "train_rows": 1080
      },
      {
        "applied_rows": 366,
        "horizon_h": 24,
        "train_rows": 1083
      },
      {
        "applied_rows": 365,
        "horizon_h": 25,
        "train_rows": 1080
      },
      {
        "applied_rows": 367,
        "horizon_h": 26,
        "train_rows": 1081
      },
      {
        "applied_rows": 367,
        "horizon_h": 27,
        "train_rows": 1083
      },
      {
        "applied_rows": 367,
        "horizon_h": 28,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 29,
        "train_rows": 1081
      },
      {
        "applied_rows": 367,
        "horizon_h": 30,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 31,
        "train_rows": 1079
      },
      {
        "applied_rows": 366,
        "horizon_h": 32,
        "train_rows": 1083
      },
      {
        "applied_rows": 367,
        "horizon_h": 33,
        "train_rows": 1082
      },
      {
        "applied_rows": 366,
        "horizon_h": 34,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 35,
        "train_rows": 1084
      },
      {
        "applied_rows": 367,
        "horizon_h": 36,
        "train_rows": 1084
      }
    ],
    "fit_data": "train_fit_only",
    "horizon_convention": "horizon_h 1..36",
    "horizon_models": 36,
    "model_family": "HGB"
  }
}
```
