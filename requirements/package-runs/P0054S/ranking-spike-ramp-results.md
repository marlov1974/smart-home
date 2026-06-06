# P0054S LABB

Status: `PASS`

```json
{
  "DayAheadSpecialized_HGB": {
    "rows": 0
  },
  "ExtraTrees": {
    "bottom20_168h_precision": 0.4025568181818182,
    "forecast_price_spike_MAE": 0.8833402714233801,
    "high_price_regime_MAE": 1.2009788014892444,
    "large_price_ramp_MAE": 1.0859311580914601,
    "low_price_detection": {
      "f1": 0.025252525252525252,
      "fn": 4225,
      "fp": 21,
      "precision": 0.7236842105263158,
      "recall": 0.012850467289719626,
      "tp": 55
    },
    "low_price_regime_MAE": 0.3313876789776959,
    "ramp_detection": {
      "f1": 0.22886133032694478,
      "fn": 1254,
      "fp": 114,
      "precision": 0.6403785488958991,
      "recall": 0.1393273850377488,
      "tp": 203
    },
    "rows": 59136,
    "spearman": 0.5983748935964608,
    "spike_detection": {
      "f1": 0.009044657998869417,
      "fn": 1579,
      "fp": 174,
      "precision": 0.04395604395604396,
      "recall": 0.005040957781978576,
      "tp": 8
    },
    "top20_168h_precision": 0.37059659090909103
  },
  "HGB": {
    "bottom20_168h_precision": 0.3727272727272725,
    "forecast_price_spike_MAE": 1.0433500221509293,
    "high_price_regime_MAE": 1.155285036492779,
    "large_price_ramp_MAE": 1.0640628958440497,
    "low_price_detection": {
      "f1": 0.05575379125780553,
      "fn": 4155,
      "fp": 79,
      "precision": 0.6127450980392157,
      "recall": 0.029205607476635514,
      "tp": 125
    },
    "low_price_regime_MAE": 0.30369873084239213,
    "ramp_detection": {
      "f1": 0.24482951369480155,
      "fn": 1238,
      "fp": 113,
      "precision": 0.6596385542168675,
      "recall": 0.15030885380919698,
      "tp": 219
    },
    "rows": 59136,
    "spearman": 0.5984922425482891,
    "spike_detection": {
      "f1": 0.01086366105377512,
      "fn": 1577,
      "fp": 244,
      "precision": 0.03937007874015748,
      "recall": 0.00630119722747322,
      "tp": 10
    },
    "top20_168h_precision": 0.3963068181818187
  },
  "HorizonBiasCorrected_WeightedEnsemble": {
    "bottom20_168h_precision": 0.3589488636363635,
    "forecast_price_spike_MAE": 0.8637290072507616,
    "high_price_regime_MAE": 1.3788419137304937,
    "large_price_ramp_MAE": 1.1027215498596423,
    "low_price_detection": {
      "f1": 0.39521072796934864,
      "fn": 2217,
      "fp": 4097,
      "precision": 0.3349025974025974,
      "recall": 0.48200934579439253,
      "tp": 2063
    },
    "low_price_regime_MAE": 0.20368474935109715,
    "ramp_detection": {
      "f1": 0.26910139356078805,
      "fn": 1177,
      "fp": 344,
      "precision": 0.44871794871794873,
      "recall": 0.19217570350034316,
      "tp": 280
    },
    "rows": 59136,
    "spearman": 0.5910028723891114,
    "spike_detection": {
      "f1": 0.0036697247706422016,
      "fn": 1584,
      "fp": 45,
      "precision": 0.0625,
      "recall": 0.001890359168241966,
      "tp": 3
    },
    "top20_168h_precision": 0.3994318181818181
  },
  "HorizonBucket_HGB": {
    "bottom20_168h_precision": 0.35383522727272704,
    "forecast_price_spike_MAE": 0.7776974738907879,
    "high_price_regime_MAE": 1.1782063053898828,
    "large_price_ramp_MAE": 1.0336659222478095,
    "low_price_detection": {
      "f1": 0.0605102731993678,
      "fn": 4146,
      "fp": 15,
      "precision": 0.8993288590604027,
      "recall": 0.03130841121495327,
      "tp": 134
    },
    "low_price_regime_MAE": 0.2965371436964556,
    "ramp_detection": {
      "f1": 0.284496537027171,
      "fn": 1190,
      "fp": 153,
      "precision": 0.6357142857142857,
      "recall": 0.1832532601235415,
      "tp": 267
    },
    "rows": 59136,
    "spearman": 0.5834937574594922,
    "spike_detection": {
      "f1": 0.03510696653867252,
      "fn": 1555,
      "fp": 204,
      "precision": 0.13559322033898305,
      "recall": 0.020163831127914304,
      "tp": 32
    },
    "top20_168h_precision": 0.36761363636363636
  },
  "LightGBM": {
    "bottom20_168h_precision": 0.38821022727272736,
    "forecast_price_spike_MAE": 0.6312678832455465,
    "high_price_regime_MAE": 1.2560090749537902,
    "large_price_ramp_MAE": 1.0755479879285652,
    "low_price_detection": {
      "f1": 0.14526315789473684,
      "fn": 3935,
      "fp": 125,
      "precision": 0.7340425531914894,
      "recall": 0.08060747663551401,
      "tp": 345
    },
    "low_price_regime_MAE": 0.28067823983160217,
    "ramp_detection": {
      "f1": 0.26321353065539116,
      "fn": 1208,
      "fp": 186,
      "precision": 0.5724137931034483,
      "recall": 0.17089910775566233,
      "tp": 249
    },
    "rows": 59136,
    "spearman": 0.5659957614834716,
    "spike_detection": {
      "f1": 0.056116722783389444,
      "fn": 1537,
      "fp": 145,
      "precision": 0.2564102564102564,
      "recall": 0.0315059861373661,
      "tp": 50
    },
    "top20_168h_precision": 0.3548295454545453
  },
  "LinearStack": {
    "bottom20_168h_precision": 0.4103693181818178,
    "forecast_price_spike_MAE": null,
    "high_price_regime_MAE": 1.5264111765208273,
    "large_price_ramp_MAE": 1.0609300323819737,
    "low_price_detection": {
      "f1": 0.0,
      "fn": 4280,
      "fp": 0,
      "precision": 0.0,
      "recall": 0.0,
      "tp": 0
    },
    "low_price_regime_MAE": 0.26506688436725817,
    "ramp_detection": {
      "f1": 0.39062499999999994,
      "fn": 1007,
      "fp": 397,
      "precision": 0.5312868949232585,
      "recall": 0.3088538091969801,
      "tp": 450
    },
    "rows": 59136,
    "spearman": 0.6039239680831051,
    "spike_detection": {
      "f1": 0.0,
      "fn": 1587,
      "fp": 0,
      "precision": 0.0,
      "recall": 0.0,
      "tp": 0
    },
    "top20_168h_precision": 0.38423295454545453
  },
  "MedianEnsemble": {
    "bottom20_168h_precision": 0.4082386363636358,
    "forecast_price_spike_MAE": 0.994181927098709,
    "high_price_regime_MAE": 1.202194766427793,
    "large_price_ramp_MAE": 1.06409596067083,
    "low_price_detection": {
      "f1": 0.05038236617183986,
      "fn": 4168,
      "fp": 54,
      "precision": 0.6746987951807228,
      "recall": 0.026168224299065422,
      "tp": 112
    },
    "low_price_regime_MAE": 0.29567209764423735,
    "ramp_detection": {
      "f1": 0.2448753462603878,
      "fn": 1236,
      "fp": 127,
      "precision": 0.6350574712643678,
      "recall": 0.151681537405628,
      "tp": 221
    },
    "rows": 59136,
    "spearman": 0.6107262317760902,
    "spike_detection": {
      "f1": 0.0034602076124567475,
      "fn": 1584,
      "fp": 144,
      "precision": 0.02040816326530612,
      "recall": 0.001890359168241966,
      "tp": 3
    },
    "top20_168h_precision": 0.3975852272727274
  },
  "ResidualCorrection_LightGBM": {
    "bottom20_168h_precision": 0.32769886363636314,
    "forecast_price_spike_MAE": 0.5826512903348186,
    "high_price_regime_MAE": 1.4726506793383487,
    "large_price_ramp_MAE": 1.0271729996052146,
    "low_price_detection": {
      "f1": 0.27002103219543766,
      "fn": 2611,
      "fp": 6413,
      "precision": 0.206508290027221,
      "recall": 0.3899532710280374,
      "tp": 1669
    },
    "low_price_regime_MAE": 0.2517271325440101,
    "ramp_detection": {
      "f1": 0.28226319135410044,
      "fn": 1013,
      "fp": 1245,
      "precision": 0.26287744227353466,
      "recall": 0.304735758407687,
      "tp": 444
    },
    "rows": 59136,
    "spearman": 0.35974344790753376,
    "spike_detection": {
      "f1": 0.0221316249271986,
      "fn": 1568,
      "fp": 111,
      "precision": 0.14615384615384616,
      "recall": 0.011972274732199117,
      "tp": 19
    },
    "top20_168h_precision": 0.3642045454545457
  },
  "WeightedEnsemble": {
    "bottom20_168h_precision": 0.409801136363636,
    "forecast_price_spike_MAE": 0.9725461600669896,
    "high_price_regime_MAE": 1.200093808420272,
    "large_price_ramp_MAE": 1.0623525564859857,
    "low_price_detection": {
      "f1": 0.05143243852921272,
      "fn": 4166,
      "fp": 39,
      "precision": 0.7450980392156863,
      "recall": 0.02663551401869159,
      "tp": 114
    },
    "low_price_regime_MAE": 0.29758879617044276,
    "ramp_detection": {
      "f1": 0.23751387347391786,
      "fn": 1243,
      "fp": 131,
      "precision": 0.6202898550724638,
      "recall": 0.14687714481811942,
      "tp": 214
    },
    "rows": 59136,
    "spearman": 0.6115767115662537,
    "spike_detection": {
      "f1": 0.003484320557491289,
      "fn": 1584,
      "fp": 132,
      "precision": 0.022222222222222223,
      "recall": 0.001890359168241966,
      "tp": 3
    },
    "top20_168h_precision": 0.39744318181818206
  },
  "XGBoost": {
    "bottom20_168h_precision": 0.403835227272727,
    "forecast_price_spike_MAE": 0.9348498049818031,
    "high_price_regime_MAE": 1.1852621573739512,
    "large_price_ramp_MAE": 1.0434924319483878,
    "low_price_detection": {
      "f1": 0.09405196478419584,
      "fn": 4061,
      "fp": 158,
      "precision": 0.5809018567639257,
      "recall": 0.05116822429906542,
      "tp": 219
    },
    "low_price_regime_MAE": 0.27856450169130353,
    "ramp_detection": {
      "f1": 0.25504782146652494,
      "fn": 1217,
      "fp": 185,
      "precision": 0.5647058823529412,
      "recall": 0.16472203157172272,
      "tp": 240
    },
    "rows": 59136,
    "spearman": 0.5841218660486119,
    "spike_detection": {
      "f1": 0.018952062430323303,
      "fn": 1570,
      "fp": 190,
      "precision": 0.0821256038647343,
      "recall": 0.010712035286704474,
      "tp": 17
    },
    "top20_168h_precision": 0.39502840909090914
  }
}
```
