# P0054R LABB

Status: `PASS`

```json
{
  "best_dayahead_daily_energy": {
    "absolute_daily_energy_error_MWh": 4381.407120291999,
    "daily_energy_error_percent_of_actual": 1.9333789651384488,
    "day_count": 358,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
    "signed_daily_energy_error_MWh": 28.879972625696315
  },
  "best_dayahead_hourly": {
    "MAE_percent_of_mean_actual": 2.6387829449358526,
    "hourly_MAE_delivery_day": 253.70062353819162,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
  },
  "best_full36": {
    "MAE_full_36h": 243.67666893537265,
    "MAE_percent_of_mean_actual": 2.500614436538169,
    "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
  },
  "dayahead_daily_energy": [
    {
      "absolute_daily_energy_error_MWh": 4873.268240691842,
      "daily_energy_error_percent_of_actual": 2.119202974964642,
      "day_count": 358,
      "model": "HGB_no_price",
      "signed_daily_energy_error_MWh": -1520.0591664296023
    },
    {
      "absolute_daily_energy_error_MWh": 5021.842610332668,
      "daily_energy_error_percent_of_actual": 2.1355635171866716,
      "day_count": 358,
      "model": "ExtraTrees_no_price",
      "signed_daily_energy_error_MWh": -1944.1877392812846
    },
    {
      "absolute_daily_energy_error_MWh": 4873.626360059099,
      "daily_energy_error_percent_of_actual": 2.10938983661445,
      "day_count": 358,
      "model": "LightGBM_no_price",
      "signed_daily_energy_error_MWh": -1707.5149789651568
    },
    {
      "absolute_daily_energy_error_MWh": 4656.51095268491,
      "daily_energy_error_percent_of_actual": 2.025690828367092,
      "day_count": 358,
      "model": "XGBoost_no_price",
      "signed_daily_energy_error_MWh": -1696.6808972918125
    },
    {
      "absolute_daily_energy_error_MWh": 4676.027979885135,
      "daily_energy_error_percent_of_actual": 2.0176464299018018,
      "day_count": 358,
      "model": "WeightedEnsemble_no_price",
      "signed_daily_energy_error_MWh": -1713.142241636285
    },
    {
      "absolute_daily_energy_error_MWh": 4698.706104578433,
      "daily_energy_error_percent_of_actual": 2.0295100125781986,
      "day_count": 358,
      "model": "MedianEnsemble_no_price",
      "signed_daily_energy_error_MWh": -1698.0437734104125
    },
    {
      "absolute_daily_energy_error_MWh": 5237.985602316879,
      "daily_energy_error_percent_of_actual": 2.3109247570353277,
      "day_count": 358,
      "model": "ResidualCorrection_XGBoost_no_price",
      "signed_daily_energy_error_MWh": 1461.4336154201126
    },
    {
      "absolute_daily_energy_error_MWh": 5924.046474784465,
      "daily_energy_error_percent_of_actual": 2.5355008217292583,
      "day_count": 358,
      "model": "HorizonSpecialized_HGB_no_price",
      "signed_daily_energy_error_MWh": -1928.0927884307193
    },
    {
      "absolute_daily_energy_error_MWh": 4381.407120291999,
      "daily_energy_error_percent_of_actual": 1.9333789651384488,
      "day_count": 358,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price",
      "signed_daily_energy_error_MWh": 28.879972625696315
    },
    {
      "absolute_daily_energy_error_MWh": 4796.960957536473,
      "daily_energy_error_percent_of_actual": 2.098889864434797,
      "day_count": 358,
      "model": "DayAheadSpecialized_HGB_no_price",
      "signed_daily_energy_error_MWh": -1378.5816116983995
    }
  ],
  "dayahead_hourly": [
    {
      "MAE_percent_of_mean_actual": 2.9404485213061404,
      "hourly_MAE_delivery_day": 282.70367017832007,
      "model": "HGB_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.967549782021206,
      "hourly_MAE_delivery_day": 285.30926786693567,
      "model": "ExtraTrees_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.8204888385698084,
      "hourly_MAE_delivery_day": 271.1703811792921,
      "model": "LightGBM_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.7744504707772264,
      "hourly_MAE_delivery_day": 266.7441123806121,
      "model": "XGBoost_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.751958313196207,
      "hourly_MAE_delivery_day": 264.58164789524204,
      "model": "WeightedEnsemble_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.761604760125123,
      "hourly_MAE_delivery_day": 265.50908666222773,
      "model": "MedianEnsemble_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.9820218164224794,
      "hourly_MAE_delivery_day": 286.70065330032855,
      "model": "ResidualCorrection_XGBoost_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 3.2563502693481303,
      "hourly_MAE_delivery_day": 313.07542569116526,
      "model": "HorizonSpecialized_HGB_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.6387829449358526,
      "hourly_MAE_delivery_day": 253.70062353819162,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
    },
    {
      "MAE_percent_of_mean_actual": 2.8983783024450345,
      "hourly_MAE_delivery_day": 278.6589112950879,
      "model": "DayAheadSpecialized_HGB_no_price"
    }
  ],
  "full36": [
    {
      "MAE_full_36h": 274.0596971432482,
      "MAE_percent_of_mean_actual": 2.812405628096644,
      "model": "HGB_no_price"
    },
    {
      "MAE_full_36h": 277.2804939037504,
      "MAE_percent_of_mean_actual": 2.8454575034019625,
      "model": "ExtraTrees_no_price"
    },
    {
      "MAE_full_36h": 261.2718866611184,
      "MAE_percent_of_mean_actual": 2.6811768828784928,
      "model": "LightGBM_no_price"
    },
    {
      "MAE_full_36h": 258.2239223929479,
      "MAE_percent_of_mean_actual": 2.6498986177727715,
      "model": "XGBoost_no_price"
    },
    {
      "MAE_full_36h": 255.71992661275382,
      "MAE_percent_of_mean_actual": 2.624202567246717,
      "model": "WeightedEnsemble_no_price"
    },
    {
      "MAE_full_36h": 256.50170119016207,
      "MAE_percent_of_mean_actual": 2.6322251522686098,
      "model": "MedianEnsemble_no_price"
    },
    {
      "MAE_full_36h": 279.3153995417136,
      "MAE_percent_of_mean_actual": 2.866339742302861,
      "model": "ResidualCorrection_XGBoost_no_price"
    },
    {
      "MAE_full_36h": 291.6097744070669,
      "MAE_percent_of_mean_actual": 2.992504842190484,
      "model": "HorizonSpecialized_HGB_no_price"
    },
    {
      "MAE_full_36h": 243.67666893537265,
      "MAE_percent_of_mean_actual": 2.500614436538169,
      "model": "HorizonBiasCorrected_WeightedEnsemble_no_price"
    }
  ],
  "workplace_reference_percent_error": "roughly 3-4 percent; P0054R remains LABB because weather is actual_as_forecast_proxy"
}
```
