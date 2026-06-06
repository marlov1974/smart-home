# P0054T4 LABB

Status: `WARN`

```json
{
  "base_families": [
    "HGB",
    "ExtraTrees",
    "LightGBM",
    "XGBoost"
  ],
  "horizon_bias": {
    "applied_rows": 52173,
    "base_model_key": "WeightedEnsemble_no_price",
    "fit_data": "internal_validation_horizon_mean_bias_only",
    "holdout_used_for_fit": false,
    "horizon_bias_mw": {
      "1": -114.0845675877112,
      "10": -120.08602022539495,
      "11": -168.6924859848134,
      "12": -152.53499224570928,
      "13": -129.77833360007756,
      "14": -169.40136668061265,
      "15": -145.562111421671,
      "16": -118.29244673539563,
      "17": -121.42451798467178,
      "18": -114.91534112794979,
      "19": -21.520067330387086,
      "2": -67.19222754272243,
      "20": 61.52594632948614,
      "21": 14.938497372472709,
      "22": -30.68986141813721,
      "23": -63.0383643526182,
      "24": -83.1954972502007,
      "25": -100.16804168507834,
      "26": -55.00166540109542,
      "27": -10.434972584381967,
      "28": 30.922523675444697,
      "29": 38.716919256747296,
      "3": -20.546663178041094,
      "30": -101.79987554872368,
      "31": -114.67679161721325,
      "32": -70.61857454616084,
      "33": -81.78174113830954,
      "34": -97.03675915510311,
      "35": -146.52464173338313,
      "36": -112.17186072824816,
      "4": 23.785564391076495,
      "5": 32.4365349895547,
      "6": -111.82875284386571,
      "7": -127.3589482841536,
      "8": -87.30734018980985,
      "9": -95.40394334806636
    }
  },
  "model": "M1_HorizonBiasCorrectedWeightedEnsemble",
  "model_reused_for_all_inference_noise_seeds": true,
  "weights": {
    "holdout_used_for_weights": false,
    "internal_validation_start": "2025-03-01T00:00:00Z",
    "method": "inverse_internal_validation_mae",
    "model_mae": {
      "ExtraTrees_no_price": 313.08342263380865,
      "HGB_no_price": 292.8569732300242,
      "LightGBM_no_price": 281.5606194933632,
      "XGBoost_no_price": 280.5587719505287
    },
    "selection_data": "internal_validation_only",
    "weights": {
      "ExtraTrees_no_price": 0.23272312870535253,
      "HGB_no_price": 0.24879637612006233,
      "LightGBM_no_price": 0.25877821192546985,
      "XGBoost_no_price": 0.25970228324911526
    }
  }
}
```
