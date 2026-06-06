# P0054T2 LABB

Status: `PASS`

```json
{
  "reproduction": {
    "best_dayahead_daily_energy": {
      "absolute_daily_energy_error_MWh": 4381.407120292,
      "daily_energy_error_percent_of_actual": 1.9333789651384485,
      "day_count": 358,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
      "signed_daily_energy_error_MWh": 28.879972625697697
    },
    "best_dayahead_hourly": {
      "MAE_percent_of_mean_actual": 2.638782944935854,
      "hourly_MAE_delivery_day": 253.70062353819173,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
    },
    "best_full36": {
      "MAE_full_36h": 243.67666893537265,
      "MAE_percent_of_mean_actual": 2.500614436538169,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
    },
    "ensemble_weight_evidence": {
      "holdout_used_for_weights": false,
      "internal_validation_start": "2025-03-01T00:00:00Z",
      "method": "inverse_internal_validation_mae",
      "model_mae": {
        "ExtraTrees_no_price": 313.08342263380854,
        "HGB_no_price": 292.8569732300242,
        "LightGBM_no_price": 281.5606194933632,
        "XGBoost_no_price": 280.5587719505287
      },
      "selection_data": "internal_validation_only",
      "weights": {
        "ExtraTrees_no_price": 0.23272312870535258,
        "HGB_no_price": 0.24879637612006233,
        "LightGBM_no_price": 0.25877821192546985,
        "XGBoost_no_price": 0.25970228324911526
      }
    },
    "horizon_bias_evidence": {
      "applied_rows": 52173,
      "base_model_key": "WeightedEnsemble_no_price",
      "fit_data": "internal_validation_horizon_mean_bias_only",
      "holdout_used_for_fit": false,
      "horizon_bias_mw": {
        "1": -114.08456758771239,
        "10": -120.08602022539621,
        "11": -168.6924859848145,
        "12": -152.53499224571004,
        "13": -129.77833360007844,
        "14": -169.40136668061365,
        "15": -145.56211142167203,
        "16": -118.29244673539648,
        "17": -121.42451798467263,
        "18": -114.91534112795075,
        "19": -21.520067330388134,
        "2": -67.19222754272347,
        "20": 61.525946329485116,
        "21": 14.938497372471543,
        "22": -30.689861418138356,
        "23": -63.03836435261945,
        "24": -83.195497250202,
        "25": -100.16804168507983,
        "26": -55.00166540109656,
        "27": -10.434972584383331,
        "28": 30.922523675443433,
        "29": 38.71691925674603,
        "3": -20.54666317804222,
        "30": -101.79987554872493,
        "31": -114.67679161721445,
        "32": -70.6185745461622,
        "33": -81.7817411383107,
        "34": -97.03675915510428,
        "35": -146.52464173338444,
        "36": -112.1718607282492,
        "4": 23.785564391075468,
        "5": 32.43653498955354,
        "6": -111.82875284386708,
        "7": -127.35894828415483,
        "8": -87.30734018981104,
        "9": -95.40394334806767
      }
    },
    "row_counts": {
      "dayahead_delivery_days": 358,
      "direct_rows": 52173,
      "full36_complete_origins": 356,
      "holdout_rows": 13188,
      "internal_train_rows": 35675,
      "internal_validation_rows": 3310,
      "path_rows": 52173,
      "source_rows": 35125,
      "train_fit_rows": 38985
    },
    "status": "PASS",
    "tmp_evidence_committed": false
  },
  "validity": "P0054R remains reproducible if R-like metrics match historic evidence within normal deterministic tolerance."
}
```
