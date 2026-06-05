# P0054L2 Ranking Spike Ramp Results

```json
{
  "baseline": {
    "bottom20_168h_precision": 0.31235795454545423,
    "forecast_price_spike_MAE": 1.1412882630076173,
    "high_price_regime_MAE": 0.9900511877756792,
    "large_price_ramp_MAE": 1.7180335706932024,
    "low_price_detection": {
      "f1": 0.2916140874153952,
      "fn": 3009,
      "fp": 3166,
      "precision": 0.2864548118097814,
      "recall": 0.2969626168224299,
      "tp": 1271
    },
    "low_price_regime_MAE": 0.226879251752336,
    "ramp_detection": {
      "f1": 0.0,
      "fn": 1457,
      "fp": 0,
      "precision": 0.0,
      "recall": 0.0,
      "tp": 0
    },
    "rows": 59136,
    "spearman": 0.5299723887225151,
    "spike_detection": {
      "f1": 0.14163768574138474,
      "fn": 1363,
      "fp": 1352,
      "precision": 0.14213197969543148,
      "recall": 0.14114681789540012,
      "tp": 224
    },
    "top20_168h_precision": 0.30213068181818203
  },
  "models": {
    "Ensemble": {
      "bottom20_168h_precision": 0.408522727272727,
      "forecast_price_spike_MAE": 0.9751497079305887,
      "high_price_regime_MAE": 1.1991714559732758,
      "large_price_ramp_MAE": 1.0618789171235719,
      "low_price_detection": {
        "f1": 0.05054151624548737,
        "fn": 4168,
        "fp": 40,
        "precision": 0.7368421052631579,
        "recall": 0.026168224299065422,
        "tp": 112
      },
      "low_price_regime_MAE": 0.29742715955810123,
      "ramp_detection": {
        "f1": 0.23862375138734737,
        "fn": 1242,
        "fp": 130,
        "precision": 0.6231884057971014,
        "recall": 0.14756348661633492,
        "tp": 215
      },
      "rows": 59136,
      "spearman": 0.6116733985652962,
      "spike_detection": {
        "f1": 0.003482298316889147,
        "fn": 1584,
        "fp": 133,
        "precision": 0.022058823529411766,
        "recall": 0.001890359168241966,
        "tp": 3
      },
      "top20_168h_precision": 0.39786931818181837
    },
    "ExtraTrees": {
      "bottom20_168h_precision": 0.4025568181818182,
      "forecast_price_spike_MAE": 0.88334027142338,
      "high_price_regime_MAE": 1.2009788014892446,
      "large_price_ramp_MAE": 1.08593115809146,
      "low_price_detection": {
        "f1": 0.025252525252525252,
        "fn": 4225,
        "fp": 21,
        "precision": 0.7236842105263158,
        "recall": 0.012850467289719626,
        "tp": 55
      },
      "low_price_regime_MAE": 0.33138767897769583,
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
}
```
